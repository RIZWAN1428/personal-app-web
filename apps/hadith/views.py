"""
Views for Hadith collections, readers, bookmarks, and reading trackers.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, ListView, TemplateView

from .forms import HadithBookmarkForm
from .models import HadithBookmark, HadithReadingLog
from .services import (
    get_collection_by_id,
    get_daily_hadith,
    get_hadith_by_number,
    get_hadith_collections,
    get_hadiths_page,
)


class HadithHomeView(LoginRequiredMixin, TemplateView):
    template_name = "hadith/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        collections = get_hadith_collections()
        daily_hadith = get_daily_hadith()

        bookmarks_count = HadithBookmark.objects.filter(user=user).count()
        total_read_count = HadithReadingLog.objects.filter(user=user).count()

        context["collections"] = collections
        context["daily_hadith"] = daily_hadith
        context["bookmarks_count"] = bookmarks_count
        context["total_read_count"] = total_read_count
        return context


class HadithCollectionView(LoginRequiredMixin, TemplateView):
    template_name = "hadith/collection.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        collection_id = self.kwargs.get("collection_id", "bukhari")
        page = int(self.request.GET.get("page", 1))

        # Check if user searched for specific hadith number
        jump_number = self.request.GET.get("hadith_number")
        if jump_number and jump_number.isdigit():
            target_hadith = get_hadith_by_number(collection_id, int(jump_number))
            page_data = {
                "collection": get_collection_by_id(collection_id),
                "hadiths": [target_hadith] if target_hadith.get("success") else [],
                "current_page": 1,
                "total_pages": 1,
                "start_num": int(jump_number),
                "end_num": int(jump_number),
                "total": 1,
                "has_prev": False,
                "has_next": False,
            }
        else:
            page_data = get_hadiths_page(collection_id, page=page, page_size=10)

        # Get user's bookmarks and read items for this collection
        bookmarked_numbers = set(
            HadithBookmark.objects.filter(user=user, collection_id=collection_id).values_list("hadith_number", flat=True)
        )
        read_numbers = set(
            HadithReadingLog.objects.filter(user=user, collection_id=collection_id).values_list("hadith_number", flat=True)
        )

        context["collection"] = page_data.get("collection")
        context["collection_id"] = collection_id
        context["hadiths"] = page_data.get("hadiths", [])
        context["page_data"] = page_data
        context["bookmarked_numbers"] = bookmarked_numbers
        context["read_numbers"] = read_numbers
        context["bookmark_form"] = HadithBookmarkForm()
        return context


class HadithDetailView(LoginRequiredMixin, TemplateView):
    template_name = "hadith/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        collection_id = self.kwargs.get("collection_id", "bukhari")
        hadith_number = int(self.kwargs.get("number", 1))

        hadith = get_hadith_by_number(collection_id, hadith_number)
        collection = get_collection_by_id(collection_id)

        # Auto mark as read when opened
        HadithReadingLog.objects.get_or_create(
            user=user,
            collection_id=collection_id,
            hadith_number=str(hadith_number),
        )

        bookmark = HadithBookmark.objects.filter(
            user=user,
            collection_id=collection_id,
            hadith_number=str(hadith_number),
        ).first()

        context["hadith"] = hadith
        context["collection"] = collection
        context["collection_id"] = collection_id
        context["hadith_number"] = hadith_number
        context["prev_number"] = hadith_number - 1 if hadith_number > 1 else None
        context["next_number"] = hadith_number + 1 if (collection and hadith_number < collection["total_hadiths"]) else None
        context["bookmark"] = bookmark
        context["bookmark_form"] = HadithBookmarkForm()
        return context


class HadithBookmarksListView(LoginRequiredMixin, ListView):
    model = HadithBookmark
    template_name = "hadith/bookmarks.html"
    context_object_name = "bookmarks"

    def get_queryset(self):
        return HadithBookmark.objects.filter(user=self.request.user)


@login_required
def add_hadith_bookmark(request):
    """Saves or updates a hadith bookmark with reflection note."""
    if request.method == "POST":
        collection_id = request.POST.get("collection_id", "bukhari")
        collection_name = request.POST.get("collection_name", "Sahih al-Bukhari")
        hadith_number = str(request.POST.get("hadith_number", "1"))
        chapter_name = request.POST.get("chapter_name", "")
        arabic_text = request.POST.get("arabic_text", "")
        translation_text = request.POST.get("translation_text", "")
        grade = request.POST.get("grade", "Sahih")
        note = request.POST.get("note", "")

        bookmark, created = HadithBookmark.objects.update_or_create(
            user=request.user,
            collection_id=collection_id,
            hadith_number=hadith_number,
            defaults={
                "collection_name": collection_name,
                "chapter_name": chapter_name,
                "arabic_text": arabic_text,
                "translation_text": translation_text,
                "grade": grade,
                "note": note,
            },
        )
        if created:
            messages.success(request, f"Bookmarked {collection_name} #{hadith_number}.")
        else:
            messages.success(request, f"Updated notes for {collection_name} #{hadith_number}.")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("hadith:home")))


class HadithBookmarkDeleteView(LoginRequiredMixin, DeleteView):
    model = HadithBookmark
    success_url = reverse_lazy("hadith:bookmarks")

    def get_queryset(self):
        return HadithBookmark.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Hadith bookmark removed.")
        return super().delete(request, *args, **kwargs)


@login_required
def toggle_hadith_read(request, collection_id, number):
    """Marks or unmarks a hadith as read."""
    hadith_num_str = str(number)
    log = HadithReadingLog.objects.filter(
        user=request.user,
        collection_id=collection_id,
        hadith_number=hadith_num_str,
    ).first()

    if log:
        log.delete()
        messages.info(request, f"Unmarked #{hadith_num_str} as read.")
    else:
        HadithReadingLog.objects.create(
            user=request.user,
            collection_id=collection_id,
            hadith_number=hadith_num_str,
        )
        messages.success(request, f"Marked #{hadith_num_str} as read.")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("hadith:home")))
