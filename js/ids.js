/*
  js/core/ids.js — Application « Rangement »
  Version : V003
  Horodatage : 2026-10-22 21:39 (heure de Paris)
  Résumé : création — génération d'identifiants uniques.
*/
(function () {
  'use strict';

  var R = window.Rangement;

  function randomPart() {
    var c = window.crypto;
    if (c && c.getRandomValues) {
      var a = new Uint32Array(2);
      c.getRandomValues(a);
      return a[0].toString(36) + a[1].toString(36);
    }
    return Math.random().toString(36).slice(2, 12);
  }

  // Ex. generate('loc') → « loc_lq3k9x2fa8d1b »
  function generate(prefix) {
    return (prefix || 'id') + '_' + Date.now().toString(36) + randomPart();
  }

  R.ids = { generate: generate };
})();
