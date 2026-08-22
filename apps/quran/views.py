"""
Views for Quran reading, tracking, bookmarking, searching, and audio playback.
"""
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import DeleteView, ListView, TemplateView, View

from .forms import QuranBookmarkForm
from .models import QuranBookmark, QuranReadingProgress, QuranSurahLog
from .services import get_surah_by_number, get_surah_list, get_surah_verses, search_quran


def get_user_progress(user):
    """Retrieves or creates QuranReadingProgress for a user."""
    progress, _ = QuranReadingProgress.objects.get_or_create(
        user=user,
        defaults={"last_surah": 1, "last_ayah": 1, "surah_name": "Al-Faatiha", "total_ayahs_read": 0},
    )
    return progress


class QuranHomeView(LoginRequiredMixin, TemplateView):
    template_name = "quran/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        progress = get_user_progress(user)

        surahs = get_surah_list()
        completed_surahs = set(
            QuranSurahLog.objects.filter(user=user, is_completed=True).values_list("surah_number", flat=True)
        )
        bookmarks_count = QuranBookmark.objects.filter(user=user).count()

        # Generate Juz list (1 to 30)
        juz_list = []
        for j in range(1, 31):
            juz_list.append({"number": j, "name": f"Juz {j} (Para {j})"})

        context["surahs"] = surahs
        context["completed_surahs"] = completed_surahs
        context["progress"] = progress
        context["bookmarks_count"] = bookmarks_count
        context["juz_list"] = juz_list
        return context


class SurahDetailView(LoginRequiredMixin, TemplateView):
    template_name = "quran/surah.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        surah_number = int(self.kwargs.get("number", 1))
        user = self.request.user

        # Fetch Surah verses and translations
        data = get_surah_verses(surah_number)
        surah_meta = data.get("surah", {})
        ayahs = data.get("ayahs", [])

        # Update last read progress
        progress = get_user_progress(user)
        target_ayah = int(self.request.GET.get("ayah", 1))
        progress.last_surah = surah_number
        progress.last_ayah = target_ayah
        progress.surah_name = surah_meta.get("englishName", f"Surah {surah_number}")
        progress.save(update_fields=["last_surah", "last_ayah", "surah_name", "last_read_at"])

        # Fetch user's existing bookmarks for this Surah
        bookmarked_ayah_numbers = set(
            QuranBookmark.objects.filter(user=user, surah_number=surah_number).values_list("ayah_number", flat=True)
        )

        # Surah log status
        surah_log = QuranSurahLog.objects.filter(user=user, surah_number=surah_number).first()
        is_completed = surah_log.is_completed if surah_log else False

        context["surah"] = surah_meta
        context["ayahs"] = ayahs
        context["surah_number"] = surah_number
        context["prev_surah"] = surah_number - 1 if surah_number > 1 else None
        context["next_surah"] = surah_number + 1 if surah_number < 114 else None
        context["bookmarked_ayahs"] = bookmarked_ayah_numbers
        context["is_completed"] = is_completed
        context["target_ayah"] = target_ayah
        context["progress"] = progress
        context["bookmark_form"] = QuranBookmarkForm()
        return context


class QuranSearchView(LoginRequiredMixin, TemplateView):
    template_name = "quran/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        context["query"] = query
        if query:
            results_data = search_quran(query)
            context["results"] = results_data.get("results", [])
            context["count"] = results_data.get("count", 0)
        else:
            context["results"] = []
            context["count"] = 0
        return context


class QuranBookmarksListView(LoginRequiredMixin, ListView):
    model = QuranBookmark
    template_name = "quran/bookmarks.html"
    context_object_name = "bookmarks"

    def get_queryset(self):
        return QuranBookmark.objects.filter(user=self.request.user)


@login_required
def add_bookmark(request):
    """Adds a bookmark for an Ayah with an optional personal reflection note."""
    if request.method == "POST":
        surah_number = int(request.POST.get("surah_number", 1))
        ayah_number = int(request.POST.get("ayah_number", 1))
        surah_name = request.POST.get("surah_name", f"Surah {surah_number}")
        arabic_text = request.POST.get("arabic_text", "")
        translation_text = request.POST.get("translation_text", "")
        note = request.POST.get("note", "")

        bookmark, created = QuranBookmark.objects.update_or_create(
            user=request.user,
            surah_number=surah_number,
            ayah_number=ayah_number,
            defaults={
                "surah_name": surah_name,
                "arabic_text": arabic_text,
                "translation_text": translation_text,
                "note": note,
            },
        )
        if created:
            messages.success(request, f"Bookmarked {surah_name} {surah_number}:{ayah_number}.")
        else:
            messages.success(request, f"Updated bookmark note for {surah_name} {surah_number}:{ayah_number}.")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("quran:home")))


class QuranBookmarkDeleteView(LoginRequiredMixin, DeleteView):
    model = QuranBookmark
    success_url = reverse_lazy("quran:bookmarks")

    def get_queryset(self):
        return QuranBookmark.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Bookmark removed.")
        return super().delete(request, *args, **kwargs)


@login_required
def update_reading_progress(request):
    """
    AJAX / POST endpoint to save current reading position and increment read verses count.
    """
    if request.method == "POST":
        surah_number = int(request.POST.get("surah_number", 1))
        ayah_number = int(request.POST.get("ayah_number", 1))
        surah_name = request.POST.get("surah_name", "")
        ayahs_read_increment = int(request.POST.get("ayahs_read", 0))

        progress = get_user_progress(request.user)
        progress.last_surah = surah_number
        progress.last_ayah = ayah_number
        if surah_name:
            progress.surah_name = surah_name
        if ayahs_read_increment > 0:
            progress.total_ayahs_read += ayahs_read_increment
        progress.save()

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "total_read": progress.total_ayahs_read,
                "khatam_pct": progress.khatam_percentage,
            })
        messages.success(request, f"Reading progress saved at {progress.surah_name} {surah_number}:{ayah_number}.")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("quran:home")))


@login_required
def toggle_surah_complete(request, number):
    """Marks or unmarks an entire Surah as completed."""
    surah_number = int(number)
    surah_meta = get_surah_by_number(surah_number)
    surah_name = surah_meta["englishName"] if surah_meta else f"Surah {surah_number}"

    log, created = QuranSurahLog.objects.get_or_create(
        user=request.user,
        surah_number=surah_number,
        defaults={"surah_name": surah_name, "is_completed": False},
    )
    log.is_completed = not log.is_completed
    if log.is_completed:
        log.completed_at = timezone.now()
        # Add surah ayahs count to total read
        if surah_meta:
            progress = get_user_progress(request.user)
            progress.total_ayahs_read += surah_meta.get("numberOfAyahs", 0)
            progress.save(update_fields=["total_ayahs_read"])
        messages.success(request, f"Surah {surah_name} marked as completed! MashAllah.")
    else:
        log.completed_at = None
        messages.info(request, f"Surah {surah_name} unmarked as completed.")
    log.save()

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("quran:surah", kwargs={"number": surah_number})))
