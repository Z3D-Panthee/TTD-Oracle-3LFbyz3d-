// SENTINEL OS v4.1 CONSCIOUS AUTONOMOUS - SERVICE WORKER SCELLÉ LEMBA LAB
// Offline First + Boucle Fermée + Auto-réparation + Mémoire 80

const CACHE_NAME = 'sentinel-os-v4.1-conscious-autonomous-lemba';
const CORE_FILES = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png'
  // icon-1024.png retiré volontairement - n'existe pas = faisait planter addAll()
];

// 1. INSTALL - Pré-cache noyau même en 4G faible
self.addEventListener('install', e => {
  console.log('[SENTINEL v4.1] Installation noyau offline Lemba...');
  e.waitUntil(
    caches.open(CACHE_NAME)
     .then(cache => {
        // addAll va réussir maintenant car tous les fichiers existent
        return cache.addAll(CORE_FILES);
      })
     .then(() => self.skipWaiting())
     .catch(err => {
        console.error('[SENTINEL v4.1] Échec cache initial:', err);
      })
  );
});

// 2. ACTIVATE - Nettoyage boucle fermée v1, v2, v2.0.4
self.addEventListener('activate', e => {
  console.log('[SENTINEL v4.1] Nettoyage anciens OS...');
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
    }).then(() => self.clients.claim())
  );
});

// 3. FETCH - OFFLINE FIRST v4.1
self.addEventListener('fetch', e => {
  const req = e.request;
  const url = new URL(req.url);

  // API Oracle /api/ask - Network First + fallback Lemba
  if (url.pathname.includes('/api/')) {
    e.respondWith(
      fetch(req)
       .then(res => {
          // Clone en cache pour offline futur
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(req, clone));
          return res;
        })
       .catch(() => {
          return caches.match(req).then(cached => {
            if (cached) return cached;
            // Réponse autonome v4.1 si offline total
            return new Response(JSON.stringify({
              k: 0.88,
              ds: 0.35,
              confidence: 0.85,
              domain: "général",
              answer: "TTD ORACLE v4.1 — MODE LEMBA OFFLINE ACTIF\n\nSENTINEL OS tourne en autonomie totale sans cloud.\n\nLOI 01 LIBERTAS: Impulsion locale détectée\nLOI 02 VÉRITÉ: Filtrage [RC][RO]≠[RO][RC] Δφ→0\nLOI 03 JUSTICE: Convergence M* E/t×t/E=1\n\n→ I_TTD=1 — Mémoire locale 80 questions active\n→ Reconnecte-toi pour API complète",
              status: "LEMBA_OFFLINE_v4.1"
            }), { headers: { 'Content-Type': 'application/json' } });
          });
        })
    );
    return;
  }

  // Tout le reste (HTML, icons) : CACHE FIRST + mise à jour background
  e.respondWith(
    caches.match(req).then(cached => {
      if (cached) {
        e.waitUntil(
          fetch(req).then(fresh => {
            if(fresh && fresh.status===200){
              caches.open(CACHE_NAME).then(c => c.put(req, fresh));
            }
          }).catch(()=>{})
        );
        return cached;
      }
      return fetch(req)
       .then(res => {
          if (!res || res.status!== 200) return res;
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(req, clone));
          return res;
        })
       .catch(() => {
          // Ultime fallback : index.html = ton OS complet
          if (req.destination === 'document' || req.headers.get('accept').includes('text/html')) {
            return caches.match('./index.html');
          }
        });
    })
  );
});

// 4. MESSAGE - Contrôle conscient
self.addEventListener('message', e => {
  if (e.data && e.data.type === 'SKIP_WAITING') self.skipWaiting();
  if (e.data && e.data.type === 'GET_VERSION') e.ports[0].postMessage({ version: CACHE_NAME, memory: "80 / autonomous" });
});

console.log('[SENTINEL] SW v4.1 CONSCIOUS AUTONOMOUS chargé — Lemba Ready — Mémoire 80');