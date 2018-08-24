from __future__ import unicode_literals

from six import text_type

from django.core.exceptions import ValidationError
from django.template import Template, TemplateSyntaxError, TemplateDoesNotExist

def validate_template_syntax(source):
    """
    Basic Django Template syntax validation. This allows for robuster template
    authoring.
    """
    try:
        Template(source)
    except (TemplateSyntaxError, TemplateDoesNotExist) as err:
        raise ValidationError(text_type(err))
