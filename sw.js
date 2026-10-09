// === QUANTUM NEXUS v10.7 - SERVICE WORKER - GINOXCO SARL x VEROLIS ===
// FrancoTech Edition - 15 Novembre 2026 - 100% GRATUIT JOUR J
const CACHE_NAME = 'quantum-nexus-v10.7-francotech-15nov2026-v5.0';

// Actifs essentiels pour mode 100% hors-ligne - QUANTUM NEXUS
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './static/icon-192.png',
  './static/icon-512.png',
  './static/icon-1024.png'
];

// Installation : Mise en cache QUANTUM NEXUS v10.7
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[QUANTUM NEXUS v10.7] Mise en cache des actifs essentiels - FrancoTech 15 Nov 2026');
        return Promise.allSettled(
          ASSETS.map(asset => cache.add(asset).catch(err => console.warn('[QN] Fichier ignoré :', asset)))
        );
      })
      .then(() => self.skipWaiting())
  );
});

// Activation : Nettoyage AGRESSIF des anciens caches SENTINEL v5.1
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.map(key => {
          // SUPPRIME TOUT ce qui n'est pas le nouveau cache QUANTUM NEXUS
          if (key !== CACHE_NAME) {
            console.log('[QUANTUM NEXUS] Suppression ancien cache obsolète :', key, '- dont SENTINEL OS v5.1');
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch : Double stratégie QUANTUM NEXUS
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // 1. NETWORK-FIRST pour API Hardware LIGO-BOX V1.2
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request)
        .catch(() => {
          console.warn('[QN] Réseau API indisponible, fallback cache...');
          return caches.match(event.request);
        })
    );
    return;
  }

  // 2. CACHE-FIRST pour UI QUANTUM NEXUS
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(event.request)
          .then(networkResponse => {
            if(networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
              const responseToCache = networkResponse.clone();
              caches.open(CACHE_NAME).then(cache => {
                cache.put(event.request, responseToCache);
              });
            }
            return networkResponse;
          })
          .catch(() => {
            if (event.request.destination === 'document' || event.request.mode === 'navigate') {
              return caches.match('./index.html');
            }
            return null;
          });
      })
  );
});