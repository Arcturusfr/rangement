/*
  js/core/events.js — Application « Rangement »
  Version : V003
  Horodatage : 2026-10-22 21:39 (heure de Paris)
  Résumé : création — mini bus d'événements.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var handlers = {};

  // Abonne `fn` à l'événement `name`. Renvoie une fonction de désabonnement.
  function on(name, fn) {
    (handlers[name] = handlers[name] || []).push(fn);
    return function () { off(name, fn); };
  }

  function off(name, fn) {
    handlers[name] = (handlers[name] || []).filter(function (h) { return h !== fn; });
  }

  // Un abonné qui plante n'empêche pas les suivants de s'exécuter.
  function emit(name, payload) {
    (handlers[name] || []).slice().forEach(function (fn) {
      try { fn(payload); } catch (err) { console.error('Erreur dans un abonné à « ' + name + ' »', err); }
    });
  }

  R.events = { on: on, off: off, emit: emit };
})();
