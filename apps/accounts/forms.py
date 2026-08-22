"""
Forms turn incoming POST data (from HTML <form> submissions) into
validated Python data, and render themselves back out as HTML if there
are errors — the classic Django pattern.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class SignupForm(forms.Form):
    """Validates a new-account request. We hash the password ourselves in the view."""

    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    display_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), min_length=8)
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}), min_length=8, label="Confirm password"
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        password_confirm = cleaned.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise ValidationError("Passwords do not match.")
        return cleaned


class EmailLoginForm(AuthenticationForm):
    """Django's built-in login form, relabelled since we log in with email."""

    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "form-control", "autofocus": True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))


class ProfileForm(forms.ModelForm):
    """Lets a logged-in user update their display name and theme preference."""

    class Meta:
        model = User
        fields = ["display_name", "theme_preference"]
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
            "theme_preference": forms.Select(attrs={"class": "form-select"}),
        }
