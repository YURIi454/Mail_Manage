from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView

from mailing.forms import (
    MailingRecipientForm,
    NewsletterForm,
    NewsletterLockForm,
    StartNewsletterForm,
    YourMessageForm,
)
from mailing.models import AttemptSend, MailingRecipient, Newsletter, YourMessage
from mailing.services import get_all_statistic, get_main_indicators
from users.forms import UpdateCustomUserFormAdmin
from users.models import CustomUser
from users.services import is_manager


class OwnerRequiredMixin(UserPassesTestMixin):
    """ Доступ к объекту только для владельца или суперпользователя. """

    def test_func(self):
        obj = self.get_object()
        owner = getattr(obj, 'owner', None)
        return owner == self.request.user or self.request.user.is_superuser


# region представления для статичных страниц приложения

class MainPageView(TemplateView):
    """  Шаблон главной страницы. """

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context.update(get_main_indicators(self.request.user))

        return context


# endregion

# region CRUD для получателя рассылки

class RecipientCreateView(LoginRequiredMixin, CreateView):
    """ Создание получателя рассылки. """

    form_class = MailingRecipientForm
    template_name = "recip_create.html"
    success_url = reverse_lazy("mailing:statistic")

    def form_valid(self, form):
        """ Заполнение поля owner данными текущего пользователя. """

        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update_mode'] = False
        return context


class RecipientUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    """ Редактирование получателя рассылки. """

    model = MailingRecipient
    form_class = MailingRecipientForm
    template_name = "recip_create.html"
    success_url = reverse_lazy("mailing:statistic")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update_mode'] = True
        return context


class RecipientListView(LoginRequiredMixin, ListView):
    """ Получатели рассылки. """

    model = MailingRecipient
    template_name = "recip_list.html"
    context_object_name = "recipients"

    def get_queryset(self):
        """ Условия для отображения получателей. """

        if is_manager(self.request.user):
            return MailingRecipient.objects.select_related('owner').all()

        return MailingRecipient.objects.filter(owner=self.request.user)


class RecipientDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    """ Удаление получателя рассылки. """

    model = MailingRecipient
    template_name = "recip_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")


# endregion

# region CRUD для сообщений

class YourMessageCreateView(LoginRequiredMixin, CreateView):
    """ Создать сообщение. """

    form_class = YourMessageForm
    template_name = "msg_create.html"
    success_url = reverse_lazy("mailing:statistic")

    def form_valid(self, form):
        """ Заполнение поля owner данными текущего пользователя. """

        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update_mode'] = False
        return context


class YourMessageUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    """ Редактировать сообщение. """

    model = YourMessage
    form_class = YourMessageForm
    template_name = "msg_create.html"
    success_url = reverse_lazy("mailing:statistic")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update_mode'] = True
        return context


class YourMessageListView(LoginRequiredMixin, ListView):
    """ Список сообщений. """

    model = YourMessage
    template_name = "msg_list.html"
    context_object_name = "message_list"

    def get_queryset(self):
        """ Условия для отображения сообщений. """

        return YourMessage.objects.filter(owner=self.request.user)


class YourMessageDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    """ Сообщение. """

    model = YourMessage
    template_name = "msg_delete.html"
    success_url = reverse_lazy("mailing:message_list")


# endregion

# region CRUD для рассылки

class NewsletterCreateView(LoginRequiredMixin, CreateView):
    """ Создать рассылку. """

    form_class = NewsletterForm
    template_name = "nws_let_create.html"
    success_url = reverse_lazy("mailing:statistic")

    def form_valid(self, form):
        """ Заполнение поля owner данными текущего пользователя. """

        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        """ Передача текущего пользователя в форму. """

        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update_mode'] = False
        return context


class NewsletterUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    """ Редактировать рассылку. """

    model = Newsletter
    form_class = NewsletterForm
    template_name = "nws_let_create.html"
    success_url = reverse_lazy("mailing:statistic")

    def get_form_kwargs(self):
        """ Передача текущего пользователя в форму. """

        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update_mode'] = True
        return context


class NewsletterListView(LoginRequiredMixin, ListView):
    """ Список рассылок. """

    model = Newsletter
    template_name = "nws_let_list.html"
    context_object_name = "newsletters"
    paginate_by = 10

    def get_queryset(self):
        """ Условия для отображения рассылок. """

        if is_manager(self.request.user):
            queryset = Newsletter.objects.all()
        else:
            queryset = Newsletter.objects.filter(owner=self.request.user)

        return queryset.select_related('owner', 'message').prefetch_related('recipients')


class NewsletterDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    """ Удаление рассылки. """

    model = Newsletter
    template_name = "nws_let_delete.html"
    success_url = reverse_lazy("mailing:newsletter_list")


# endregion

# region Статистика
class AttemptSendListView(LoginRequiredMixin, ListView):
    """ Список попыток рассылки. """

    model = AttemptSend
    template_name = "attempt_send_all.html"
    context_object_name = "attempts"

    def get_queryset(self):
        """ Условия для отображения попыток. """

        if is_manager(self.request.user):
            return AttemptSend.objects.select_related('newsletter', 'recipient').all()

        return AttemptSend.objects.select_related('newsletter', 'recipient').filter(
            newsletter__owner=self.request.user
        )


class AttemptSendDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """ Подробная информация попытки рассылки. """

    model = AttemptSend
    template_name = "attempt_send_detail.html"
    context_object_name = "attempt"

    def test_func(self):
        """ Условия получения объекта. """

        attempt = self.get_object()

        if is_manager(self.request.user):
            return True

        return attempt.newsletter is not None and attempt.newsletter.owner == self.request.user


class StatisticAllView(LoginRequiredMixin, TemplateView):
    """ Общая статистика текущего пользователя. """

    template_name = 'all_your_statistic.html'

    def get(self, request, *args, **kwargs):
        if is_manager(request.user) and not request.user.is_superuser:
            return redirect(reverse_lazy('mailing:manager_all_newsletters'))

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_all_statistic(self.request.user))
        return context


class ManagerNewslettersListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """ Просмотр всех рассылок. """

    permission_required = 'mailing.change_nws_let'
    model = Newsletter
    template_name = 'manager_all_newsletters.html'
    context_object_name = 'newsletters'

    def get_queryset(self):
        """ Получить всех пользователей и их рассылки. """

        return Newsletter.objects.select_related('message', 'owner').all()


class ManagerUserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """ Просмотр списка пользователей сервиса. """

    permission_required = 'users.change_users'
    model = CustomUser
    template_name = 'manager_all_users.html'
    context_object_name = 'users'

    def get_queryset(self):
        """ Получить всех пользователей сервиса. """

        return CustomUser.objects.all()


class ManagerChangeStatusNewsletterView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """ Изменение статуса рассылки. """

    permission_required = 'mailing.change_nws_let'
    model = Newsletter
    form_class = NewsletterLockForm
    template_name = 'manager_newsletter.html'
    success_url = reverse_lazy('mailing:manager_all_newsletters')
    context_object_name = 'newsletter'


class ManagerChangeStatusCustomUserView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """ Редактирование пользователя для модератора. """

    template_name = "manager_user.html"
    permission_required = "users.change_users"
    model = CustomUser
    form_class = UpdateCustomUserFormAdmin
    success_url = reverse_lazy('mailing:manager_all_users')
    context_object_name = 'edited_user'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if obj == self.request.user:
            raise PermissionDenied("Вы не можете редактировать собственный профиль.")

        return obj


# endregion

# region Запуск рассылки
class SendNewsletterView(LoginRequiredMixin, FormView):
    """ Запуск рассылки. """

    form_class = StartNewsletterForm
    template_name = 'all_your_statistic.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_all_statistic(self.request.user))
        return context

    def form_valid(self, form):
        user = self.request.user
        newsletter_id = form.cleaned_data['newsletter_id']

        if user.is_superuser:
            newsletter = get_object_or_404(Newsletter, pk=newsletter_id)
        else:
            newsletter = get_object_or_404(Newsletter, pk=newsletter_id, owner=user)

        now = timezone.now()

        if not (newsletter.start_time <= now <= newsletter.end_time):
            send_result = (
                f'Рассылка «{newsletter.name}» не запущена: текущее время вне периода отправки '
                f'({newsletter.start_time:%d.%m.%Y %H:%M} — {newsletter.end_time:%d.%m.%Y %H:%M}).'
            )
            return self.render_to_response(self.get_context_data(form=form, send_result=send_result))

        call_command(
            'start_spam_generator',
            newsletter_id=newsletter.pk,
            owner_id=None if user.is_superuser else user.pk,
        )

        send_result = f'Рассылка «{newsletter.name}» запущена.'

        return self.render_to_response(self.get_context_data(form=form, send_result=send_result))
# endregion
