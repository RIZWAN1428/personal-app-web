"""
Database model for user accounts.

WHAT THIS DOES (plain English):
Defines the "User" table (who can log in). Email is the login field
instead of Django's default username.
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """A person who can log in to the app. Email is the login field."""

    email = models.EmailField(unique=True, db_index=True)  # unique constraint: no duplicate accounts
    display_name = models.CharField(max_length=100, blank=True)
    theme_preference = models.CharField(
        max_length=10,
        choices=[("light", "Light"), ("dark", "Dark"), ("system", "Follow System")],
        default="system",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # can log in to Django admin
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # email + password is all that's required to create an account

    def __str__(self):
        return self.email
