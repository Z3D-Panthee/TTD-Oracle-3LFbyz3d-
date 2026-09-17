// SENTINEL OS v4.1.3 CONSCIOUS AUTONOMOUS - FIX FINAL PNG
const CACHE_NAME = 'sentinel-os-v4.1.3-fix-png-lemba';

const CORE_FILES = [
  './',
  './manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/icon-1024.png'
];

self.addEventListener('install', e => {
  console.log('[SENTINEL v4.1.3] Installation Lemba FIX PNG...');
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(CORE_FILES))
      .then(() => self.skipWaiting())
      .catch(err => console.error('[SENTINEL] Échec cache:', err))
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.map(k => {
        // Supprime TOUS les anciens caches avec .jpg
        if (k !== CACHE_NAME) {
          console.log('[SENTINEL] Suppression ancien cache:', k);
          return caches.delete(k);
        }
      })
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  const url = new URL(req.url);

  if (url.pathname.includes('/api/')) {
    e.respondWith(
      fetch(req).then(res => {
        const clone = res.clone();
        caches.open(CACHE_NAME).then(c => c.put(req, clone));
        return res;
      }).catch(() => caches.match(req).then(cached => cached || new Response(JSON.stringify({
        k: 0.88, ds: 0.35, confidence: 0.85, domain: "général",
        answer: "TTD ORACLE v4.1.3 — LEMBA OFFLINE ACTIF\n\nSENTINEL tourne en autonomie.\n\n→ Mémoire locale 80 questions active",
        status: "LEMBA_OFFLINE_v4.1.3"
      }), { headers: { 'Content-Type': 'application/json' } })))
    );
    return;
  }

  e.respondWith(
    caches.match(req).then(cached => {
      if (cached) {
        e.waitUntil(fetch(req).then(f => f.status === 200 && caches.open(CACHE_NAME).then(c => c.put(req, f))).catch(()=>{}));
        return cached;
      }
      return fetch(req).then(res => {
        if (res && res.status === 200) {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(req, clone));
        }
        return res;
      }).catch(() => req.destination === 'document' ? caches.match('./') : null);
    })
  );
});

self.addEventListener('message', e => {
  if (e.data?.type === 'SKIP_WAITING') self.skipWaiting();
});