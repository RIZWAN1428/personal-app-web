/**
 * offline-db.js — Lightweight IndexedDB wrapper for offline-first PWA.
 *
 * Two object stores:
 *   1. sync_queue  — Queued form submissions waiting to be replayed online
 *   2. cached_pages — Cached page HTML / JSON for offline viewing
 *
 * Usage:
 *   await offlineDB.addToQueue(url, method, body, csrfToken);
 *   const items = await offlineDB.getQueue();
 *   await offlineDB.removeFromQueue(id);
 */
(function (root) {
  'use strict';

  const DB_NAME = 'personalapp_offline';
  const DB_VERSION = 1;
  const SYNC_STORE = 'sync_queue';
  const CACHE_STORE = 'cached_pages';

  let _db = null;

  /**
   * Opens (or creates) the IndexedDB database. Returns a promise.
   */
  function openDB() {
    if (_db) return Promise.resolve(_db);

    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        if (!db.objectStoreNames.contains(SYNC_STORE)) {
          const syncStore = db.createObjectStore(SYNC_STORE, {
            keyPath: 'id',
            autoIncrement: true,
          });
          syncStore.createIndex('url', 'url', { unique: false });
          syncStore.createIndex('createdAt', 'createdAt', { unique: false });
        }

        if (!db.objectStoreNames.contains(CACHE_STORE)) {
          db.createObjectStore(CACHE_STORE, { keyPath: 'key' });
        }
      };

      request.onsuccess = (event) => {
        _db = event.target.result;
        resolve(_db);
      };

      request.onerror = (event) => {
        console.error('[offlineDB] Failed to open IndexedDB:', event.target.error);
        reject(event.target.error);
      };
    });
  }

  /**
   * Add a form submission to the sync queue.
   * @param {string} url - The target endpoint URL
   * @param {string} method - HTTP method (POST, PUT, DELETE)
   * @param {object|string} body - The form data as an object or URL-encoded string
   * @param {string} csrfToken - CSRF token for Django
   * @returns {Promise<number>} - The ID of the queued item
   */
  async function addToQueue(url, method, body, csrfToken) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(SYNC_STORE, 'readwrite');
      const store = tx.objectStore(SYNC_STORE);
      const item = {
        url: url,
        method: method || 'POST',
        body: body,
        csrfToken: csrfToken || '',
        createdAt: new Date().toISOString(),
        retryCount: 0,
      };
      const request = store.add(item);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get all pending items from the sync queue, ordered by creation time.
   * @returns {Promise<Array>}
   */
  async function getQueue() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(SYNC_STORE, 'readonly');
      const store = tx.objectStore(SYNC_STORE);
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get the count of pending sync items.
   * @returns {Promise<number>}
   */
  async function getQueueCount() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(SYNC_STORE, 'readonly');
      const store = tx.objectStore(SYNC_STORE);
      const request = store.count();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Remove a successfully synced item from the queue.
   * @param {number} id
   * @returns {Promise<void>}
   */
  async function removeFromQueue(id) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(SYNC_STORE, 'readwrite');
      const store = tx.objectStore(SYNC_STORE);
      const request = store.delete(id);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Clear the entire sync queue (e.g. after successful full sync).
   * @returns {Promise<void>}
   */
  async function clearQueue() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(SYNC_STORE, 'readwrite');
      const store = tx.objectStore(SYNC_STORE);
      const request = store.clear();
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Cache page data (HTML or JSON) for offline viewing.
   * @param {string} key - Cache key (usually the URL path)
   * @param {*} data - Data to cache
   */
  async function setCachedData(key, data) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(CACHE_STORE, 'readwrite');
      const store = tx.objectStore(CACHE_STORE);
      const request = store.put({ key: key, data: data, cachedAt: new Date().toISOString() });
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Retrieve cached page data.
   * @param {string} key
   * @returns {Promise<*|null>}
   */
  async function getCachedData(key) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(CACHE_STORE, 'readonly');
      const store = tx.objectStore(CACHE_STORE);
      const request = store.get(key);
      request.onsuccess = () => {
        const result = request.result;
        resolve(result ? result.data : null);
      };
      request.onerror = () => reject(request.error);
    });
  }

  // Public API
  const offlineDB = {
    openDB,
    addToQueue,
    getQueue,
    getQueueCount,
    removeFromQueue,
    clearQueue,
    setCachedData,
    getCachedData,
  };

  // Export for both browser globals and service worker importScripts
  if (typeof root !== 'undefined') {
    root.offlineDB = offlineDB;
  }
  if (typeof self !== 'undefined') {
    self.offlineDB = offlineDB;
  }

})(typeof window !== 'undefined' ? window : self);
