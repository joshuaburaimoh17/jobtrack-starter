import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from tracker.models import JobLead


class Command(BaseCommand):
    help = ('Dismiss lead(s) (= the Dismiss button) and delete their tailored CVs from the archive, '
            'so it only holds CVs that were actually sent. Usage: dismiss_lead 5 6 [--keep-cv]')

    def add_arguments(self, parser):
        parser.add_argument('lead_ids', nargs='+', type=int)
        parser.add_argument('--keep-cv', action='store_true', help="Don't delete the tailored CV files.")

    def handle(self, *args, **opts):
        root = Path(settings.CV_APPLICATIONS_PATH)
        for pk in opts['lead_ids']:
            try:
                lead = JobLead.objects.get(pk=pk)
            except JobLead.DoesNotExist:
                raise CommandError(f'No lead with id {pk}.')
            lead.status = JobLead.STATUS_DISMISSED
            lead.save(update_fields=['status'])
            removed = []
            if not opts['keep_cv'] and root.exists():
                # Same naming as cv_tailor.build_tailored_docx: <company>_<role>_<date>.docx
                prefix = f"{re.sub(r'[^\w]', '_', lead.company)[:30]}_{re.sub(r'[^\w]', '_', lead.role)[:30]}_"
                for f in root.glob(f'*/{prefix}*.docx'):
                    f.unlink()
                    removed.append(f.name)
            extra = f' (deleted {", ".join(removed)})' if removed else ''
            self.stdout.write(f'Dismissed lead {pk}: {lead.role} at {lead.company}{extra}')
