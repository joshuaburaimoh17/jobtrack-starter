from datetime import date

from django.core.management.base import BaseCommand

from tracker.models import GoalSetting


class Command(BaseCommand):
    help = 'Set the dashboard application goal. Usage: set_goal 100 --start 2026-11-04 --end 2027-02-28'

    def add_arguments(self, parser):
        parser.add_argument('target', type=int)
        parser.add_argument('--start', type=date.fromisoformat, default=None)
        parser.add_argument('--end', type=date.fromisoformat, default=None)

    def handle(self, *args, **opts):
        goal = GoalSetting.load()
        goal.target = opts['target']
        if opts['start']:
            goal.window_start = opts['start']
        if opts['end']:
            goal.window_end = opts['end']
        goal.save()
        self.stdout.write(f'Goal: {goal}')
