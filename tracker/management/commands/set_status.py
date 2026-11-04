from datetime import date

from django.core.management.base import BaseCommand, CommandError

from tracker.models import Application
from tracker.services.applications import set_status


class Command(BaseCommand):
    help = ('Change an application status the right way (status_updated_at moves only on a real change). '
            'Usage: set_status 12 rejected --note "Rejection email 4 Nov" [--follow-up 2026-11-11]. '
            'Statuses: applied, in_review, interview_scheduled, interview_done, offer, rejected, withdrawn')

    def add_arguments(self, parser):
        parser.add_argument('application_id', type=int)
        parser.add_argument('status')
        parser.add_argument('--note', default='', help='Dated line appended to the notes.')
        parser.add_argument('--follow-up', type=date.fromisoformat, default=None,
                            help='Follow-up date YYYY-MM-DD.')

    def handle(self, *args, **opts):
        try:
            app = Application.objects.get(pk=opts['application_id'])
        except Application.DoesNotExist:
            raise CommandError(f"No application with id {opts['application_id']}.")
        if opts['follow_up']:
            app.follow_up_date = opts['follow_up']
        try:
            changed = set_status(app, opts['status'], opts['note'])
        except ValueError as e:
            raise CommandError(str(e))
        self.stdout.write(f"{'Updated' if changed else 'Status unchanged'}: {app} -> {app.get_status_display()}")
