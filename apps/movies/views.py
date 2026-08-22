"""
Views for Movies & Series watchlist, IMDb-style gallery, reviews, and discovery.
"""
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import MovieForm
from .models import Movie
from .services import get_curated_movies, search_free_movie_api


class MovieListView(LoginRequiredMixin, ListView):
    model = Movie
    template_name = "movies/list.html"
    context_object_name = "movies"

    def get_queryset(self):
        user = self.request.user
        qs = Movie.objects.filter(user=user)

        status = self.request.GET.get("status")
        if status in ["watched", "watching", "plan_to_watch", "on_hold", "dropped"]:
            qs = qs.filter(status=status)
        elif status == "favorites":
            qs = qs.filter(is_favorite=True)

        industry = self.request.GET.get("industry")
        if industry:
            qs = qs.filter(industry=industry)

        genre = self.request.GET.get("genre")
        if genre:
            qs = qs.filter(genre=genre)

        media_type = self.request.GET.get("media_type")
        if media_type:
            qs = qs.filter(media_type=media_type)

        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(director__icontains=q) | Q(cast__icontains=q))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        all_user_movies = Movie.objects.filter(user=user)

        context["total_movies"] = all_user_movies.count()
        context["watched_count"] = all_user_movies.filter(status="watched").count()
        context["watching_count"] = all_user_movies.filter(status="watching").count()
        context["plan_to_watch_count"] = all_user_movies.filter(status="plan_to_watch").count()
        context["favorites_count"] = all_user_movies.filter(is_favorite=True).count()

        context["bollywood_count"] = all_user_movies.filter(industry="bollywood").count()
        context["hollywood_count"] = all_user_movies.filter(industry="hollywood").count()
        context["series_count"] = all_user_movies.filter(media_type="series").count()

        context["current_status"] = self.request.GET.get("status", "all")
        context["current_industry"] = self.request.GET.get("industry", "")
        context["current_genre"] = self.request.GET.get("genre", "")
        context["current_media_type"] = self.request.GET.get("media_type", "")
        context["search_query"] = self.request.GET.get("q", "")
        return context


class MovieDetailView(LoginRequiredMixin, DetailView):
    model = Movie
    template_name = "movies/detail.html"
    context_object_name = "movie"

    def get_queryset(self):
        return Movie.objects.filter(user=self.request.user)


class MovieCreateView(LoginRequiredMixin, CreateView):
    model = Movie
    form_class = MovieForm
    template_name = "movies/form.html"
    success_url = reverse_lazy("movies:list")

    def get_initial(self):
        initial = super().get_initial()
        for field in ["title", "media_type", "industry", "genre", "status", "poster_url", "release_year", "director", "cast", "imdb_rating", "where_to_watch"]:
            if field in self.request.GET:
                initial[field] = self.request.GET[field]
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f"'{form.instance.title}' added to your movie collection!")
        return super().form_valid(form)


class MovieUpdateView(LoginRequiredMixin, UpdateView):
    model = Movie
    form_class = MovieForm
    template_name = "movies/form.html"
    success_url = reverse_lazy("movies:list")

    def get_queryset(self):
        return Movie.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f"'{form.instance.title}' updated successfully.")
        return super().form_valid(form)


class MovieDeleteView(LoginRequiredMixin, DeleteView):
    model = Movie
    template_name = "movies/confirm_delete.html"
    success_url = reverse_lazy("movies:list")

    def get_queryset(self):
        return Movie.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Movie removed from your list.")
        return super().delete(request, *args, **kwargs)


@login_required
def toggle_movie_favorite(request, pk):
    """1-Click favorite toggle."""
    movie = get_object_or_404(Movie, pk=pk, user=request.user)
    movie.is_favorite = not movie.is_favorite
    movie.save(update_fields=["is_favorite"])
    if movie.is_favorite:
        messages.success(request, f"Added '{movie.title}' to favourites (⭐).")
    else:
        messages.info(request, f"Removed '{movie.title}' from favourites.")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("movies:list")))


@login_required
def quick_change_movie_status(request, pk, new_status):
    """1-Click change watch status (e.g. mark Watched, Plan to Watch)."""
    movie = get_object_or_404(Movie, pk=pk, user=request.user)
    if new_status in ["watched", "watching", "plan_to_watch", "on_hold", "dropped"]:
        movie.status = new_status
        if new_status == "watched" and not movie.watched_date:
            movie.watched_date = date.today()
        movie.save()
        messages.success(request, f"Status of '{movie.title}' updated to {movie.get_status_display()}.")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("movies:detail", kwargs={"pk": pk})))


class DiscoverMoviesView(LoginRequiredMixin, TemplateView):
    """
    Explore curated popular Bollywood & Hollywood movies/series and live search.
    """
    template_name = "movies/discover.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curated_movies = get_curated_movies()
        query = self.request.GET.get("q", "").strip()

        search_results = []
        if query:
            search_results = search_free_movie_api(query)

        user_titles = set(Movie.objects.filter(user=self.request.user).values_list("title", flat=True))

        context["curated_movies"] = curated_movies
        context["search_results"] = search_results
        context["query"] = query
        context["user_titles"] = user_titles
        return context


@login_required
def quick_add_curated_movie(request):
    """1-Click adds a curated movie/series to user's collection."""
    if request.method == "POST":
        title = request.POST.get("title")
        media_type = request.POST.get("media_type", "movie")
        industry = request.POST.get("industry", "bollywood")
        genre = request.POST.get("genre", "rom_com")
        release_year = int(request.POST.get("release_year")) if request.POST.get("release_year") else None
        director = request.POST.get("director", "")
        cast = request.POST.get("cast", "")
        imdb_rating = float(request.POST.get("imdb_rating")) if request.POST.get("imdb_rating") else None
        where_to_watch = request.POST.get("where_to_watch", "")
        poster_url = request.POST.get("poster_url", "")
        review = request.POST.get("review", "")
        status = request.POST.get("status", "watched")

        movie, created = Movie.objects.get_or_create(
            user=request.user,
            title=title,
            defaults={
                "media_type": media_type,
                "industry": industry,
                "genre": genre,
                "release_year": release_year,
                "director": director,
                "cast": cast,
                "imdb_rating": imdb_rating,
                "where_to_watch": where_to_watch,
                "poster_url": poster_url,
                "review": review,
                "status": status,
            },
        )
        if created:
            messages.success(request, f"'{title}' added to your movies!")
        else:
            messages.info(request, f"'{title}' is already in your list.")

    return redirect("movies:list")


@login_required
def search_movie_api_endpoint(request):
    """AJAX endpoint for instant live movie metadata auto-fill."""
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"results": []})
    results = search_free_movie_api(q)
    return JsonResponse({"results": results})
