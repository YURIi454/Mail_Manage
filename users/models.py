from django.contrib.auth.models import AbstractUser
from django.db import models
from uuid import uuid4


class CustomUser(AbstractUser):
    """ Пользователь. """

    user_status_list = [
        ("active", "активный"),
        ("not_active", "не активный"),
        ("temp_ban", "временный бан"),
        ("forever_ban", "бан навсегда"),
        ("for_delete", "на удаление"),
    ]

    email = models.EmailField(unique=True, verbose_name="Ваш Email")
    first_name = models.CharField(null=True, blank=True, verbose_name="Имя")
    last_name = models.CharField(null=True, blank=True, verbose_name="Фамилия")
    activate_token = models.UUIDField(default=uuid4, editable=False)
    is_active = models.BooleanField(default=False)
    user_status = models.CharField(choices=user_status_list, default="not_active", verbose_name="Статус пользователя")
    comment = models.TextField(max_length=300, null=True, blank=True, verbose_name="комментарий")
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", ]

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']
        permissions = [
            ('watch_users', 'Просмотр пользователя'),
            ('change_users', 'Редактирование пользователя'),
            ('delete_users', 'Удаление пользователя'),
        ]
