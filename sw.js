// === QUANTUM NEXUS v11.1 - SERVICE WORKER - YANG-MILLS AFFIRMÉ + 8 SECTEURS 3D PRO MAX ===
// GINOXCO x VEROLIS - FrancoTech 15 Nov 2026 FREE - LIGO-BOX V1.2 LIVE • ε=1e-5 • Tr(T)≠0
const CACHE = 'quantum-nexus-v11-1-yang-mills-8-secteurs-3d-pro-max-v1.0';

const ASSETS = [
  '/',
  '/templates/index.html',
  '/index.html',
  '/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/icon-1024.png',
  // Blueprints 3D Pro Max (si tu les as mis dans /static/)
  '/static/blueprint_energy_342W.png',
  '/static/blueprint_mine_HX711.png',
  '/static/energy-blueprint.png',
  '/static/water-agro-blueprint.png',
  '/static/mine-blueprint.png',
  '/static/micro-cirt-blueprint.png'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(async c => {
      console.log('[QUANTUM NEXUS v11.1] Installation — YANG-MILLS AFFIRMÉ + 8 secteurs 3D');
      for (const url of ASSETS) {
        try {
          const req = new Request(url, {cache: 'reload'});
          const res = await fetch(req);
          if (res.ok) await c.put(req, res);
        } catch(err) {
          console.warn('[QN v11.1] Asset non trouvé ignoré:', url);
        }
      }
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => 
      Promise.all(keys.filter(k => k !== CACHE).map(k => {
        console.log('[QN v11.1] Suppression ancien cache:', k);
        return caches.delete(k);
      }))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (u.origin !== location.origin) return;

  // 1. API -> Network First + OFFLINE MOCKS COMPLETS v11.1
  if (u.pathname.startsWith('/api/')) {
    e.respondWith(
      fetch(e.request).then(r => {
        // cache API en background pour offline
        if (r.ok) {
          const clone = r.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone)).catch(()=>{});
        }
        return r;
      }).catch(() => {
        // === MOCKS OFFLINE v11.1 — YANG-MILLS + 8 SECTEURS ===
        if (u.pathname.includes('/yang-mills/proof')) {
          return new Response(JSON.stringify({
            theory:"Yang-Mills Mass Gap Program • PMV-1.0 Operator • RC ○ RO ○ RI = Id + T",
            formula:{composition:"RC ○ RO ○ RI = Id + T", norm_T:"||T|| = ε ≈ 1e-5", trace:"Tr(T) ≠ 0", epsilon:1e-5, Tr_T_live:0.0021, RC_RO_live:0.0042},
            prediction:{formula:"Δφ(f)= ε·(f/100Hz)·(D/1Gpc) rad", f_hz:104.2, D_gpc:1, delta_phi_rad:0.0012, unit:"rad"},
            falsifiability:{criterion_1:"If {RC,RO}=0 → theory falsified", criterion_2:"If Tr(T)=0 → theory falsified", current_status:"NOT FALSIFIED — LIVE LOCK ON OFFLINE", falsified:false},
            doi:"10.5281/zenodo.19852087",
            mode:"OFFLINE 3D PRO MAX"
          }), {headers:{'Content-Type':'application/json'}});
        }
        if (u.pathname.includes('/dossier-8-secteurs')) {
          return new Response(JSON.stringify({
            version:"v11.1 OFFLINE",
            total:{pertes_an:"8,5 Mds$ / an", pertes_mois:"708M$/mois — 9Mds$/mois temps réel national", gain70:"5,95Mds$/an", gain98:"8,33Mds$/an"},
            secteurs:[
              {id:"energy", pertes_mois:"100M$/mois", gain70:"+840M$"},
              {id:"mine", pertes_mois:"333M$/mois", gain70:"+2,8Mds$", b2g:"B2G 3% =84M$ ROI x33"}
            ],
            mode:"OFFLINE"
          }), {headers:{'Content-Type':'application/json'}});
        }
        if (u.pathname.includes('/quantum/matrice-3d')) {
          return new Response(JSON.stringify({
            module:"Matrice 3D Tradique v11.1 OFFLINE",
            torus:{radius:2.2, tube:0.04, color:"#ffd166"},
            sphere:{radius:1.4, color:"#00eaff", wireframe:true},
            particles:900,
            mode:"OFFLINE"
          }), {headers:{'Content-Type':'application/json'}});
        }
        if (u.pathname.includes('/rc/control')) {
          return new Response(JSON.stringify({app:"TRUE NORTH RC", gps:"-4.325°S 15.322°E LEMBA OFFLINE 3D", status:"Monitoring OFFLINE ACTIF YANG-MILLS"}), {headers:{'Content-Type':'application/json'}});
        }
        if (u.pathname.includes('/ro/vpn')) {
          return new Response(JSON.stringify({app:"SUPERVPN RO", tunnel:"AES-256 OFFLINE 3D", status:"Réseau protégé OFFLINE", ip_vpn:"10.8.0.2"}), {headers:{'Content-Type':'application/json'}});
        }
        if (u.pathname.includes('/ri/vault')) {
          return new Response(JSON.stringify({app:"VAULT RI", files_count:5, status:"Coffre OFFLINE OK YANG-MILLS", encryption:"AES-256 OFFLINE", files:[{filename:"yang_mills_proof_TTD.pdf",size_kb:420},{filename:"blueprint_energy_342W.png",size_kb:2048}]}), {headers:{'Content-Type':'application/json'}});
        }
        if (u.pathname.includes('/ligo-box')) {
          return new Response(JSON.stringify({module:"Ligo-Box V1.2 LIVE OFFLINE", version:"11.1", parametres:{Tr_T:0.0021, RC_RO:0.0042, epsilon:1e-5, delta_phi_rad:0.0012, formula:"RC ○ RO ○ RI = Id + T", status:"NOT FALSIFIED OFFLINE", doi:"10.5281/zenodo.19852087"}}), {headers:{'Content-Type':'application/json'}});
        }
        return new Response(JSON.stringify({mode:"OFFLINE 3D PRO MAX", error:"API offline — mock Yang-Mills + 8 secteurs actif"}), {headers:{'Content-Type':'application/json'}});
      })
    );
    return;
  }

  // 2. Pages -> Cache First + Update background
  if (e.request.method !== 'GET') return;

  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) {
        fetch(e.request).then(r => {
          if (r.ok) caches.open(CACHE).then(c => c.put(e.request, r.clone()));
        }).catch(()=>{});
        return cached;
      }
      return fetch(e.request).then(r => {
        if (r.ok) caches.open(CACHE).then(c => c.put(e.request, r.clone()));
        return r;
      }).catch(() => 
        caches.match('/') || 
        caches.match('/templates/index.html') || 
        caches.match('/index.html')
      );
    })
  );
});