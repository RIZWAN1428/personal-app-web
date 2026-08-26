/**
 * Service Worker for Personal App PWA.
 *
 * Strategy:
 *   - App shell (all main routes + assets): Pre-cached on install
 *   - Static assets (CSS, JS, fonts, icons): Cache-first
 *   - HTML pages: Network-first, fallback to cache (ignoreSearch: true)
 *   - Form POSTs: Pass through when online; queue to IndexedDB & serve cached page when offline
 *   - Background Sync: Replay queued POSTs when connectivity returns
 */
const CACHE_NAME = 'personalapp-v3';
const SYNC_TAG = 'personalapp-sync';

// App shell — all key pages & assets to pre-cache on install
const APP_SHELL = [
  '/',
  '/salah/',
  '/notes/',
  '/checklist/',
  '/reminders/',
  '/streaks/',
  '/quran/',
  '/hadith/',
  '/books/',
  '/movies/',
  '/static/css/app.css',
  '/static/css/theme.css',
  '/static/js/offline-db.js',
  '/static/js/offline-sync.js',
  '/manifest.json',
];

// External CDN resources to cache on first fetch
const CDN_PATTERNS = [
  'cdn.jsdelivr.net',
  'fonts.googleapis.com',
  'fonts.gstatic.com',
];

// ───────────────────────────────────────────────
// INSTALL — Pre-cache the entire app shell
// ───────────────────────────────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Pre-caching full app shell');
        return cache.addAll(APP_SHELL);
      })
      .then(() => self.skipWaiting())
      .catch((err) => {
        console.warn('[SW] Pre-cache warning:', err);
        return self.skipWaiting();
      })
  );
});

// ───────────────────────────────────────────────
// ACTIVATE — Clean up old caches
// ───────────────────────────────────────────────
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    }).then(() => self.clients.claim())
  );
});

// ───────────────────────────────────────────────
// FETCH — Intercept network requests
// ───────────────────────────────────────────────
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET/non-POST, or Chrome extension requests
  if (!['GET', 'POST'].includes(request.method)) return;
  if (url.protocol === 'chrome-extension:') return;

  // ─── POST requests (form submissions) ───
  if (request.method === 'POST') {
    event.respondWith(handlePost(event));
    return;
  }

  // ─── Static assets: Cache-first ───
  if (isStaticAsset(url)) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // ─── CDN resources: Cache-first ───
  if (CDN_PATTERNS.some((pattern) => url.hostname.includes(pattern))) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // ─── HTML pages: Network-first, fallback to cache ───
  event.respondWith(networkFirst(request));
});

/**
 * Cache-first strategy for static assets.
 */
async function cacheFirst(request) {
  const cached = await caches.match(request, { ignoreSearch: true });
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    return new Response('Offline Asset Unavailable', { status: 503, statusText: 'Service Unavailable' });
  }
}

/**
 * Network-first strategy for HTML pages.
 */
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    // Network failed — serve cached version (ignoring query params like ?city=Jaunpur)
    let cached = await caches.match(request);
    if (!cached) {
      cached = await caches.match(request, { ignoreSearch: true });
    }
    if (!cached) {
      const url = new URL(request.url);
      cached = await caches.match(url.pathname, { ignoreSearch: true });
    }
    if (cached) return cached;

    // Fallback to home page cache
    const fallback = await caches.match('/', { ignoreSearch: true });
    if (fallback) return fallback;

    return new Response(
      '<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Offline</title><link rel="stylesheet" href="/static/css/app.css"></head><body class="p-5 text-center"><h2>📡 You are offline</h2><p>Please connect to the internet once to sync.</p></body></html>',
      { status: 503, headers: { 'Content-Type': 'text/html' } }
    );
  }
}

/**
 * Handle POST requests — pass through when online, queue & return cached HTML when offline.
 */
