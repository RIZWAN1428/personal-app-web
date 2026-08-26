"""
Sync API endpoints — lightweight JSON API for the offline-first PWA layer.

These endpoints mirror the existing form-based Django views but accept/return
JSON instead of HTML. They use the same session authentication (login cookies).

Supported modules: Notes, Checklist, Reminders, Salah prayer log, Streaks.
"""
import json
from datetime import date, datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

from apps.checklist.models import ChecklistItem
from apps.notes.models import Note
from apps.reminders.models import Reminder
from apps.salah.models import SalahDailyLog
from apps.streaks.models import Habit, HabitLog
from apps.streaks.services import ensure_default_habits, get_habit_stats


def _parse_json_body(request):
    """Parse JSON body from request, falling back to POST data."""
    content_type = request.content_type or ''
    if 'application/json' in content_type:
        try:
            return json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return {}
    # Fallback: treat as form-encoded POST
    return dict(request.POST)


def _error(msg, status=400):
    return JsonResponse({'success': False, 'error': msg}, status=status)


# ---------------------------------------------------------------------------
# NOTES
# ---------------------------------------------------------------------------
@login_required
@require_POST
def sync_note(request):
    """Create or update a note. Send {title, body, is_pinned, server_id?}."""
    data = _parse_json_body(request)
    title = data.get('title', '').strip()
    if not title:
        return _error('Title is required.')

    body = data.get('body', '')
    is_pinned = data.get('is_pinned', False)
    server_id = data.get('server_id')  # if updating an existing note

    if server_id:
        try:
            note = Note.objects.get(pk=server_id, user=request.user)
            note.title = title
            note.body = body
            note.is_pinned = bool(is_pinned)
            note.save()
        except Note.DoesNotExist:
            return _error('Note not found.', 404)
    else:
        note = Note.objects.create(
            user=request.user,
            title=title,
            body=body,
            is_pinned=bool(is_pinned),
        )

    return JsonResponse({
        'success': True,
        'id': note.pk,
        'title': note.title,
        'updated_at': note.updated_at.isoformat(),
    })


@login_required
@require_POST
def sync_note_delete(request):
    """Delete a note. Send {server_id}."""
    data = _parse_json_body(request)
    server_id = data.get('server_id')
    if not server_id:
        return _error('server_id is required.')

    try:
        note = Note.objects.get(pk=server_id, user=request.user)
        note.delete()
        return JsonResponse({'success': True, 'deleted_id': server_id})
    except Note.DoesNotExist:
        # Already deleted — treat as success (idempotent)
        return JsonResponse({'success': True, 'deleted_id': server_id})


# ---------------------------------------------------------------------------
# CHECKLIST
# ---------------------------------------------------------------------------
@login_required
@require_POST
def sync_checklist(request):
    """Create a checklist item. Send {text, due_date?}."""
    data = _parse_json_body(request)
    text = data.get('text', '').strip()
    if not text:
        return _error('Text is required.')

    due_date = data.get('due_date')
    if due_date:
        try:
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            due_date = None

    item = ChecklistItem.objects.create(
        user=request.user,
        text=text,
        due_date=due_date,
    )

    return JsonResponse({
        'success': True,
        'id': item.pk,
        'text': item.text,
    })


@login_required
@require_POST
def sync_checklist_toggle(request):
    """Toggle is_done on a checklist item. Send {server_id}."""
    data = _parse_json_body(request)
    server_id = data.get('server_id')
    if not server_id:
        return _error('server_id is required.')

    try:
        item = ChecklistItem.objects.get(pk=server_id, user=request.user)
        item.is_done = not item.is_done
        item.save(update_fields=['is_done'])
        return JsonResponse({'success': True, 'id': item.pk, 'is_done': item.is_done})
    except ChecklistItem.DoesNotExist:
        return _error('Checklist item not found.', 404)


