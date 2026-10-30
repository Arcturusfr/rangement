/*
  js/features/furniture.js — Application « Rangement »
  Version : V011
  Horodatage : 2026-10-30 00:22 (heure de Paris)
  Résumé : grille de placement (colonnes, lignes, bandes au-dessus / en dessous du meuble) ; position et taille en cases de chaque sous-emplacement, stockées dans `geometry`.
*/
(function () {
  'use strict';

  var R = window.Rangement;

  var RATIOS = [
    { id: 'haut', label: 'Haut', value: 0.7 },
    { id: 'carre', label: 'Carré', value: 1 },
    { id: 'large', label: 'Large', value: 1.5 },
    { id: 'tres-large', label: 'Très large', value: 2.2 }
  ];
  var DEFAULT_RATIO = 1.5;
  var LIMITS = { cols: 6, rows: 8, band: 3 };      // bornes proposées dans les réglages
  var ABS = { cols: 12, rows: 30, band: 10 };      // bornes acceptées en lecture (une grille agrandie automatiquement reste lisible)
  var GRID_REFUSED = 'Des emplacements occupent les cases à supprimer : déplacez-les d\u2019abord.';

  function fail(error) { return { ok: false, error: error }; }

  // Un meuble = emplacement de premier niveau (directement dans une pièce).
  function isFurniture(id) { return !!R.store.getLocation(id) && R.store.depthOf(id) === 1; }

  function geomOf(l) { return (l && l.geometry && typeof l.geometry === 'object') ? l.geometry : {}; }
  function intIn(v, min, max) { return (typeof v === 'number' && v === Math.floor(v) && v >= min && v <= max) ? v : null; }

  // Réglages d'un emplacement dessiné : { ratio, feet, cols, rows, top, bottom } (0 = automatique pour cols et rows).
  function get(id) {
    var g = geomOf(R.store.getLocation(id));
    return {
      ratio: (typeof g.ratio === 'number' && g.ratio >= 0.3 && g.ratio <= 4) ? g.ratio : DEFAULT_RATIO,
      feet: g.feet === true,
      cols: intIn(g.cols, 1, ABS.cols) || 0,
      rows: intIn(g.rows, 1, ABS.rows) || 0,
      top: intIn(g.top, 0, ABS.band) || 0,
      bottom: intIn(g.bottom, 0, ABS.band) || 0
    };
  }

  function posOf(l) { var g = geomOf(l); return typeof g.pos === 'number' ? g.pos : Infinity; }

  // Sous-emplacements dans l'ordre de remplissage automatique : ancien ordre manuel (V010), sinon alphabétique.
  function ordered(parentId) {
    return R.store.childLocations(parentId).map(function (l, i) { return { l: l, i: i }; })
      .sort(function (a, b) {
        var pa = posOf(a.l), pb = posOf(b.l);
        return pa === pb ? a.i - b.i : (pa < pb ? -1 : 1);
      }).map(function (x) { return x.l; });
  }

  function ival(v) { return (typeof v === 'number' && v === Math.floor(v) && v >= 0) ? v : null; }

  // Placement enregistré d'un sous-emplacement, ou null s'il n'en a pas encore.
  function explicit(l) {
    var g = geomOf(l);
    var z = (g.zone === 'top' || g.zone === 'body' || g.zone === 'bottom') ? g.zone : null;
    var c = ival(g.col), r = ival(g.row), w = ival(g.w), h = ival(g.h);
    if (!z || c === null || r === null || !w || !h) { return null; }
    return { zone: z, col: c, row: r, w: w, h: h };
  }

  // Grille de `id` : { C colonnes, L lignes du meuble, T lignes au-dessus, B lignes en dessous, cells: [{ id, zone, col, row, w, h }] }.
  // Les sous-emplacements sans place enregistrée prennent la première case libre ; la grille s'agrandit si besoin (rien n'est jamais caché).
  // `override` ({ cols, rows, top, bottom }) : réglages à essayer à la place de ceux enregistrés (les places automatiques sont recalculées).
  function layout(id, override) {
    var kids = ordered(id);
    var n = kids.length;
    var cfg = Object.assign(get(id), override || {});
    var cells = [];
    var pending = [];
    kids.forEach(function (l) {
      var e = explicit(l);
      if (e) { e.id = l.id; cells.push(e); } else { pending.push(l); }
    });
    var C = cfg.cols || (n <= 3 ? 1 : (n <= 8 ? 2 : 3));
    cells.forEach(function (c) { C = Math.max(C, c.col + c.w); });

    var occ = { top: {}, body: {}, bottom: {} };
    function free(z, c, r, w, h) {
      for (var i = r; i < r + h; i++) { for (var j = c; j < c + w; j++) { if (occ[z][i + ',' + j]) { return false; } } }
      return true;
    }
    function mark(z, c, r, w, h) {
      for (var i = r; i < r + h; i++) { for (var j = c; j < c + w; j++) { occ[z][i + ',' + j] = true; } }
    }
    var kept = [];
    cells.forEach(function (c) {      // un placement enregistré qui en chevauche un autre (fichier modifié) est replacé
      if (free(c.zone, c.col, c.row, c.w, c.h)) { mark(c.zone, c.col, c.row, c.w, c.h); kept.push(c); }
      else { pending.push(R.store.getLocation(c.id)); }
    });
    pending.forEach(function (l) {
      var w = Math.min(geomOf(l).span === 2 ? 2 : 1, C);
      for (var r = 0; ; r++) {
        var placed = false;
        for (var c = 0; c + w <= C; c++) {
          if (free('body', c, r, w, 1)) { mark('body', c, r, w, 1); kept.push({ id: l.id, zone: 'body', col: c, row: r, w: w, h: 1 }); placed = true; break; }
        }
        if (placed) { break; }
      }
    });
    function end(z) { return kept.reduce(function (m, c) { return c.zone === z ? Math.max(m, c.row + c.h) : m; }, 0); }
    return { C: C, L: Math.max(1, cfg.rows, end('body')), T: Math.max(cfg.top, end('top')), B: Math.max(cfg.bottom, end('bottom')), cells: kept };
  }

  function rowsOf(p, z) { return z === 'top' ? p.T : (z === 'bottom' ? p.B : p.L); }

  // Contrôle d'une grille : message d'erreur ou null.
  function check(p) {
    var seen = {};
    for (var k = 0; k < p.cells.length; k++) {
      var c = p.cells[k];
      if (c.col < 0 || c.row < 0 || c.w < 1 || c.h < 1 || c.col + c.w > p.C || c.row + c.h > rowsOf(p, c.zone)) {
        return 'Cet emplacement sortirait de la grille.';
      }
      for (var i = c.row; i < c.row + c.h; i++) {
        for (var j = c.col; j < c.col + c.w; j++) {
          var key = c.zone + ':' + i + ',' + j;
          if (seen[key]) { return 'Cette place est déjà occupée par un autre emplacement.'; }
          seen[key] = true;
        }
      }
    }
    return null;
  }

  // Enregistre toute la grille (y compris les places jusque-là automatiques, qui ne bougent plus ensuite).
  function commit(parentId, p) {
    var res = R.store.update(function (d) {
      var byId = {};
      d.locations.forEach(function (l) { byId[l.id] = l; });
      var t = byId[parentId];
      t.geometry = Object.assign({}, t.geometry || {}, { cols: p.C, rows: p.L, top: p.T, bottom: p.B });
      p.cells.forEach(function (c) {
        var k = byId[c.id];
        var g = Object.assign({}, k.geometry || {}, { zone: c.zone, col: c.col, row: c.row, w: c.w, h: c.h });
        delete g.pos;
        delete g.span;
        k.geometry = g;
        k.updatedAt = new Date().toISOString();
      });
    });
    return res.ok ? { ok: true } : fail('Enregistrement refusé : ' + (res.errors || []).join(' '));
  }

  function edit(cid, fn) {
    var l = R.store.getLocation(cid);
    if (!l || !l.parentId) { return fail('Cet emplacement n\u2019existe plus.'); }
    var p = layout(l.parentId);
    var c = p.cells.filter(function (x) { return x.id === cid; })[0];
    var err = fn(p, c) || check(p);
    return err ? fail(err) : commit(l.parentId, p);
  }

  function zoneAt(p, g) {
    if (g < 0) { return null; }
    if (g < p.T) { return { z: 'top', row: g }; }
    if (g < p.T + p.L) { return { z: 'body', row: g - p.T }; }
    if (g < p.T + p.L + p.B) { return { z: 'bottom', row: g - p.T - p.L }; }
    return null;
  }

  // Décale un sous-emplacement de `dc` colonnes et `dr` lignes (le passage d'une zone à l'autre se fait ligne par ligne).
  function move(cid, dc, dr) {
    return edit(cid, function (p, c) {
      var start = { top: 0, body: p.T, bottom: p.T + p.L };
      var g = start[c.zone] + c.row + dr;
      var at = zoneAt(p, g);
      var last = zoneAt(p, g + c.h - 1);
      if (!at || c.col + dc < 0 || c.col + dc + c.w > p.C) { return 'Déjà au bord de la grille.'; }
      if (!last || last.z !== at.z) { return 'Cet emplacement chevaucherait deux zones : réduisez sa hauteur ou choisissez une autre place.'; }
      c.zone = at.z; c.row = at.row; c.col += dc;
      return null;
    });
  }

  // Change la taille d'un sous-emplacement, en cases.
  function resize(cid, dw, dh) {
    return edit(cid, function (p, c) {
      c.w += dw; c.h += dh;
      return (c.w < 1 || c.h < 1) ? 'Taille minimale : une case.' : null;
    });
  }

  // patch : { cols?, rows?, top?, bottom? } — refusé si des emplacements occupent les cases supprimées.
  function setGrid(id, patch) {
    if (!R.store.getLocation(id)) { return fail('Cet emplacement n\u2019existe plus.'); }
    var p = layout(id, patch);
    if (patch.cols !== undefined) { p.C = patch.cols; }
    if (patch.rows !== undefined) { p.L = patch.rows; }
    if (patch.top !== undefined) { p.T = patch.top; }
    if (patch.bottom !== undefined) { p.B = patch.bottom; }
    if (p.C < 1 || p.L < 1 || p.T < 0 || p.B < 0) { return fail('Valeur de grille invalide.'); }
    return check(p) ? fail(GRID_REFUSED) : commit(id, p);
  }

  // patch : { ratio?, feet? }
  function set(id, patch) {
    if (!R.store.getLocation(id)) { return fail('Cet emplacement n\u2019existe plus.'); }
    var clean = {};
    if (patch.ratio !== undefined && typeof patch.ratio === 'number' && patch.ratio >= 0.3 && patch.ratio <= 4) { clean.ratio = patch.ratio; }
    if (patch.feet !== undefined) { clean.feet = patch.feet === true; }
    var res = R.store.update(function (d) {
      var t = d.locations.filter(function (l) { return l.id === id; })[0];
      t.geometry = Object.assign({}, t.geometry || {}, clean);
      t.updatedAt = new Date().toISOString();
    });
    return res.ok ? { ok: true } : fail('Enregistrement refusé : ' + (res.errors || []).join(' '));
  }

  R.ns('features').furniture = {
    ratios: RATIOS, limits: LIMITS, isFurniture: isFurniture, get: get, ordered: ordered, layout: layout,
    set: set, setGrid: setGrid, move: move, resize: resize
  };
})();
