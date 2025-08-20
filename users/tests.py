from django.test import TestCase

# Create your tests here.
class MailingSendView(LoginRequiredMixin, View):
    def get(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        if mailing.owner != request.user:
            messages.error(request, "У вас нет прав на отправку этой рассылки.")
            return redirect("mailings:mailing_detail", pk=pk)

        clients = mailing.clients.all()
        success_count = 0

        for client in clients:
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=None,
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                status = "Успешно"
                response = "OK"
                success_count += 1
            except Exception as e:
                status = "Не успешно"
                response = str(e)

            MailingAttempt.objects.create(
                mailing=mailing,
                status=status,
                server_response=response,
            )

        mailing.status = "Запущена"
        mailing.save()

        messages.success(
            request,
            f"Рассылка отправлена. Успешно: {success_count}/{clients.count()}",
        )
        return redirect("mailings:mailing_detail", pk=pk)