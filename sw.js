// SENTINEL OS v9.3 FINAL FUSI + VOICE FIX V3.5.1 + HARDWARE V1.2
const CACHE_NAME = 'sentinel-os-v93-final-complete-hw-v12-voice-fix-v351-lemba';
const CORE_FILES = ['./','./index.html','./manifest.json','/static/icon-192.png','/static/icon-512.png','/static/icon-1024.png'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME).then(c=>c.addAll(CORE_FILES)).then(()=>self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(k=>Promise.all(k.map(x=>{if(x!==CACHE_NAME)return caches.delete(x)}))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch', e => {
  e.respondWith(caches.match(e.request).then(c=>c||fetch(e.request).then(r=>{caches.open(CACHE_NAME).then(cache=>cache.put(e.request,r.clone()));return r;}).catch(()=>e.request.destination==='document'?caches.match('./'):null)));
});