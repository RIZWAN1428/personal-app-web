"""
Views for Books Library, in-browser PDF reader, study notes, and discovery.
"""
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
import urllib.request
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import BookForm, BookNoteForm
from .models import Book, BookNote
from .services import get_curated_free_books, resolve_direct_pdf_url, search_open_library_books


class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = "books/list.html"
    context_object_name = "books"

    def get_queryset(self):
        user = self.request.user
        qs = Book.objects.filter(user=user)

        status = self.request.GET.get("status")
        if status in ["reading", "completed", "want_to_read", "on_hold"]:
            qs = qs.filter(status=status)
        elif status == "favorites":
            qs = qs.filter(is_favorite=True)

        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category=category)

        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(author__icontains=q))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        all_user_books = Book.objects.filter(user=user)

        context["total_books"] = all_user_books.count()
        context["completed_count"] = all_user_books.filter(status="completed").count()
        context["reading_count"] = all_user_books.filter(status="reading").count()
        context["want_to_read_count"] = all_user_books.filter(status="want_to_read").count()
        context["favorites_count"] = all_user_books.filter(is_favorite=True).count()

        context["religious_count"] = all_user_books.filter(category="religious").count()
        context["non_religious_count"] = all_user_books.filter(category="non_religious").count()
        context["self_help_count"] = all_user_books.filter(category="self_help").count()

        context["current_status"] = self.request.GET.get("status", "all")
        context["current_category"] = self.request.GET.get("category", "")
        context["search_query"] = self.request.GET.get("q", "")
        return context


class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = "books/detail.html"
    context_object_name = "book"

    def get_queryset(self):
        return Book.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["notes"] = self.object.notes.all()
        context["note_form"] = BookNoteForm()
        return context


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = "books/form.html"
    success_url = reverse_lazy("books:list")

    def get_initial(self):
        initial = super().get_initial()
        for field in ["title", "author", "cover_image_url", "total_pages", "category", "pdf_url"]:
            if field in self.request.GET:
                initial[field] = self.request.GET[field]
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f"'{form.instance.title}' added to your library!")
        return super().form_valid(form)


class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = "books/form.html"
    success_url = reverse_lazy("books:list")

    def get_queryset(self):
        return Book.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f"'{form.instance.title}' updated successfully.")
        return super().form_valid(form)


class BookDeleteView(LoginRequiredMixin, DeleteView):
    model = Book
    template_name = "books/confirm_delete.html"
    success_url = reverse_lazy("books:list")

    def get_queryset(self):
        return Book.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Book deleted from your library.")
        return super().delete(request, *args, **kwargs)


class BookPDFReaderView(LoginRequiredMixin, DetailView):
    """
    Dedicated full-screen reader view powered by PDF.js with auto-resume.
    """
    model = Book
    template_name = "books/reader.html"
    context_object_name = "book"

    def get_queryset(self):
        return Book.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["notes"] = self.object.notes.all()
        context["note_form"] = BookNoteForm()
        return context


@login_required
def proxy_pdf(request, pk):
    """
    Proxies external PDF requests through Django backend to bypass browser CORS restrictions.
    """
    book = get_object_or_404(Book, pk=pk, user=request.user)
    if book.pdf_file:
        return HttpResponseRedirect(book.pdf_file.url)

    raw_url = book.pdf_url
    if not raw_url:
        raise Http404("No PDF URL found for this book.")

    url = resolve_direct_pdf_url(raw_url)

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )
        response = urllib.request.urlopen(req, timeout=25)

        def stream_bytes():
            while True:
                chunk = response.read(64 * 1024)
                if not chunk:
                    break
                yield chunk

        res = StreamingHttpResponse(stream_bytes(), content_type="application/pdf")
        res["Access-Control-Allow-Origin"] = "*"
        res["Content-Disposition"] = f'inline; filename="{book.title}.pdf"'
        if "Content-Length" in response.headers:
            res["Content-Length"] = response.headers["Content-Length"]
        return res
    except Exception as e:
        return HttpResponse(f"Error proxying PDF: {str(e)}", status=502)


