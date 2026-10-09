// === QUANTUM NEXUS v11.5 - VALIDE - 8 Secteurs + Devis M/A + B2G SaaS + Protocole 90j + Matrice 3D Clickable ===
const CACHE = 'quantum-nexus-v11-5-VALIDE-8SECTEURS-MATRICE-CLICKABLE';

const ASSETS_CORE = [
  '/',
  '/templates/index.html',
  '/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/icon-1024.png'
];

self.addEventListener('install', e => {
  console.log('[QN v11.5] Install VALIDE - 8 secteurs devis M/A + matrice clickable');
  e.waitUntil(
    caches.open(CACHE).then(async c => {
      for (const url of ASSETS_CORE) {
        try {
          const r = await fetch(url, {cache: 'reload'});
          if (r.ok && r.status !== 500) await c.put(url, r);
        } catch(err) {
          console.warn('[QN v11.5] Skip:', url);
        }
      }
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => 
      Promise.all(keys.filter(k => k !== CACHE).map(k => {
        console.log('[QN v11.5] Delete ancien cache:', k);
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
        // OFFLINE FALLBACKS VALIDÉS
        if (u.pathname.includes('/yang-mills/proof')) {
          return new Response(JSON.stringify({
            theory:"Yang-Mills Mass Gap • RC ○ RO ○ RI = Id + T • v11.5 VALIDE",
            formula:{composition:"RC ○ RO ○ RI = Id + T", norm_T:"||T||=ε≈1e-5", trace:"Tr(T)≠0", epsilon:1e-5, Tr_T_live:0.0021, RC_RO_live:0.0042},
            prediction:{delta_phi_rad:0.0012, f_hz:104.2, D_gpc:1, formula:"Δφ(f)= ε·(f/100Hz)·(D/1Gpc) rad"},
            falsifiability:{falsified:false, status:"NOT FALSIFIED — v11.5 VALIDE"},
            doi:"10.5281/zenodo.19852087",
            mode:"OFFLINE v11.5 VALIDE"
          }), {headers:{'Content-Type':'application/json'}});
        }
        if (u.pathname.includes('/dossier-8-secteurs')) {
          return new Response(JSON.stringify({
            version:"v11.5 OFFLINE VALIDE", total:{pertes_an:"8,5Mds$/an", pertes_mois_local:"708M$/mois", pertes_mois_national:"9Mds$/mois", gain70:"5,95Mds$/an", gain98:"8,33Mds$/an"},
            secteurs:8, b2g:"ROI x33", mode:"OFFLINE VALIDE"
          }), {headers:{'Content-Type':'application/json'}});
        }
        if (u.pathname.includes('/quantum/matrice-3d')) {
          return new Response(JSON.stringify({
            module:"Matrice 3D Tradique v11.5 OFFLINE Clickable",
            torus:{radius:2.4,color:"#ffd166"}, particles:900,
            sentinels:[
              {id:"energy",icone:"⚡",nom:"Energy Sentinel"},{id:"mine",icone:"⛏️",nom:"Mine Sentinel ★"},
              {id:"water",icone:"💧",nom:"Water Sentinel"},{id:"pharma",icone:"🧪",nom:"Pharma Sentinel"},
              {id:"security",icone:"🛡️",nom:"Security Sentinel"},{id:"logistics",icone:"🚚",nom:"Logistics Sentinel"},
              {id:"brasserie",icone:"🍺",nom:"Brasserie Sentinel"},{id:"agro",icone:"🌱",nom:"Agro Sentinel"}
            ],
            clickable:true, mode:"OFFLINE"
          }), {headers:{'Content-Type':'application/json'}});
        }
        if (u.pathname.includes('/modele/b2g-saas')) {
          return new Response(JSON.stringify({B2G:"3% ROI x33", SaaS:"10$/mois à 5000$/mois", pack_3204:"3204$ OIF max 3000$ reste 204$", mode:"OFFLINE VALIDE"}), {headers:{'Content-Type':'application/json'}});
        }
        if (u.pathname.includes('/protocole/90j')) {
          return new Response(JSON.stringify({protocole:"J1-J7 INOX, J8-J15 REF, J16-J30 CAPTEURS, J31-J75 EXPLOIT, J76-J90 AUDIT", mode:"OFFLINE VALIDE"}), {headers:{'Content-Type':'application/json'}});
        }
        if (u.pathname.includes('/blueprint/')) {
          const id = u.pathname.split('/').pop();
          return new Response(JSON.stringify({id, nom:`Blueprint ${id} OFFLINE`, blueprint:"Blueprint détaillé disponible offline v11.5", devis_mois:"Devis M/A offline", devis_an:"Devis annuel offline", mode:"OFFLINE"}), {headers:{'Content-Type':'application/json'}});
        }
        return new Response(JSON.stringify({mode:"OFFLINE v11.5 VALIDE", status:"API mock actif"}), {headers:{'Content-Type':'application/json'}});
      })
    );
    return;
  }

  // Pages -> Network First = anti écran blanc + garde WOW v11.0
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