from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView, ListView
from django.views.generic.edit import UpdateView, DeleteView, CreateView, FormView

from mailing.forms import MailingRecipientForm, YourMessageForm, NewsletterForm, StartNewsletterForm
from mailing.models import MailingRecipient, YourMessage, Newsletter, AttemptSend
from mailing.services import get_all_statistic
from users.forms import UpdateCustomUserFormAdmin
from users.models import CustomUser


# region представления для статичных страниц приложения

class MainPageView(TemplateView):
    """  Шаблон главной страницы. """

    template_name = "home.html"


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


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
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

        user = self.request.user

        if user.is_superuser or user.groups.filter(name='managers').exists():
            return MailingRecipient.objects.all()
        elif MailingRecipient.objects.filter(owner=user).exists():
            return MailingRecipient.objects.filter(owner=user)


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
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


class YourMessageUpdateView(LoginRequiredMixin, UpdateView):
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
    context_object_name = "messages"

    def get_queryset(self):
        """ Условия для отображения сообщений. """

        user = self.request.user
        return YourMessage.objects.filter(owner=user)


class YourMessageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """ Сообщение. """

    model = YourMessage
    template_name = "msg_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def test_func(self):
        """ Условия для удаления сообщения. """

        obj = self.get_object()
        return obj.owner == self.request.user


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
        """ Just developer magic """

        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update_mode'] = False
        return context


class NewsletterUpdateView(LoginRequiredMixin, UpdateView):
    """ Редактировать рассылку. """

    model = Newsletter
    form_class = NewsletterForm
    template_name = "nws_let_create.html"
    success_url = reverse_lazy("mailing:statistic")

    def get_form_kwargs(self):
        """ Just developer magic """

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

        user = self.request.user

        if user.is_superuser or user.groups.filter(name='managers').exists():
            queryset = Newsletter.objects.all()
            return queryset.select_related('owner').prefetch_related('recipients').all()

        elif user.is_authenticated:
            queryset = Newsletter.objects.filter(owner=user)
            return queryset.select_related('owner').prefetch_related('recipients').all()


class NewsletterDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """ Удаление рассылки. """

    model = Newsletter
    template_name = "nws_let_delete.html"
    success_url = reverse_lazy("mailing:newsletter_list")

    def test_func(self):
        """ Условия для удаления рассылки. """

        obj = self.get_object()
        return obj.owner == self.request.user or self.request.user.is_superuser


# endregion

# region Статистика
class AttemptSendListView(LoginRequiredMixin, ListView):
    """ Список попыток рассылки. """

    model = AttemptSend
    template_name = "attempt_send_all.html"
    context_object_name = "attempts"

    def get_queryset(self):
        """ Условия для отображения попыток. """

        user = self.request.user

        if user.is_superuser or user.groups.filter(name='managers').exists():
            return AttemptSend.objects.select_related('newsletter', 'recipient').all()

        elif user.is_authenticated:
            return AttemptSend.objects.select_related('newsletter', 'recipient', ).filter(newsletter__owner=user)


class AttemptSendDetailView(LoginRequiredMixin, DetailView):
    """ Подробная информация попытки рассылки. """

    model = AttemptSend
    template_name = "attempt_send_detail.html"
    context_object_name = "attempt"

    def get_object(self, queryset=None):
        """ Условия получения объекта. """

        objct = super().get_object(queryset=queryset)

        user = self.request.user

        if user.is_superuser or user.groups.filter(name='managers').exists():
            return objct

        elif user.is_authenticated and hasattr(objct.newsletter, 'owner'):
            if objct.newsletter.owner == user:
                return objct


class StatisticAllView(LoginRequiredMixin, TemplateView):
    """ Общая статистика текущего пользователя. """

    template_name = 'all_your_statistic.html'

    def get(self, request, *args, **kwargs):
        if request.user.groups.filter(name='moderators').exists():
            return redirect(reverse_lazy('mailing:manager_all_newsletters'))

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        context.update(get_all_statistic(current_user))
        return context


class ManagerNewslettersListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """ Просмотр всех рассылок. """

    permission_required = 'mailing.change_nws_let'
    model = Newsletter
    template_name = 'manager_all_newsletters.html'
    context_object_name = 'newsletters'

    def get_queryset(self):
        """ Получить всех пользователей и их рассылки. """

        queryset = Newsletter.objects.select_related('message', 'owner').all()
        return queryset


class ManagerUserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """ Просмотр списка пользователей сервиса. """

    permission_required = 'mailing.change_nws_let'
    model = CustomUser
    template_name = 'manager_all_users.html'
    context_object_name = 'users'

    def get_queryset(self):
        """ Получить всех пользователей сервиса. """

        return CustomUser.objects.all()


class ManagerChangeStatusNewsletterView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """ Изменение статуса рассылки. """

    permission_required = 'mailing.change_nws_let',
    model = Newsletter
    fields = ['status']
    template_name = 'manager_newsletter.html'
    success_url = reverse_lazy('mailing:manager_all_newsletters')
    context_object_name = 'newsletter'

    def get_context_data(self, **kwargs):
        """ Передача списка статусов в шаблон. """

        context = super().get_context_data(**kwargs)
        context['status_choices'] = Newsletter.status_list
        return context


class ManagerChangeStatusCustomUserView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    """ Редактирование пользователя для модератора. """

    template_name = "manager_user.html"
    permission_required = "users.change_users",
    model = CustomUser
    form_class = UpdateCustomUserFormAdmin
    success_url = reverse_lazy('mailing:manager_all_users')
    context_object_name = 'user'

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
    success_url = reverse_lazy('mailing:statistic')
    template_name = 'all_your_statistic.html'

    def form_valid(self, form):
        user_id = form.cleaned_data['user_id']
        newsletter_id = form.cleaned_data['newsletter_id']
        call_command('start_spam_generator', user_id=user_id, newsletter_id=newsletter_id)
        return HttpResponseRedirect(reverse_lazy('mailing:newsletter_list'))
# endregion
