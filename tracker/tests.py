from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import ApplicationForm
from .models import Application, JobLead


class MarkAppliedTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', password='x')
        self.client.force_login(self.user)
        self.lead = JobLead.objects.create(
            company='Acme',
            role='Data Analyst',
            location='Dublin, Ireland',
            salary_range='€35k–€40k',
            job_description='Analyse data.',
            source_url='https://example.com/jobs/1',
            status=JobLead.STATUS_READY,
        )

    def test_mark_applied_creates_linked_application(self):
        response = self.client.post(reverse('tracker:mark_applied', args=[self.lead.pk]))

        self.lead.refresh_from_db()
        application = self.lead.application
        self.assertIsNotNone(application)
        self.assertRedirects(response, reverse('tracker:application_detail', args=[application.pk]))
        self.assertEqual(self.lead.status, JobLead.STATUS_APPLIED)
        self.assertEqual(application.company, 'Acme')
        self.assertEqual(application.role, 'Data Analyst')
        self.assertEqual(application.location, 'Dublin, Ireland')
        self.assertEqual(application.salary_range, '€35k–€40k')
        self.assertEqual(application.job_url, 'https://example.com/jobs/1')
        self.assertEqual(application.job_description, 'Analyse data.')
        self.assertEqual(application.status, Application.STATUS_APPLIED)
        self.assertEqual(application.date_applied, date.today())
        self.assertIsNotNone(application.status_updated_at)

    def test_mark_applied_twice_does_not_duplicate(self):
        self.client.post(reverse('tracker:mark_applied', args=[self.lead.pk]))
        self.client.post(reverse('tracker:mark_applied', args=[self.lead.pk]))
        self.assertEqual(Application.objects.count(), 1)


class StatusUpdatedAtTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', password='x')
        self.client.force_login(self.user)
        self.application = Application.objects.create(
            company='Acme',
            role='Data Analyst',
            date_applied=date.today(),
            status=Application.STATUS_APPLIED,
        )

    def test_status_change_sets_timestamp(self):
        self.assertIsNone(self.application.status_updated_at)
        self.client.post(
            reverse('tracker:update_status', args=[self.application.pk]),
            {'status': Application.STATUS_IN_REVIEW},
        )
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Application.STATUS_IN_REVIEW)
        self.assertIsNotNone(self.application.status_updated_at)

    def test_same_status_does_not_set_timestamp(self):
        self.client.post(
            reverse('tracker:update_status', args=[self.application.pk]),
            {'status': Application.STATUS_APPLIED},
        )
        self.application.refresh_from_db()
        self.assertIsNone(self.application.status_updated_at)


class UrlLengthTests(TestCase):
    def test_application_form_accepts_long_job_url(self):
        long_url = 'https://example.com/careers/' + 'a' * 400
        form = ApplicationForm(data={
            'company': 'Acme',
            'role': 'Data Analyst',
            'date_applied': date.today(),
            'status': Application.STATUS_APPLIED,
            'job_url': long_url,
        })
        self.assertTrue(form.is_valid(), form.errors)


# ── Profile + CV tailoring with a CV that is NOT laid out like the default ──

import json
import shutil
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import override_settings
from docx import Document

FRIEND_PROFILE = """# My JobTrack profile

Some notes for Claude that the app ignores.

```yaml
name: Test Friend
cv:
  path: cvs/base_cv.docx
  summary: Profile
  skills: Technical Skills
  experience: Experience
  headings: [Profile, Experience, Technical Skills, Education]
honesty_rules:
  - Never say I led the project.
```
"""


def _make_friend_cv(path: Path):
    doc = Document()
    doc.add_paragraph('Test Friend')
    doc.add_paragraph('PROFILE:')  # case + colon differ from profile.md on purpose
    doc.add_paragraph('Original summary sentence.')
    doc.add_paragraph('')  # spacer that must survive
    doc.add_paragraph('Experience')
    doc.add_paragraph('Shop Assistant, Corner Shop, 2024-2025')
    doc.add_paragraph('- Served customers')
    doc.add_paragraph('Technical Skills')
    doc.add_paragraph('Languages:  Python, SQL')
    doc.add_paragraph('Education')
    doc.add_paragraph('BSc Computing, 2:1')
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(path))


