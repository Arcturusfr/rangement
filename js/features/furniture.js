/*
  js/features/furniture.js — Application « Rangement »
  Version : V010
  Horodatage : 2026-10-26 15:33 (heure de Paris)
  Résumé : création — géométrie d'un meuble (proportions, pieds, colonnes) et ordre / largeur des sous-emplacements, stockés dans `geometry`.
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

  function fail(error) { return { ok: false, error: error }; }

  // Un meuble = emplacement de premier niveau (directement dans une pièce).
  function isFurniture(id) { return !!R.store.getLocation(id) && R.store.depthOf(id) === 1; }

  // Réglages d'un emplacement dessiné : { ratio, feet, cols } (cols 0 = automatique).
  function get(id) {
    var l = R.store.getLocation(id);
    var g = (l && l.geometry && typeof l.geometry === 'object') ? l.geometry : {};
    return {
      ratio: (typeof g.ratio === 'number' && g.ratio >= 0.3 && g.ratio <= 4) ? g.ratio : DEFAULT_RATIO,
      feet: g.feet === true,
      cols: [1, 2, 3, 4].indexOf(g.cols) !== -1 ? g.cols : 0
    };
  }

  function posOf(l) { return (l.geometry && typeof l.geometry.pos === 'number') ? l.geometry.pos : Infinity; }

  // Sous-emplacements dans l'ordre d'affichage : ordre choisi à la main, sinon ordre alphabétique.
  function ordered(parentId) {
    return R.store.childLocations(parentId).map(function (l, i) { return { l: l, i: i }; })
      .sort(function (a, b) {
        var pa = posOf(a.l), pb = posOf(b.l);
        return pa === pb ? a.i - b.i : (pa < pb ? -1 : 1);
      }).map(function (x) { return x.l; });
  }

  // Largeur d'un sous-emplacement : 1 ou 2 colonnes.
  function span(l) { return l.geometry && l.geometry.span === 2 ? 2 : 1; }

  // Nombre de colonnes de la grille pour `n` sous-emplacements.
  function columns(id, n) {
    var c = get(id).cols;
    if (c) { return Math.max(1, Math.min(c, n)); }
    return n <= 3 ? 1 : (n <= 8 ? 2 : 3);
  }

  function failure(res) { return fail('Enregistrement refusé : ' + (res.errors || []).join(' ')); }

  // patch : { ratio?, feet?, cols?, span?, pos? }
  function set(id, patch) {
    if (!R.store.getLocation(id)) { return fail('Cet emplacement n\u2019existe plus.'); }
    var res = R.store.update(function (d) {
      var t = d.locations.filter(function (l) { return l.id === id; })[0];
      t.geometry = Object.assign({}, t.geometry || {}, patch);
      t.updatedAt = new Date().toISOString();
    });
    return res.ok ? { ok: true } : failure(res);
  }

  // Décale un sous-emplacement d'un cran (dir = -1 vers le début, +1 vers la fin) parmi ses frères.
  function shift(id, dir) {
    var l = R.store.getLocation(id);
    if (!l) { return fail('Cet emplacement n\u2019existe plus.'); }
    var ids = ordered(l.parentId).map(function (x) { return x.id; });
    var i = ids.indexOf(id);
    var j = i + dir;
    if (i < 0 || j < 0 || j >= ids.length) { return { ok: true, unchanged: true }; }
    ids[i] = ids[j];
    ids[j] = id;
    var res = R.store.update(function (d) {
      ids.forEach(function (k, pos) {
        var t = d.locations.filter(function (x) { return x.id === k; })[0];
        t.geometry = Object.assign({}, t.geometry || {}, { pos: pos });
      });
    });
    return res.ok ? { ok: true } : failure(res);
  }

  function toggleSpan(id) {
    var l = R.store.getLocation(id);
    return l ? set(id, { span: span(l) === 2 ? 1 : 2 }) : fail('Cet emplacement n\u2019existe plus.');
  }

  R.ns('features').furniture = {
    ratios: RATIOS, isFurniture: isFurniture, get: get, set: set, ordered: ordered,
    span: span, columns: columns, shift: shift, toggleSpan: toggleSpan
  };
})();
