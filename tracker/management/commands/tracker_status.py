from django.core.management.base import BaseCommand
from django.utils import timezone

from tracker.models import Application, GoalSetting, JobLead


class Command(BaseCommand):
    help = 'One-screen summary for Claude: every application and open lead with ids, statuses and ages.'

    def handle(self, *args, **opts):
        now = timezone.now()
        apps = Application.objects.order_by('-date_applied')
        self.stdout.write(f'APPLICATIONS ({apps.count()})')
        for a in apps:
            days = (now - (a.status_updated_at or now)).days
            flag = '  <- 3+ weeks silent, treat as a no' if a.status == Application.STATUS_APPLIED and days >= 21 else ''
            follow = f' | follow-up {a.follow_up_date}' if a.follow_up_date else ''
            self.stdout.write(
                f'  [{a.pk}] {a.company} | {a.role} | {a.status} | applied {a.date_applied} '
                f'| status set {days}d ago{follow}{flag}'
            )

        leads = JobLead.objects.exclude(status=JobLead.STATUS_APPLIED).order_by('status', '-date_found')
        self.stdout.write(f'\nLEADS NOT YET APPLIED ({leads.count()})')
        for lead in leads:
            cv = 'CV ready' if lead.cv_tailored_json else 'no CV'
            self.stdout.write(
                f'  [{lead.pk}] {lead.company} | {lead.role} | {lead.status} | {cv} | {lead.source_url or "-"}'
            )

        goal = GoalSetting.load()
        n = Application.objects.filter(date_applied__range=(goal.window_start, goal.window_end)).count()
        self.stdout.write(f'\nGOAL: {n}/{goal.target} applications between {goal.window_start} and {goal.window_end}')
