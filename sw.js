// SENTINEL OS v9.3 FINAL FUSI + VOICE FIX V3.5.1 + HARDWARE V1.2 - FIX FINAL LEMBA
const CACHE_NAME = 'sentinel-os-v93-final-complete-hw-v12-voice-fix-v351-lemba';

const CORE_FILES = [
  './',
  './index.html',
  './manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/icon-1024.png'
];

self.addEventListener('install', e => {
  console.log('[SENTINEL v9.3 FINAL COMPLETE] Installation Lemba VOICE FIX + HW V1.2...');
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(CORE_FILES))
      .then(() => self.skipWaiting())
      .catch(err => console.error('[SENTINEL v9.3] Échec cache:', err))
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.map(k => {
        // Supprime TOUS les anciens caches : v4.1.3, v9.3 old, png.jpg, etc.
        if (k !== CACHE_NAME) {
          console.log('[SENTINEL v9.3] Suppression ancien cache:', k);
          return caches.delete(k);
        }
      })
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  const url = new URL(req.url);

  // API TTD offline
  if (url.pathname.includes('/api/')) {
    e.respondWith(
      fetch(req).then(res => {
        const clone = res.clone();
        caches.open(CACHE_NAME).then(c => c.put(req, clone));
        return res;
      }).catch(() => caches.match(req).then(cached => cached || new Response(JSON.stringify({
        k: 0.88, ds: 0.35, confidence: 0.85, domain: "général",
        answer: "SENTINEL OS v9.3 FINAL COMPLETE + HW V1.2 + VOICE FIX V3.5.1\n\nLEMBA OFFLINE ACTIF - CHUNKED anti-coupure\n\n→ Hardware V1.2 Micro-CIRT + App v9.3 + Voix TTD débloquée\n→ Mémoire locale 80 questions + 8 questions Jury + Pitch 90s",
        status: "LEMBA_OFFLINE_v93_FINAL_COMPLETE_HW_V12"
      }), { headers: { 'Content-Type': 'application/json' } })))
    );
    return;
  }

  // Stratégie Cache First + Update en arrière-plan (pour éviter entrecoupage)
  e.respondWith(
    caches.match(req).then(cached => {
      if (cached) {
        // Update silencieux
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