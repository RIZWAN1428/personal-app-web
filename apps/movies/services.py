"""
Service helper for Movie & TV Series discovery, metadata fetching, and curated classics.
"""
import json
import logging
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)

# Curated Bollywood & Hollywood classics ready to add in 1 click
CURATED_MOVIES = [
    # Bollywood
    {
        "title": "3 Idiots",
        "media_type": "movie",
        "industry": "bollywood",
        "genre": "comedy",
        "release_year": 2009,
        "director": "Rajkumar Hirani",
        "cast": "Aamir Khan, Kareena Kapoor, R. Madhavan, Sharman Joshi",
        "imdb_rating": 8.4,
        "where_to_watch": "Prime Video / YouTube",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BNTkyOGVjMGEtNmQzZi00NzFlLTlhOWQtODYyMDc2ZGJmYzFhXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_FMjpg_UX1000_.jpg",
        "review": "All-time masterpiece about true education, passion, and friendship.",
    },
    {
        "title": "Jab We Met",
        "media_type": "movie",
        "industry": "bollywood",
        "genre": "rom_com",
        "release_year": 2007,
        "director": "Imtiaz Ali",
        "cast": "Shahid Kapoor, Kareena Kapoor",
        "imdb_rating": 7.9,
        "where_to_watch": "Netflix / Prime Video",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BMjA4Njg1MjcyMV5BMl5BanBnXkFtZTcwMzAxOTk1MQ@@._V1_FMjpg_UX1000_.jpg",
        "review": "Iconic romantic comedy with unforgettable songs and characters.",
    },
    {
        "title": "Dangal",
        "media_type": "movie",
        "industry": "bollywood",
        "genre": "biography",
        "release_year": 2016,
        "director": "Nitesh Tiwari",
        "cast": "Aamir Khan, Fatima Sana Shaikh, Sanya Malhotra",
        "imdb_rating": 8.3,
        "where_to_watch": "Netflix",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BMTQ4MzQzMzM2Nl5BMl5BanBnXkFtZTgwMTQ1NzU3MDI@._V1_FMjpg_UX1000_.jpg",
        "review": "Incredible inspiring story of hard work, grit, and breaking stereotypes.",
    },
    {
        "title": "Panchayat",
        "media_type": "series",
        "industry": "bollywood",
        "genre": "comedy",
        "release_year": 2020,
        "director": "Deepak Kumar Mishra",
        "cast": "Jitendra Kumar, Neena Gupta, Raghubir Yadav",
        "imdb_rating": 8.9,
        "where_to_watch": "Prime Video",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BMTNjODU4YWYtZmQ3Ny00NDY4LWI3NzEtYmZiMzg3Zjg1MWNkXkEyXkFqcGdeQXVyODg4MDY4MTA@._V1_FMjpg_UX1000_.jpg",
        "review": "Heartwarming and realistic portrayal of rural Indian life with exceptional writing.",
    },
    # Hollywood
    {
        "title": "Interstellar",
        "media_type": "movie",
        "industry": "hollywood",
        "genre": "sci_fi",
        "release_year": 2014,
        "director": "Christopher Nolan",
        "cast": "Matthew McConaughey, Anne Hathaway, Jessica Chastain",
        "imdb_rating": 8.7,
        "where_to_watch": "Prime Video / Netflix",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_FMjpg_UX1000_.jpg",
        "review": "Breathtaking sci-fi epic about love, time, human survival, and relativity.",
    },
    {
        "title": "Inception",
        "media_type": "movie",
        "industry": "hollywood",
        "genre": "sci_fi",
        "release_year": 2010,
        "director": "Christopher Nolan",
        "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt, Elliot Page",
        "imdb_rating": 8.8,
        "where_to_watch": "Netflix / JioCinema",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_FMjpg_UX1000_.jpg",
        "review": "Mind-bending heist thriller through layers of subconscious dreams.",
    },
    {
        "title": "Stranger Things",
        "media_type": "series",
        "industry": "hollywood",
        "genre": "sci_fi",
        "release_year": 2016,
        "director": "The Duffer Brothers",
        "cast": "Millie Bobby Brown, Finn Wolfhard, Winona Ryder",
        "imdb_rating": 8.7,
        "where_to_watch": "Netflix",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BMDZkYmVhNjMtNWU4MC00MDQxLWE3YTItYjkwZGY0ZTBlZDNlXkEyXkFqcGdeQXVyMTkxNjUyNQ@@._V1_FMjpg_UX1000_.jpg",
        "review": "Thrilling 80s nostalgic supernatural series with memorable characters.",
    },
    {
        "title": "La La Land",
        "media_type": "movie",
        "industry": "hollywood",
        "genre": "rom_com",
        "release_year": 2016,
        "director": "Damien Chazelle",
        "cast": "Ryan Gosling, Emma Stone",
        "imdb_rating": 8.0,
        "where_to_watch": "Lionsgate Play / Prime Video",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BMzUzNDM2NzM2MV5BMl5BanBnXkFtZTgwNTM3NTg4OTE@._V1_FMjpg_UX1000_.jpg",
        "review": "Gorgeous romantic musical celebrating dreams, passion, and heartbreak in Los Angeles.",
    },
]


def get_curated_movies():
    """Returns curated popular movies & series."""
    return CURATED_MOVIES


def search_free_movie_api(query):
    """
    Searches for movie/series metadata and poster image using TVMaze and open media endpoints.
    """
    if not query:
        return []

    encoded = urllib.parse.quote(query)
    url = f"https://api.tvmaze.com/search/shows?q={encoded}"
    results = []

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PersonalApp-Movies/1.0"})
        with urllib.request.urlopen(req, timeout=6) as response:
            data = json.loads(response.read().decode("utf-8"))
            for item in data[:8]:
                show = item.get("show", {})
                image_data = show.get("image") or {}
                poster = image_data.get("medium") or image_data.get("original") or ""

                genres = show.get("genres", [])
                genre_str = ", ".join(genres) if genres else "Drama"

                premiered = show.get("premiered") or ""
                year = int(premiered.split("-")[0]) if premiered and "-" in premiered else None

                rating_data = show.get("rating") or {}
                rating = rating_data.get("average")

                # Clean summary HTML tags
                summary = show.get("summary") or ""
                clean_summary = summary.replace("<p>", "").replace("</p>", "").replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")

                results.append({
                    "title": show.get("name", ""),
                    "media_type": "series" if show.get("type") in ["Scripted", "Animation"] else "movie",
                    "genre": genre_str,
                    "release_year": year,
                    "imdb_rating": rating,
                    "poster_url": poster,
                    "summary": clean_summary[:200] + "..." if len(clean_summary) > 200 else clean_summary,
                })
    except Exception as e:
        logger.warning(f"Error searching movie API: {e}")

    # Fallback / match from curated if nothing returned
    if not results:
        q_lower = query.lower()
        for m in CURATED_MOVIES:
            if q_lower in m["title"].lower():
                results.append({
                    "title": m["title"],
                    "media_type": m["media_type"],
                    "genre": m["genre"].replace("_", " ").title(),
                    "release_year": m["release_year"],
                    "imdb_rating": m["imdb_rating"],
                    "poster_url": m["poster_url"],
                    "summary": m["review"],
                })

    return results
