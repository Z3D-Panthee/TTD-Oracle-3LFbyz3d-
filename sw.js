// SENTINEL OS v9.3 FINAL
const CACHE='sentinel-v93-hw-v12-v351';
const FILES=['./','./index.html','./manifest.json','/static/icon-192.png','/static/icon-512.png','/static/icon-1024.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.map(x=>{if(x!==CACHE)return caches.delete(x)}))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{e.respondWith(caches.match(e.request).then(c=>c||fetch(e.request).then(r=>{caches.open(CACHE).then(ch=>ch.put(e.request,r.clone()));return r}).catch(()=>e.request.destination==='document'?caches.match('./'):null)))});