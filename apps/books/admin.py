from django.contrib import admin
from .models import Book, BookNote


class BookNoteInline(admin.TabularInline):
    model = BookNote
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "user", "category", "status", "is_favorite", "current_page", "total_pages", "rating", "updated_at")
    list_filter = ("category", "status", "is_favorite", "rating")
    search_fields = ("title", "author", "user__email", "review")
    inlines = [BookNoteInline]


@admin.register(BookNote)
class BookNoteAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "page_number", "created_at")
    search_fields = ("book__title", "user__email", "quote_text", "note_text")
