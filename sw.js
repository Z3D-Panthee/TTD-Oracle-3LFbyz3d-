// === QUANTUM NEXUS v11.2 - FIX APP OUVERTURE - TTD x YANG-MILLS ===
const CACHE = 'quantum-nexus-v11-2-TTD-FIX-OPEN';

const ASSETS_CORE = [
  '/',
  '/templates/index.html',
  '/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/icon-1024.png'
];

self.addEventListener('install', e => {
  console.log('[QN v11.2] Install FIX ouverture');
  e.waitUntil(
    caches.open(CACHE).then(async c => {
      for (const url of ASSETS_CORE) {
        try {
          const r = await fetch(url, {cache: 'reload'});
          if (r.ok && r.status !== 500) await c.put(url, r);
        } catch(err) {
          console.warn('[QN v11.2] Skip:', url);
        }
      }
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => 
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (u.origin !== location.origin) return;
  if (e.request.method !== 'GET') return;

  // API -> Network First
  if (u.pathname.startsWith('/api/')) {
    e.respondWith(
      fetch(e.request).then(r => {
        if (r.ok) {
          const clone = r.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return r;
      }).catch(() => {
        if (u.pathname.includes('/yang-mills/proof')) {
          return new Response(JSON.stringify({
            theory:"Yang-Mills • RC ○ RO ○ RI = Id + T",
            formula:{composition:"RC ○ RO ○ RI = Id + T", norm_T:"||T||=ε≈1e-5", trace:"Tr(T)≠0", epsilon:1e-5, Tr_T_live:0.0021},
            prediction:{delta_phi_rad:0.0012, f_hz:104.2},
            falsifiability:{falsified:false, status:"NOT FALSIFIED"},
            doi:"10.5281/zenodo.19852087",
            mode:"OFFLINE v11.2 FIX"
          }), {headers:{'Content-Type':'application/json'}});
        }
        return new Response(JSON.stringify({mode:"OFFLINE", status:"API mock actif"}), {headers:{'Content-Type':'application/json'}});
      })
    );
    return;
  }

  // Pages -> Network First pour éviter écran blanc
  e.respondWith(
    fetch(e.request).then(r => {
      if (r.ok && r.status !== 500) {
        const clone = r.clone();
        caches.open(CACHE).then(c => c.put(e.request, clone));
      }
      return r;
    }).catch(() => caches.match(e.request).then(c => c || caches.match('/') || caches.match('/templates/index.html')))
  );
});