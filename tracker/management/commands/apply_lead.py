from datetime import date

from django.core.management.base import BaseCommand, CommandError

from tracker.models import JobLead
from tracker.services.applications import mark_lead_applied


class Command(BaseCommand):
    help = ('Mark queued lead(s) as applied: exactly what the Apply button does. '
            'Usage: apply_lead 4 7 9 [--date 2026-11-04]')

    def add_arguments(self, parser):
        parser.add_argument('lead_ids', nargs='+', type=int)
        parser.add_argument('--date', type=date.fromisoformat, default=None,
                            help='Date applied (YYYY-MM-DD). Default: today.')

    def handle(self, *args, **opts):
        for pk in opts['lead_ids']:
            try:
                lead = JobLead.objects.get(pk=pk)
            except JobLead.DoesNotExist:
                raise CommandError(f'No lead with id {pk}.')
            app, created = mark_lead_applied(lead, opts['date'])
            verb = 'Created' if created else 'Already applied:'
            self.stdout.write(f'{verb} application {app.pk}: {app.role} at {app.company}')
