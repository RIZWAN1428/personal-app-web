/**
 * offline-sync.js — Frontend companion for the Service Worker.
 *
 * Responsibilities:
 *   1. Register the Service Worker
 *   2. Listen for SW messages (QUEUED_OFFLINE, SYNC_COMPLETE)
 *   3. Show/hide the offline status indicator
 *   4. Show toast notifications for offline saves & sync results
 *   5. When coming online, trigger sync if Background Sync API isn't supported
 *   6. Update pending count badge
 */
(function () {
  'use strict';

  // ─── Service Worker Registration ───
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker
        .register('/sw.js', { scope: '/' })
        .then((reg) => {
          console.log('[App] Service Worker registered, scope:', reg.scope);

          // Listen for updates
          reg.addEventListener('updatefound', () => {
            const newWorker = reg.installing;
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'activated') {
                console.log('[App] New Service Worker activated.');
              }
            });
          });
        })
        .catch((err) => {
          console.warn('[App] Service Worker registration failed:', err);
        });
    });
  }

  // ─── Listen for Service Worker messages ───
  if (navigator.serviceWorker) {
    navigator.serviceWorker.addEventListener('message', (event) => {
      const data = event.data;

      if (data.type === 'QUEUED_OFFLINE') {
        showToast('📥 ' + (data.message || 'Saved offline — will sync when connected.'), 'warning');
        updatePendingBadge();
      }

      if (data.type === 'SYNC_COMPLETE') {
        if (data.synced > 0) {
          showToast(`✅ Synced ${data.synced} item(s) to server!`, 'success');
          // Reload to show fresh data from the server
          setTimeout(() => window.location.reload(), 1500);
        }
        if (data.failed > 0) {
          showToast(`⚠️ ${data.failed} item(s) failed to sync. Will retry.`, 'danger');
        }
        updatePendingBadge();
      }
    });
  }

  // ─── Online / Offline status indicator ───
  function updateOnlineStatus() {
    const indicator = document.getElementById('offlineIndicator');
    const dot = document.getElementById('offlineDot');
    const label = document.getElementById('offlineLabel');

    if (!indicator) return;

    if (navigator.onLine) {
      indicator.classList.add('d-none');
      indicator.classList.remove('offline-pulse');
    } else {
      indicator.classList.remove('d-none');
      indicator.classList.add('offline-pulse');
      if (dot) dot.className = 'offline-dot bg-warning';
      if (label) label.textContent = 'Offline';
    }
  }

  window.addEventListener('online', () => {
    updateOnlineStatus();
    showToast('🌐 Back online! Syncing...', 'success');

    // Trigger sync if Background Sync not supported
    if (navigator.serviceWorker && navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({ type: 'TRIGGER_SYNC' });
    }
  });

  window.addEventListener('offline', () => {
    updateOnlineStatus();
    showToast('📡 You are offline — changes will be saved locally.', 'warning');
  });

  // ─── Pending sync badge ───
  async function updatePendingBadge() {
    if (typeof offlineDB === 'undefined') return;

    try {
      const count = await offlineDB.getQueueCount();
      const badge = document.getElementById('syncPendingBadge');
      if (!badge) return;

      if (count > 0) {
        badge.textContent = count;
        badge.classList.remove('d-none');
      } else {
        badge.classList.add('d-none');
      }
    } catch (e) {
      // IndexedDB not available — silently ignore
    }
  }

  // ─── Toast notification ───
  function showToast(message, type) {
    // Remove any existing toasts
    const existing = document.querySelectorAll('.offline-toast');
    existing.forEach((el) => el.remove());

    const toast = document.createElement('div');
    toast.className = `offline-toast offline-toast-${type || 'info'}`;
    toast.innerHTML = `
      <span>${message}</span>
      <button type="button" class="offline-toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    document.body.appendChild(toast);

    // Auto-dismiss after 4 seconds
    setTimeout(() => {
      if (toast.parentElement) {
        toast.classList.add('offline-toast-fade');
        setTimeout(() => toast.remove(), 400);
      }
    }, 4000);
  }

  // ─── Initialize on page load ───
  document.addEventListener('DOMContentLoaded', () => {
    updateOnlineStatus();
    updatePendingBadge();
  });

})();