class FriendCVTests(TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / 'profile.md').write_text(FRIEND_PROFILE, encoding='utf-8')
        _make_friend_cv(self.tmp / 'cvs' / 'base_cv.docx')
        self.override = override_settings(
            BASE_DIR=self.tmp,
            PROFILE_PATH=self.tmp / 'profile.md',
            CV_APPLICATIONS_PATH=self.tmp / 'cvs' / 'applications',
        )
        self.override.enable()
        self.lead = JobLead.objects.create(company='Acme', role='Data Analyst', job_description='SQL')

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_profile_yaml_is_read(self):
        from .profile import cv_config, load_settings
        cv = cv_config()
        self.assertEqual(cv['summary'], 'Profile')
        self.assertEqual(cv['path'], self.tmp / 'cvs' / 'base_cv.docx')
        self.assertEqual(load_settings()['honesty_rules'], ['Never say I led the project.'])

    def test_sections_found_with_custom_headings(self):
        from .services.cv_tailor import read_base_sections
        s = read_base_sections()
        self.assertEqual(s['summary'], 'Original summary sentence.')
        self.assertEqual(s['experience'], 'Shop Assistant, Corner Shop, 2024-2025\n- Served customers')
        self.assertEqual(s['skills'], 'Languages:  Python, SQL')

    def test_missing_heading_fails_loudly(self):
        from .services.cv_tailor import CVStructureError, read_base_sections
        (self.tmp / 'profile.md').write_text(
            FRIEND_PROFILE.replace('experience: Experience', 'experience: Work History'), encoding='utf-8')
        with self.assertRaises(CVStructureError) as ctx:
            read_base_sections()
        self.assertIn('Work History', str(ctx.exception))

    def test_save_tailoring_command_builds_docx_with_friend_content(self):
        data = {
            'summary': 'Tailored summary for Acme.',
            'skills': 'Languages:  SQL, Python',
            'experience': 'Shop Assistant, Corner Shop, 2024-2025\n- Served customers and reconciled the till',
            'changes_made': 'Put SQL first.',
        }
        json_path = self.tmp / 'tailored.json'
        json_path.write_text(json.dumps(data), encoding='utf-8')
        call_command('save_tailoring', self.lead.pk, str(json_path), stdout=StringIO())

        self.lead.refresh_from_db()
        self.assertEqual(self.lead.cv_changes, 'Put SQL first.')
        files = list((self.tmp / 'cvs' / 'applications').rglob('*.docx'))
        self.assertEqual(len(files), 1)
        texts = [p.text for p in Document(str(files[0])).paragraphs]
        self.assertIn('Tailored summary for Acme.', texts)
        self.assertIn('- Served customers and reconciled the till', texts)
        self.assertIn('Languages:  SQL, Python', texts)
        self.assertNotIn('Original summary sentence.', texts)
        # Headings, the spacer and untouched sections survive.
        for kept in ('PROFILE:', '', 'Experience', 'Education', 'BSc Computing, 2:1'):
            self.assertIn(kept, texts)


class CommandTests(TestCase):
    def test_add_leads_skips_duplicates(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            f = tmp / 'leads.json'
            f.write_text(json.dumps([
                {'company': 'Acme', 'role': 'Analyst', 'job_description': 'x', 'source_url': 'https://e.com/1'},
                {'company': 'acme', 'role': 'analyst', 'job_description': 'x', 'source_url': 'https://e.com/2'},
            ]), encoding='utf-8')
            out = StringIO()
            call_command('add_leads', str(f), stdout=out)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual(JobLead.objects.count(), 1)
        self.assertIn('SKIPPED', out.getvalue())

    def test_apply_lead_and_set_status(self):
        lead = JobLead.objects.create(company='Acme', role='Analyst', job_description='x')
        call_command('apply_lead', lead.pk, stdout=StringIO())
        lead.refresh_from_db()
        app = lead.application
        self.assertEqual(app.status, Application.STATUS_APPLIED)
        self.assertIsNotNone(app.status_updated_at)

        call_command('set_status', app.pk, 'rejected', note='Email 4 Nov', stdout=StringIO())
        app.refresh_from_db()
        self.assertEqual(app.status, Application.STATUS_REJECTED)
        self.assertIn('Email 4 Nov', app.notes)

    def test_dismiss_lead_deletes_its_tailored_cv(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            month = tmp / 'November 2026'
            month.mkdir()
            mine = month / 'Acme_Analyst_2026-11-04.docx'
            other = month / 'Globex_Analyst_2026-11-04.docx'
            mine.write_bytes(b'x')
            other.write_bytes(b'x')
            lead = JobLead.objects.create(company='Acme', role='Analyst', job_description='x')
            with override_settings(CV_APPLICATIONS_PATH=tmp):
                call_command('dismiss_lead', lead.pk, stdout=StringIO())
            lead.refresh_from_db()
            self.assertEqual(lead.status, JobLead.STATUS_DISMISSED)
            self.assertFalse(mine.exists())
            self.assertTrue(other.exists())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_set_goal(self):
        from .models import GoalSetting
        call_command('set_goal', 80, '--start', '2026-11-01', '--end', '2027-01-31', stdout=StringIO())
        goal = GoalSetting.load()
        self.assertEqual((goal.target, str(goal.window_end)), (80, '2027-01-31'))


class PagesRenderTests(TestCase):
    def test_every_page_loads(self):
        self.client.force_login(User.objects.create_user('tester', password='x'))
        lead = JobLead.objects.create(company='Acme', role='Analyst', job_description='x')
        app = Application.objects.create(company='Acme', role='Analyst', date_applied=date.today())
        for name, args in [
            ('tracker:dashboard', []), ('tracker:analytics', []), ('tracker:application_list', []),
            ('tracker:application_add', []), ('tracker:application_detail', [app.pk]),
            ('tracker:job_queue', []), ('tracker:add_job', []), ('tracker:job_lead_detail', [lead.pk]),
            ('tracker:cv_archive', []),
        ]:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 200)
