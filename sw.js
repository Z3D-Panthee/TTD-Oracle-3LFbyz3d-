// SENTINEL OS v9.3 FINAL FUSI + VOICE FIX V3.5.1 + HARDWARE V1.2 - FIX FINAL LEMBA
const CACHE_NAME = 'sentinel-os-v93-final-complete-hw-v12-voice-fix-v351-lemba';
const CORE_FILES = ['./','./index.html','./manifest.json','/static/icon-192.png','/static/icon-512.png','/static/icon-1024.png'];
self.addEventListener('install', e => {
  console.log('[SENTINEL v9.3 FINAL COMPLETE] Installation Lemba VOICE FIX + HW V1.2...');
  e.waitUntil(caches.open(CACHE_NAME).then(c=>c.addAll(CORE_FILES)).then(()=>self.skipWaiting()).catch(err=>console.error('[SENTINEL v9.3] Echec cache:',err)));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys=>Promise.all(keys.map(k=>{if(k!==CACHE_NAME){console.log('[SENTINEL] Suppression ancien cache:',k);return caches.delete(k);}}))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req=e.request; const url=new URL(req.url);
  if(url.pathname.includes('/api/')){
    e.respondWith(fetch(req).then(res=>{const clone=res.clone(); caches.open(CACHE_NAME).then(c=>c.put(req,clone)); return res;}).catch(()=>caches.match(req).then(cached=>cached||new Response(JSON.stringify({k:0.88,ds:0.35,answer:"SENTINEL OS v9.3 FINAL COMPLETE + HW V1.2 + VOICE FIX V3.5.1 - LEMBA OFFLINE ACTIF CHUNKED"}),{headers:{'Content-Type':'application/json'}}))));
    return;
  }
  e.respondWith(caches.match(req).then(cached=>{if(cached){e.waitUntil(fetch(req).then(f=>f.status===200&&caches.open(CACHE_NAME).then(c=>c.put(req,f))).catch(()=>{})); return cached;} return fetch(req).then(res=>{if(res&&res.status===200){const clone=res.clone(); caches.open(CACHE_NAME).then(c=>c.put(req,clone));} return res;}).catch(()=>req.destination==='document'?caches.match('./'):null);}));
});
self.addEventListener('message', e=>{if(e.data?.type==='SKIP_WAITING') self.skipWaiting();});

{
  "name": "SENTINEL OS v9.3 FINAL FUSI + VOICE FIX V3.5.1 + HARDWARE V1.2",
  "short_name": "SENTINEL OS v9.3",
  "description": "SENTINEL OS v9.3 FINAL FUSI - VOICE FIX V3.5.1 CHUNKED + HARDWARE V1.2 Micro-CIRT TTD Prototylse - App + Hardware Réel Arduino RPi - I_TTD 1.000 - Vérolis SARL & AIIFAC-ASBL Kinshasa 2026",
  "start_url": "./",
  "display": "fullscreen",
  "background_color": "#0b0f19",
  "theme_color": "#ffd43b",
  "orientation": "portrait-primary",
  "scope": "./",
  "lang": "fr",
  "id": "sentinel-os-v93-final-complete-hw-v12-voice-fix",
  "icons": [
    {"src": "/static/icon-192.png","sizes": "192x192","type": "image/png","purpose": "any maskable"},
    {"src": "/static/icon-512.png","sizes": "512x512","type": "image/png","purpose": "any maskable"},
    {"src": "/static/icon-1024.png","sizes": "1024x1024","type": "image/png","purpose": "any maskable"}
  ],
  "shortcuts": [
    {"name": "Pitch 30s","url": "./#pitch30","icons": [{"src": "/static/icon-192.png","sizes": "192x192"}]},
    {"name": "Pitch 90s JURY + HW","url": "./#pitch90","icons": [{"src": "/static/icon-512.png","sizes": "512x512"}]},
    {"name": "Jury Mode","url": "./#jury","icons": [{"src": "/static/icon-192.png","sizes": "192x192"}]},
    {"name": "Hardware V1.2","url": "./#hardware","icons": [{"src": "/static/icon-1024.png","sizes": "1024x1024"}]}
  ]
}