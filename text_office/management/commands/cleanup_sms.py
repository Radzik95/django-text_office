import datetime

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from text_office.models import SMS


class Command(BaseCommand):
    help = 'Remove messages that were sent long time ago.'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--days',
            type=int,
            default=90,
            help="Cleanup messages older than this many days, defaults to 90."
        )

    def handle(self, verbosity, days, **options):
        self.stdout.write(self.style.INFO(
            "Deletinig sms created before {1}.".format(count, cutoff_date)
        ))
        cutoff_date = now() - datetime.timedelta(days)
        count = SMS.objects.filter(
            created__lt=cutoff_date
        ).delete()
        self.stdout.write(self.style.SUCCESS(
            "Deleted {0} sms created before {1}.".format(count, cutoff_date)
        ))
