"""
Service helper for Books discovery, Open Library search, and curated free public domain PDFs.
"""
import json
import logging
import re
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)


def resolve_direct_pdf_url(url):
    """
    Resolves external webpage URLs (e.g. Internet Archive details page, Google Drive links)
    to direct raw PDF download URLs.
    """
    if not url:
        return ""

    url = url.strip()

    # Internet Archive resolution
    if "archive.org/details/" in url or "archive.org/stream/" in url or "archive.org/embed/" in url:
        match = re.search(r'archive\.org/(?:details|stream|embed)/([^/]+)(?:/([^/]+))?', url)
        if match:
            item_id = match.group(1)
            sub_file = match.group(2) if match.group(2) else ""
            meta_url = f"https://archive.org/metadata/{item_id}"
            try:
                req = urllib.request.Request(meta_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                with urllib.request.urlopen(req, timeout=8) as res:
                    data = json.loads(res.read().decode("utf-8"))
                    files = data.get("files", [])
                    pdf_files = [f["name"] for f in files if f.get("name", "").endswith(".pdf")]
                    if pdf_files:
                        if sub_file:
                            sub_clean = sub_file.lower()
                            for pdf in pdf_files:
                                if sub_clean in pdf.lower():
                                    return f"https://archive.org/download/{item_id}/{pdf}"
                        main_pdfs = [p for p in pdf_files if not p.endswith("_text.pdf")]
                        chosen = main_pdfs[0] if main_pdfs else pdf_files[0]
                        return f"https://archive.org/download/{item_id}/{chosen}"
            except Exception as e:
                logger.warning(f"Archive metadata lookup error: {e}")

    # Google Drive resolution
    drive_match = re.search(r'drive\.google\.com/(?:file/d/|open\?id=)([a-zA-Z0-9_-]+)', url)
    if drive_match:
        file_id = drive_match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"

    return url

# Curated catalog of free, permanent, public domain and open-access books with verified PDF links
CURATED_FREE_BOOKS = [
    {
        "title": "The Sealed Nectar (Ar-Raheeq Al-Makhtum)",
        "author": "Safi-ur-Rahman al-Mubarakpuri",
        "category": "religious",
        "description": "The award-winning authoritative biography (Seerah) of the Prophet Muhammad (ﷺ).",
        "cover_image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=400&q=80",
        "pdf_url": "https://www.muslim-library.com/dl/books/English_ArRaheeq_AlMakhtum_THE_SEALED_NECTAR.pdf",
        "total_pages": 480,
    },
    {
        "title": "Don't Be Sad (La Tahzan)",
        "author": "Dr. A'id al-Qarni",
        "category": "religious",
        "description": "An immensely practical Islamic self-help and psychological guide to overcoming distress and grief.",
        "cover_image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=400&q=80",
        "pdf_url": "https://www.islamicbulletin.org/free_downloads/women/dont_be_sad.pdf",
        "total_pages": 472,
    },
    {
        "title": "Meditations",
        "author": "Marcus Aurelius",
        "category": "self_help",
        "description": "Timeless reflections on stoic philosophy, self-discipline, resilience, and inner tranquility.",
        "cover_image_url": "https://images.unsplash.com/photo-1532012164546-f432f2e3edd4?auto=format&fit=crop&w=400&q=80",
        "pdf_url": "https://www.gutenberg.org/files/2680/2680-pdf.pdf",
        "total_pages": 190,
    },
    {
        "title": "As a Man Thinketh",
        "author": "James Allen",
        "category": "self_help",
        "description": "Classic essay on the power of thoughts and mindset in shaping one's character and circumstances.",
        "cover_image_url": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=400&q=80",
        "pdf_url": "https://www.gutenberg.org/files/4507/4507-pdf.pdf",
        "total_pages": 65,
    },
    {
        "title": "The Art of War",
        "author": "Sun Tzu",
        "category": "history",
        "description": "Ancient military treatise on strategy, tactical positioning, leadership, and conflict resolution.",
        "cover_image_url": "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?auto=format&fit=crop&w=400&q=80",
        "pdf_url": "https://www.gutenberg.org/files/17405/17405-pdf.pdf",
        "total_pages": 110,
    },
]


def get_curated_free_books():
    """Returns curated free books list."""
    return CURATED_FREE_BOOKS


def search_open_library_books(query):
    """
    Searches Open Library for books matching the query.
    Returns title, author, cover image, and page count.
    """
    if not query:
        return []

    encoded = urllib.parse.quote(query)
    url = f"https://openlibrary.org/search.json?q={encoded}&limit=8"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PersonalApp-Books/1.0"})
        with urllib.request.urlopen(req, timeout=7) as response:
            data = json.loads(response.read().decode("utf-8"))
            docs = data.get("docs", [])
            results = []
            for doc in docs:
                cover_id = doc.get("cover_i")
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else ""
                authors = doc.get("author_name", [])
                author_str = ", ".join(authors[:2]) if authors else "Unknown"

                results.append({
                    "title": doc.get("title", ""),
                    "author": author_str,
                    "first_publish_year": doc.get("first_publish_year", ""),
                    "cover_image_url": cover_url,
                    "total_pages": doc.get("number_of_pages_median") or 200,
                })
            return results
    except Exception as e:
        logger.warning(f"Failed to search Open Library: {e}")
        return []
