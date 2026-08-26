/**
 * offline-sync.js — Frontend companion for the Service Worker & Offline-First UI.
 *
 * Responsibilities:
 *   1. Register the Service Worker (scope '/')
 *   2. Listen for SW messages (QUEUED_OFFLINE, SYNC_COMPLETE)
 *   3. Show/hide the offline status indicator in navbar
 *   4. Show toast notifications for offline saves & sync results
 *   5. Intercept form submits when offline for Instant Optimistic UI updates
 *   6. When coming online, trigger sync if Background Sync API isn't supported
 *   7. Update pending sync count badge
 */
(function () {
  'use strict';

  // ─── 1. Service Worker Registration ───
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker
        .register('/sw.js', { scope: '/' })
        .then((reg) => {
          console.log('[App] Service Worker registered, scope:', reg.scope);

          reg.addEventListener('updatefound', () => {
            const newWorker = reg.installing;
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'activated') {
                  console.log('[App] Service Worker activated.');
                }
              });
            }
          });
        })
        .catch((err) => {
          console.warn('[App] Service Worker registration failed:', err);
        });
    });
  }

  // ─── 2. Listen for Service Worker messages ───
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
          setTimeout(() => window.location.reload(), 1200);
        }
        if (data.failed > 0) {
          showToast(`⚠️ ${data.failed} item(s) failed to sync. Will retry.`, 'danger');
        }
        updatePendingBadge();
      }
    });
  }

  // ─── 3. Online / Offline status indicator ───
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

    if (navigator.serviceWorker && navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({ type: 'TRIGGER_SYNC' });
    }
  });

  window.addEventListener('offline', () => {
    updateOnlineStatus();
    showToast('📡 You are offline — changes will be saved locally.', 'warning');
  });

  // ─── 4. Pending sync badge ───
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
      // Ignore if IndexedDB error
    }
  }

  // ─── 5. Toast notification ───
  function showToast(message, type) {
    const existing = document.querySelectorAll('.offline-toast');
    existing.forEach((el) => el.remove());

    const toast = document.createElement('div');
    toast.className = `offline-toast offline-toast-${type || 'info'}`;
    toast.innerHTML = `
      <span>${message}</span>
      <button type="button" class="offline-toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
      if (toast.parentElement) {
        toast.classList.add('offline-toast-fade');
        setTimeout(() => toast.remove(), 400);
      }
    }, 4000);
  }

  // ─── 6. Client-Side Form Interceptor & Optimistic UI Updates ───
  document.addEventListener('submit', async function (e) {
    const form = e.target;
    if (!form || form.tagName !== 'FORM') return;

    // Check if offline or action target is known
    if (!navigator.onLine) {
      e.preventDefault(); // Stop full-page reload crash while offline

      const url = form.action || window.location.href;
      const method = (form.method || 'POST').toUpperCase();
      const formData = new FormData(form);
      const params = new URLSearchParams(formData);
      const csrfToken = formData.get('csrfmiddlewaretoken') || '';

      // Save action to IndexedDB
      if (typeof offlineDB !== 'undefined') {
        try {
          await offlineDB.addToQueue(url, method, params.toString(), csrfToken);
          updatePendingBadge();
        } catch (err) {
          console.error('[Offline] Error queuing action:', err);
        }
      }

      // Optimistic UI updates based on action URL
      handleOptimisticUI(form, url, formData);

      showToast('📥 Saved offline — will auto-sync when online.', 'warning');
    }
  });

  /**
   * Performs instant visual updates on screen when offline
   */
  function handleOptimisticUI(form, url, formData) {
    // ─── A. Salah Prayer Toggle (e.g. /salah/toggle/fajr/) ───
    if (url.includes('/salah/toggle/')) {
      const btn = form.querySelector('button[type="submit"]');
      if (btn) {
        const isCurrentlyPrayed = btn.classList.contains('btn-success');
        if (isCurrentlyPrayed) {
          btn.className = 'btn btn-sm btn-outline-secondary rounded-pill';
          btn.innerHTML = '<i class="bi bi-circle me-1"></i>Mark Prayed';
        } else {
          btn.className = 'btn btn-sm btn-success rounded-pill';
          btn.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i>Prayed';
        }

        // Update header count if present
        const countBadges = document.querySelectorAll('.badge');
        countBadges.forEach((badge) => {
          if (badge.textContent.includes('Prayed') || badge.textContent.includes('/ 5')) {
            const match = badge.textContent.match(/(\d+)\s*\/\s*5/);
            if (match) {
              let currentCount = parseInt(match[1], 10);
              currentCount = isCurrentlyPrayed ? Math.max(0, currentCount - 1) : Math.min(5, currentCount + 1);
              badge.innerHTML = `<i class="bi bi-check-circle-fill me-1"></i>${currentCount} / 5 Prayers Prayed`;
            }
          }
        });
      }
      return;
    }

    // ─── B. Checklist Item Toggle (e.g. /checklist/.../toggle/) ───
    if (url.includes('/checklist/') && url.includes('/toggle/')) {
      const row = form.closest('tr') || form.closest('.list-group-item') || form.closest('.card');
      if (row) {
        const textSpan = row.querySelector('.item-text') || row.querySelector('span');
        if (textSpan) {
          textSpan.classList.toggle('text-decoration-line-through');
          textSpan.classList.toggle('text-muted');
        }
        const icon = form.querySelector('i');
        if (icon) {
          icon.classList.toggle('bi-check-square-fill');
          icon.classList.toggle('bi-square');
        }
      }
      return;
    }

    // ─── C. Streak Habit Toggle (e.g. /streaks/.../toggle/) ───
    if (url.includes('/streaks/') && url.includes('toggle')) {
      const btn = form.querySelector('button[type="submit"]');
      if (btn) {
        btn.classList.toggle('btn-success');
        btn.classList.toggle('btn-outline-secondary');
      }
      return;
    }

    // ─── D. Creating New Items (Note, Reminder, Checklist Item) ───
    if (url.includes('/notes/new/') || url.includes('/reminders/new/') || url.includes('/checklist/new/')) {
      // Redirect back to list page smoothly
      let targetList = '/notes/';
      if (url.includes('/reminders/')) targetList = '/reminders/';
      if (url.includes('/checklist/')) targetList = '/checklist/';

      setTimeout(() => {
        window.location.href = targetList;
      }, 500);
      return;
    }
  }

  // ─── 7. Initialize on DOM load ───
  document.addEventListener('DOMContentLoaded', () => {
    updateOnlineStatus();
    updatePendingBadge();
  });

})();
