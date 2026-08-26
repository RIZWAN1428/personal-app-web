# 🌟 Personal Productivity & Spiritual Dashboard (PWA)

A feature-packed, **offline-first Progressive Web Application (PWA)** built with Django, Bootstrap 5, PostgreSQL (Neon), and modern Web APIs (Service Worker, IndexedDB, Background Sync). 

Live Production URL: [https://personalapp-web.onrender.com/](https://personalapp-web.onrender.com/)

---

## 🚀 Key Highlights & Architecture

- **Offline-First PWA Support**: Installable on Android, iOS, and Desktop home screens. Operates completely offline with automatic local storage and background synchronization when reconnected to the internet.
- **Serverless PostgreSQL Backend**: Powered by **Neon PostgreSQL** with `dj-database-url` and connection pooling.
- **No Complex Dependencies**: Runs without Node.js, npm, or heavy frontend build pipelines. Pure Django templates enhanced with Bootstrap 5, vanilla JavaScript, and modern CSS.
- **Hosted on Render & Neon**: Deployed on Render's free tier paired with Neon's permanent free PostgreSQL serverless tier.

```mermaid
graph TD
    User["📱 Mobile / Desktop Device"] --> PWA["Service Worker (sw.js)"]
    PWA -->|"Offline"| IDB[("IndexedDB (offline-db.js)")]
    PWA -->|"Online"| Django["Django Server (Render)"]
    IDB -->|"Background Sync API"| Django
    Django --> Database[("Neon PostgreSQL DB")]
```

---

## ✨ Features & Functional Modules

### 🕌 1. Salah Timings & Daily Habit Tracker
- **Location-based Prayer Times**: Fetches precise prayer times using juristic calculation methods (ISNA, MWL, Umm Al-Qura, Karachi Hanafi/Standard).
- **Daily Prayer Logging**: Mark Fajr, Dhuhr, Asr, Maghrib, and Isha completed for the day.
- **Monthly Hijri Calendar**: Monthly view with Hijri dates and full prayer schedules.

### 📖 2. Holy Quran Reading Tracker & Bookmarks
- **Khatam Progress Tracker**: Visual progress bar tracking overall percentage (out of 6,236 Ayahs).
- **Verse Bookmarks**: Save favorite Ayahs with Arabic text, translation, and personal reflection notes.
- **Surah Completion Log**: Mark individual completed Surahs.

### 📜 3. Hadith Reflection & Daily Hadith
- **Featured Daily Hadith**: Rotating daily Hadith displayed right on the dashboard.
- **Collections Explorer**: Bookmark Hadiths from Sahih al-Bukhari, Sahih Muslim, Nawawi 40, and add personal study notes.

### 📚 4. Books Library & PDF Reader
- **Shelf Categorization**: Categorize by Religious, Productivity/Self-Help, Novels, Academic, etc.
- **In-Browser PDF Reader**: Built-in PDF reader powered by PDF.js with proxying to bypass CORS restrictions.
- **Auto-Resume & Notes**: Automatically saves reading page position and lets you annotate key quotes and study notes.
- **Open Library Discovery**: Search online catalog and 1-click add books to your library.

### 🎬 5. Movies & TV Shows Watchlist
- **Media Catalog**: Track Movies, TV/Web Series, Anime, and Documentaries across Bollywood, Hollywood, and Regional cinema.
- **Status & Rating**: Categorize into *Watched*, *Currently Watching*, or *Plan to Watch* with personal ratings ⭐ and reviews.
- **Live Search Auto-Fill**: Live search API integrations to quickly auto-populate movie poster URLs, directors, release year, and cast.

### 🔥 6. Daily Streak & Habit Tracker
- **Habit Categories**: Track daily habits including GitHub code pushes, DSA problem solving, Quran reading, and Naukri/LinkedIn job applications.
- **Heatmap & Calendar Detail**: Interactive monthly calendar with cross-marks (❌) and continuous streak calculations.

### 📝 7. Editable Notes
- **Personal Notes**: Markdown-supported rich notes with pin-to-top functionality, real-time search, and instant updates.

### 📋 8. Task Checklist
- **To-Do Management**: Simple checklist items with optional deadline dates and 1-click completion toggles.

### 🔔 9. Smart Reminders
- **Live-Checked Reminders**: Set single or repeating (daily/weekly) reminders. Automatically checked and surfaced on dashboard loads without needing heavy background Celery workers.

### ⚡ 10. Offline PWA Engine & Auto-Sync
- **App Shell Caching**: Service worker pre-caches CSS, JavaScript, fonts, icons, and HTML shells.
- **IndexedDB Action Queue**: Captures offline form submissions (creating notes, toggling tasks, marking habits, logging prayers).
- **Background Sync API**: When internet connectivity is restored, automatically replays queued actions to `/api/sync/` endpoints and updates Neon PostgreSQL.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Core Framework** | Python 3.12, Django 5.0.7 |
| **Database** | PostgreSQL (Hosted on Neon Serverless) |
| **Frontend** | Django Templates, Bootstrap 5.3.3, Bootstrap Icons, Google Fonts |
| **PWA & Offline** | Service Workers (`sw.js`), IndexedDB (`offline-db.js`), Background Sync, Web Manifest (`manifest.json`) |
| **Static Files** | WhiteNoise 6.7.0 (compressed static file serving) |
| **Production Server** | Gunicorn 22.0.0 |
| **Environment & Config** | `django-environ`, `dj-database-url` |

---

## 📁 Repository Structure

```
webapp/
├── apps/
│   ├── accounts/     # Custom User model (email login), profile, auth
│   ├── books/        # Books library, PDF reader proxy, study notes
│   ├── checklist/    # To-do items and completion logic
│   ├── core/         # Dashboard views, home statistics, PWA JSON Sync API
│   ├── hadith/       # Hadith bookmarks & daily Hadith service
│   ├── movies/       # Movie/Series watchlist & metadata search
│   ├── notes/        # Pinned & sorted personal notes
│   ├── quran/        # Quran progress, verse bookmarks, surah logs
│   ├── reminders/    # Live-checked scheduled reminders
│   ├── salah/        # Prayer timings calculation & daily Salah logs
│   └── streaks/      # Habit streak tracker & heatmaps
├── config/
│   ├── settings.py   # Django settings (12-factor env configuration)
│   ├── urls.py       # Main URL routing + Service Worker root routes
│   └── wsgi.py       # WSGI entrypoint for Gunicorn
├── static/
│   ├── css/          # app.css, theme.css (light/dark mode & offline UI)
│   ├── icons/        # PWA icons (192x192, 512x512, SVG)
│   ├── js/           # offline-db.js, offline-sync.js
│   ├── manifest.json # Web App Manifest
│   └── sw.js         # Service Worker script
├── templates/        # HTML templates for all apps & base.html
├── manage.py         # Django management script
├── render.yaml       # Render Blueprint configuration
└── requirements.txt  # Python package dependencies
```

---

## ⚙️ Local Development Setup

### Prerequisites
- Python 3.12+
- Git

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RIZWAN1428/personal-app-web.git
   cd personal-app-web
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to include your Neon PostgreSQL `DATABASE_URL` (or local Postgres details):
   ```env
   DJANGO_SECRET_KEY=your-secret-key
   DJANGO_DEBUG=True
   DATABASE_URL=postgresql://USER:PASSWORD@ep-xxxx.region.aws.neon.tech/dbname?sslmode=require
   ```

5. **Apply Database Migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```
   Open `http://127.0.0.1:8000` in your browser.

---

## 🌐 Deploying to Render & Neon DB

1. **Create Neon Database**: Sign up at [neon.tech](https://neon.tech), create a project, and copy the PostgreSQL connection string.
2. **Connect to Render**:
   - Push code to GitHub.
   - Go to [Render Dashboard](https://dashboard.render.com/) -> **New** -> **Blueprint**.
   - Select your repository. Render will automatically read `render.yaml`.
   - In Environment Variables, set `DATABASE_URL` to your Neon connection string.
3. **Deploy**: Render executes the build command (`pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`) and starts Gunicorn.

---

## 📱 Testing PWA Offline Mode

1. Open the app in Chrome or mobile browser.
2. Open **DevTools** (`F12`) -> **Application** -> **Service Workers** to verify `sw.js` is registered.
3. Switch to **Network** tab -> Check **Offline**.
4. Try creating a Note, checking off a task, or logging a prayer. An amber toast notification will say `📥 Saved offline`.
5. Uncheck **Offline**. The Service Worker will replay queued actions via Background Sync, and a green `✅ Synced!` toast will appear.

---

## 📄 License & Credits

Built for personal productivity and spiritual habit tracking. Designed with clean modular Django architecture.
