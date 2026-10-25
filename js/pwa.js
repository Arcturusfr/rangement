/*
  js/pwa.js — Application « Rangement »
  Version : V008
  Horodatage : 2026-10-25 00:52 (heure de Paris)
  Résumé : création — enregistrement du service worker, mise à jour sur accord de l'utilisateur, vidage du cache, installation.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var CACHE_PREFIX = 'rangement-';

  var state = {
    supported: false,      // service worker utilisable (https ou localhost, pas file://)
    registered: false,
    cacheName: null,       // cache actif, ex. « rangement-V008 »
    updateReady: false,    // une nouvelle version attend l'accord de l'utilisateur
    canInstall: false,     // le navigateur propose « Installer l'application »
    standalone: false,     // l'application tourne déjà installée
    error: null
  };
  var reg = null;
  var installEvent = null;
  var userRequested = false;   // le rechargement n'a lieu que si l'utilisateur a demandé la mise à jour

  function emit() { R.events.emit('pwa:changed', {}); }

  function isSupported() {
    return 'serviceWorker' in navigator && (location.protocol === 'https:' || location.protocol === 'http:');
  }

  function status() { return Object.assign({}, state); }

  // Demande au service worker actif le nom de son cache ; à défaut, lit la liste des caches.
  function refreshCacheName() {
    var ctrl = navigator.serviceWorker.controller;
    function fromKeys() {
      if (!window.caches) { return Promise.resolve(); }
      return caches.keys().then(function (keys) {
        var mine = keys.filter(function (k) { return k.indexOf(CACHE_PREFIX) === 0; });
        state.cacheName = mine.length ? mine[0] : null;
      });
    }
    if (!ctrl) { return fromKeys().then(emit, emit); }
    return new Promise(function (resolve) {
      var done = false;
      var channel = new MessageChannel();
      var timer = setTimeout(function () { if (!done) { done = true; resolve(false); } }, 1500);
      channel.port1.onmessage = function (e) {
        if (done) { return; }
        done = true;
        clearTimeout(timer);
        state.cacheName = e.data && e.data.cache ? e.data.cache : null;
        resolve(true);
      };
      ctrl.postMessage({ type: 'GET_VERSION' }, [channel.port2]);
    }).then(function (ok) { return ok ? null : fromKeys(); }).then(emit, emit);
  }

  function watch(registration) {
    function check() {
      if (registration.waiting && navigator.serviceWorker.controller) { state.updateReady = true; emit(); }
    }
    check();
    registration.addEventListener('updatefound', function () {
      var worker = registration.installing;
      if (!worker) { return; }
      worker.addEventListener('statechange', function () {
        if (worker.state === 'installed') { check(); }
      });
    });
  }

  function init() {
    state.standalone = (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) || navigator.standalone === true;

    window.addEventListener('beforeinstallprompt', function (event) {
      event.preventDefault();
      installEvent = event;
      state.canInstall = true;
      emit();
    });
    window.addEventListener('appinstalled', function () {
      installEvent = null;
      state.canInstall = false;
      state.standalone = true;
      emit();
    });

    if (!isSupported()) { return; }
    state.supported = true;

    navigator.serviceWorker.addEventListener('controllerchange', function () {
      if (userRequested) { window.location.reload(); } else { refreshCacheName(); }
    });

    navigator.serviceWorker.register('sw.js', { updateViaCache: 'none' }).then(function (registration) {
      reg = registration;
      state.registered = true;
      watch(registration);
      refreshCacheName();
    }).catch(function (err) {
      state.error = (err && err.message) ? err.message : 'Enregistrement impossible.';
      emit();
    });
  }

  // Cherche une nouvelle version. Renvoie une promesse { ok, updateReady }.
  function checkUpdate() {
    if (!reg) { return Promise.resolve({ ok: false, updateReady: false }); }
    return reg.update().then(function () {
      return new Promise(function (resolve) {
        setTimeout(function () { resolve({ ok: true, updateReady: state.updateReady }); }, 600);
      });
    }, function () { return { ok: false, updateReady: false }; });
  }

  // Active la nouvelle version (la page se recharge d'elle-même une fois la bascule faite).
  function applyUpdate() {
    if (!reg || !reg.waiting) { return false; }
    userRequested = true;
    reg.waiting.postMessage({ type: 'SKIP_WAITING' });
    return true;
  }

  // Supprime les caches de l'application et le service worker, puis recharge la page. Les données (localStorage) ne sont pas touchées.
  function clearCache() {
    var wipe = window.caches
      ? caches.keys().then(function (keys) {
          return Promise.all(keys.filter(function (k) { return k.indexOf(CACHE_PREFIX) === 0; }).map(function (k) { return caches.delete(k); }));
        })
      : Promise.resolve();
    return wipe.then(function () { return reg ? reg.unregister() : null; }).then(function () {
      window.location.reload();
      return { ok: true };
    }, function () { return { ok: false }; });
  }

  function promptInstall() {
    if (!installEvent) { return Promise.resolve(false); }
    var ev = installEvent;
    installEvent = null;
    state.canInstall = false;
    emit();
    ev.prompt();
    return ev.userChoice.then(function (c) { return c && c.outcome === 'accepted'; }, function () { return false; });
  }

  R.pwa = {
    init: init,
    status: status,
    checkUpdate: checkUpdate,
    applyUpdate: applyUpdate,
    clearCache: clearCache,
    promptInstall: promptInstall
  };
})();
