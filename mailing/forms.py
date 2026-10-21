from django import forms
from django.core.validators import MinLengthValidator
from django.utils import timezone

from mailing.models import MailingRecipient, Newsletter, YourMessage


class ContactForm(forms.Form):
    """ Форма обратной связи. """

    name = forms.CharField(
        max_length=100,
        required=True,
        validators=[MinLengthValidator(2)],
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя'})
    )
    email = forms.EmailField(
        required=True,
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваш email'})
    )
    message = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше сообщение',
            'rows': 3})
    )


class MailingRecipientForm(forms.ModelForm):
    """ Форма получатель рассылки. """

    class Meta:
        model = MailingRecipient
        fields = ["email", "recipient_data", "comment", ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )
        self.fields["recipient_data"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )
        self.fields["comment"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )


class YourMessageForm(forms.ModelForm):
    """ Форма сообщение. """

    class Meta:
        model = YourMessage
        fields = ["message_topic", "message", ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["message_topic"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': 'Тема сообщения'}
        )
        self.fields["message"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': 'Сообщение'}
        )


class NewsletterForm(forms.ModelForm):
    """ Форма рассылка. """

    class Meta:
        model = Newsletter
        fields = ["name", "recipients", "message", "start_time", "end_time", ]
        widgets = {
            "start_time": forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'class': 'form-control', 'type': 'datetime-local'},
            ),
            "end_time": forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'class': 'form-control', 'type': 'datetime-local'},
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["start_time"].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M']
        self.fields["end_time"].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M']

        self.fields["name"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )
        self.fields["recipients"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )
        self.fields["message"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )

        if user is not None:
            self.fields["recipients"].queryset = self.fields["recipients"].queryset.filter(owner=user)
            self.fields["message"].queryset = self.fields["message"].queryset.filter(owner=user)

    def clean_start_time(self):
        """ Дата начала не может быть в прошлом. """

        start_time = self.cleaned_data["start_time"]

        if start_time < timezone.now() and start_time != self.initial.get("start_time"):
            raise forms.ValidationError("Дата и время начала отправки не может быть в прошлом.")

        return start_time

    def clean(self):
        """ Дата начала должна быть раньше даты окончания. """

        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and start_time >= end_time:
            self.add_error("end_time", "Дата окончания должна быть позже даты начала.")

        return cleaned_data


class NewsletterLockForm(forms.ModelForm):
    """ Форма отключения рассылки для менеджера. """

    class Meta:
        model = Newsletter
        fields = ["is_locked"]
        labels = {"is_locked": "Отключить рассылку"}
        widgets = {"is_locked": forms.CheckboxInput(attrs={"class": "form-check-input"})}


class StartNewsletterForm(forms.Form):
    """  Скрытая форма запуск рассылки"""

    newsletter_id = forms.IntegerField(widget=forms.HiddenInput())
