from django.contrib import admin

from mailing.models import MailingRecipient, YourMessage, Newsletter, AttemptSend


@admin.register(MailingRecipient)
class MailingRecipientAdmin(admin.ModelAdmin):
    """ Отображение получателей рассылки в админ-панели"""

    list_display = ("email", "recipient_data", "comment", "owner", "created_at",)
    list_filter = ("email",)
    search_fields = ("email", "owner")


@admin.register(YourMessage)
class YourMessageAdmin(admin.ModelAdmin):
    """ Отображение сообщения в админ-панели"""

    exclude = ['message']
    list_display = ("message_topic", "owner", "created_at")
    list_filter = ("owner",)
    search_fields = ("owner",)


@admin.register(Newsletter)
class NewsletterRecipientAdmin(admin.ModelAdmin):
    """ Отображение рассылки в админ-панели"""

    list_display = ("created_at", "started_at", "stopped_at", "status", "owner",)
    list_filter = ("owner",)
    search_fields = ("owner",)


@admin.register(AttemptSend)
class AttemptSendAdmin(admin.ModelAdmin):
    """ Отображение попытки рассылки в админ-панели"""

    list_display = ("created_at", "status", "newsletter", "recipient",)
    list_filter = ("status",)
    search_fields = ("newsletter",)
