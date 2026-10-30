/*
  sw.js — Application « Rangement »
  Version : V011
  Horodatage : 2026-10-30 00:22 (heure de Paris)
  Résumé : version V011 (jalon 7, grille de placement des meubles).
*/
'use strict';

var VERSION = 'V011';                       // doit être identique à js/config.js (vérifié par les tests)
var CACHE_PREFIX = 'rangement-';
var CACHE = CACHE_PREFIX + VERSION;

// Liste écrite en dur, à mettre à jour à chaque livraison (chemins relatifs à ce fichier).
var FILES = [
  './',
  'index.html',
  'manifest.webmanifest',
  'css/base.css',
  'css/layout.css',
  'css/components.css',
  'css/furniture.css',
  'js/config.js',
  'js/core/events.js',
  'js/core/ids.js',
  'js/core/models.js',
  'js/core/storage.js',
  'js/core/store.js',
  'js/features/demo.js',
  'js/features/locations.js',
  'js/features/items.js',
  'js/features/search.js',
  'js/features/backup.js',
  'js/features/furniture.js',
  'js/ui/dom.js',
  'js/ui/router.js',
  'js/ui/components/breadcrumb.js',
  'js/ui/components/list.js',
  'js/ui/components/form.js',
  'js/ui/components/dialog.js',
  'js/ui/components/detailbar.js',
  'js/ui/layout.js',
  'js/ui/views/treerail.js',
  'js/ui/views/browse.js',
  'js/ui/views/location-actions.js',
  'js/ui/views/item-actions.js',
  'js/ui/views/item.js',
  'js/ui/views/search.js',
  'js/ui/views/searchbar.js',
  'js/ui/views/settings.js',
  'js/ui/views/furniture.js',
  'js/ui/views/location.js',
  'js/pwa.js',
  'js/main.js',
  'icons/icon-192x192.png',
  'icons/icon-512x512.png',
  'icons/maskable-icon-192x192.png',
  'icons/maskable-icon-512x512.png'
];

// Installation : tout ou rien. Pas de skipWaiting automatique : la nouvelle version attend l'accord de l'utilisateur.
self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE).then(function (cache) {
      // cache: 'reload' : on ne veut jamais pré-cacher une copie périmée du cache HTTP du navigateur.
      return cache.addAll(FILES.map(function (f) { return new Request(f, { cache: 'reload' }); }));
    })
  );
});

// Activation : suppression de tous les anciens caches de l'application.
self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys
        .filter(function (k) { return k.indexOf(CACHE_PREFIX) === 0 && k !== CACHE; })
        .map(function (k) { return caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

// Messages de la page : activer la nouvelle version (accord de l'utilisateur), connaître la version du cache.
self.addEventListener('message', function (event) {
  var data = event.data || {};
  if (data.type === 'SKIP_WAITING') { self.skipWaiting(); }
  if (data.type === 'GET_VERSION' && event.ports && event.ports[0]) { event.ports[0].postMessage({ cache: CACHE, version: VERSION }); }
});

// Cache d'abord pour les fichiers de l'application ; aucune interception des autres domaines.
self.addEventListener('fetch', function (event) {
  var req = event.request;
  if (req.method !== 'GET') { return; }
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) { return; }
  event.respondWith(
    caches.open(CACHE).then(function (cache) {
      return cache.match(req, { ignoreSearch: true }).then(function (hit) {
        if (hit) { return hit; }
        return fetch(req).catch(function () {
          // Hors ligne et fichier inconnu : pour une page, on retombe sur l'application.
          return req.mode === 'navigate' ? cache.match('index.html') : Response.error();
        });
      });
    })
  );
});
