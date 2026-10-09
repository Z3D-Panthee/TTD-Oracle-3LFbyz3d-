// === QUANTUM NEXUS v10.8.1d - SERVICE WORKER - PATCH TEMPLATES ===
// GINOXCO x VEROLIS - FrancoTech 15 Nov 2026 FREE - 3 APPS DASHBOARD
const CACHE = 'quantum-nexus-v10-8-1-francotech-free-3apps-v5.0';

const ASSETS = [
  '/',
  '/templates/index.html',
  '/index.html',
  '/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/icon-1024.png'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(async c => {
      console.log('[QUANTUM NEXUS v10.8.1d] Installation 3 Apps FREE');
      for (const url of ASSETS) {
        try {
          const req = new Request(url, {cache: 'reload'});
          const res = await fetch(req);
          if (res.ok) await c.put(req, res);
        } catch(err) {
          console.warn('[QN] Asset non trouvé ignoré:', url);
        }
      }
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => 
      Promise.all(keys.filter(k => k !== CACHE).map(k => {
        console.log('[QUANTUM NEXUS] Suppression ancien cache:', k);
        return caches.delete(k);
      }))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (u.origin !== location.origin) return;

  // 1. API -> Network only + mock offline
  if (u.pathname.startsWith('/api/')) {
    e.respondWith(
      fetch(e.request).catch(() => {
        if (u.pathname.includes('/rc/control')) {
          return new Response(JSON.stringify({app:"TRUE NORTH RC", gps:"-4.325°S 15.322°E LEMBA OFFLINE", status:"Monitoring OFFLINE ACTIF"}), {headers:{'Content-Type':'application/json'}});
        }
        if (u.pathname.includes('/ro/vpn')) {
          return new Response(JSON.stringify({app:"SUPERVPN RO", tunnel:"AES-256 OFFLINE", status:"Réseau protégé OFFLINE", ip_vpn:"10.8.0.2"}), {headers:{'Content-Type':'application/json'}});
        }
        if (u.pathname.includes('/ri/vault')) {
          return new Response(JSON.stringify({app:"VAULT RI", files_count:3, status:"Coffre OFFLINE OK", encryption:"AES-256 OFFLINE"}), {headers:{'Content-Type':'application/json'}});
        }
        return new Response(JSON.stringify({mode:"OFFLINE", error:"API offline"}), {headers:{'Content-Type':'application/json'}});
      })
    );
    return;
  }

  // 2. Pages -> Cache First
  if (e.request.method !== 'GET') return;

  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) {
        // Update en background
        fetch(e.request).then(r => {
          if (r.ok) caches.open(CACHE).then(c => c.put(e.request, r.clone()));
        }).catch(()=>{});
        return cached;
      }
      return fetch(e.request).then(r => {
        if (r.ok) caches.open(CACHE).then(c => c.put(e.request, r.clone()));
        return r;
      }).catch(() => caches.match('/') || caches.match('/templates/index.html') || caches.match('/index.html'));
    })
  );
});