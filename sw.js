// === SENTINEL OS v9.3 - SERVICE WORKER ROBUSTE V3.7 ===
const CACHE_NAME = 'sentinel-v93-v37-ultra-fluide-final';

// Utilisation de chemins relatifs sécurisés pour éviter les erreurs 404 sur les sous-dossiers
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './static/icon-192.png',
  './static/icon-512.png',
  './static/icon-1024.png'
];

// Installation : Mise en cache des fichiers essentiels
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[ServiceWorker] Mise en cache des actifs essentiels');
        return cache.addAll(ASSETS);
      })
      .then(() => self.skipWaiting())
      .catch(err => console.error('[ServiceWorker] Erreur lors de l\'installation du cache :', err))
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
  // Ignorer les requêtes non-GET (ex: extensions Chrome, POST, etc.)
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        // Retourne le cache s'il existe, sinon va chercher sur le réseau
        if (cachedResponse) {
          return cachedResponse;
        }

        return fetch(event.request)
          .then(networkResponse => {
            // Cloner et stocker dynamiquement la nouvelle ressource dans le cache
            if(networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
              const responseToCache = networkResponse.clone();
              caches.open(CACHE_NAME).then(cache => {
                cache.put(event.request, responseToCache);
              });
            }
            return networkResponse;
          })
          .catch(() => {
            // Si le réseau échoue et que c'est une navigation (document HTML), renvoyer l'index.html de secours
            if (event.request.destination === 'document' || event.request.mode === 'navigate') {
              return caches.match('./index.html');
            }
            return null;
          });
      })
  );
});
