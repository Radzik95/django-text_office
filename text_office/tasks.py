# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from text_office.models import STATUS
from celery import task

from text_office.models import SMS

logger = logging.getLogger(__name__)


@task(bind=True, max_retries=3, default_retry_delay=30)
def send_sms(self, sms_id):
    sms = SMS.objects.get(pk=sms_id)
    logger.debug('Starting celery task send_sms with id: %s', sms_id)
    try:
        sms.sms_message().send()
    except Exception as e:
        logger.warning(
            'Sending sms failed. Retrying...',
            extra={'sms_id': sms_id}, exc_info=True
        )
        raise self.retry(exc=e)
    logger.debug(u'Celery task send_sms id %s successful', sms_id)
    return sms_id


@task()
def send_sms_callback(sms_id):
    sms = SMS.objects.get(pk=sms_id)
    sms.status = STATUS.sent
    sms.save(update_fields=['status'])


@task()
def send_sms_errback(task_id, sms_id):
    sms = SMS.objects.get(pk=sms_id)
    sms.status = STATUS.failed
    sms.save(update_fields=['status'])
