#-*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from smsapi.client import SmsAPI

class SmsBackend(object):
    """
    SMSAPI backend implementation.

    SMSApi is a polish sms service provider see _`https://www.smsapi.pl/` for
    more information.
    """
    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        self.username = kwargs.get('username', None)
        self.password = kwargs.get('password', None)
        self.auth_token = kwargs.get('auth_token', None)
        if not self.username and not self.password and not self.auth_token:
            raise ImproperlyConfigured(
                'Please provide user credentials or auth_token for SMSApi '
                'backend in settings'
            )
        self.api = SmsAPI(
            username=self.username, password=self.password,
            auth_token=self.auth_token
        )

    def send_messages(self, messages):
        """
        Sends one or more SmsMessage objects and returns the number of messages sent
        """
        for message in messages:
            self.api.service('sms').action('send')
            self.api.set_content(message.body)
            self.api.set_to(message.to)
            self.api.execute()
        return len(messages)