from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from django.contrib import admin
from django.contrib import messages
# Register your models here.
from text_office.models import SMS, STATUS, SMSTemplate


@admin.register(SMS)
class SMSAdmin(admin.ModelAdmin):

    list_display = ('id', 'sender', 'recipient', 'template',
                    'status', 'last_updated')

    list_filter = ['status', 'template']
    date_hierarchy = 'created'
    search_fields = ['sender', 'recipient']

    def get_queryset(self, request):
        return super(SMSAdmin, self).get_queryset(
            request
        ).select_related('template')

    def requeue(self, request, queryset):
        """An admin action to requeue messages."""
        queryset.update(status=STATUS.queued)

    def send(self, request, queryset):
        for sms in queryset.filter(status=STATUS.queued):
            sms.dispatch()
        messages.success(
            request,
            _('Succesfully dispatched {count} sms messages').format(
                count=queryset.count()
            )
        )

    requeue.short_description = _('Requeue selected messages')
    send.short_description = _('Send selected messages')

    actions = [send, requeue]


@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    pass
