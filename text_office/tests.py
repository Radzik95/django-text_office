# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sendsms

from unittest.case import skip

from django.test import TestCase
from django.test.utils import override_settings

from text_office.models import SMS, STATUS, PRIORITY, SMSTemplate


class SMSManagerTest(TestCase):
    def test_create(self):
        sms = SMS.objects.create(
            recipient='+48666000000',
            message='test', backend_alias='default'
        )
        self.assertIsNotNone(sms.pk)
        self.assertEquals(sms.status, STATUS.queued)

    def test_create_from_template(self):
        template = SMSTemplate.objects.create(
            name='test_template',
            description='test',
            content='{{var}} test'
        )
        sms = SMS.objects.create(
            recipient='+48666000000', template=template,
            context={'var': 'test'}, backend_alias='default',

        )
        self.assertEquals(sms.message, 'test test')
        self.assertIsNone(sms.template)

    def test_create_from_template_nonserializable(self):
        class NonSerializableClass(object):
            def __repr__(self):
                return 'test'

        template = SMSTemplate.objects.create(
            name='test_template',
            description='test',
            content='{{var}} test'
        )
        sms = SMS.objects.create(
            recipient='+48666000000', template=template,
            context={'var': NonSerializableClass()}, backend_alias='default',
        )
        self.assertEquals(sms.message, 'test test')


@override_settings(
    TEXT_OFFICE = {
        'BACKENDS': {
            'default': {
                'class': 'sendsms.backends.locmem.SmsBackend',
            }
        }
    }
)
class SMSTest(TestCase):

    def test_send_now(self):
        sms = SMS.objects.create(
            recipient='+48666000000', priority=PRIORITY.now,
            backend_alias='default',
        )
        self.assertEquals(sms.status, STATUS.sent)

    def test_no_backend_passed(self):
        sms = SMS.objects.create(
            recipient='+48666000000'
        )
        sms.dispatch()
        self.assertEquals(sms.status, STATUS.sent)


@override_settings(
    TEXT_OFFICE = {
        'BACKENDS': {
            'default': {
                'class': 'sendsms.backends.locmem.SmsBackend',
            }
        }
    }
)
class NoRelayTest(TestCase):
    """
    Text office dispatches a text message without relay.
    """

    def setUp(self):
        self.sms = SMS.objects.create(
            sender='+48604353503', recipient='+48604353503',
            message='test', backend_alias='default'
        )

    def test_dispatch(self):
        self.assertEquals(self.sms.status, STATUS.queued)
        self.sms.dispatch()
        self.assertEquals(self.sms.status, STATUS.sent)


@override_settings(
    TEXT_OFFICE = {
        'BACKENDS': {
            'default': {
                'class': 'sendsms.backends.locmem.SmsBackend',
                'relay': {
                    'class': 'text_office.relays.CeleryRelay',
                }
            }
        }
    },
    CELERY_ALWAYS_EAGER=True,
)
class CeleryRelayTest(TestCase):

    def setUp(self):
        from celery import Celery
        app = Celery()
        app.config_from_object('django.conf:settings')
        from text_office.tasks import send_sms
        app.tasks.register(send_sms)
        self.sms = SMS.objects.create(
            sender='+48604353503', recipient='+48604353503',
            message='test', backend_alias='default'
        )

    def test_dispatch_successful(self):
        self.assertEquals(self.sms.status, STATUS.queued)
        self.sms.dispatch()
        self.sms.refresh_from_db()
        self.assertEquals(self.sms.status, STATUS.sent)
        self.assertEquals(len(sendsms.outbox), 1)



@override_settings(
    TEXT_OFFICE = {
        'BACKENDS': {
            'default': {
                'class': 'text_office.backends.sms_api.SmsBackend',
                'settings': {
                    'auth_token': 'badtokenanyway'
                }
            }
        }
    },
)
@skip('TODO: Patch requests')
class SMSApiBackendTest(TestCase):

    def setUp(self):
        self.sms = SMS.objects.create(
            sender='+48604353503', recipient='+48604353503',
            message='test', backend_alias='default'
        )

    def test_dispatch(self):
        self.assertEquals(self.sms.status, STATUS.queued)
        self.sms.dispatch()
        self.assertEquals(self.sms.status, STATUS.sent)
        self.assertEquals(len(sendsms.outbox), 1)


@override_settings(
    TEXT_OFFICE = {
        'BACKENDS': {
            'default': {
                'class': 'text_office.backends.justsend.SmsBackend',
                'settings': {
                    'sender': 'Test',
                    'bulk_variant': 'PRO'
                }
            }
        }
    },
)
# @skip('TODO: Patch requests')
class JustSendBackendTest(TestCase):

    def setUp(self):
        self.sms = SMS.objects.create(
            recipient='+48666000000',
            message='test', backend_alias='default'
        )

    def test_dispatch(self):
        self.assertEquals(self.sms.status, STATUS.queued)
        self.sms.dispatch()
        self.assertEquals(self.sms.status, STATUS.sent)
