// Service Worker for Kinder-Supermarkt PWA
const CACHE_NAME = 'kinder-supermarkt-v1';

self.addEventListener('install', (event) => {
    console.log('[SW] Service Worker installed');
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    console.log('[SW] Service Worker activated');
    return self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    // Pass-through fetch handler required for PWA installation criteria
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});
