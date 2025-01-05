const CACHE_NAME = 'my-app-cache-v5';
const QUEUE_NAME = 'crud-queue';
const STATIC_DIRS = [
    "/",
    "/static/manifest.json",
    "/static/css/build.css",
    "/static/css/selectize.bootstrap3.min.css",
    "/static/icon/android-chrome-192x192.png",
    "/static/icon/android-chrome-512x512.png",
    "/static/icon/android-icon-144x144.png",
    "/static/icon/android-icon-48x48.png",
    "/static/icon/android-icon-72x72.png",
    "/static/icon/android-icon-96x96.png",
    "/static/icon/apple-icon-152x152.png",
    "/static/icon/apple-touch-icon.png",
    "/static/icon/favicon-16x16.png",
    "/static/icon/favicon-32x32.png",
    "/static/icon/favicon-96x96.png",
    "/static/icon/favicon.ico",
    "/static/icon/favicon.svg",
    "/static/icon/web-app-manifest-192x192.png",
    "/static/icon/web-app-manifest-512x512.png",
    "/static/images/Binaaul-Mustaqbal.png",
    "/static/images/blank-profile.png",
    "/static/images/favicon.ico",
    "/static/images/hero.png",
    "/static/images/logo.png",
    "/static/screenshots/desktop-screenshot.png",
    "/static/screenshots/mobile-screenshot.png",
    "/static/screenshots/tablet-screenshot.png",
]
// Install event to cache static assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(STATIC_DIRS);
        })
    );
    console.log("Service Worker has been installed", event)
});

// Activate event to clean up old caches
self.addEventListener('activate', event => {
    console.log("Service Worker has been activate", event)
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.filter(name => name !== CACHE_NAME).map(name => caches.delete(name))
            );
        })
    );
});

// Intercept fetch requests and serve cached files
self.addEventListener('fetch', (event) => {
    console.log('Fetching:', event.request.url);
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        }).catch(() => console.log("Offline!")) // Fallback to offline.html
    );
});


self.addEventListener('push', event => {
    const data = event.data.json();
    const options = {
        body: data.body,
        icon: data.icon || '/default-icon.png',
        badge: data.badge || '/default-badge.png'
    };
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});
