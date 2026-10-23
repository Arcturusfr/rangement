/*
  js/features/locations.js — Application « Rangement »
  Version : V004
  Horodatage : 2026-10-23 11:34 (heure de Paris)
  Résumé : création — créer, modifier, déplacer et supprimer des emplacements (avec garde-fous).
*/
(function () {
  'use strict';

  var R = window.Rangement;

  function fail(error) { return { ok: false, error: error }; }

  function cleanText(value) { return typeof value === 'string' ? value.trim() : ''; }

  function now() { return new Date().toISOString(); }

  // Un frère portant déjà ce nom (sans tenir compte de la casse ni des accents) ?
  function siblingClash(parentId, name, exceptId) {
    var wanted = R.models.normalizeText(name);
    return R.store.childLocations(parentId).some(function (l) {
      return l.id !== exceptId && R.models.normalizeText(l.name) === wanted;
    });
  }

  function isInSubtree(id, rootId) {
    return R.store.pathOf(id).some(function (l) { return l.id === rootId; });
  }

  function storeFailure(res) {
    return fail('Enregistrement refusé : ' + (res.errors || []).join(' '));
  }

  // fields : { name, kind, note, parentId }
  function create(fields) {
    var f = fields || {};
    var name = cleanText(f.name);
    var parentId = f.parentId || null;
    if (!name) { return fail('Le nom est obligatoire.'); }
    if (parentId && !R.store.getLocation(parentId)) { return fail('L\u2019emplacement parent est introuvable.'); }
    if (siblingClash(parentId, name, null)) { return fail('Un emplacement portant ce nom existe déjà à cet endroit.'); }

    var loc = R.models.newLocation({ name: name, kind: f.kind, note: f.note, parentId: parentId });
    var res = R.store.update(function (d) { d.locations.push(loc); });
    return res.ok ? { ok: true, location: loc } : storeFailure(res);
  }

  // fields : { name, kind, note }
  function update(id, fields) {
    var f = fields || {};
    var loc = R.store.getLocation(id);
    if (!loc) { return fail('Cet emplacement n\u2019existe plus.'); }
    var name = cleanText(f.name);
    if (!name) { return fail('Le nom est obligatoire.'); }
    if (siblingClash(loc.parentId, name, id)) { return fail('Un emplacement portant ce nom existe déjà à cet endroit.'); }

    var res = R.store.update(function (d) {
      var target = d.locations.filter(function (l) { return l.id === id; })[0];
      target.name = name;
      target.kind = cleanText(f.kind) || 'autre';
      target.note = cleanText(f.note);
      target.updatedAt = now();
    });
    return res.ok ? { ok: true } : storeFailure(res);
  }

  // Change le parent d'un emplacement (null = racine du logement).
  function move(id, newParentId) {
    var loc = R.store.getLocation(id);
    var parentId = newParentId || null;
    if (!loc) { return fail('Cet emplacement n\u2019existe plus.'); }
    if (parentId && !R.store.getLocation(parentId)) { return fail('Le nouvel emplacement parent est introuvable.'); }
    if (parentId === id || (parentId && isInSubtree(parentId, id))) {
      return fail('Un emplacement ne peut pas être déplacé dans lui-même ni dans son propre contenu.');
    }
    if ((loc.parentId || null) === parentId) { return { ok: true, unchanged: true }; }
    if (siblingClash(parentId, loc.name, id)) { return fail('Un emplacement portant ce nom existe déjà à la destination.'); }

    var res = R.store.update(function (d) {
      var target = d.locations.filter(function (l) { return l.id === id; })[0];
      target.parentId = parentId;
      target.updatedAt = now();
    });
    return res.ok ? { ok: true } : storeFailure(res);
  }

  // Supprime un emplacement vide ; refuse s'il contient encore des emplacements ou des objets.
  function remove(id) {
    var loc = R.store.getLocation(id);
    if (!loc) { return fail('Cet emplacement n\u2019existe plus.'); }
    var n = R.store.countIn(id);
    if (n.locations || n.items) {
      return fail('« ' + loc.name + ' » n\u2019est pas vide : il ne peut pas être supprimé.');
    }
    var res = R.store.update(function (d) {
      d.locations = d.locations.filter(function (l) { return l.id !== id; });
    });
    return res.ok ? { ok: true } : storeFailure(res);
  }

  // Destinations possibles pour déplacer `id` : tout sauf lui-même et son contenu.
  // Renvoie [{ value, label }] ; value '' = racine du logement.
  function parentChoices(id) {
    var choices = R.store.locations()
      .filter(function (l) { return l.id !== id && !isInSubtree(l.id, id); })
      .map(function (l) {
        return { value: l.id, label: R.store.pathOf(l.id).map(function (p) { return p.name; }).join(' \u203a ') };
      })
      .sort(function (a, b) { return a.label.localeCompare(b.label, 'fr', { sensitivity: 'base', numeric: true }); });
    return [{ value: '', label: 'Logement (racine)' }].concat(choices);
  }

  R.ns('features').locations = {
    create: create,
    update: update,
    move: move,
    remove: remove,
    parentChoices: parentChoices
  };
})();
