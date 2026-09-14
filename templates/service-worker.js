// SENTINEL OS v4.1.2 CONSCIOUS AUTONOMOUS - SCELLÉ LEMBA - FIX .jpg
const CACHE_NAME = 'sentinel-os-v4.1.2-conscious-autonomous-lemba';
const CORE_FILES = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png.jpg',
  './icon-512.png.jpg',
  './icon-1024.png.jpg'
];

self.addEventListener('install', e => {
  console.log('[SENTINEL v4.1.2] Installation Lemba...');
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
      keys.map(k => k !== CACHE_NAME ? caches.delete(k) : null)
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
        answer: "TTD ORACLE v4.1.2 — LEMBA OFFLINE ACTIF\n\nSENTINEL tourne en autonomie.\n\n→ Mémoire locale 80 questions active",
        status: "LEMBA_OFFLINE_v4.1.2"
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
      }).catch(() => req.destination === 'document' ? caches.match('./index.html') : null);
    })
  );
});

self.addEventListener('message', e => {
  if (e.data?.type === 'SKIP_WAITING') self.skipWaiting();
});