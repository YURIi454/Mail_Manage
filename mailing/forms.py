from django import forms
from django.core.validators import MinLengthValidator

from mailing.models import MailingRecipient, YourMessage, Newsletter


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
        fields = ["name", "recipients", "message", ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        self.fields["name"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )
        self.fields["recipients"].queryset = self.fields["recipients"].queryset.filter(owner=user)
        self.fields["recipients"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )
        self.fields["message"].queryset = self.fields["message"].queryset.filter(owner=user)
        self.fields["message"].widget.attrs.update(
            {'class': 'form-control',
             'placeholder': ''}
        )


class StartNewsletterForm(forms.Form):
    """  Скрытая форма запуск рассылки"""

    user_id = forms.IntegerField(widget=forms.HiddenInput())
    newsletter_id = forms.IntegerField(widget=forms.HiddenInput())