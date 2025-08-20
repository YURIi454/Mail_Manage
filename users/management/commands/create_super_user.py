from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    """ Создание суперпользователя"""

    def handle(self, *args, **options):
        user = get_user_model()
        user = user.objects.create(
            email="admin@admin.com",
            first_name="Admin",
            last_name="Admin",
            user_status="active",
            is_active=True,
        )

        user.set_password("mr_bin")

        user.is_staff = True
        user.is_superuser = True

        user.save()

        self.stdout.write(self.style.SUCCESS(f" Суперпользователь {user.first_name} успешно создан!"))
