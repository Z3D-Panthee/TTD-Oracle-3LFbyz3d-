// === SENTINEL OS v10.7 - SERVICE WORKER QUANTUM NEXUS ===
const CACHE_NAME = 'sentinel-os-v10.7-nexus-v4.0';

// Actifs essentiels mis en cache pour le mode 100% hors-ligne
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './static/icon-192.png',
  './static/icon-512.png',
  './static/icon-1024.png'
];

// Installation : Mise en cache sécurisée élément par élément
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[ServiceWorker] Mise en cache des actifs essentiels v10.7');
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

// Interception des requêtes : Double stratégie (API Hardware vs Interface Statique)
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // 1. STRATÉGIE NETWORK-FIRST POUR L'API & LE MATÉRIEL (LIGO-BOX, SQLite, Télémétrie)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request)
        .catch(() => {
          console.warn('[ServiceWorker] Réseau indisponible pour l\'API hardware, tentative cache...');
          return caches.match(event.request);
        })
    );
    return;
  }

  // 2. STRATÉGIE CACHE-FIRST POUR LES ACTIFS STATIQUES ET L'INTERFACE
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
