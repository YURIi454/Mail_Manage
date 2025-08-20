from uuid import uuid4

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, TemplateView

from users.forms import CreateCustomUserForm, UpdateCustomUserForm, UpdateCustomUserFormAdmin
from users.models import CustomUser
from users.services import register_user


# class RequestForDeleteUser(LoginRequiredMixin, TemplateView):
#     """ Заявка на удаление пользователя. """
#
#     template_name = "request_for_delete.html"
#
#     def post(self, request, *args, **kwargs):
#         current_user = request.user
#
#         if current_user.is_authenticated and not current_user.is_superuser:  # TODO
#             current_user.user_status = "for_delete"
#             current_user.save()
#             return reverse_lazy("home")  # TODO
#
#         return super().post(request, *args, **kwargs)  # TODO


class CreateCustomUser(CreateView):
    """ Создание пользователя. """

    template_name = "create_user.html"
    model = CustomUser
    form_class = CreateCustomUserForm
    success_url = reverse_lazy('mailing:statistic')

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        email = cleaned_data['email']
        password = cleaned_data['password1']

        token = str(uuid4())

        user = form.save(commit=False)
        user.username = email
        user.set_password(password)
        user.activate_token = token
        user.save()

        print(f"\n\nСсылка подтверждения отправлена на адрес {email}. "
              f"Перейдите по ссылке для активации:\n"
              f"{self.request.build_absolute_uri(reverse_lazy('users:activate_user', kwargs={'token': token}))}\n\n")

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


class UpdateCustomUserModer(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    """ Редактирование пользователя для модератора. """

    template_name = "update_user.html"
    permission_required = ["watch_users", "change_users", "delete_users", ]
    model = CustomUser
    form_class = UpdateCustomUserFormAdmin

    def get_object(self, queryset=None):
        return CustomUser.objects.only('is_active', 'user_status', 'comment', ).get(pk=self.request.user.pk)


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
            print(f'Ошибка активации {e}')
            return redirect(reverse("users:login"))


# def email_verification(request, token):
#     """ Верификация пользователя. """
#
#     user = get_object_or_404(CustomUser, token=token)
#     user.is_active = True
#     user.user_status = "active"
#     user.save()
#
#     return redirect(reverse("users:login"))
