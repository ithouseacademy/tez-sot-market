const CACHE = 'tezsot-v2';
const STATIC_CACHE = 'tezsot-static-v2';
const CACHE_DURATION = 86400000; // 24 soat

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(STATIC_CACHE).then(cache => {
      return cache.addAll([
        '/static/css/tezsot.css',
        '/static/manifest.json',
        '/static/img/logo.png',
        '/static/img/logo.png',
      ]).catch(() => {});
    })
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    Promise.all([
      clients.claim(),
      caches.keys().then(keys => {
        return Promise.all(
          keys.filter(k => k !== CACHE && k !== STATIC_CACHE)
            .map(k => caches.delete(k))
        );
      })
    ])
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;

  // Static files - cache first
  if (e.request.url.includes('/static/')) {
    e.respondWith(
      caches.match(e.request).then(cached => {
        const fetchPromise = fetch(e.request).then(response => {
          if (response && response.ok) {
            const copy = response.clone();
            caches.open(STATIC_CACHE).then(cache => cache.put(e.request, copy));
          }
          return response;
        }).catch(() => cached);
        return cached || fetchPromise;
      })
    );
    return;
  }

  // Navigation pages - network first
  e.respondWith(
    fetch(e.request).then(response => {
      if (response && response.ok) {
        const copy = response.clone();
        caches.open(CACHE).then(cache => cache.put(e.request, copy));
      }
      return response;
    }).catch(() => {
      return caches.match(e.request).then(cached => {
        if (cached) return cached;
        return caches.match('/');
      });
    })
  );
});

self.addEventListener('push', e => {
  let data = { title: 'TezSot', body: 'Yangi xabar', icon: '/static/img/iconlogo192.png', badge: '/static/img/iconlogo192.png', url: '/' };
  try {
    if (e.data) data = { ...data, ...e.data.json() };
  } catch (_) { data.body = e.data.text(); }
  e.waitUntil(self.registration.showNotification(data.title, {
    body: data.body,
    icon: data.icon,
    badge: data.badge,
    vibrate: [200, 100, 200],
    data: { url: data.url },
    tag: 'tezsot-' + Date.now(),
    renotify: true,
    requireInteraction: true,
    actions: [
      { action: 'open', title: 'Ko\'rish' },
      { action: 'close', title: 'Yopish' },
    ]
  }));
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  if (e.action === 'close') return;
  const url = e.notification.data?.url || '/';
  e.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(cls => {
      for (const c of cls) {
        if (c.url === url && 'focus' in c) return c.focus();
      }
      return clients.openWindow(url);
    })
  );
});
