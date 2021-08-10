# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from six import PY2

logger = logging.getLogger(__name__)


class DummyBackend(object):
    """
    Dummy implementation for testing purposes.

    """
    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently

    def __repr__(self):
        r = "<DummyBackend>"
        if PY2:
            r = r.encode('ascii', errors='replace')
        return r

    def send_messages(self, messages):
        """
        Sends one or more SmsMessage objects and returns the number of messages
        sent
        """
        for message in messages:
            try:
                logger.debug(
                    "Sending SMS via DummyBackend to {to} message: "
                    "\"{message}\"".format(
                        to=message.to, message=message.body
                ))
            except Exception as e:
                if not self.fail_silently:
                    raise
        return len(messages)
