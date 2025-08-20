from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mass_mail
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from config.settings import EMAIL_HOST_USER

from mailing.models import Newsletter, AttemptSend, MailingRecipient


class Command(BaseCommand):
    """ Запуск главного реактора.
              Отойдите на безопасное расстояние. """

    help = "Запускает рассылку."

    def add_arguments(self, parser):
        parser.add_argument(
            '--user_id',
            type=int,
            required=True,
            help="ID пользователя.",
        )
        parser.add_argument(
            "--newsletter_id",
            type=int,
            required=True,
            help="ID рассылки.",
        )

    def handle(self, *args, **options):
        user_id = options['user_id']
        newsletter_id = options["newsletter_id"]

        try:
            newsletter = Newsletter.objects.get(pk=newsletter_id, owner__pk=user_id)
        except ObjectDoesNotExist:
            self.stdout.write(f"Рассылка с номером ({newsletter_id}) не найдена.")
            return

        messages = self.get_mass_message(newsletter)

        if len(messages) > 0:
            try:
                result = send_mass_mail(messages)

                if newsletter.status != 'launched':

                    newsletter.status = 'launched'
                    newsletter.started_at = timezone.now()
                    newsletter.stopped_at = timezone.now() + timedelta(days=30)
                    newsletter.save()

                else:
                    self.stdout.write(f"Рассылка ({newsletter_id}) запущена.")

                for message_data in messages:
                    topic, _, _, _ = message_data

                    attempt_send = AttemptSend(
                        newsletter=newsletter,
                        recipient=MailingRecipient.objects.first(),
                        status="success" if result else "fail",
                        server_response=str(result),
                    )
                    attempt_send.save()

            except Exception as e:
                print(f"Ошибка отправки: {e}")

                for message_data in messages:
                    topic, _, _, _ = message_data

                    attempt_send = AttemptSend(
                        newsletter=newsletter,
                        recipient=MailingRecipient.objects.first(),
                        status="fail",
                        server_response=f"{type(e).__name__}: {str(e)}",
                    )
                    attempt_send.save()

        else:
            print("Нет сообщений для отправки.")

    def get_mass_message(self, newsletter):
        """ Создание данных для массового письма. """

        mass_mess_tuple = []

        your_topic = newsletter.message.message_topic
        your_message = newsletter.message.message
        from_email = EMAIL_HOST_USER
        recipients = list(newsletter.recipients.values_list("email", flat=True))

        if not your_topic or not recipients:
            raise ValueError("Список получателей пуст.")

        mass_mess_tuple.append((your_topic, your_message, from_email, recipients))

        return tuple(mass_mess_tuple)
