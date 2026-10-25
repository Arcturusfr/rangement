/*
  js/features/backup.js — Application « Rangement »
  Version : V009
  Horodatage : 2026-10-25 16:10 (heure de Paris)
  Résumé : ajout de needsBackup() (pastille « modifications non sauvegardées ») ; sinon inchangé.
*/
(function () {
  'use strict';

  var R = window.Rangement;

  var META = 'meta';             // { lastExportAt, dirty }
  var PREIMPORT = 'preimport';   // { savedAt, data } : données d'avant la dernière importation
  var MAX_CHARS = 4500000;       // au-delà, le localStorage (≈ 5 Mo) ne suivrait pas

  var meta = { lastExportAt: null, dirty: false };

  function fail(error) { return { ok: false, error: error }; }

  function pad(n) { return (n < 10 ? '0' : '') + n; }

  function counts(data) { return { locations: data.locations.length, items: data.items.length }; }

  // Copie des données courantes sous forme d'enveloppe complète.
  function snapshot() {
    return JSON.parse(JSON.stringify({
      schemaVersion: R.config.schemaVersion,
      appVersion: R.config.version,
      locations: R.store.locations(),
      items: R.store.items()
    }));
  }

  // ---------- suivi de la dernière sauvegarde ----------

  function saveMeta() { R.storage.setAux(META, JSON.stringify(meta)); }

  function loadMeta() {
    var raw = R.storage.getAux(META);
    if (!raw) { return; }
    try {
      var m = JSON.parse(raw);
      meta = {
        lastExportAt: typeof m.lastExportAt === 'string' ? m.lastExportAt : null,
        dirty: m.dirty === true
      };
    } catch (err) { /* suivi illisible : on repart de zéro */ }
  }

  // À appeler après store.init().
  function init() {
    loadMeta();
    R.events.on('store:changed', function () {
      if (!meta.dirty) { meta.dirty = true; saveMeta(); }
    });
  }

  // Renvoie { lastExportAt: ISO | null, dirty: boolean, counts }.
  function status() {
    return {
      lastExportAt: meta.lastExportAt,
      dirty: meta.dirty,
      counts: { locations: R.store.locations().length, items: R.store.items().length }
    };
  }

  // Vrai s'il y a des données qui ne figurent dans aucune sauvegarde exportée (jamais exportées, ou modifiées depuis).
  function needsBackup() {
    var has = R.store.locations().length > 0 || R.store.items().length > 0;
    return has && (meta.dirty || !meta.lastExportAt);
  }

  // ---------- export ----------

  // Nom de fichier horodaté (heure de l'appareil) : rangement-2026-10-24-2230.json
  function fileName(date) {
    var d = date || new Date();
    return 'rangement-' + d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) +
      '-' + pad(d.getHours()) + pad(d.getMinutes()) + '.json';
  }

  // Prépare le contenu à télécharger. Renvoie { filename, text, counts }.
  function prepareExport() {
    var data = snapshot();
    data.exportedAt = new Date().toISOString();
    return { filename: fileName(new Date()), text: JSON.stringify(data, null, 2), counts: counts(data) };
  }

  // À appeler une fois le téléchargement déclenché.
  function markExported() {
    meta = { lastExportAt: new Date().toISOString(), dirty: false };
    saveMeta();
    R.events.emit('backup:changed', {});
  }

  // ---------- import ----------

  function str(value) { return typeof value === 'string' ? value : ''; }

  // Ne conserve que les champs connus, avec des types sûrs (un fichier peut avoir été modifié à la main).
  function cleanLocation(l) {
    if (!l || typeof l !== 'object') { return l; }
    return {
      id: l.id,
      parentId: (l.parentId === undefined || l.parentId === '') ? null : l.parentId,
      name: l.name,
      kind: str(l.kind).trim() || 'autre',
      note: str(l.note),
      geometry: (l.geometry && typeof l.geometry === 'object') ? l.geometry : null,
      createdAt: str(l.createdAt) || new Date().toISOString(),
      updatedAt: str(l.updatedAt) || str(l.createdAt) || new Date().toISOString()
    };
  }

  function cleanItem(it) {
    if (!it || typeof it !== 'object') { return it; }
    return {
      id: it.id,
      locationId: it.locationId,
      name: it.name,
      quantity: it.quantity,
      tags: Array.isArray(it.tags) ? it.tags.filter(function (t) { return typeof t === 'string'; }) : it.tags,
      note: str(it.note),
      createdAt: str(it.createdAt) || new Date().toISOString(),
      updatedAt: str(it.updatedAt) || str(it.createdAt) || new Date().toISOString()
    };
  }

  // Analyse le contenu d'un fichier de sauvegarde.
  // Renvoie { ok, data, counts, exportedAt } ou { ok: false, error } (message en français).
  function parse(text) {
    if (typeof text !== 'string' || !text.trim()) { return fail('Ce fichier est vide.'); }
    if (text.length > MAX_CHARS) { return fail('Ce fichier est trop volumineux pour être importé.'); }
    var raw;
    try {
      raw = JSON.parse(text.charCodeAt(0) === 0xFEFF ? text.slice(1) : text);
    } catch (err) {
      return fail('Ce fichier n\u2019est pas un fichier JSON valide.');
    }
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
      return fail('Ce fichier n\u2019est pas une sauvegarde de Rangement.');
    }
    if (raw.schemaVersion !== R.config.schemaVersion) {
      return fail('Ce fichier utilise un format de données différent (version ' +
        (raw.schemaVersion === undefined ? 'inconnue' : String(raw.schemaVersion)) +
        ') : il ne peut pas être importé par cette version de l\u2019application.');
    }
    if (!Array.isArray(raw.locations) || !Array.isArray(raw.items)) {
      return fail('Ce fichier n\u2019est pas une sauvegarde de Rangement (listes « locations » et « items » absentes).');
    }

    var data = {
      schemaVersion: R.config.schemaVersion,
      appVersion: R.config.version,
      locations: raw.locations.map(cleanLocation),
      items: raw.items.map(cleanItem)
    };
    var check = R.models.validateData(data);
    if (!check.ok) {
      var shown = check.errors.slice(0, 3).join(' ');
      var more = check.errors.length > 3 ? ' (et ' + (check.errors.length - 3) + ' autre(s) problème(s))' : '';
      return fail('Ce fichier contient des données incohérentes : ' + shown + more);
    }
    return {
      ok: true,
      data: data,
      counts: counts(data),
      exportedAt: typeof raw.exportedAt === 'string' ? raw.exportedAt : null
    };
  }

  // Remplace toutes les données par `data` (résultat de parse). Une copie des données actuelles est
  // d'abord mise de côté ; si elle ne peut pas l'être, rien n'est modifié.
  function importData(data) {
    var saved = R.storage.setAux(PREIMPORT, JSON.stringify({ savedAt: new Date().toISOString(), data: snapshot() }));
    if (!saved.ok) {
      return fail('Importation annulée : la copie de sécurité de vos données actuelles n\u2019a pas pu être conservée (espace de stockage insuffisant).');
    }
    var res = R.store.replaceAll(data);
    if (!res.ok) {
      R.storage.removeAux(PREIMPORT);
      return fail('Importation refusée : ' + (res.errors || []).join(' '));
    }
    R.events.emit('backup:changed', {});
    return { ok: true, counts: counts(data) };
  }

  // ---------- annulation de la dernière importation ----------

  function readPreimport() {
    var raw = R.storage.getAux(PREIMPORT);
    if (!raw) { return null; }
    try {
      var p = JSON.parse(raw);
      return (p && p.data && R.models.validateData(p.data).ok) ? p : null;
    } catch (err) { return null; }
  }

  // Renvoie { savedAt, counts } si une copie de sécurité est disponible, sinon null.
  function undoInfo() {
    var p = readPreimport();
    return p ? { savedAt: p.savedAt, counts: counts(p.data) } : null;
  }

  function undoImport() {
    var p = readPreimport();
    if (!p) { return fail('Aucune copie de sécurité à restaurer.'); }
    var res = R.store.replaceAll(p.data);
    if (!res.ok) { return fail('Restauration refusée : ' + (res.errors || []).join(' ')); }
    R.storage.removeAux(PREIMPORT);
    R.events.emit('backup:changed', {});
    return { ok: true, counts: counts(p.data) };
  }

  R.ns('features').backup = {
    init: init,
    status: status,
    needsBackup: needsBackup,
    fileName: fileName,
    prepareExport: prepareExport,
    markExported: markExported,
    parse: parse,
    importData: importData,
    undoInfo: undoInfo,
    undoImport: undoImport
  };
})();
