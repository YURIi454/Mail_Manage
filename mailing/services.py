from django.utils import timezone

from mailing.models import AttemptSend, MailingRecipient, Newsletter
from users.services import is_manager


def get_main_indicators(user):
    """ Показатели для главной страницы. """

    now = timezone.now()
    newsletters = _get_newsletters(user)

    total_newsletters = newsletters.count()
    active_newsletters = newsletters.filter(
        is_locked=False,
        start_time__lte=now,
        end_time__gte=now,
    ).count()

    if is_manager(user):
        recipients = MailingRecipient.objects.all()
    else:
        recipients = MailingRecipient.objects.filter(owner=user)

    return {
        'total_newsletters': total_newsletters,
        'active_newsletters': active_newsletters,
        'unique_recipients': recipients.distinct().count(),
    }


def get_all_statistic(current_user):
    """ Получение полной статистики. """

    newsletters = _get_newsletters(current_user)
    attempts = AttemptSend.objects.filter(newsletter__in=newsletters)

    total_attempts = attempts.count()
    attempts_success = attempts.filter(status='success').count()
    attempts_fail = attempts.filter(status='fail').count()
    attempts_not_used = attempts.filter(status='not_used').count()

    if total_attempts:
        percent_success = round((attempts_success / total_attempts) * 100, 2)
    else:
        percent_success = 0

    return {
        'messages_count': newsletters.filter(message__isnull=False).values('message').distinct().count(),
        'newsletters_count': newsletters.count(),
        'recipients_count': MailingRecipient.objects.filter(newsletter__in=newsletters).distinct().count(),
        'attempts_not_used': attempts_not_used,
        'attempts_success': attempts_success,
        'attempts_fail': attempts_fail,
        'attempts_total': total_attempts,
        'sent_count': attempts_success,
        'percent_success': percent_success,
    }


def _get_newsletters(user):
    """ Рассылки, доступные пользователю. """

    if is_manager(user):
        return Newsletter.objects.all()

    return Newsletter.objects.filter(owner=user)
