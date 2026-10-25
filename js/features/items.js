/*
  js/features/items.js — Application « Rangement »
  Version : V009
  Horodatage : 2026-10-25 16:10 (heure de Paris)
  Résumé : duplicate(id, { name, locationId }) ; quantityError(raw) pour la validation de saisie.
*/
(function () {
  'use strict';

  var R = window.Rangement;

  var QUANTITY_ERROR = 'La quantité doit être un nombre entier positif ou nul (par exemple 3, ou 0 si l\u2019objet est épuisé).';
  var CLASH_ERROR = 'Un objet portant ce nom existe déjà dans cet emplacement. Utilisez la quantité, ou numérotez-les (par exemple \u00ab sac à dos 1 \u00bb et \u00ab sac à dos 2 \u00bb).';
  var CLASH_MOVE_ERROR = 'Un objet portant ce nom existe déjà dans l\u2019emplacement de destination.';

  function fail(error) { return { ok: false, error: error }; }

  function cleanText(value) { return typeof value === 'string' ? value.trim() : ''; }

  function now() { return new Date().toISOString(); }

  // Un objet de même nom (casse et accents ignorés) dans cet emplacement ?
  function nameClash(locationId, name, exceptId) {
    var wanted = R.models.normalizeText(name);
    return R.store.itemsIn(locationId).some(function (it) {
      return it.id !== exceptId && R.models.normalizeText(it.name) === wanted;
    });
  }

  // Quantité saisie : vide = 1 ; nombre entier uniquement (0 accepté). Renvoie { ok, value? }.
  function parseQuantity(raw) {
    if (typeof raw === 'number') {
      return (isFinite(raw) && raw >= 0 && Math.floor(raw) === raw) ? { ok: true, value: raw } : { ok: false };
    }
    var t = typeof raw === 'string' ? raw.trim() : '';
    if (t === '') { return { ok: true, value: 1 }; }
    if (!/^\d+$/.test(t)) { return { ok: false }; }
    var q = Number(t);
    if (!isFinite(q) || q > 1000000) { return { ok: false }; }
    return { ok: true, value: q };
  }

  // Mots-clés : texte séparé par des virgules (ou tableau). Doublons ignorés (casse et accents).
  function parseTags(raw) {
    var list = Array.isArray(raw) ? raw : (typeof raw === 'string' ? raw.split(',') : []);
    var seen = {};
    var out = [];
    list.forEach(function (t) {
      var tag = cleanText(t);
      var key = R.models.normalizeText(tag);
      if (!tag || seen[key]) { return; }
      seen[key] = true;
      out.push(tag);
    });
    return out;
  }

  // Les anciennes quantités décimales éventuelles s'affichent avec une virgule (2,5).
  function formatQuantity(q) { return String(q).replace('.', ','); }

  // fields : { name, quantity, tags, note, locationId }
  function create(fields) {
    var f = fields || {};
    var name = cleanText(f.name);
    if (!name) { return fail('Le nom est obligatoire.'); }
    if (!f.locationId || !R.store.getLocation(f.locationId)) { return fail('L\u2019emplacement est introuvable.'); }
    var q = parseQuantity(f.quantity);
    if (!q.ok) { return fail(QUANTITY_ERROR); }
    if (nameClash(f.locationId, name, null)) { return fail(CLASH_ERROR); }

    var item = R.models.newItem({
      name: name,
      locationId: f.locationId,
      quantity: q.value,
      tags: parseTags(f.tags),
      note: f.note
    });
    var res = R.store.update(function (d) { d.items.push(item); });
    return res.ok ? { ok: true, item: item } : fail('Enregistrement refusé : ' + (res.errors || []).join(' '));
  }

  // fields : { name, quantity, tags, note } — un champ absent (undefined) reste inchangé.
  function update(id, fields) {
    var f = fields || {};
    var item = R.store.getItem(id);
    if (!item) { return fail('Cet objet n\u2019existe plus.'); }

    var name = f.name !== undefined ? cleanText(f.name) : item.name;
    if (!name) { return fail('Le nom est obligatoire.'); }
    if (nameClash(item.locationId, name, id)) { return fail(CLASH_ERROR); }

    var quantity = item.quantity;
    if (f.quantity !== undefined) {
      var q = parseQuantity(f.quantity);
      if (!q.ok) { return fail(QUANTITY_ERROR); }
      quantity = q.value;
    }
    var tags = f.tags !== undefined ? parseTags(f.tags) : item.tags.slice();
    var note = f.note !== undefined ? cleanText(f.note) : item.note;

    var res = R.store.update(function (d) {
      var target = d.items.filter(function (it) { return it.id === id; })[0];
      target.name = name;
      target.quantity = quantity;
      target.tags = tags;
      target.note = note;
      target.updatedAt = now();
    });
    return res.ok ? { ok: true } : fail('Enregistrement refusé : ' + (res.errors || []).join(' '));
  }

  // Range l'objet dans un autre emplacement.
  function move(id, locationId) {
    var item = R.store.getItem(id);
    if (!item) { return fail('Cet objet n\u2019existe plus.'); }
    if (!locationId || !R.store.getLocation(locationId)) { return fail('Le nouvel emplacement est introuvable.'); }
    if (item.locationId === locationId) { return { ok: true, unchanged: true }; }
    if (nameClash(locationId, item.name, id)) { return fail(CLASH_MOVE_ERROR); }

    var res = R.store.update(function (d) {
      var target = d.items.filter(function (it) { return it.id === id; })[0];
      target.locationId = locationId;
      target.updatedAt = now();
    });
    return res.ok ? { ok: true } : fail('Enregistrement refusé : ' + (res.errors || []).join(' '));
  }

  function remove(id) {
    if (!R.store.getItem(id)) { return fail('Cet objet n\u2019existe plus.'); }
    var res = R.store.update(function (d) {
      d.items = d.items.filter(function (it) { return it.id !== id; });
    });
    return res.ok ? { ok: true } : fail('Enregistrement refusé : ' + (res.errors || []).join(' '));
  }

  var DUP_CLASH = 'Modifiez le nom ou choisissez un autre emplacement : un objet portant ce nom existe déjà dans cet emplacement.';

  // Duplique un objet (quantité, mots-clés et note repris). fields : { name, locationId }
  function duplicate(id, fields) {
    var f = fields || {};
    var src = R.store.getItem(id);
    if (!src) { return fail('Cet objet n\u2019existe plus.'); }
    var name = cleanText(f.name);
    if (!name) { return fail('Le nom est obligatoire.'); }
    if (!f.locationId || !R.store.getLocation(f.locationId)) { return fail('L\u2019emplacement est introuvable.'); }
    if (nameClash(f.locationId, name, null)) { return fail(DUP_CLASH); }
    var item = R.models.newItem({ name: name, locationId: f.locationId, quantity: src.quantity, tags: src.tags, note: src.note });
    var res = R.store.update(function (d) { d.items.push(item); });
    return res.ok ? { ok: true, item: item } : fail('Enregistrement refusé : ' + (res.errors || []).join(' '));
  }

  // Message d'erreur si la quantité saisie est interdite, sinon null (sert à la validation champ par champ).
  function quantityError(raw) { return parseQuantity(raw).ok ? null : QUANTITY_ERROR; }

  // Emplacements où ranger un objet : tous, avec leur chemin complet. Renvoie [{ value, label }].
  function locationChoices() {
    return R.store.locations()
      .map(function (l) {
        return { value: l.id, label: R.store.pathOf(l.id).map(function (p) { return p.name; }).join(' \u203a ') };
      })
      .sort(function (a, b) { return a.label.localeCompare(b.label, 'fr', { sensitivity: 'base', numeric: true }); });
  }

  R.ns('features').items = {
    create: create,
    update: update,
    move: move,
    duplicate: duplicate,
    quantityError: quantityError,
    remove: remove,
    locationChoices: locationChoices,
    parseQuantity: parseQuantity,
    parseTags: parseTags,
    formatQuantity: formatQuantity
  };
})();
