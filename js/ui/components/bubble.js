/*
  js/ui/components/bubble.js — Application « Rangement »
  Version : V016
  Horodatage : 2026-11-06 12:00 (heure de Paris)
  Résumé : création — info-bulle ouverte près d'un bouton (ℹ️, chevron du libellé) ; fermée par Échap, un appui ailleurs ou un changement d'écran.
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
    if (c.anchor) { c.anchor.setAttribute('aria-expanded', 'false'); }
    if (c.backdrop.parentNode) { c.backdrop.parentNode.removeChild(c.backdrop); }
    if (c.box.parentNode) { c.box.parentNode.removeChild(c.box); }
    if (restoreFocus && c.anchor && document.contains(c.anchor) && c.anchor.focus) { c.anchor.focus(); }
  }

  // Sous le bouton si la place suffit, sinon au-dessus ; toujours dans l'écran.
  function position(box, anchor) {
    var vw = window.innerWidth, vh = window.innerHeight;
    var rect = anchor.getBoundingClientRect();
    var bw = box.offsetWidth, bh = box.offsetHeight;
    var below = vh - rect.bottom - 8, above = rect.top - 8;
    var top = (below >= bh || below >= above) ? rect.bottom + 6 : rect.top - bh - 6;
    top = Math.max(8, Math.min(top, vh - bh - 8));
    var left = Math.max(8, Math.min(rect.left, vw - bw - 8));
    box.style.top = top + 'px';
    box.style.left = left + 'px';
  }

  // cfg : { anchor, title?, lines: string[], level?, label? } — le texte est toujours inséré comme texte.
  function open(cfg) {
    close(false);
    var nodes = [];
    if (cfg.title) { nodes.push(el('p', { class: 'bubble-title' }, [cfg.title])); }
    (cfg.lines || []).forEach(function (line) { nodes.push(el('p', { class: 'bubble-line' }, [line])); });
    var box = el('div', {
      class: 'bubble', role: 'dialog', tabindex: '-1',
      'aria-label': cfg.label || cfg.title || 'Information', 'data-level': cfg.level || null
    }, nodes);
    var backdrop = el('div', { class: 'bubble-backdrop', onclick: function () { close(true); } });
    var onKey = function (event) { if (event.key === 'Escape') { event.stopPropagation(); close(true); } };
    document.addEventListener('keydown', onKey, true);
    document.body.appendChild(backdrop);
    document.body.appendChild(box);
    current = { backdrop: backdrop, box: box, anchor: cfg.anchor, onKey: onKey };
    if (cfg.anchor) {
      cfg.anchor.setAttribute('aria-expanded', 'true');
      position(box, cfg.anchor);
    }
    box.focus();
  }

  function toggle(cfg) {
    if (current && current.anchor === cfg.anchor) { close(true); } else { open(cfg); }
  }

  R.events.on('route:changed', function () { close(false); });
  R.events.on('store:changed', function () { close(false); });
  R.events.on('view:changed', function () { close(false); });
  window.addEventListener('resize', function () { close(false); });

  R.ns('ui.components').bubble = { open: open, toggle: toggle, close: function () { close(false); }, isOpen: function () { return !!current; } };
})();
