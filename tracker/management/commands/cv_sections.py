from django.core.management.base import BaseCommand, CommandError

from tracker.profile import ProfileError, cv_config
from tracker.services.cv_tailor import CVStructureError, read_base_sections


class Command(BaseCommand):
    help = ('Print the base CV sections that tailoring rewrites (summary / skills / experience), '
            'using the heading map in profile.md. Fails loudly if a heading is not found. '
            '--all lists every paragraph with its Word style, which helps map headings during setup.')

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true')

    def handle(self, *args, **opts):
        try:
            cv = cv_config()
            if opts['all']:
                from docx import Document
                if not cv['path'].exists():
                    raise CommandError(f"No CV at {cv['path']}.")
                doc = Document(str(cv['path']))
                for i, p in enumerate(doc.paragraphs):
                    if p.text.strip():
                        self.stdout.write(f'{i:>3} [{p.style.name}] {p.text.strip()}')
                if doc.tables:
                    self.stdout.write(
                        f'\nNOTE: this CV has {len(doc.tables)} table(s). Text inside tables is NOT '
                        'listed above and cannot be tailored.'
                    )
                return
            sections = read_base_sections()
        except (ProfileError, CVStructureError) as e:
            raise CommandError(str(e))
        for key in ('summary', 'skills', 'experience'):
            heading = cv.get(key) or '(not configured)'
            self.stdout.write(f'=== {key.upper()}  <- heading "{heading}" ===')
            self.stdout.write(sections[key] or '(empty)')
            self.stdout.write('')
