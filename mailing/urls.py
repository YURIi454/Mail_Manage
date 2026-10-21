from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from config.settings import CACHE_TTL
from mailing.views import (
    AttemptSendDetailView,
    AttemptSendListView,
    MainPageView,
    ManagerChangeStatusCustomUserView,
    ManagerChangeStatusNewsletterView,
    ManagerNewslettersListView,
    ManagerUserListView,
    NewsletterCreateView,
    NewsletterDeleteView,
    NewsletterListView,
    NewsletterUpdateView,
    RecipientCreateView,
    RecipientDeleteView,
    RecipientListView,
    RecipientUpdateView,
    SendNewsletterView,
    StatisticAllView,
    YourMessageCreateView,
    YourMessageDeleteView,
    YourMessageListView,
    YourMessageUpdateView,
)


def cached(view):
    """ Серверное кеширование страницы с учетом сессии пользователя. """

    return cache_page(CACHE_TTL)(vary_on_cookie(view))


app_name = "mailing"

urlpatterns = [
    path("", cached(MainPageView.as_view()), name="home"),
    path("statistic", cached(StatisticAllView.as_view()), name="statistic"),

    path("recipient_create", RecipientCreateView.as_view(), name="recipient_create"),
    path("recipient_list/", cached(RecipientListView.as_view()), name="recipient_list"),
    path("recipient_update/<int:pk>/", RecipientUpdateView.as_view(), name="recipient_update"),
    path("recipient_delete/<int:pk>/", RecipientDeleteView.as_view(), name="recipient_delete"),

    path("newsletter_create/", NewsletterCreateView.as_view(), name="newsletter_create"),
    path("newsletter_list/", cached(NewsletterListView.as_view()), name="newsletter_list"),
    path("newsletter_update/<int:pk>/", NewsletterUpdateView.as_view(), name="newsletter_update"),
    path("newsletter_delete/<int:pk>/", NewsletterDeleteView.as_view(), name="newsletter_delete"),
    path('newsletter_send/', SendNewsletterView.as_view(), name='newsletter_send'),

    path("message_create", YourMessageCreateView.as_view(), name="message_create"),
    path("message_list/", cached(YourMessageListView.as_view()), name="message_list"),
    path("message_update/<int:pk>/", YourMessageUpdateView.as_view(), name="message_update"),
    path("message_delete/<int:pk>/", YourMessageDeleteView.as_view(), name="message_delete"),

    path("attempt_send_detail/<int:pk>/", cached(AttemptSendDetailView.as_view()), name="attempt_send_detail"),
    path("attempt_send_all/", cached(AttemptSendListView.as_view()), name="attempt_send_all"),

    path("manager_all_newsletters/", ManagerNewslettersListView.as_view(), name="manager_all_newsletters"),
    path("manager_all_users/", ManagerUserListView.as_view(), name="manager_all_users"),
    path("manager_user/<int:pk>/", ManagerChangeStatusCustomUserView.as_view(), name="manager_user"),
    path("manager_newsletter/<int:pk>/", ManagerChangeStatusNewsletterView.as_view(), name="manager_newsletter"),
]
