import logging

from django.apps import AppConfig
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save

logger = logging.getLogger(__name__)


def invalidate_response_cache(**kwargs):
    """ Сброс серверного кеша страниц после изменений данных. """

    try:
        cache.clear()
    except Exception:
        logger.warning('Не удалось сбросить кеш страниц.', exc_info=True)


class MailingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailing'

    def ready(self):
        from mailing.models import AttemptSend, MailingRecipient, Newsletter, YourMessage

        for model in (MailingRecipient, YourMessage, Newsletter, AttemptSend):
            post_save.connect(
                invalidate_response_cache,
                sender=model,
                dispatch_uid=f'mailing_cache_save_{model.__name__}',
            )
            post_delete.connect(
                invalidate_response_cache,
                sender=model,
                dispatch_uid=f'mailing_cache_delete_{model.__name__}',
            )
