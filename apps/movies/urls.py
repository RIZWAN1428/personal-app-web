"""
URL routing for Movies and Series app.
"""
from django.urls import path
from . import views

app_name = "movies"

urlpatterns = [
    path("", views.MovieListView.as_view(), name="list"),
    path("add/", views.MovieCreateView.as_view(), name="create"),
    path("discover/", views.DiscoverMoviesView.as_view(), name="discover"),
    path("quick-add/", views.quick_add_curated_movie, name="quick_add"),
    path("api/search/", views.search_movie_api_endpoint, name="api_search"),
    path("<int:pk>/", views.MovieDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.MovieUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.MovieDeleteView.as_view(), name="delete"),
    path("<int:pk>/favorite/", views.toggle_movie_favorite, name="favorite"),
    path("<int:pk>/status/<str:new_status>/", views.quick_change_movie_status, name="change_status"),
]
