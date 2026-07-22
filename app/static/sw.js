// Service Worker for Kinder-Supermarkt PWA
// Update SW_VERSION whenever static assets change to force cache refresh
const SW_VERSION = '2.0.7';
const CACHE_NAME = `kinder-supermarkt-${SW_VERSION}`;

// Static assets to cache on install for faster repeat loads
const PRECACHE_ASSETS = [
    '/static/css/main.css',
    '/static/css/admin.css',
    '/static/js/cashier.js',
];

self.addEventListener('install', (event) => {
    console.log(`[SW] v${SW_VERSION} installing...`);
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(PRECACHE_ASSETS).catch(() => {
                // Silently skip if assets not available (offline install)
            });
        }).then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', (event) => {
    console.log(`[SW] v${SW_VERSION} activated`);
    // Delete old cache versions
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(
                keys
                    .filter((key) => key !== CACHE_NAME)
                    .map((key) => caches.delete(key))
            )
        ).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
    // Network-first for HTML/API, cache-first for static assets
    const url = new URL(event.request.url);
    const isStatic = url.pathname.startsWith('/static/');

    if (isStatic && event.request.method === 'GET') {
        event.respondWith(
            caches.match(event.request).then((cached) => {
                return cached || fetch(event.request).then((response) => {
                    const toCache = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(event.request, toCache));
                    return response;
                });
            }).catch(() => caches.match(event.request))
        );
    } else {
        event.respondWith(
            fetch(event.request).catch(() => caches.match(event.request))
        );
    }
});
