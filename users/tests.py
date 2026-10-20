from django.contrib.auth.models import Group
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser
from users.services import is_manager


class CustomUserModelTest(TestCase):
    """ Проверка модели пользователя. """

    def test_str_returns_email(self):
        user = CustomUser.objects.create_user(username="user", email="user@example.com", password="StrongPass123")

        self.assertEqual(str(user), "user@example.com")


class IsManagerTest(TestCase):
    """ Проверка определения прав модератора. """

    def setUp(self):
        self.user = CustomUser.objects.create_user(username="user", email="user@example.com", password="StrongPass123")
        self.moderators = Group.objects.create(name="moderators")

    def test_regular_user_is_not_manager(self):
        self.assertFalse(is_manager(self.user))

    def test_moderator_group_user_is_manager(self):
        self.user.groups.add(self.moderators)

        self.assertTrue(is_manager(self.user))

    def test_superuser_is_manager(self):
        self.user.is_superuser = True

        self.assertTrue(is_manager(self.user))


class CreateCustomUserViewTest(TestCase):
    """ Проверка регистрации пользователя. """

    def test_registration_creates_inactive_user_and_sends_email(self):
        response = self.client.post(reverse("users:create_user"), {
            "username": "newbie",
            "email": "newbie@example.com",
            "first_name": "New",
            "last_name": "Bie",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        })

        self.assertEqual(response.status_code, 302)

        user = CustomUser.objects.get(email="newbie@example.com")
        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(str(user.activate_token), mail.outbox[0].body)


class ActivateCustomUserViewTest(TestCase):
    """ Проверка активации пользователя. """

    def test_activation_activates_user(self):
        user = CustomUser.objects.create_user(
            username="user", email="user@example.com", password="StrongPass123", is_active=False,
        )

        response = self.client.get(
            reverse("users:activate_user", kwargs={"token": str(user.activate_token)})
        )

        self.assertEqual(response.status_code, 302)

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertEqual(user.user_status, "active")
