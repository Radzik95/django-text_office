# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import importlib


from collections import namedtuple

from django.conf import settings
from django.db import models
from django.template import Context, Template
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from phonenumber_field.modelfields import PhoneNumberField
from sendsms.message import SmsMessage
from sendsms.api import get_connection
from six import text_type

from text_office.validators import validate_template_syntax

PRIORITY = namedtuple('PRIORITY', 'low medium high now')._make(range(4))
STATUS = namedtuple('STATUS', 'sent failed dispatched queued')._make(range(4))

logger = logging.getLogger(__name__)


class SMSManager(models.Manager):

    def create(self, render_on_delivery=False, *args, **kwargs):
        """
        Creates a SMS from supplied keyword arguments. If template is
        specified, email subject and content will be rendered during delivery.
        """
        kwargs.pop('status', None)
        priority = kwargs.get('priority', PRIORITY.medium)
        status = None if priority == PRIORITY.now else STATUS.queued
        context = kwargs.get('context', '')

        # If email is to be rendered during delivery, save all necessary
        # information
        if render_on_delivery:
            sms = super(SMSManager, self).objects.create(*args, **kwargs)
        else:
            template = kwargs.get('template', None)
            if template:
                message = template.content
            else:
                message = kwargs.pop('message', '')
            _context = Context(context or {})
            message = Template(message).render(_context)
            sms = super(SMSManager, self).create(
                status=status, message=message,
                *args, **kwargs
            )
        if priority == PRIORITY.now:
            sms.dispatch()

        return sms


@python_2_unicode_compatible
class SMS(models.Model):
    """
    A model to hold SMS message information.
    """

    PRIORITY_CHOICES = [(PRIORITY.low, _("low")), (PRIORITY.medium, _("medium")),
                        (PRIORITY.high, _("high")), (PRIORITY.now, _("now"))]
    STATUS_CHOICES = [
        (STATUS.sent, _("sent")), (STATUS.failed, _("failed")),
        (STATUS.dispatched, _("dispatched")), (STATUS.queued,_("queued"))
    ]

    sender = models.CharField(
        max_length=32, verbose_name=_("Sender"),
        help_text=_("Sender number or name"), null=True, blank=True
    )
    recipient = PhoneNumberField(_("Phone Number To"))
    message = models.TextField(_("Message"), blank=True)
    status = models.PositiveSmallIntegerField(
        _("Status"),
        choices=STATUS_CHOICES, db_index=True,
        blank=True, null=True)
    priority = models.PositiveSmallIntegerField(_("Priority"),
                                                choices=PRIORITY_CHOICES,
                                                blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_updated = models.DateTimeField(db_index=True, auto_now=True)
    scheduled_time = models.DateTimeField(_('The scheduled sending time'),
                                          blank=True, null=True, db_index=True)
    template = models.ForeignKey('text_office.SMSTemplate', blank=True,
                                 null=True, verbose_name=_('Message template'))
    context = JSONField(_('Context'), blank=True, null=True)
    backend_alias = models.CharField(_('Backend alias'), blank=True, default='',
                                     max_length=64)

    objects = SMSManager()

    class Meta:
        app_label = 'text_office'
        verbose_name = _("SMS")
        verbose_name_plural = _("SMS")

    def __init__(self, *args, **kwargs):
        super(SMS, self).__init__(*args, **kwargs)
        self._cached_message = None

    def __str__(self):
        return u'%s' % self.recipient

    def __repr__(self):
        return ("SMS: [sender: {sender}, to: {to}, message: {message}, "
                "status: {status}").format(
            sender=self.sender, to=self.recipient,
            message=self.message[:32] + (self.message[:32] + '...'),
            status=self.status
        )

    def sms_message(self):
        """
        Returns Django EmailMessage object for sending.
        """
        if self._cached_message:
            return self._cached_message

        return self.prepare_message()

    def prepare_message(self):
        """
        Returns a django ``EmailMessage`` or ``EmailMultiAlternatives`` object,
        depending on whether html_message is empty.
        """

        if self.template is not None:
            _context = Context(self.context)
            message = Template(self.template.content).render(_context)

        else:
            message = self.message

        conf = getattr(settings, 'TEXT_OFFICE')
        backend_conf = conf['BACKENDS'].get(self.backend_alias or 'default')
        klass = backend_conf.get('class')
        connection = get_connection(
            klass, **backend_conf.get('settings', {})
        )

        sms = SmsMessage(
            body=message,
            from_phone=self.sender,
            to=[text_type(self.recipient), ],
            connection=connection
        )

        self._cached_sms = sms
        return sms

    def dispatch(self, commit=True):
        """
        Sends SMS using selected backend through relay.

        If no relay is selected, SMS is sent directly using selected backend.
        """
        try:
            conf = getattr(settings, 'TEXT_OFFICE')
            backend_conf = conf['BACKENDS'].get(self.backend_alias or 'default')
            relay_conf = backend_conf.get('relay', None)
            if relay_conf:
                relay_class_path = relay_conf.get('class')
                relay_class_params = relay_conf.get('settings', {})
                split = relay_class_path.split('.')
                relay_module = importlib.import_module('.'.join(split[:-1]))
                relay_class = getattr(
                    relay_module, relay_class_path.split('.')[-1]
                )
                relay = relay_class(**relay_class_params)
                status = STATUS.dispatched
                if commit:
                    self.status = status
                    self.save(update_fields=['status'])
                relay.dispatch(self)
            else:
                self.sms_message().send()
                self.status = STATUS.sent
                self.save(update_fields=['status'])

        except EnvironmentError as e:
            errno, strerror = e.message
            logger.error(
                'Sending SMS message failed', extra={
                    'message_id': self.pk,
                    'errno': errno,
                    'streerror': text_type(
                        strerror.decode('utf-8', errors='replace')
                    ),
                },
                exc_info=True
            )
            self.status = STATUS.failed
            self.save(update_fields=['status'])

        except Exception as e:
            logger.error(
                'Sending SMS message failed', extra={
                    'message_id': self.pk,
                },
                exc_info=True
            )
            self.status = STATUS.failed
            self.save(update_fields=['status'])

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(SMS, self).save(*args, **kwargs)


@python_2_unicode_compatible
class SMSTemplate(models.Model):
    """
    Model to hold template information from db
    """
    name = models.CharField(_("Name"), max_length=255,
                            help_text=_("e.g: 'welcome_email'"))
    description = models.TextField(
        _("Description"), blank=True,
        help_text=_("Description of this template.")
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    content = models.TextField(
        blank=True, verbose_name=_("Content"),
        validators=[validate_template_syntax]
    )
    language = models.CharField(
        max_length=12, verbose_name=_("Language"),
        help_text=_("Render template in alternative language"),
        default='', blank=True
    )
    default_template = models.ForeignKey(
        'self', related_name='translated_templates',
        null=True, default=None, verbose_name=_('Default template')
    )

    class Meta:
        app_label = 'text_office'
        unique_together = ('name', 'language', 'default_template')
        verbose_name = _("Message Template")
        verbose_name_plural = _("Message Templates")

    def __str__(self):
        return u'%s %s' % (self.name, self.language)

    def save(self, *args, **kwargs):
        # If template is a translation, use default template's name
        if self.default_template and not self.name:
            self.name = self.default_template.name

        template = super(SMSTemplate, self).save(*args, **kwargs)
        return template
