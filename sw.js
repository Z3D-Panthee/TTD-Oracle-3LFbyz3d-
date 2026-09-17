// === SENTINEL OS v9.3 - SERVICE WORKER ROBUSTE V3.7 ===
const CACHE_NAME = 'sentinel-os-v9.3-fusi-v3.7';

// Utilisation de chemins relatifs sécurisés
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './static/icon-192.png',
  './static/icon-512.png',
  './static/icon-1024.png'
];

// Installation : Mise en cache sécurisée (élément par élément pour éviter un échec global)
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[ServiceWorker] Mise en cache des actifs essentiels');
        return Promise.allSettled(
          ASSETS.map(asset => cache.add(asset).catch(err => console.warn('[ServiceWorker] Fichier non trouvé ignoré :', asset)))
        );
      })
      .then(() => self.skipWaiting())
  );
});

// Activation : Nettoyage des anciens caches obsolètes
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            console.log('[ServiceWorker] Suppression de l\'ancien cache :', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Interception des requêtes : Stratégie Cache-First avec fallback réseau et mode hors-ligne
self.addEventListener('fetch', event => {
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
