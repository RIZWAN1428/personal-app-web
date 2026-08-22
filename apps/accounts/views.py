"""
Views for accounts: signup, login (Django's built-in), logout, profile.
"""
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.views import View

from .forms import EmailLoginForm, ProfileForm, SignupForm
from .models import User


class SignupView(View):
    """GET shows the signup form. POST creates the account and logs the user in."""

    template_name = "accounts/signup.html"

    def get(self, request):
        return render(request, self.template_name, {"form": SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                display_name=form.cleaned_data["display_name"],
            )
            auth_login(request, user)  # sign them in immediately after signup
            messages.success(request, f"Welcome, {user.display_name or user.email}!")
            return redirect("home")
        return render(request, self.template_name, {"form": form})


class EmailLoginView(LoginView):
    """Django's built-in login view, using our email-based form and template."""

    template_name = "accounts/login.html"
    authentication_form = EmailLoginForm


class EmailLogoutView(LogoutView):
    """Logs the user out. Django handles session cleanup for us."""

    next_page = "accounts:login"


@login_required
def profile(request):
    """GET shows the profile form. POST saves display name / theme preference."""
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})
