from __future__ import unicode_literals

import logging
import sys

from django.core.management.base import BaseCommand

from text_office.models import SMS, STATUS

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Dispatch queued sms to appropriate backend via selected rely ' \
           'channel'

    def handle(self, *args, **options):
        messages = SMS.objects.filter(
            status=STATUS.queued
        )
        self.stdout.write(self.style.INFO('Sending {count} sms messages'.format(
            count=messages.count()
        )))
        for message in messages:
            message.dispatch()
        self.stdout.write(
            self.style.SUCCESS('Dispatched {count} sms messages'.format(
                count=messages.count()
            ))
        )
