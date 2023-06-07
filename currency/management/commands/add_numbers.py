from django.core.management.base import BaseCommand, CommandError
from currency.tasks import plus


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument('x', type=int)
        parser.add_argument('y', type=int)

    def handle(self, *args, **options):
        x = options.get('x')
        y = options.get('y')

        plus.delay(x, y)