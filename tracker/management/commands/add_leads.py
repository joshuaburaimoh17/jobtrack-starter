import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from tracker.models import Application, JobLead


class Command(BaseCommand):
    help = ('Add job leads from a UTF-8 JSON file: a list of objects with company, role, '
            'location, salary_range, job_description, source_url. Skips duplicates '
            '(same source_url, or same company+role already tracked). Usage: add_leads leads.json')

    def add_arguments(self, parser):
        parser.add_argument('json_file')

    def handle(self, *args, **opts):
        try:
            items = json.loads(Path(opts['json_file']).read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as e:
            raise CommandError(f"Could not read {opts['json_file']}: {e}")
        if isinstance(items, dict):
            items = [items]
        for item in items:
            company = (item.get('company') or '').strip()
            role = (item.get('role') or '').strip()
            if not company or not role or not item.get('job_description'):
                raise CommandError(f'Each lead needs company, role and job_description: {item}')
            url = item.get('source_url') or None
            dupe = (
                (url and JobLead.objects.filter(source_url=url).exists())
                or JobLead.objects.filter(company__iexact=company, role__iexact=role).exists()
                or Application.objects.filter(company__iexact=company, role__iexact=role).exists()
            )
            if dupe:
                self.stdout.write(f'SKIPPED (already tracked): {role} at {company}')
                continue
            lead = JobLead.objects.create(
                company=company,
                role=role,
                location=item.get('location', ''),
                salary_range=item.get('salary_range') or 'Not disclosed',
                job_description=item['job_description'],
                source_url=url,
            )
            self.stdout.write(f'Added lead {lead.pk}: {role} at {company}')
