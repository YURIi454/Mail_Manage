from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from mailing.models import YourMessage, MailingRecipient, Newsletter
from users.models import CustomUser


class Command(BaseCommand):
    """ Добавляет тестовые данные пользователей, сообщений и получателей. """

    help = 'Добавляет тестовые данные пользователей, сообщений и получателей.'

    def handle(self, *args, **options):

        admin_group, _ = Group.objects.get_or_create(name='administrators')
        moderator_group, _ = Group.objects.get_or_create(name='moderators')
        all_permissions = Permission.objects.all()

        change_user_perm = Permission.objects.get(codename='change_users')
        change_nws_perm = Permission.objects.get(codename='change_nws_let')

        moderator_group.permissions.add(change_user_perm, change_nws_perm,)
        admin_group.permissions.set(all_permissions)

        users = []
        for i in range(3):
            username = f'user{i + 1}'
            password = 'password123'
            email = f'{username}@user.com'
            status = CustomUser.user_status_list[i % len(CustomUser.user_status_list)][0]

            if i == 0:
                user = CustomUser.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    user_status=status,
                    comment = 'админ',
                    is_active=True
                )
                user.groups.add(admin_group)

            elif i == 1:
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    user_status=status,
                    comment='модератор',
                    is_active=True
                )
                user.groups.add(moderator_group)

            else:
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    user_status=status,
                    comment='пользователь',
                    is_active=False
                )
            users.append(user)

        messages = []
        for user in users:
            for j in range(2):
                topic = f'Сообщение №{j + 1} от {user.username}'
                text = f'Это сообщение создано автоматически для тестирования системы.'
                message = YourMessage.objects.create(
                    message_topic=topic,
                    message=text,
                    owner=user
                )
                messages.append(message)

        recipients = []
        for user in users:
            for k in range(2):
                email = f'recipient{k + 1}-of-{user.username}@example.com'
                data = f'Данные получателя {k + 1}'
                recipient = MailingRecipient.objects.create(
                    email=email,
                    recipient_data=data,
                    owner=user
                )
                recipients.append(recipient)

        newsletter = Newsletter.objects.create(
            name=f'Тестовая рассылка',
            message=messages[0],
            owner=users[0],
            status='create'
        )
        newsletter.recipients.set([recipients[0], recipients[1]])

        self.stdout.write('Тестовые данные успешно добавлены в БД !')
