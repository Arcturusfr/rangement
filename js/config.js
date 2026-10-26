/*
  js/config.js — Application « Rangement »
  Version : V010
  Horodatage : 2026-10-26 15:33 (heure de Paris)
  Résumé : version V010 (jalon 7).
*/
(function () {
  'use strict';

  var R = window.Rangement = window.Rangement || {};

  // Crée (si besoin) et renvoie un sous-espace de noms, ex. R.ns('ui.views').
  R.ns = function (path) {
    var node = R;
    path.split('.').forEach(function (key) {
      node[key] = node[key] || {};
      node = node[key];
    });
    return node;
  };

  R.config = Object.freeze({
    appName: 'Rangement',
    version: 'V010',
    dwellingName: '',          // précision affichée après « Logement » (plusieurs logements, plus tard)
    schemaVersion: 1,
    storageKey: 'rangement.data',
    twoPanesMinWidth: 720,
    kinds: Object.freeze([
      { id: 'piece', label: 'Pièce' },
      { id: 'meuble', label: 'Meuble' },
      { id: 'tiroir', label: 'Tiroir' },
      { id: 'etagere', label: 'Étagère' },
      { id: 'boite', label: 'Boîte' },
      { id: 'autre', label: 'Autre' }
    ])
  });
})();
