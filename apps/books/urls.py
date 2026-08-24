"""
URL routing for Books library, PDF reader, and notes.
"""
from django.urls import path
from . import views

app_name = "books"

urlpatterns = [
    path("", views.BookListView.as_view(), name="list"),
    path("add/", views.BookCreateView.as_view(), name="create"),
    path("discover/", views.DiscoverBooksView.as_view(), name="discover"),
    path("quick-add/", views.quick_add_curated, name="quick_add"),
    path("<int:pk>/", views.BookDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.BookUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.BookDeleteView.as_view(), name="delete"),
    path("<int:pk>/read/", views.BookPDFReaderView.as_view(), name="reader"),
    path("<int:pk>/pdf-proxy/", views.proxy_pdf, name="pdf_proxy"),
    path("<int:pk>/progress/", views.update_reading_progress, name="progress"),
    path("<int:pk>/status/<str:new_status>/", views.quick_change_status, name="change_status"),
    path("<int:pk>/favorite/", views.toggle_favorite, name="favorite"),
    path("<int:pk>/notes/add/", views.add_book_note, name="note_add"),
    path("<int:pk>/notes/<int:note_id>/delete/", views.delete_book_note, name="note_delete"),
]
