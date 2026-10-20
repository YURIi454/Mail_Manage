import logging
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView

from users.forms import CreateCustomUserForm, UpdateCustomUserForm
from users.models import CustomUser

logger = logging.getLogger(__name__)


class CreateCustomUser(CreateView):
    """ Создание пользователя. """

    template_name = "create_user.html"
    model = CustomUser
    form_class = CreateCustomUserForm
    success_url = reverse_lazy('mailing:statistic')

    def form_valid(self, form):
        """ Создание неактивного пользователя и отправка письма подтверждения. """

        email = form.cleaned_data['email']
        token = str(uuid4())

        user = form.save(commit=False)
        user.username = email
        user.activate_token = token
        user.save()

        activation_url = self.request.build_absolute_uri(
            reverse('users:activate_user', kwargs={'token': token})
        )

        try:
            send_mail(
                subject='Подтверждение регистрации',
                message=f'Для активации аккаунта перейдите по ссылке:\n{activation_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception:
            logger.error('Не удалось отправить письмо подтверждения на %s. Ссылка: %s',
                         email, activation_url, exc_info=True)

        return super().form_valid(form)


class UpdateCustomUser(LoginRequiredMixin, UpdateView):
    """ Редактирование пользователя. """

    template_name = "update_user.html"
    model = CustomUser
    form_class = UpdateCustomUserForm

    def get_object(self, queryset=None):
        return (CustomUser.objects.only
                    (
                    'email', 'first_name', 'last_name', 'is_active', 'user_status', 'comment', 'created_at',
                ).get(pk=self.request.user.pk))


class DetailCustomUser(LoginRequiredMixin, DetailView):
    """ Информация о пользователе. """

    template_name = "detail_user.html"
    model = CustomUser

    def get_object(self, queryset=None):
        return (CustomUser.objects.only
                    (
                    'email', 'first_name', 'last_name', 'is_active', 'user_status', 'comment', 'created_at',
                ).get(pk=self.request.user.pk))


class ActivateCustomUserView(View):
    """ Подтверждения аккаунта пользователя """

    def get(self, request, token):

        try:
            user = get_object_or_404(CustomUser, activate_token=token)
            user.is_active = True
            user.user_status = "active"
            user.save()

            return redirect("users:login")

        except Exception as e:
            logger.warning('Ошибка активации пользователя: %s', e)
            return redirect(reverse("users:login"))