@login_required
@require_POST
def sync_checklist_delete(request):
    """Delete a checklist item. Send {server_id}."""
    data = _parse_json_body(request)
    server_id = data.get('server_id')
    if not server_id:
        return _error('server_id is required.')

    try:
        item = ChecklistItem.objects.get(pk=server_id, user=request.user)
        item.delete()
    except ChecklistItem.DoesNotExist:
        pass  # Idempotent

    return JsonResponse({'success': True, 'deleted_id': server_id})


# ---------------------------------------------------------------------------
# REMINDERS
# ---------------------------------------------------------------------------
@login_required
@require_POST
def sync_reminder(request):
    """Create a reminder. Send {title, notes?, remind_at, repeat?}."""
    data = _parse_json_body(request)
    title = data.get('title', '').strip()
    remind_at_str = data.get('remind_at', '')

    if not title:
        return _error('Title is required.')
    if not remind_at_str:
        return _error('remind_at is required.')

    try:
        remind_at = datetime.fromisoformat(remind_at_str)
    except (ValueError, TypeError):
        return _error('Invalid remind_at format. Use ISO format.')

    notes = data.get('notes', '')
    repeat = data.get('repeat', 'none')
    if repeat not in ('none', 'daily', 'weekly'):
        repeat = 'none'

    reminder = Reminder.objects.create(
        user=request.user,
        title=title,
        notes=notes,
        remind_at=remind_at,
        repeat=repeat,
    )

    return JsonResponse({
        'success': True,
        'id': reminder.pk,
        'title': reminder.title,
    })


# ---------------------------------------------------------------------------
# SALAH — Toggle prayer log
# ---------------------------------------------------------------------------
@login_required
@require_POST
def sync_salah_toggle(request):
    """Toggle a specific prayer for today. Send {prayer_name}."""
    data = _parse_json_body(request)
    prayer_name = data.get('prayer_name', '').lower().strip()

    valid_prayers = ('fajr', 'dhuhr', 'asr', 'maghrib', 'isha')
    if prayer_name not in valid_prayers:
        return _error(f'Invalid prayer name. Must be one of: {", ".join(valid_prayers)}')

    today = date.today()
    log, _ = SalahDailyLog.objects.get_or_create(user=request.user, date=today)

    current_val = getattr(log, prayer_name)
    setattr(log, prayer_name, not current_val)
    log.save(update_fields=[prayer_name, 'updated_at'])

    return JsonResponse({
        'success': True,
        'prayer': prayer_name,
        'is_done': not current_val,
        'completed_count': log.completed_count,
    })


# ---------------------------------------------------------------------------
# STREAKS — Toggle habit for today
# ---------------------------------------------------------------------------
@login_required
@require_POST
def sync_streak_toggle(request):
    """Toggle a habit for today. Send {habit_id}."""
    data = _parse_json_body(request)
    habit_id = data.get('habit_id')
    if not habit_id:
        return _error('habit_id is required.')

    try:
        habit = Habit.objects.get(pk=habit_id, user=request.user)
    except Habit.DoesNotExist:
        return _error('Habit not found.', 404)

    today = date.today()
    log, created = HabitLog.objects.get_or_create(
        user=request.user,
        habit=habit,
        date=today,
        defaults={'is_completed': True},
    )

    if not created:
        log.is_completed = not log.is_completed
        log.save(update_fields=['is_completed'])

    stats = get_habit_stats(habit)

    return JsonResponse({
        'success': True,
        'habit_id': habit.pk,
        'is_completed': log.is_completed,
        'current_streak': stats['current_streak'],
    })


# ---------------------------------------------------------------------------
# SYNC STATUS — How many items are pending?
# ---------------------------------------------------------------------------
@login_required
@require_GET
def sync_status(request):
    """Returns a simple ping/status for the sync system. Used as health check."""
    return JsonResponse({
        'success': True,
        'online': True,
        'user': request.user.email,
    })
