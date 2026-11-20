/*
  js/ui/components/longpress.js — Application « Rangement »
  Version : V020
  Horodatage : 2026-11-20 22:57 (heure de Paris)
  Résumé : V020 : option filter(event) — un conteneur peut ignorer les appuis venant de ses enfants.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var DELAY = 450;     // durée de l'appui long (ms)
  var SLOP = 10;       // déplacement toléré pendant l'appui (px) ; au-delà, c'est un défilement

  // cfg : { onShort(event), onLong(event), delay?, filter?(event) → false pour ignorer l'événement }
  // Appui simple = clic (la touche Entrée sur un bouton compte aussi). Appui long = doigt ou souris maintenu,
  // ou clic droit, ou touche Menu / Maj+F10 (événement « contextmenu »). Le menu natif du navigateur est supprimé.
  function attach(node, cfg) {
    var timer = null;
    var resetTimer = null;
    var fired = false;        // un appui long vient d'avoir lieu : le clic qui suit est ignoré
    var tracking = false;
    var x0 = 0, y0 = 0;

    function stop() {
      if (timer) { clearTimeout(timer); timer = null; }
      tracking = false;
    }
    function releaseSoon() {
      if (!fired) { return; }
      if (resetTimer) { clearTimeout(resetTimer); }
      resetTimer = setTimeout(function () { fired = false; resetTimer = null; }, 400);
    }
    function fire(event) {
      fired = true;
      try { if (navigator.vibrate) { navigator.vibrate(15); } } catch (err) { /* sans suite */ }
      cfg.onLong(event);
    }

    node.addEventListener('pointerdown', function (event) {
      if (cfg.filter && !cfg.filter(event)) { return; }
      if (event.pointerType === 'mouse' && event.button !== 0) { return; }
      if (resetTimer) { clearTimeout(resetTimer); resetTimer = null; }
      fired = false;
      tracking = true;
      x0 = event.clientX;
      y0 = event.clientY;
      if (timer) { clearTimeout(timer); }
      timer = setTimeout(function () {
        timer = null;
        if (tracking) { fire(event); }
      }, cfg.delay || DELAY);
    });
    node.addEventListener('pointermove', function (event) {
      if (!timer) { return; }
      if (Math.abs(event.clientX - x0) > SLOP || Math.abs(event.clientY - y0) > SLOP) { stop(); }
    });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (name) {
      node.addEventListener(name, function () { stop(); releaseSoon(); });
    });
    node.addEventListener('contextmenu', function (event) {
      if (cfg.filter && !cfg.filter(event)) { return; }
      event.preventDefault();
      if (fired) { return; }
      stop();
      fire(event);
      releaseSoon();
    });
    node.addEventListener('click', function (event) {
      if (cfg.filter && !cfg.filter(event)) { return; }
      if (fired && event.detail !== 0) { fired = false; event.preventDefault(); event.stopPropagation(); return; }   // le clic qui suit un appui long est ignoré (pas celui du clavier, detail = 0)
      cfg.onShort(event);
    });
  }

  R.ns('ui.components').longpress = { attach: attach, delay: DELAY };
})();
