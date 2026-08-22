"""
URL routing for Hadith reader, collections, bookmarks, and tracking.
"""
from django.urls import path
from . import views

app_name = "hadith"

urlpatterns = [
    path("", views.HadithHomeView.as_view(), name="home"),
    path("collection/<str:collection_id>/", views.HadithCollectionView.as_view(), name="collection"),
    path("collection/<str:collection_id>/<int:number>/", views.HadithDetailView.as_view(), name="detail"),
    path("bookmarks/", views.HadithBookmarksListView.as_view(), name="bookmarks"),
    path("bookmarks/add/", views.add_hadith_bookmark, name="bookmark_add"),
    path("bookmarks/<int:pk>/delete/", views.HadithBookmarkDeleteView.as_view(), name="bookmark_delete"),
    path("toggle-read/<str:collection_id>/<int:number>/", views.toggle_hadith_read, name="toggle_read"),
]
