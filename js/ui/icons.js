/*
  js/ui/icons.js — Application « Rangement »
  Version : V022
  Horodatage : 2026-11-25 22:05 (heure de Paris)
  Résumé : V022 : nouveau pictogramme « Actions » (éclair dans un carré) ; pictogrammes des commandes des menus (ouvrir, ajouter pièce / objet, grille, déplacer, dupliquer, supprimer).
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
    // V021 : arborescence (père en haut à gauche, fils alignés verticalement dessous), « Actions » (trois points)
    'tree': [
      ['rect', { x: 3, y: 3, width: 9, height: 4, rx: 1 }], ['rect', { x: 12, y: 17, width: 9, height: 4, rx: 1 }], ['rect', { x: 12, y: 10, width: 9, height: 4, rx: 1 }],
      ['path', { d: 'M6 7v12M6 12h6M6 19h6', 'stroke-opacity': 0.5 }]
    ],
    // V022 : « Actions » = éclair plein dans un carré arrondi
    'actions': [
      ['rect', { x: 3, y: 3, width: 18, height: 18, rx: 3.5, 'stroke-width': 2 }],
      ['path', { d: 'M13 6.5L8.5 13h3.5l-1 4.5 4.5-6.5H12l1-4.5z', fill: 'currentColor', 'stroke-width': 1 }]
    ],
    // V022 : commandes des menus (« Actions », menu d'une case, menu d'une case libre)
    'open': [['path', { d: 'M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4' }], ['path', { d: 'M10 17l5-5-5-5M15 12H3' }]],
    'add-place': [
      ['path', { d: 'M3 3h11M3 3v18h18V11M9 3v18M3 12h6M15 21v-6h5', 'stroke-opacity': 0.7 }],
      ['path', { d: 'M18 3v6M15 6h6' }]
    ],
    'add-item': [
      ['path', { d: 'M16 17h6M19 14v6' }],
      ['path', { d: 'M12 22V12M21 10.535V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.729l7 4a2 2 0 0 0 2 .001l1.675-.955M3.29 7 12 12l8.71-5' }]
    ],
    'grid': [
      ['rect', { x: 1, y: 1, width: 14, height: 14, rx: 2, 'stroke-width': 1.5, 'stroke-opacity': 0.55 }],
      ['path', { d: 'M8 1v14M1 8h14', 'stroke-width': 1.5, 'stroke-opacity': 0.55 }],
      ['path', { d: 'M19 5l2-4 2 4M21 4v11m-2-4l2 4 2-4', 'stroke-width': 1.5 }],
      ['path', { d: 'M5 19l-4 2 4 2M4 21h11m-4-2l4 2-4 2', 'stroke-width': 1.5 }]
    ],
    'move-to': [
      ['rect', { x: 2, y: 14, width: 9, height: 9 }], ['rect', { x: 14, y: 2, width: 9, height: 9, opacity: 0.5 }],
      ['path', { d: 'M6.5 18L19 6h-8M19 6v8' }]
    ],
    'duplicate': [
      ['line', { x1: 15, x2: 15, y1: 12, y2: 18 }], ['line', { x1: 12, x2: 18, y1: 15, y2: 15 }],
      ['rect', { width: 14, height: 14, x: 8, y: 8, rx: 2, ry: 2 }],
      ['path', { d: 'M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2' }]
    ],
    'delete': [
      ['path', { d: 'M10 11v6' }], ['path', { d: 'M14 11v6' }], ['path', { d: 'M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6' }],
      ['path', { d: 'M3 6h18' }], ['path', { d: 'M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2' }]
    ],
    'search': [['circle', { cx: 11, cy: 11, r: 7 }], ['path', { d: 'M21 21l-5-5' }]],
    'help': [['circle', { cx: 12, cy: 12, r: 10 }], ['path', { d: 'M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3' }], ['line', { x1: 12, y1: 17, x2: 12.01, y2: 17 }]],
    'arrow-left': [['path', { d: 'M19 12H5M12 19l-7-7 7-7' }]],
    // V021 : élargir / réduire le volet d'arborescence — écran, séparation du volet, arborescence, chevron dans le sens du changement
    'expand-h': [
      ['rect', { x: 3, y: 3, width: 18, height: 18, rx: 1 }], ['path', { d: 'M15 9l3 2.5-3 2.5' }],
      ['line', { x1: 12, y1: 2, x2: 12, y2: 21.5, 'stroke-width': 1, 'stroke-linecap': 'butt' }],
      ['rect', { x: 5.5, y: 7, width: 4, height: 1.5, 'stroke-width': 1, 'stroke-linecap': 'butt', 'stroke-linejoin': 'miter' }], ['rect', { x: 5.5, y: 11, width: 4, height: 1.5, 'stroke-width': 1, 'stroke-linecap': 'butt', 'stroke-linejoin': 'miter' }], ['rect', { x: 5.5, y: 15, width: 4, height: 1.5, 'stroke-width': 1, 'stroke-linecap': 'butt', 'stroke-linejoin': 'miter' }]
    ],
    'collapse-h': [
      ['rect', { x: 3, y: 3, width: 18, height: 18, rx: 1 }], ['path', { d: 'M18 9l-3 2.5 3 2.5' }],
      ['line', { x1: 8, y1: 2, x2: 8, y2: 21.5, 'stroke-width': 1, 'stroke-linecap': 'butt' }],
      ['rect', { x: 4.5, y: 7, width: 2, height: 1.5, 'stroke-width': 1, 'stroke-linecap': 'butt', 'stroke-linejoin': 'miter' }], ['rect', { x: 4.5, y: 11, width: 2, height: 1.5, 'stroke-width': 1, 'stroke-linecap': 'butt', 'stroke-linejoin': 'miter' }], ['rect', { x: 4.5, y: 15, width: 2, height: 1.5, 'stroke-width': 1, 'stroke-linecap': 'butt', 'stroke-linejoin': 'miter' }]
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