@login_required
def update_reading_progress(request, pk):
    """
    AJAX / POST endpoint to save the user's current reading page in a book.
    """
    book = get_object_or_404(Book, pk=pk, user=request.user)
    if request.method == "POST":
        current_page = int(request.POST.get("current_page", book.current_page))
        total_pages = int(request.POST.get("total_pages", book.total_pages))

        book.current_page = max(1, current_page)
        if total_pages > 0:
            book.total_pages = total_pages

        if book.status == "want_to_read" and book.current_page > 1:
            book.status = "reading"
            if not book.started_at:
                book.started_at = date.today()

        if book.total_pages > 1 and book.current_page >= book.total_pages:
            book.status = "completed"
            if not book.finished_at:
                book.finished_at = date.today()

        book.save()

        if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("is_ajax"):
            return JsonResponse({
                "success": True,
                "current_page": book.current_page,
                "total_pages": book.total_pages,
                "progress_percentage": book.progress_percentage,
                "status": book.status,
            })

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("books:detail", kwargs={"pk": pk})))


@login_required
def quick_change_status(request, pk, new_status):
    """1-Click change status of a book (e.g. mark as completed, reading, or want to read)."""
    book = get_object_or_404(Book, pk=pk, user=request.user)
    if new_status in ["reading", "completed", "want_to_read", "on_hold"]:
        book.status = new_status
        if new_status == "completed":
            if not book.finished_at:
                book.finished_at = date.today()
            if book.total_pages > 0:
                book.current_page = book.total_pages
            messages.success(request, f"Marked '{book.title}' as Completed! Great job.")
        elif new_status == "reading":
            if not book.started_at:
                book.started_at = date.today()
            messages.success(request, f"Marked '{book.title}' as Currently Reading.")
        elif new_status == "want_to_read":
            messages.info(request, f"Moved '{book.title}' to Want to Read shelf.")
        book.save()

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("books:detail", kwargs={"pk": pk})))


@login_required
def toggle_favorite(request, pk):
    """Toggles favorite status for a book."""
    book = get_object_or_404(Book, pk=pk, user=request.user)
    book.is_favorite = not book.is_favorite
    book.save(update_fields=["is_favorite"])
    if book.is_favorite:
        messages.success(request, f"Added '{book.title}' to favourites (⭐).")
    else:
        messages.info(request, f"Removed '{book.title}' from favourites.")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("books:list")))


@login_required
def add_book_note(request, pk):
    """Adds a page note or quote to a book."""
    book = get_object_or_404(Book, pk=pk, user=request.user)
    if request.method == "POST":
        form = BookNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.book = book
            note.save()
            messages.success(request, "Note saved successfully.")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("books:detail", kwargs={"pk": pk})))


@login_required
def delete_book_note(request, pk, note_id):
    """Deletes a book study note."""
    book = get_object_or_404(Book, pk=pk, user=request.user)
    note = get_object_or_404(BookNote, pk=note_id, book=book, user=request.user)
    note.delete()
    messages.info(request, "Note deleted.")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("books:detail", kwargs={"pk": pk})))


class DiscoverBooksView(LoginRequiredMixin, TemplateView):
    """
    Explore curated free books and search Open Library catalog.
    """
    template_name = "books/discover.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curated_books = get_curated_free_books()
        query = self.request.GET.get("q", "").strip()

        search_results = []
        if query:
            search_results = search_open_library_books(query)

        user_book_titles = set(Book.objects.filter(user=self.request.user).values_list("title", flat=True))

        context["curated_books"] = curated_books
        context["search_results"] = search_results
        context["query"] = query
        context["user_book_titles"] = user_book_titles
        return context


@login_required
def quick_add_curated(request):
    """1-Click adds a curated public domain book to user's library."""
    if request.method == "POST":
        title = request.POST.get("title")
        author = request.POST.get("author")
        category = request.POST.get("category", "religious")
        cover_image_url = request.POST.get("cover_image_url", "")
        pdf_url = request.POST.get("pdf_url", "")
        total_pages = int(request.POST.get("total_pages", 100))

        book, created = Book.objects.get_or_create(
            user=request.user,
            title=title,
            defaults={
                "author": author,
                "category": category,
                "cover_image_url": cover_image_url,
                "pdf_url": pdf_url,
                "total_pages": total_pages,
                "status": "reading",
            },
        )
        if created:
            messages.success(request, f"'{title}' added to your library!")
        else:
            messages.info(request, f"'{title}' is already in your library.")

    return redirect("books:list")
