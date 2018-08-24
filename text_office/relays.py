# -*- coding: utf-8 -*-
import logging

from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import connection as db_connection
from django.db.models import Q
from django.template import Context, Template
from django.utils.timezone import now

from text_office.tasks import send_sms, send_sms_callback, send_sms_errback
from .models import SMS, PRIORITY, STATUS

logger = logging.getLogger(__name__)


class Relay(object):

    def dispatch(self, message):
        raise NotImplementedError()


class BasicRelay(Relay):

    def __init__(self, *args, **kwargs):
        pass

    def dispatch(self, message):
        try:
            message.sms_message().send()
        except Exception as e:
            message.status = STATUS.failed
            message.save(fields=['status'])


class CeleryRelay(Relay):

    def dispatch(self, message):
        send_sms.apply_async(
            (message.pk,),
            link=[send_sms_callback.s(),],
            link_error=[send_sms_errback.s(message.pk),],
            eta=message.scheduled_time
        )
