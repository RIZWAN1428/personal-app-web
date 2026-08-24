"""
Database models for Books Library, Categorization, Reading Status, and PDF Reader Progress.
"""
from django.conf import settings
from django.db import models


CATEGORY_CHOICES = [
    ("religious", "Religious / Islamic"),
    ("non_religious", "Non-Religious / General"),
    ("self_help", "Self-Help / Productivity"),
    ("fiction", "Fiction / Novels"),
    ("history", "History / Biography"),
    ("academic", "Academic / Science / Tech"),
]

STATUS_CHOICES = [
    ("reading", "Currently Reading"),
    ("completed", "Completed (Read Till Now)"),
    ("want_to_read", "Want to Read (Gonna Read)"),
    ("on_hold", "On Hold"),
]

RATING_CHOICES = [
    (1, "★☆☆☆☆ (1/5)"),
    (2, "★★☆☆☆ (2/5)"),
    (3, "★★★☆☆ (3/5)"),
    (4, "★★★★☆ (4/5)"),
    (5, "★★★★★ (5/5)"),
]


class Book(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="books",
    )
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="non_religious")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="want_to_read")
    is_favorite = models.BooleanField(default=False)
    
    # Cover & PDF files
    cover_image_url = models.URLField(max_length=500, blank=True)
    pdf_file = models.FileField(upload_to="books/pdfs/", blank=True, null=True)
    pdf_url = models.URLField(max_length=500, blank=True, help_text="Direct link to free online PDF")

    # Reading progress for PDF auto-resume
    current_page = models.PositiveIntegerField(default=1)
    total_pages = models.PositiveIntegerField(default=1)

    # Personal review & ratings
    rating = models.PositiveSmallIntegerField(null=True, blank=True, choices=RATING_CHOICES)
    review = models.TextField(blank=True)

    # Timestamps
    started_at = models.DateField(null=True, blank=True)
    finished_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "category"]),
            models.Index(fields=["user", "is_favorite"]),
        ]

    def __str__(self):
        return f"{self.title} by {self.author or 'Unknown'}"

    @property
    def progress_percentage(self):
        if not self.total_pages or self.total_pages <= 0:
            return 0
        pct = (self.current_page / self.total_pages) * 100
        return min(100, max(0, int(pct)))

    @property
    def has_pdf(self):
        return bool(self.pdf_file or self.pdf_url)

    @property
    def pdf_source(self):
        if self.pdf_file:
            return self.pdf_file.url
        if self.pdf_url:
            from django.urls import reverse
            return reverse("books:pdf_proxy", kwargs={"pk": self.pk})
        return ""



class BookNote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="book_notes",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    page_number = models.PositiveIntegerField(null=True, blank=True)
    quote_text = models.TextField(blank=True, help_text="Key quote or excerpt from the book")
    note_text = models.TextField(help_text="Personal thoughts, lessons, or takeaways")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["page_number", "-created_at"]

    def __str__(self):
        return f"Note on {self.book.title} (Page {self.page_number or 'General'})"
