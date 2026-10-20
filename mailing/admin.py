from django.contrib import admin

from mailing.models import AttemptSend, MailingRecipient, Newsletter, YourMessage


@admin.register(MailingRecipient)
class MailingRecipientAdmin(admin.ModelAdmin):
    """ Отображение получателей рассылки в админ-панели"""

    list_display = ("email", "recipient_data", "comment", "owner", "created_at",)
    list_filter = ("email",)
    search_fields = ("email", "owner__email")


@admin.register(YourMessage)
class YourMessageAdmin(admin.ModelAdmin):
    """ Отображение сообщения в админ-панели"""

    list_display = ("message_topic", "owner", "created_at")
    list_filter = ("owner",)
    search_fields = ("message_topic", "owner__email")


@admin.register(Newsletter)
class NewsletterRecipientAdmin(admin.ModelAdmin):
    """ Отображение рассылки в админ-панели"""

    list_display = ("created_at", "start_time", "end_time", "status", "owner",)
    list_filter = ("owner", "is_locked",)
    search_fields = ("name", "owner__email")


@admin.register(AttemptSend)
class AttemptSendAdmin(admin.ModelAdmin):
    """ Отображение попытки рассылки в админ-панели"""

    list_display = ("attempt_time", "status", "newsletter", "recipient",)
    list_filter = ("status",)
    search_fields = ("newsletter__name",)
