import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from tracker.models import JobLead
from tracker.services.cv_tailor import CVStructureError, archive_tailored_docx, save_tailoring


class Command(BaseCommand):
    help = ('Store a CV tailored by Claude on a lead, then build and archive the .docx. '
            'JSON file: {"summary": "...", "skills": "...", "experience": "...", "changes_made": "..."} '
            'with lines separated by newlines and the same line structure as the base CV. '
            'Usage: save_tailoring 4 tailored.json')

    def add_arguments(self, parser):
        parser.add_argument('lead_id', type=int)
        parser.add_argument('json_file')

    def handle(self, *args, **opts):
        try:
            lead = JobLead.objects.get(pk=opts['lead_id'])
        except JobLead.DoesNotExist:
            raise CommandError(f"No lead with id {opts['lead_id']}.")
        try:
            data = json.loads(Path(opts['json_file']).read_text(encoding='utf-8'))
            save_tailoring(lead, data, data.get('changes_made', ''))
            path = archive_tailored_docx(lead)
        except (OSError, json.JSONDecodeError, CVStructureError) as e:
            raise CommandError(str(e))
        self.stdout.write(f'Saved tailored CV for lead {lead.pk} ({lead.role} at {lead.company}): {path}')
