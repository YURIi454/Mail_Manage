from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import AttemptSend, Newsletter


class Command(BaseCommand):
    """ Запуск главного реактора.
              Отойдите на безопасное расстояние. """

    help = "Запускает рассылку."

    def add_arguments(self, parser):
        parser.add_argument(
            '--newsletter_id',
            type=int,
            required=True,
            help="ID рассылки.",
        )
        parser.add_argument(
            "--owner_id",
            type=int,
            required=False,
            default=None,
            help="ID владельца рассылки (для проверки прав).",
        )

    def handle(self, *args, **options):
        newsletter_id = options['newsletter_id']
        owner_id = options.get('owner_id')

        try:
            if owner_id:
                newsletter = Newsletter.objects.prefetch_related('recipients').get(
                    pk=newsletter_id, owner_id=owner_id,
                )
            else:
                newsletter = Newsletter.objects.prefetch_related('recipients').get(pk=newsletter_id)
        except Newsletter.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Рассылка с номером ({newsletter_id}) не найдена."))
            return

        now = timezone.now()

        if not (newsletter.start_time <= now <= newsletter.end_time):
            self.stderr.write(self.style.ERROR(
                f"Рассылка ({newsletter_id}) не запущена: текущее время вне периода отправки "
                f"({newsletter.start_time:%d.%m.%Y %H:%M} — {newsletter.end_time:%d.%m.%Y %H:%M})."
            ))
            return

        if newsletter.message is None:
            self.stderr.write(self.style.ERROR(f"У рассылки ({newsletter_id}) не указано сообщение."))
            return

        recipients = list(newsletter.recipients.all())

        if not recipients:
            self.stderr.write(self.style.WARNING(f"У рассылки ({newsletter_id}) нет получателей."))
            return

        subject = newsletter.message.message_topic
        body = newsletter.message.message or ""
        from_email = settings.DEFAULT_FROM_EMAIL

        success_count = 0

        for recipient in recipients:
            try:
                send_mail(subject, body, from_email, [recipient.email], fail_silently=False)
            except Exception as e:
                AttemptSend.objects.create(
                    newsletter=newsletter,
                    recipient=recipient,
                    status="fail",
                    server_response=f"{type(e).__name__}: {e}",
                )
                self.stderr.write(self.style.WARNING(f"Ошибка отправки на {recipient.email}: {e}"))
            else:
                AttemptSend.objects.create(
                    newsletter=newsletter,
                    recipient=recipient,
                    status="success",
                    server_response="Письмо принято почтовым сервером.",
                )
                success_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Рассылка ({newsletter_id}): успешно отправлено {success_count} из {len(recipients)}."
        ))
