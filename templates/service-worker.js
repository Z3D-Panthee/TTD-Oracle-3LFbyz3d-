// SENTINEL SERVICE WORKER v2.0 CONSCIOUS - LEMBA LAB
// Gère offline total + boucle fermée + auto-réparation

const CACHE_NAME = 'sentinel-os-v2.0.4-conscious';
const CORE_FILES = [
  './',
  './index.html',
  './manifest.json',
  './icon-512.png',
  './icon-192.png',
  './icon-1024.png'
];

// 1. INSTALL - Pré-cache tout, même si 4G est faible
self.addEventListener('install', e => {
  console.log('[SENTINEL] Installation du noyau offline...');
  e.waitUntil(
    caches.open(CACHE_NAME)
     .then(cache => {
        return cache.addAll(CORE_FILES);
      })
     .then(() => {
        // Force le nouveau SW à prendre le contrôle immédiatement
        return self.skipWaiting();
      })
  );
});

// 2. ACTIVATE - Nettoie les vieux caches (v1, v2...) = boucle fermée
self.addEventListener('activate', e => {
  console.log('[SENTINEL] Nettoyage des anciens OS...');
  e.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.map(key => {
          if (key!== CACHE_NAME) {
            console.log('[SENTINEL] Suppression ancien cache:', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => {
      return self.clients.claim(); // Prend contrôle de toutes les pages direct
    })
  );
});

// 3. FETCH - Stratégie OFFLINE FIRST + Fallback intelligent
self.addEventListener('fetch', e => {
  const req = e.request;
  const url = new URL(req.url);

  // Ne cache pas les requêtes vers l'API Oracle si en ligne, mais garde en mémoire si offline
  if (url.hostname.includes('onrender.com') && url.pathname.includes('/api/')) {
    e.respondWith(
      fetch(req)
       .then(res => {
          // Si API répond, clone en cache pour offline
          const clone = res.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(req, clone));
          return res;
        })
       .catch(() => {
          // Si offline, renvoie le dernier cache API ou une réponse SENTINEL
          return caches.match(req).then(cached => {
            if (cached) return cached;
            return new Response(JSON.stringify({
              lot: 'SENTINEL-OFFLINE-'+Date.now(),
              status: 'OFFLINE_MODE_ACTIVE',
              message: 'SENTINEL OS tourne en mode autonome Lemba - Pas besoin de cloud',
              telemetry: { ph: 7.12, tds: '42ppm', state: 'AUTONOMOUS_ACTIVE' }
            }), {
              headers: { 'Content-Type': 'application/json' }
            });
          });
        })
    );
    return;
  }

  // Pour tout le reste (HTML, icons, CSS) : CACHE FIRST
  e.respondWith(
    caches.match(req).then(cached => {
      if (cached) {
        // En arrière-plan, met à jour le cache pour la prochaine fois
        e.waitUntil(
          fetch(req).then(fresh => {
            return caches.open(CACHE_NAME).then(cache => cache.put(req, fresh));
          }).catch(()=>{})
        );
        return cached;
      }
      // Si pas en cache, va sur réseau puis cache
      return fetch(req)
       .then(res => {
          if (!res || res.status!== 200 || res.type!== 'basic') return res;
          const clone = res.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(req, clone));
          return res;
        })
       .catch(() => {
          // ULTIME FALLBACK : Si tout échoue, renvoie index.html (ton OS)
          if (req.destination === 'document' || req.headers.get('accept').includes('text/html')) {
            return caches.match('./index.html');
          }
        });
    })
  );
});

// 4. SYNC & MESSAGE - Permet à SENTINEL de se parler lui-même
self.addEventListener('message', e => {
  if (e.data && e.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  if (e.data && e.data.type === 'GET_VERSION') {
    e.ports[0].postMessage({ version: CACHE_NAME });
  }
});

console.log('[SENTINEL] Service Worker CONSCIOUS chargé - v2.0.4');