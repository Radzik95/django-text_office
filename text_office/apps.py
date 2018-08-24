from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from django.apps import AppConfig, apps as django_apps
from django.conf import settings
from django.core.checks import Error, register


class TextOfficeConfig(AppConfig):
    name = 'text_office'
    verbose_name = 'Text Office'


@register()
def text_office_configuration_check(app_configs, **kwargs):
    errors = []
    if not hasattr(settings, 'TEXT_OFFICE'):
        errors.append(
            Error(
                _('Missing configuration parameter ``TEXT_OFFICE``'),
                hint=_('Please configure ``TEXT_OFFICE`` in settings '
                        'with BACKENDS parameter.'),
                obj=django_apps.get_app_config('text_office'),
                id='text_office.E001',
            )
        )
    return errors
