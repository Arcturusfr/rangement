/*
  js/core/storage.js — Application « Rangement »
  Version : V007
  Horodatage : 2026-10-24 22:30 (heure de Paris)
  Résumé : clés annexes (getAux / setAux / removeAux) pour la copie de sécurité avant import et le suivi des sauvegardes ; sinon inchangé.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var KEY = R.config.storageKey;
  var memory = null;                 // repli si localStorage est indisponible
  var memoryAux = {};                // idem pour les clés annexes
  var persistent = probe();

  function probe() {
    try {
      var ls = window.localStorage;
      var test = KEY + '.probe';
      ls.setItem(test, '1');
      ls.removeItem(test);
      return true;
    } catch (err) {
      return false;
    }
  }

  // Renvoie { raw, data, error } ; error vaut null ou 'parse'.
  function load() {
    var raw = null;
    try { raw = persistent ? window.localStorage.getItem(KEY) : memory; } catch (err) { raw = null; }
    if (raw === null || raw === undefined) { return { raw: null, data: null, error: null }; }
    try {
      return { raw: raw, data: JSON.parse(raw), error: null };
    } catch (err) {
      return { raw: raw, data: null, error: 'parse' };
    }
  }

  // Renvoie { ok, error } ; error vaut 'quota' ou 'write'.
  function save(data) {
    var raw = JSON.stringify(data);
    if (!persistent) { memory = raw; return { ok: true }; }
    try {
      window.localStorage.setItem(KEY, raw);
      return { ok: true };
    } catch (err) {
      return { ok: false, error: err && err.name === 'QuotaExceededError' ? 'quota' : 'write' };
    }
  }

  // Met de côté des données illisibles avant qu'elles ne soient écrasées.
  function quarantine(raw) {
    if (!persistent || raw === null || raw === undefined) { return; }
    try { window.localStorage.setItem(KEY + '.corrupt', raw); } catch (err) { /* sans suite */ }
  }

  // Clés annexes (copie de sécurité avant import, suivi des sauvegardes) : « rangement.data.<nom> ».
  // Renvoie le texte enregistré ou null.
  function getAux(name) {
    if (!persistent) { return memoryAux[name] === undefined ? null : memoryAux[name]; }
    try { return window.localStorage.getItem(KEY + '.' + name); } catch (err) { return null; }
  }

  // Renvoie { ok, error } ; error vaut 'quota' ou 'write'.
  function setAux(name, raw) {
    if (!persistent) { memoryAux[name] = raw; return { ok: true }; }
    try {
      window.localStorage.setItem(KEY + '.' + name, raw);
      return { ok: true };
    } catch (err) {
      return { ok: false, error: err && err.name === 'QuotaExceededError' ? 'quota' : 'write' };
    }
  }

  function removeAux(name) {
    delete memoryAux[name];
    if (!persistent) { return; }
    try { window.localStorage.removeItem(KEY + '.' + name); } catch (err) { /* sans suite */ }
  }

  function clear() {
    memory = null;
    if (!persistent) { return; }
    try { window.localStorage.removeItem(KEY); } catch (err) { /* sans suite */ }
  }

  R.storage = {
    load: load,
    save: save,
    quarantine: quarantine,
    getAux: getAux,
    setAux: setAux,
    removeAux: removeAux,
    clear: clear,
    isPersistent: function () { return persistent; }
  };
})();
