/*
  js/ui/components/contextmenu.js — Application « Rangement »
  Version : V015
  Horodatage : 2026-11-05 02:30 (heure de Paris)
  Résumé : création — menu contextuel ouvert près d'un élément (commande principale « Ouvrir » plus grande, puis les autres commandes).
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;
  var current = null;   // { backdrop, box, anchor, onKey }

  function close(restoreFocus) {
    if (!current) { return; }
    var c = current;
    current = null;
    document.removeEventListener('keydown', c.onKey, true);
    if (c.anchor) { c.anchor.classList.remove('has-menu'); }
    if (c.backdrop.parentNode) { c.backdrop.parentNode.removeChild(c.backdrop); }
    if (c.box.parentNode) { c.box.parentNode.removeChild(c.box); }
    if (restoreFocus && c.focusTo && document.contains(c.focusTo) && c.focusTo.focus) { c.focusTo.focus(); }
  }

  // Place le menu près de l'ancre : dessous si la place suffit (ou si c'est le côté le plus dégagé), sinon dessus ; toujours dans l'écran.
  function position(box, anchor) {
    var vw = window.innerWidth, vh = window.innerHeight;
    var rect = anchor.getBoundingClientRect();
    var bw = box.offsetWidth, bh = box.offsetHeight;
    var below = vh - rect.bottom - 8, above = rect.top - 8;
    var top = (below >= bh || below >= above) ? rect.bottom + 4 : rect.top - bh - 4;
    top = Math.max(8, Math.min(top, vh - bh - 8));
    var left = Math.max(8, Math.min(rect.left, vw - bw - 8));
    box.style.top = top + 'px';
    box.style.left = left + 'px';
  }

  // cfg : { anchor (sert au placement), focusTo? (reçoit le focus à la fermeture, sinon l'ancre), title, subtitle?, level?, label?, primary?: { label, run }, items: [{ label, run, danger? }] }
  // Choisir une commande ferme le menu, puis l'exécute. Échap ou un appui ailleurs ferme sans rien faire.
  function open(cfg) {
    close(false);
    function choose(run) { return function () { close(false); run(); }; }

    var nodes = [
      el('div', { class: 'ctx-head' }, [
        cfg.subtitle ? el('p', { class: 'ctx-path' }, [cfg.subtitle]) : null,
        el('p', { class: 'ctx-name' }, [cfg.title])
      ])
    ];
    var primary = null;
    if (cfg.primary) {
      primary = el('button', { class: 'button ctx-primary', type: 'button', 'data-level': cfg.level || null, onclick: choose(cfg.primary.run) }, [cfg.primary.label]);
      nodes.push(primary);
    }
    nodes.push(el('div', { class: 'ctx-list' }, cfg.items.map(function (it) {
      return el('button', { class: 'ctx-item' + (it.danger ? ' ctx-item--danger' : ''), type: 'button', onclick: choose(it.run) }, [it.label]);
    })));

    var box = el('div', { class: 'ctx-menu', role: 'group', 'aria-label': cfg.label || ('Commandes : ' + cfg.title), 'data-level': cfg.level || null }, nodes);
    var backdrop = el('div', { class: 'ctx-backdrop', onclick: function () { close(true); } });
    var onKey = function (event) { if (event.key === 'Escape') { event.stopPropagation(); close(true); } };
    document.addEventListener('keydown', onKey, true);
    document.body.appendChild(backdrop);
    document.body.appendChild(box);
    current = { backdrop: backdrop, box: box, anchor: cfg.anchor, focusTo: cfg.focusTo || cfg.anchor, onKey: onKey };
    if (cfg.anchor) {
      cfg.anchor.classList.add('has-menu');
      position(box, cfg.anchor);
    }
    var first = primary || box.querySelector('.ctx-item');
    if (first) { first.focus(); }
  }

  R.events.on('route:changed', function () { close(false); });
  window.addEventListener('resize', function () { close(false); });

  R.ns('ui.components').contextmenu = { open: open, close: function () { close(false); }, isOpen: function () { return !!current; } };
})();
