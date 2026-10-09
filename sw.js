// === QUANTUM NEXUS v10.8.1 - SERVICE WORKER - 3 APPS DASHBOARD ===
// GINOXCO SARL x VEROLIS SARL - FrancoTech 15 Nov 2026 - FREE FOR ALL
// TRUE NORTH RC + SUPERVPN RO + VAULT RI + LIGO-BOX V1.2 LIVE

const CACHE = 'quantum-nexus-v10-8-1-francotech-free-3apps-v5.0';

// Tous les actifs pour mode 100% hors-ligne - 3 Apps incluses
const ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/icon-1024.png'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => {
        console.log('[QUANTUM NEXUS v10.8.1] Cache 3 Apps FREE - Installation FrancoTech 15 Nov 2026');
        return c.addAll(ASSETS.map(url => new Request(url, {cache: 'reload'})))
          .catch(err => {
            console.warn('[QN] Certains assets non trouvés, cache partiel:', err);
            // Cache au moins la racine
            return c.addAll(['/','/index.html','/manifest.json'].map(u => new Request(u, {cache: 'reload'}))).catch(()=>{});
          });
      })
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => 
      Promise.all(
        keys.map(k => {
          // SUPPRIME AGRESSIVEMENT tout ancien cache SENTINEL OS
          if (k !== CACHE) {
            console.log('[QUANTUM NEXUS] Suppression ancien cache obsolète:', k, '-> dont SENTINEL OS v5.1/v10.8');
            return caches.delete(k);
          }
        })
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  
  // 1. NE PAS CACHER les API - Toujours réseau (RC/RO/RI + LIGO-BOX + telemetry)
  if (u.pathname.startsWith('/api/') || e.request.method !== 'POST' && u.pathname.startsWith('/api/')) {
    // Pour /api/* : network-first, pas de cache
    if (u.origin === location.origin) {
      e.respondWith(
        fetch(e.request)
          .catch(() => {
            // Offline: retourne une réponse mock pour les 3 apps
            if (u.pathname.includes('/rc/control')) {
              return new Response(JSON.stringify({app:"TRUE NORTH RC", gps:"-4.325°S 15.322°E LEMBA OFFLINE", status:"Monitoring OFFLINE ACTIF"}), {headers:{'Content-Type':'application/json'}});
            }
            if (u.pathname.includes('/ro/vpn')) {
              return new Response(JSON.stringify({app:"SUPERVPN RO", tunnel:"AES-256 OFFLINE", status:"Réseau protégé OFFLINE"}), {headers:{'Content-Type':'application/json'}});
            }
            if (u.pathname.includes('/ri/vault')) {
              return new Response(JSON.stringify({app:"VAULT RI", files_count:3, status:"Coffre OFFLINE OK"}), {headers:{'Content-Type':'application/json'}});
            }
            return new Response(JSON.stringify({error:"Offline - API non dispo", mode:"OFFLINE"}), {headers:{'Content-Type':'application/json'}});
          })
      );
    }
    return;
  }

  // 2. Pour les pages/assets statiques : CACHE-FIRST avec mise à jour en arrière-plan
  if (e.request.method !== 'GET' || u.origin !== location.origin) return;

  e.respondWith(
    caches.match(e.request).then(cached => {
      const fetchPromise = fetch(e.request)
        .then(networkRes => {
          if (networkRes && networkRes.ok) {
            const clone = networkRes.clone();
            caches.open(CACHE).then(c => c.put(e.request, clone));
          }
          return networkRes;
        })
        .catch(() => {
          // Offline fallback
          if (e.request.destination === 'document' || e.request.mode === 'navigate') {
            return caches.match('/') || caches.match('/index.html');
          }
          return cached || null;
        });

      // Retourne cache immédiatement si dispo (offline instant), sinon attend réseau
      return cached || fetchPromise;
    })
  );
});