from django.urls import path
from .views import signup_view, dashboard_view,forgot_password,reset_password,password_reset_sent
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("", dashboard_view, name="dashboard"),

    path(
        "login/",
        LoginView.as_view(
            template_name="accounts/login.html"
        ),
        name="login"
    ),

    path(
        "logout/",
        LogoutView.as_view(),
        name="logout"
    ),

    path(
        "dashboard/",
        dashboard_view,
        name="dashboard"
    ),

    path("forgot-password/", forgot_password, name="forgot_password"),
    path("password-reset-sent/", password_reset_sent, name="password_reset_sent"),
    path("reset-password/<uidb64>/<token>/", reset_password, name="reset_password"),

]