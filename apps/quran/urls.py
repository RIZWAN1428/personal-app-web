"""
URL routing for Quran reader, tracker, bookmarks, and search.
"""
from django.urls import path
from . import views

app_name = "quran"

urlpatterns = [
    path("", views.QuranHomeView.as_view(), name="home"),
    path("surah/<int:number>/", views.SurahDetailView.as_view(), name="surah"),
    path("search/", views.QuranSearchView.as_view(), name="search"),
    path("bookmarks/", views.QuranBookmarksListView.as_view(), name="bookmarks"),
    path("bookmarks/add/", views.add_bookmark, name="bookmark_add"),
    path("bookmarks/<int:pk>/delete/", views.QuranBookmarkDeleteView.as_view(), name="bookmark_delete"),
    path("progress/update/", views.update_reading_progress, name="progress_update"),
    path("surah/<int:number>/complete/", views.toggle_surah_complete, name="surah_complete"),
]
