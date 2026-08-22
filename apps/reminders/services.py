"""
Reminder "due" logic, computed live instead of via a background worker.

WHAT THIS DOES (plain English):
The original app used Celery to check every minute for due reminders and
push a phone notification. In a plain browser app there's no background
worker and no push notifications — instead, every time the reminders page
(or the dashboard) loads, we check: which of this user's reminders are
now in the past and not yet handled? Those get shown as a "due now"
banner right there in the page, and repeating reminders get rolled
forward to their next occurrence automatically.
"""
from datetime import timedelta

from django.utils import timezone

from .models import Reminder


def get_and_process_due_reminders(user):
    """
    Returns the list of reminders that just became due for this user, and
    updates them in the same call: one-off reminders are marked as sent,
    repeating ones are rolled forward to their next date/time.
    """
    now = timezone.now()
    due = list(Reminder.objects.filter(user=user, is_sent=False, remind_at__lte=now))

    for reminder in due:
        if reminder.repeat == "none":
            reminder.is_sent = True
        elif reminder.repeat == "daily":
            reminder.remind_at = reminder.remind_at + timedelta(days=1)
        elif reminder.repeat == "weekly":
            reminder.remind_at = reminder.remind_at + timedelta(weeks=1)
        reminder.save()

    return due
