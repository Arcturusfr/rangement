/*
  js/ui/layout.js — Application « Rangement »
  Version : V003
  Horodatage : 2026-10-22 21:39 (heure de Paris)
  Résumé : création — bascule 1 volet / 2 volets selon la largeur de la fenêtre.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var mql = null;

  function apply() {
    var panes = mql.matches ? '2' : '1';
    document.documentElement.setAttribute('data-panes', panes);
    R.events.emit('layout:changed', { panes: Number(panes) });
  }

  function init() {
    mql = window.matchMedia('(min-width: ' + R.config.twoPanesMinWidth + 'px)');
    if (mql.addEventListener) { mql.addEventListener('change', apply); }
    else if (mql.addListener) { mql.addListener(apply); }
    apply();
  }

  function panes() { return Number(document.documentElement.getAttribute('data-panes')) || 1; }

  R.ns('ui').layout = { init: init, panes: panes };
})();
