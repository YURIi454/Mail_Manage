from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

from users.views import (
    UpdateCustomUser,
    CreateCustomUser,
    DetailCustomUser,
    ActivateCustomUserView,
)

app_name = "users"

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login_user.html",next_page = "mailing:statistic"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("create_user/", CreateCustomUser.as_view(), name="create_user"),
    path("update_user/", UpdateCustomUser.as_view(), name="update_user"),
    path("detail_user/", DetailCustomUser.as_view(), name="detail_user"),
    path('activate/<str:token>/', ActivateCustomUserView.as_view(), name="activate_user"),

    path("password_reset/", PasswordResetView.as_view
        (
        template_name='users/password_reset_form.html',
        email_template_name='users/password_reset_email.html',
        success_url=reverse_lazy("users:password_reset_done")
    ),
         name="password_reset_form"),

    path("password_reset/done/", PasswordResetDoneView.as_view
        (
        template_name="users/password_reset_done.html"
    ),
         name="password_reset_done"),

    path("password_reset_confirm/<uidb64>/<token>/", PasswordResetConfirmView.as_view
        (
        template_name="users/password_reset_confirm.html",
        success_url=reverse_lazy("users:password_reset_complete")
    ),
         name="password_reset_confirm"),

    path("password_reset_complete/", PasswordResetCompleteView.as_view
        (
        template_name="users/password_reset_complete.html"
    ), name="password_reset_complete"),
]
