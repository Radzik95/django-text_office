# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
import logging
import json
from raven.contrib.django.raven_compat.models import client

from six import PY2

logger = logging.getLogger(__name__)


class SmsBackend(object):
    """
    JUST Send backend implementation.

    SMSApi is a polish sms service provider see _`https://justsend.pl/` for
    more information.
    """
    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        self.api_key = kwargs.get("api_key", None)
        self.sender = kwargs.get("sender", "")
        self.bulk_variant = kwargs.get("bulk_variant", "")
        self.url = "https://justsend.pl/api/rest/message/send/{key}"

    def __repr__(self):
        r = ("<justsend.SMSBackend {{'sender': {sender}, "
             "'bulk_variant': {bulk_variant}}}>").format(
                sender=self.sender, bulk_variant=self.bulk_variant
        )
        if PY2:
            r = r.encode('ascii', errors='replace')
        return r

    def send_messages(self, messages):
        """
        Sends one or more SmsMessage objects and returns the number of messages sent
        """
        for message in messages:
            try:
                sender = message.from_phone or self.sender
                logger.debug("Executing JustSend API. Sending {count} messages "
                    "from {sender}".format(
                    count=len(message.to), sender=sender
                ))
                request_json = {
                    "from": sender,
                    "to": message.to[0],
                    "message": message.body,
                    "bulkVariant": self.bulk_variant
                }
                response = requests.post(
                    url=self.url.format(key=self.api_key),
                    json=request_json
                )
                logger.debug("Executed JustSend API. Result: {response}".format(
                    response=response
                ))
                if response.status_code != 200:
                    if self.fail_silently:
                        logger.error(
                            "JustSend API request failed",
                            extra={
                                'stack': True,
                                'response_text': response.text,
                            },

                        )
                    else:
                        client.extra_context({
                            'stack': True,
                            'request_json': request_json,
                            'reponse_text': response.text,
                        })
                        raise Exception("Error invoking JustSend API")
                else:
                    result = response.json()
                    if result['responseCode'] != 'OK':
                        if self.fail_silently:
                            logger.error(
                                "Sending SMS via JustSend API failed",
                                extra={'stack': True,}
                            )
                        else:
                            client.extra_context({
                                'reponse_text': response.text,
                            })
                            raise Exception(
                                "Error sending SMS using JustSend API"
                            )
            except Exception as e:
                if not self.fail_silently:
                    raise
        return len(messages)
