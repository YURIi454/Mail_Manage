from uuid import uuid4

from django.shortcuts import redirect, render

from users.models import CustomUser


def get_user_status_for_delete(user):
    """ Изменяет статус пользователя на удаление. """

    if user.is_authenticated and not user.is_superuser:
        user.user_status = "for_delete"
        user.save()


def register_user(request):
    """  Подтверждение регистрации пользователя. """

    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        token = str(uuid4())

        profile = CustomUser(username=email, email=email, password=password, activation_token=token)
        profile.save()

        print(f"\n\nСсылка подтверждение отправлена на адрес {email} \n"
              f"Подтвердите email перейдя по ссылке:\n"
              f"/activate/{token}\n\n")

        return redirect('confirmation_page')

    return render(request, 'register.html')
