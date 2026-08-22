"""
URL routes for the accounts app, mounted at /accounts/ (see config/urls.py).
"""
from django.urls import path

from .views import EmailLoginView, EmailLogoutView, SignupView, profile

app_name = "accounts"

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", EmailLoginView.as_view(), name="login"),
    path("logout/", EmailLogoutView.as_view(), name="logout"),
    path("profile/", profile, name="profile"),
]
