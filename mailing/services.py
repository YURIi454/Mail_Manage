from django.db.models import Count, Case, When, Value, IntegerField

from mailing.models import Newsletter


def get_all_statistic(current_user):
    """ Получение полной статистики. """

    if not current_user.is_superuser:
        newsletters = Newsletter.objects.filter(owner=current_user)
    else:
        newsletters = Newsletter.objects.all()

    statistics = newsletters.aggregate(
        messages_count=Count('message', distinct=True),
        recipients_count=Count('recipients', distinct=True),
        attempts_not_used=Count(Case(When(attemptsend__status='not_used', then=Value(1)), output_field=IntegerField())),
        attempts_success=Count(Case(When(attemptsend__status='success', then=Value(1)), output_field=IntegerField())),
        attempts_fail=Count(Case(When(attemptsend__status='fail', then=Value(1)), output_field=IntegerField())),
        attempts_locked=Count(Case(When(attemptsend__status='locked', then=Value(1)), output_field=IntegerField())),
        total_newsletters=Count('*'),
        total_attempts=Count('attemptsend')
    )

    attempts_total = statistics.get('total_attempts', 0)
    attempts_success = statistics.get('attempts_success', 0)

    if attempts_total > 0 and attempts_success is not None:
        percent_success = round((attempts_success / attempts_total) * 100, 2)
    else:
        percent_success = 0

    return {
        'messages_count': statistics.get('messages_count', 0),
        'newsletters_count': statistics.get('total_newsletters', 0),
        'recipients_count': statistics.get('recipients_count', 0),
        'attempts_not_used': statistics.get('attempts_not_used', 0),
        'attempts_success': attempts_success,
        'attempts_fail': statistics.get('attempts_fail', 0),
        'attempts_locked': statistics.get('attempts_locked', 0),
        'attempts_total': attempts_total,
        'percent_success': percent_success,
    }
