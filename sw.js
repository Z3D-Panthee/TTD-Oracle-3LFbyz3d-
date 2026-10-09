// === QUANTUM NEXUS v11.4 - WOW COMPLET FIX - TOUTES INFOS CONSERVEES ===
const CACHE = 'quantum-nexus-v11-4-WOW-COMPLET-FIX';

const ASSETS_CORE = [
  '/',
  '/templates/index.html',
  '/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/icon-1024.png'
];

self.addEventListener('install', e => {
  console.log('[QN v11.4] Install WOW COMPLET - toutes infos');
  e.waitUntil(
    caches.open(CACHE).then(async c => {
      for (const url of ASSETS_CORE) {
        try {
          const r = await fetch(url, {cache: 'reload'});
          if (r.ok && r.status !== 500) await c.put(url, r);
        } catch(err) {
          console.warn('[QN v11.4] Skip:', url);
        }
      }
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => 
      Promise.all(keys.filter(k => k !== CACHE).map(k => {
        console.log('[QN v11.4] Delete ancien cache:', k);
        return caches.delete(k);
      }))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (u.origin !== location.origin) return;
  if (e.request.method !== 'GET') return;

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
            theory:"Yang-Mills Mass Gap • RC ○ RO ○ RI = Id + T • WOW COMPLET",
            formula:{composition:"RC ○ RO ○ RI = Id + T", norm_T:"||T||=ε≈1e-5", trace:"Tr(T)≠0", epsilon:1e-5, Tr_T_live:0.0021, RC_RO_live:0.0042},
            prediction:{delta_phi_rad:0.0012, f_hz:104.2, D_gpc:1, formula:"Δφ(f)= ε·(f/100Hz)·(D/1Gpc) rad"},
            falsifiability:{falsified:false, status:"NOT FALSIFIED — WOW COMPLET"},
            dossier_8_secteurs:{total:"8,5Mds$/an — 9Mds$/mois national", mine:"333M$/mois → +2,8Mds$/an B2G 84M$ ROI x33", energy:"100M$/mois → +840M$/an"},
            doi:"10.5281/zenodo.19852087",
            mode:"OFFLINE v11.4 WOW COMPLET - TOUTES INFOS"
          }), {headers:{'Content-Type':'application/json'}});
        }
        if (u.pathname.includes('/dossier-8-secteurs')) {
          return new Response(JSON.stringify({version:"v11.4 OFFLINE WOW COMPLET", total:"8,5Mds$/an", secteurs:8, mode:"OFFLINE"}), {headers:{'Content-Type':'application/json'}});
        }
        return new Response(JSON.stringify({mode:"OFFLINE WOW COMPLET", status:"API mock actif v11.4"}), {headers:{'Content-Type':'application/json'}});
      })
    );
    return;
  }

  // Pages -> Network First = anti écran blanc mais garde WOW
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