/*
  js/core/store.js — Application « Rangement »
  Version : V013
  Horodatage : 2026-11-01 12:00 (heure de Paris)
  Résumé : plan du logement (state.plan, plan()) conservé, sauvegardé et remplacé avec les données.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var state = { locations: [], items: [], plan: null };
  var byId = {};          // id → emplacement
  var childrenOf = {};    // parentId ('' = racine) → emplacements triés
  var itemsOf = {};       // locationId → objets triés
  var itemById = {};      // id → objet
  var notices = [];       // messages à afficher après le démarrage

  function byName(a, b) {
    return a.name.localeCompare(b.name, 'fr', { sensitivity: 'base', numeric: true });
  }

  function clone(value) { return JSON.parse(JSON.stringify(value)); }

  function envelope(s) {
    var env = {
      schemaVersion: R.config.schemaVersion,
      appVersion: R.config.version,
      locations: s.locations,
      items: s.items
    };
    if (s.plan) { env.plan = s.plan; }
    return env;
  }

  function reindex() {
    byId = {};
    childrenOf = {};
    itemsOf = {};
    itemById = {};
    state.locations.forEach(function (l) {
      byId[l.id] = l;
      var key = l.parentId || '';
      (childrenOf[key] = childrenOf[key] || []).push(l);
    });
    state.items.forEach(function (it) {
      itemById[it.id] = it;
      (itemsOf[it.locationId] = itemsOf[it.locationId] || []).push(it);
    });
    Object.keys(childrenOf).forEach(function (k) { childrenOf[k].sort(byName); });
    Object.keys(itemsOf).forEach(function (k) { itemsOf[k].sort(byName); });
  }

  // Charge les données persistantes ; en cas de problème, démarre à vide
  // sans perdre les données illisibles (copie de sauvegarde).
  function init() {
    notices = [];
    var res = R.storage.load();

    if (!R.storage.isPersistent()) {
      notices.push('Le stockage du navigateur est indisponible : les données ne seront pas conservées après fermeture.');
    }

    if (res.error) {
      R.storage.quarantine(res.raw);
      notices.push('Les données enregistrées étaient illisibles. Une copie a été mise de côté et l\u2019application démarre à vide.');
    } else if (res.data) {
      var check = R.models.validateData(res.data);
      if (check.ok) {
        state = { locations: res.data.locations, items: res.data.items, plan: R.models.cleanPlan(res.data.plan) };
      } else {
        R.storage.quarantine(res.raw);
        notices.push('Les données enregistrées sont incohérentes. Une copie a été mise de côté et l\u2019application démarre à vide.');
      }
    }

    reindex();
    R.events.emit('store:ready', {});
  }

  function persist() {
    var res = R.storage.save(envelope(state));
    if (!res.ok) {
      var msg = res.error === 'quota'
        ? 'Enregistrement impossible : espace de stockage plein.'
        : 'Enregistrement impossible : les dernières modifications ne sont pas sauvegardées.';
      R.events.emit('store:error', { message: msg });
    }
  }

  // Applique `fn` à une copie des données ; la copie n'est adoptée que si elle
  // reste cohérente. Renvoie { ok, errors? }.
  function update(fn) {
    var draft = clone(state);
    fn(draft);
    var check = R.models.validateData(envelope(draft));
    if (!check.ok) { return { ok: false, errors: check.errors }; }
    state = draft;
    reindex();
    persist();
    R.events.emit('store:changed', {});
    return { ok: true };
  }

  // Remplace tout le contenu (import, données de démonstration).
  function replaceAll(data) {
    var check = R.models.validateData(data);
    if (!check.ok) { return { ok: false, errors: check.errors }; }
    return update(function (d) {
      d.locations = clone(data.locations);
      d.items = clone(data.items);
      d.plan = R.models.cleanPlan(data.plan);
    });
  }

  // Lecture
  function getLocation(id) { return byId[id] || null; }
  function getItem(id) { return itemById[id] || null; }
  function locations() { return state.locations; }
  function items() { return state.items; }
  // Plan du logement : { cols, rows } ou null (0 = automatique).
  function plan() { return state.plan; }
  function childLocations(parentId) { return childrenOf[parentId || ''] || []; }
  function itemsIn(locationId) { return itemsOf[locationId] || []; }

  // Chemin de la racine jusqu'à l'emplacement inclus.
  function pathOf(id) {
    var path = [];
    var cur = byId[id];
    var guard = 0;
    while (cur && guard < 100) {
      path.unshift(cur);
      cur = cur.parentId ? byId[cur.parentId] : null;
      guard += 1;
    }
    return path;
  }

  // Profondeur d'un emplacement (0 = pièce à la racine).
  function depthOf(id) { return Math.max(0, pathOf(id).length - 1); }

  // Nombre d'emplacements et d'objets contenus (à tous les niveaux).
  function countIn(id) {
    var total = { locations: 0, items: itemsIn(id).length };
    childLocations(id).forEach(function (child) {
      var sub = countIn(child.id);
      total.locations += 1 + sub.locations;
      total.items += sub.items;
    });
    return total;
  }

  R.store = {
    init: init,
    update: update,
    replaceAll: replaceAll,
    locations: locations,
    items: items,
    plan: plan,
    getLocation: getLocation,
    getItem: getItem,
    childLocations: childLocations,
    itemsIn: itemsIn,
    pathOf: pathOf,
    depthOf: depthOf,
    countIn: countIn,
    notices: function () { return notices.slice(); }
  };
})();
