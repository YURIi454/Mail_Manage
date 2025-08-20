from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from users.models import CustomUser


class CreateCustomUserForm(UserCreationForm):
    """ Регистрация пользователя."""

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(CreateCustomUserForm, self).__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': 'ваш ник'}
        )

        self.fields["email"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )

        self.fields["first_name"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )

        self.fields["last_name"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )

        self.fields["password1"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )

        self.fields["password2"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )


class UpdateCustomUserForm(UserChangeForm):
    """ Обновление данных пользователя. """

    password = None

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name',)

    def __init__(self, *args, **kwargs):
        super(UpdateCustomUserForm, self).__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': 'ваш ник'}
        )

        self.fields["email"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )

        self.fields["first_name"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )

        self.fields["last_name"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )


class UpdateCustomUserFormAdmin(UserChangeForm):
    """ Обновление данных пользователя для админа. """

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("is_active", "user_status", "comment",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["user_status"].widget.attrs.update(
            {'class': 'form-select',
             'placeholder': ''}
        )

        self.fields["is_active"].widget.attrs.update(
            {'class': 'form-check-input',
             'placeholder': ''}
        )

        self.fields["comment"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': '',
             'rows': 3}
        )