async function handlePost(event) {
  try {
    const response = await fetch(event.request.clone());
    return response;
  } catch (err) {
    // Network failed — we're offline. Queue the form data safely.
    try {
      const formData = await event.request.clone().text();
      const url = event.request.url;

      importScripts('/static/js/offline-db.js');

      let csrfToken = '';
      const csrfMatch = formData.match(/csrfmiddlewaretoken=([^&]+)/);
      if (csrfMatch) {
        csrfToken = decodeURIComponent(csrfMatch[1]);
      }

      await self.offlineDB.addToQueue(url, 'POST', formData, csrfToken);

      if ('sync' in self.registration) {
        await self.registration.sync.register(SYNC_TAG);
      }

      // Notify open windows
      const clients = await self.clients.matchAll();
      clients.forEach((client) => {
        client.postMessage({
          type: 'QUEUED_OFFLINE',
          url: url,
          message: 'Saved offline — will auto-sync when back online.',
        });
      });

      // Serve referrer page or request page from cache so browser navigation DOES NOT BREAK
      const referrer = event.request.referrer;
      let cached = null;
      if (referrer) {
        cached = await caches.match(referrer, { ignoreSearch: true });
      }
      if (!cached) {
        cached = await caches.match(url, { ignoreSearch: true });
      }
      if (!cached) {
        cached = await caches.match('/', { ignoreSearch: true });
      }

      if (cached) {
        return cached;
      }

      return new Response(
        '<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Saved Offline</title><link rel="stylesheet" href="/static/css/app.css"></head><body class="p-4 text-center"><h3>📥 Saved Offline!</h3><p>Your changes were saved locally and will auto-sync when online.</p><a href="/" class="btn btn-primary rounded-pill mt-3">Back to Dashboard</a></body></html>',
        { headers: { 'Content-Type': 'text/html' } }
      );
    } catch (queueErr) {
      console.error('[SW] Failed to queue offline:', queueErr);
      return new Response('Offline Save Error', { status: 500 });
    }
  }
}

/**
 * Check if a URL is a static asset.
 */
function isStaticAsset(url) {
  const path = url.pathname;
  return (
    path.startsWith('/static/') ||
    path.startsWith('/media/') ||
    path.endsWith('.css') ||
    path.endsWith('.js') ||
    path.endsWith('.woff') ||
    path.endsWith('.woff2') ||
    path.endsWith('.ttf') ||
    path.endsWith('.png') ||
    path.endsWith('.jpg') ||
    path.endsWith('.svg') ||
    path.endsWith('.ico') ||
    path.endsWith('.webp')
  );
}

// ───────────────────────────────────────────────
// BACKGROUND SYNC — Replay queued form POSTs
// ───────────────────────────────────────────────
self.addEventListener('sync', (event) => {
  if (event.tag === SYNC_TAG) {
    event.waitUntil(replayQueue());
  }
});

/**
 * Replay all queued form submissions in order.
 */
async function replayQueue() {
  importScripts('/static/js/offline-db.js');

  const queue = await self.offlineDB.getQueue();
  if (!queue.length) return;

  console.log(`[SW] Replaying ${queue.length} queued item(s)...`);

  let synced = 0;
  let failed = 0;

  for (const item of queue) {
    try {
      const headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
      };
      if (item.csrfToken) {
        headers['X-CSRFToken'] = item.csrfToken;
      }

      const response = await fetch(item.url, {
        method: item.method || 'POST',
        headers: headers,
        body: item.body,
        credentials: 'include',
        redirect: 'follow',
      });

      if (response.ok || response.status === 302 || response.status === 301) {
        await self.offlineDB.removeFromQueue(item.id);
        synced++;
      } else if (response.status === 403) {
        console.warn('[SW] CSRF expired for queued item, removing:', item.url);
        await self.offlineDB.removeFromQueue(item.id);
        failed++;
      } else {
        console.warn(`[SW] Sync failed for ${item.url}: ${response.status}`);
        failed++;
      }
    } catch (err) {
      console.error('[SW] Sync fetch error:', err);
      failed++;
    }
  }

  // Notify all pages about sync result
  const clients = await self.clients.matchAll();
  clients.forEach((client) => {
    client.postMessage({
      type: 'SYNC_COMPLETE',
      synced: synced,
      failed: failed,
      remaining: queue.length - synced,
    });
  });

  console.log(`[SW] Sync complete: ${synced} synced, ${failed} failed.`);
}

// ───────────────────────────────────────────────
// MESSAGE — Handle messages from the page
// ───────────────────────────────────────────────
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'TRIGGER_SYNC') {
    replayQueue();
  }
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
