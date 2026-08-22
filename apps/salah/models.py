"""
Database models for Salah (Prayer Times) preferences and daily prayer habit tracking.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone

CALCULATION_METHODS = [
    (1, "University of Islamic Sciences, Karachi"),
    (2, "Islamic Society of North America (ISNA)"),
    (3, "Muslim World League (MWL)"),
    (4, "Umm Al-Qura University, Makkah"),
    (5, "Egyptian General Authority of Survey"),
    (7, "Institute of Geophysics, University of Tehran"),
    (12, "Union des Organisations Islamiques de France"),
    (13, "Diyanet İşleri Başkanlığı, Turkey"),
    (15, "Moonsighting Committee Worldwide"),
]

JURISTIC_SCHOOLS = [
    (0, "Shafi'i / Maliki / Hanbali (Standard)"),
    (1, "Hanafi (Later Asr)"),
]


class SalahPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="salah_preference",
    )
    city = models.CharField(max_length=100, default="Jaunpur")
    state = models.CharField(max_length=100, default="Uttar Pradesh", blank=True)
    country = models.CharField(max_length=100, default="India")
    method = models.IntegerField(default=1, choices=CALCULATION_METHODS)
    school = models.IntegerField(default=1, choices=JURISTIC_SCHOOLS)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Salah prefs for {self.user} ({self.city}, {self.country})"


class SalahDailyLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="salah_logs",
    )
    date = models.DateField(default=timezone.now)
    fajr = models.BooleanField(default=False)
    dhuhr = models.BooleanField(default=False)
    asr = models.BooleanField(default=False)
    maghrib = models.BooleanField(default=False)
    isha = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(fields=["user", "date"], name="unique_user_daily_salah_log")
        ]

    def __str__(self):
        return f"{self.user} - Salah Log {self.date}"

    @property
    def completed_count(self):
        return sum([self.fajr, self.dhuhr, self.asr, self.maghrib, self.isha])
