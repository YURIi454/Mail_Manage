from django.db import models
from django.utils import timezone

from users.models import CustomUser


class MailingRecipient(models.Model):
    """ Получатель рассылки. """

    email = models.EmailField(unique=True, verbose_name='почта')
    recipient_data = models.CharField(max_length=150, blank=True, null=True, verbose_name='данные получателя')
    comment = models.TextField(max_length=150, blank=True, null=True, verbose_name='комментарий')
    owner = models.ForeignKey(CustomUser, on_delete=models.PROTECT, verbose_name='владелец')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='создан')

    def __str__(self):
        """ Вывод информации. """

        return f'{self.email}, {self.recipient_data}'

    class Meta:
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'
        ordering = ['created_at']
        indexes = [models.Index(fields=['email', ])]
        permissions = [
            ('change_recipient', 'редактирование получателя'),
            ('watch_recipient', 'просмотр получателя'),
        ]


class YourMessage(models.Model):
    """ Сообщение. """

    message_topic = models.CharField(max_length=150, verbose_name='тема письма')
    message = models.TextField(max_length=5000, blank=True, null=True, verbose_name='текст письма')
    owner = models.ForeignKey(CustomUser, on_delete=models.PROTECT, verbose_name='владелец')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='создан')

    def __str__(self):
        """ Вывод информации. """

        return f'{self.message_topic}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['created_at']
        permissions = [
            ('change_message', 'Редактирование получателя'),
            ('watch_message', 'Просмотр получателя'),
        ]


class Newsletter(models.Model):
    """ Рассылка. """

    status_list = [
        ('create', 'Создана'),
        ('launched', 'Запущена'),
        ('completed', 'Завершена'),
        ('locked', 'Заблокирована')
    ]
    name = models.CharField(unique=True, max_length=50, default='', verbose_name='название рассылки')
    recipients = models.ManyToManyField(MailingRecipient, verbose_name='получатель')
    message = models.ForeignKey(YourMessage, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='сообщение')
    owner = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='владелец')
    status_comment = models.TextField(null=True, blank=True, verbose_name='комментарий к статусу')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='создана')
    start_time = models.DateTimeField(verbose_name='дата и время начала отправки')
    end_time = models.DateTimeField(verbose_name='дата и время окончания отправки')
    is_locked = models.BooleanField(default=False, verbose_name='отключена')

    def __str__(self):
        """Вывод информации."""

        if self.status_comment:
            return f"{self.get_status_display()} ({self.status_comment})"
        else:
            return f"{self.get_status_display()}"

    @property
    def status(self):
        """ Динамический статус рассылки. """

        if self.is_locked:
            return 'locked'

        now = timezone.now()

        if now < self.start_time:
            return 'create'
        if now <= self.end_time:
            return 'launched'
        return 'completed'

    def get_status_display(self):
        """ Текстовое отображение динамического статуса. """

        return dict(self.status_list).get(self.status, self.status)

    @property
    def is_active(self):
        """ Активна ли рассылка в текущий момент. """

        return self.status == 'launched'

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['created_at']
        indexes = [models.Index(fields=['owner', ])]
        permissions = [
            ('change_nws_let', 'Редактирование рассылки'),
            ('watch_nws_let', 'Просмотр рассылки'),
        ]


class AttemptSend(models.Model):
    """ Попытка рассылки. """

    send_status = [
        ('not_used', 'Не запускалась'),
        ('success', 'Успешно'),
        ('fail', 'Не успешно'),
    ]

    newsletter = models.ForeignKey(Newsletter, null=True, blank=True, on_delete=models.SET_NULL,
                                   verbose_name='рассылка')
    recipient = models.ForeignKey(MailingRecipient, null=True, blank=True, on_delete=models.SET_NULL,
                                  verbose_name='получатель')
    status = models.CharField(choices=send_status, default='not_used', verbose_name='статус')
    server_response = models.TextField(null=True, blank=True, verbose_name='ответ сервера')
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name='дата и время попытки')

    def __str__(self):
        """ Вывод информации. """

        return f'{self.status}'

    class Meta:
        verbose_name = 'Попытка'
        verbose_name_plural = 'Попытки'
        ordering = ['attempt_time']
        permissions = [
            ('change_attempt', 'Редактирование попытки'),
            ('watch_attempt', 'Просмотр попытки'),
        ]
