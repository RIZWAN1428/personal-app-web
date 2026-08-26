/**
 * Service Worker for Personal App PWA.
 *
 * Strategy:
 *   - Static assets (CSS, JS, fonts, icons): Cache-first
 *   - HTML pages: Network-first, fall back to cache
 *   - Form POSTs: Pass through when online; queue to IndexedDB when offline
 *   - Background Sync: Replay queued POSTs when connectivity returns
 */
const CACHE_NAME = 'personalapp-v1';
const SYNC_TAG = 'personalapp-sync';

// App shell — files to pre-cache on install
const APP_SHELL = [
  '/',
  '/static/css/app.css',
  '/static/css/theme.css',
  '/static/js/offline-db.js',
  '/static/js/offline-sync.js',
  '/static/manifest.json',
];

// External CDN resources to cache on first fetch
const CDN_PATTERNS = [
  'cdn.jsdelivr.net',
  'fonts.googleapis.com',
  'fonts.gstatic.com',
];

// ───────────────────────────────────────────────
// INSTALL — Pre-cache the app shell
// ───────────────────────────────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Pre-caching app shell');
        return cache.addAll(APP_SHELL);
      })
      .then(() => self.skipWaiting())
      .catch((err) => {
        console.warn('[SW] Some app shell files failed to cache:', err);
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
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    // Return a basic offline response if nothing cached
    return new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
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
    // Network failed — serve cached version
    const cached = await caches.match(request);
    if (cached) return cached;

    // Nothing cached — return the cached home page as fallback
    const fallback = await caches.match('/');
    if (fallback) return fallback;

    return new Response(
      '<html><body style="font-family:Inter,sans-serif;text-align:center;padding:4rem;">' +
      '<h2>📡 You are offline</h2>' +
      '<p>Please connect to the internet to load this page for the first time.</p>' +
      '</body></html>',
      { status: 503, headers: { 'Content-Type': 'text/html' } }
    );
  }
}

/**
 * Handle POST requests — pass through when online, queue when offline.
 */
async function handlePost(event) {
  try {
    const response = await fetch(event.request.clone());
    return response;
  } catch (err) {
    // Network failed — we're offline. Queue the form data.
    try {
      const formData = await event.request.clone().text();
      const url = event.request.url;

      // Import the offline-db helper
      importScripts('/static/js/offline-db.js');

      // Extract CSRF token from form data
      let csrfToken = '';
      const csrfMatch = formData.match(/csrfmiddlewaretoken=([^&]+)/);
      if (csrfMatch) {
        csrfToken = decodeURIComponent(csrfMatch[1]);
      }

      await self.offlineDB.addToQueue(url, 'POST', formData, csrfToken);

      // Register background sync
      if ('sync' in self.registration) {
        await self.registration.sync.register(SYNC_TAG);
      }

      // Notify the page that we queued the action
      const clients = await self.clients.matchAll();
      clients.forEach((client) => {
        client.postMessage({
          type: 'QUEUED_OFFLINE',
          url: url,
          message: 'Saved offline — will sync when connected.',
        });
      });

      // Return a redirect-like response back to the referring page
      return new Response(null, {
        status: 302,
        headers: {
          'Location': event.request.referrer || '/',
        },
      });
    } catch (queueErr) {
      console.error('[SW] Failed to queue offline:', queueErr);
      return new Response(
        '<html><body style="font-family:Inter,sans-serif;text-align:center;padding:4rem;">' +
        '<h2>⚠️ Offline — could not save</h2>' +
        '<p>Please try again when connected.</p>' +
        '</body></html>',
        { status: 503, headers: { 'Content-Type': 'text/html' } }
      );
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
        // CSRF token expired — we'll need a fresh one. Remove and let user retry.
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
      // Don't remove — will retry on next sync
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
