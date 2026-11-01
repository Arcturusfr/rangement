/*
  js/core/models.js — Application « Rangement »
  Version : V013
  Horodatage : 2026-11-01 12:00 (heure de Paris)
  Résumé : cleanPlan (plan du logement : colonnes et lignes de la grille).
*/
(function () {
  'use strict';

  var R = window.Rangement;

  function nowIso() { return new Date().toISOString(); }

  function text(value) { return typeof value === 'string' ? value.trim() : ''; }

  // Minuscules, sans accents, espaces rognés : sert aux comparaisons de noms et à la recherche.
  function normalizeText(value) {
    var t = typeof value === 'string' ? value : '';
    if (t.normalize) { t = t.normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
    return t.toLowerCase().trim();
  }

  // Niveau d'un emplacement selon sa profondeur : sert au code couleur (0 = pièce, 1 = emplacement de premier ordre, 2+ = sous-emplacement).
  function levelOf(depth) {
    return depth <= 0 ? 'piece' : (depth === 1 ? 'emplacement' : 'sous');
  }

  // Libellé de la racine : « Logement » + précision éventuelle (R.config.dwellingName).
  function rootLabel() {
    var n = R.config.dwellingName;
    return 'Logement' + (n ? ' \u2014 ' + n : '');
  }

  function kindLabel(kind) {
    var found = R.config.kinds.filter(function (k) { return k.id === kind; })[0];
    return found ? found.label : (kind || '');
  }

  function newLocation(fields) {
    var f = fields || {};
    var now = nowIso();
    return {
      id: R.ids.generate('loc'),
      parentId: f.parentId || null,
      name: text(f.name),
      kind: text(f.kind) || 'autre',
      note: text(f.note),
      geometry: null,           // réservé au futur plan SVG
      createdAt: now,
      updatedAt: now
    };
  }

  function cleanTags(tags) {
    var seen = {};
    return (Array.isArray(tags) ? tags : []).map(text).filter(function (t) {
      if (!t || seen[t.toLowerCase()]) { return false; }
      seen[t.toLowerCase()] = true;
      return true;
    });
  }

  function newItem(fields) {
    var f = fields || {};
    var now = nowIso();
    var given = f.quantity !== undefined && f.quantity !== null && f.quantity !== '';
    var q = Number(f.quantity);
    return {
      id: R.ids.generate('itm'),
      locationId: f.locationId,
      name: text(f.name),
      quantity: (given && isFinite(q) && q >= 0) ? q : 1,
      tags: cleanTags(f.tags),
      note: text(f.note),
      createdAt: now,
      updatedAt: now
    };
  }

  // Plan du logement : { cols, rows } (entiers positifs) ou null. Tout le reste est ignoré.
  function cleanPlan(plan) {
    if (!plan || typeof plan !== 'object' || Array.isArray(plan)) { return null; }
    function n(v, max) { return (typeof v === 'number' && v === Math.floor(v) && v >= 1 && v <= max) ? v : null; }
    var cols = n(plan.cols, 40), rows = n(plan.rows, 60);
    return (cols || rows) ? { cols: cols || 0, rows: rows || 0 } : null;
  }

  function emptyData() {
    return { schemaVersion: R.config.schemaVersion, appVersion: R.config.version, locations: [], items: [] };
  }

  // Vérifie la cohérence d'un jeu de données complet. Renvoie { ok, errors[] }.
  function validateData(data) {
    var errors = [];
    if (!data || typeof data !== 'object' || Array.isArray(data)) {
      return { ok: false, errors: ['Les données ne sont pas un objet.'] };
    }
    if (data.schemaVersion !== R.config.schemaVersion) {
      errors.push('Version de format non prise en charge : ' + data.schemaVersion + '.');
    }
    if (!Array.isArray(data.locations) || !Array.isArray(data.items)) {
      errors.push('Les listes « locations » et « items » sont obligatoires.');
      return { ok: false, errors: errors };
    }

    var locIds = {};
    data.locations.forEach(function (l) {
      if (!l || typeof l.id !== 'string' || !l.id) { errors.push('Emplacement sans identifiant.'); return; }
      if (locIds[l.id]) { errors.push('Identifiant d\u2019emplacement en double : ' + l.id + '.'); }
      locIds[l.id] = l;
      if (typeof l.name !== 'string' || !l.name.trim()) { errors.push('Emplacement sans nom : ' + l.id + '.'); }
    });

    data.locations.forEach(function (l) {
      if (!l || !l.id) { return; }
      if (l.parentId !== null && l.parentId !== undefined && !locIds[l.parentId]) {
        errors.push('Parent introuvable pour l\u2019emplacement « ' + l.name + ' ».');
      }
    });

    data.locations.forEach(function (l) {
      if (!l || !l.id) { return; }
      var seen = {};
      var cur = l;
      while (cur && cur.parentId) {
        if (seen[cur.id]) { errors.push('Boucle dans l\u2019arborescence autour de « ' + l.name + ' ».'); return; }
        seen[cur.id] = true;
        cur = locIds[cur.parentId];
      }
    });

    var itemIds = {};
    data.items.forEach(function (it) {
      if (!it || typeof it.id !== 'string' || !it.id) { errors.push('Objet sans identifiant.'); return; }
      if (itemIds[it.id]) { errors.push('Identifiant d\u2019objet en double : ' + it.id + '.'); }
      itemIds[it.id] = true;
      if (typeof it.name !== 'string' || !it.name.trim()) { errors.push('Objet sans nom : ' + it.id + '.'); }
      if (!locIds[it.locationId]) { errors.push('Emplacement introuvable pour l\u2019objet « ' + it.name + ' ».'); }
      if (typeof it.quantity !== 'number' || !isFinite(it.quantity) || it.quantity < 0) {
        errors.push('Quantité invalide pour l\u2019objet « ' + it.name + ' ».');
      }
      if (!Array.isArray(it.tags)) { errors.push('Mots-clés invalides pour l\u2019objet « ' + it.name + ' ».'); }
    });

    return { ok: errors.length === 0, errors: errors };
  }

  R.models = {
    newLocation: newLocation,
    newItem: newItem,
    emptyData: emptyData,
    cleanPlan: cleanPlan,
    validateData: validateData,
    normalizeText: normalizeText,
    kindLabel: kindLabel,
    levelOf: levelOf,
    rootLabel: rootLabel
  };
})();
