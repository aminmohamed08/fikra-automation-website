const STATIC = 'fikra-static-v1';
const IMAGES = 'fikra-img-v1';
const MAX_IMAGES = 150;
const SHELL = ['/', '/logo-mybusiness_fikra-automation.png', '/photo_without_bg-removebg-preview.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(STATIC)
      .then((c) => Promise.allSettled(SHELL.map((u) => c.add(u))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== STATIC && k !== IMAGES).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

async function trim(cacheName, max) {
  const cache = await caches.open(cacheName);
  const keys = await cache.keys();
  if (keys.length > max) await Promise.all(keys.slice(0, keys.length - max).map((k) => cache.delete(k)));
}

async function cacheFirst(req, cacheName) {
  const cache = await caches.open(cacheName);
  const hit = await cache.match(req);
  if (hit) return hit;
  const res = await fetch(req);
  if (res && (res.ok || res.type === 'opaque')) {
    cache.put(req, res.clone());
    if (cacheName === IMAGES) trim(IMAGES, MAX_IMAGES);
  }
  return res;
}

async function staleWhileRevalidate(req) {
  const cache = await caches.open(STATIC);
  const hit = await cache.match(req);
  const net = fetch(req).then((res) => {
    if (res && (res.ok || res.type === 'opaque')) cache.put(req, res.clone());
    return res;
  }).catch(() => hit);
  return hit || net;
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Never cache Supabase API / auth / realtime (data is cached in localStorage by FikraCache)
  if (url.hostname.endsWith('supabase.co') && !url.pathname.includes('/storage/')) return;

  if (req.destination === 'image' || /\.(png|jpe?g|webp|gif|svg|avif)(\?|$)/i.test(url.pathname)) {
    e.respondWith(cacheFirst(req, IMAGES).catch(() => caches.match(req)));
    return;
  }
  if (url.hostname === 'fonts.gstatic.com' || url.hostname === 'fonts.googleapis.com') {
    e.respondWith(cacheFirst(req, STATIC));
    return;
  }
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then((res) => {
      const copy = res.clone();
      caches.open(STATIC).then((c) => c.put(req, copy));
      return res;
    }).catch(() => caches.match(req).then((r) => r || caches.match('/'))));
    return;
  }
  if (url.origin === location.origin || /cdn\.jsdelivr\.net|cdn\.tailwindcss\.com|cdnjs\.cloudflare\.com/.test(url.hostname)) {
    e.respondWith(staleWhileRevalidate(req));
  }
});