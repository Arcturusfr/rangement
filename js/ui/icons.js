/*
  js/ui/icons.js — Application « Rangement »
  Version : V019
  Horodatage : 2026-11-17 07:12 (heure de Paris)
  Résumé : création — pictogrammes SVG filaires (liste, plan, réglages, modifier, modifier le plan, déplacer, agrandir…), construits sans HTML.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var NS = 'http://www.w3.org/2000/svg';

  // Chaque pictogramme : liste de formes [balise, attributs] dans un carré de 24 × 24 (trait de 2, extrémités rondes, couleur du texte).
  var SHAPES = {
    'list': [
      ['line', { x1: 8, y1: 6, x2: 21, y2: 6 }], ['line', { x1: 8, y1: 12, x2: 21, y2: 12 }], ['line', { x1: 8, y1: 18, x2: 21, y2: 18 }],
      ['line', { x1: 3, y1: 6, x2: 3.01, y2: 6 }], ['line', { x1: 3, y1: 12, x2: 3.01, y2: 12 }], ['line', { x1: 3, y1: 18, x2: 3.01, y2: 18 }]
    ],
    'plan': [
      ['path', { d: 'M3 3h18v18H3z' }], ['path', { d: 'M9 3v18' }], ['path', { d: 'M3 12h6' }], ['path', { d: 'M15 21v-8h6' }]
    ],
    'settings': [
      ['circle', { cx: 12, cy: 12, r: 3 }],
      ['path', { d: 'M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82 1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z' }]
    ],
    'edit-text': [
      ['path', { d: 'M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7' }],
      ['path', { d: 'M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z' }]
    ],
    'edit-plan': [
      ['path', { d: 'M3 3h11M3 3v18h18V10M9 3v18M3 12h6M15 21v-8', 'stroke-opacity': 0.5 }],
      ['path', { d: 'M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z', 'stroke-width': 2.5 }]
    ],
    'move-cell': [
      ['rect', { x: 3, y: 3, width: 18, height: 18, rx: 2, 'stroke-opacity': 0.3, 'stroke-dasharray': '3 3' }],
      ['rect', { x: 8, y: 8, width: 8, height: 8, rx: 1, 'stroke-width': 2.5 }],
      ['path', { d: 'M12 2v3M12 19v3M2 12h3M19 12h3' }],
      ['path', { d: 'M10 3l2-2 2 2M10 21l2 2 2-2M3 14l-2-2 2-2M21 14l2-2-2-2' }]
    ],
    'enlarge-cell': [
      ['rect', { x: 7, y: 7, width: 10, height: 10, rx: 1, 'stroke-width': 2.5 }],
      ['path', { d: 'M3 3l5 5M3 3v5M3 3h5' }], ['path', { d: 'M21 3l-5 5M21 3v5M21 3h-5' }],
      ['path', { d: 'M3 21l5-5M3 21v-5M3 21h5' }], ['path', { d: 'M21 21l-5-5M21 21v-5M21 21h-5' }]
    ],
    // Agrandir le plan (coins vers l'extérieur) / l'ajuster à l'écran (coins vers l'intérieur)
    'zoom-in': [['path', { d: 'M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5' }]],
    'zoom-out': [['path', { d: 'M9 4v5H4M15 4v5h5M9 20v-5H4M15 20v-5h5' }]]
  };

  // Renvoie un élément <svg> (décoratif : aria-hidden). `size` en pixels (22 par défaut).
  function create(name, size) {
    var shapes = SHAPES[name] || [];
    var svg = document.createElementNS(NS, 'svg');
    var px = String(size || 22);
    [['viewBox', '0 0 24 24'], ['width', px], ['height', px], ['aria-hidden', 'true'], ['focusable', 'false'], ['class', 'icon'],
      ['fill', 'none'], ['stroke', 'currentColor'], ['stroke-width', '2'], ['stroke-linecap', 'round'], ['stroke-linejoin', 'round']
    ].forEach(function (a) { svg.setAttribute(a[0], a[1]); });
    shapes.forEach(function (s) {
      var node = document.createElementNS(NS, s[0]);
      Object.keys(s[1]).forEach(function (k) { node.setAttribute(k, String(s[1][k])); });
      svg.appendChild(node);
    });
    return svg;
  }

  R.ns('ui').icons = { create: create, has: function (name) { return !!SHAPES[name]; } };
})();
