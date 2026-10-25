/*
  js/ui/router.js — Application « Rangement »
  Version : V009
  Horodatage : 2026-10-25 16:10 (heure de Paris)
  Résumé : suivi de la position dans l'historique (bouton Retour de l'application), fermeture des Réglages vers la vue précédente.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var route = { locationId: null, itemId: null, query: null, settings: false };
  var lastHash = null;   // dernière adresse traitée (évite de traiter deux fois la même)
  var index = 0;         // position de l'entrée courante dans l'historique de l'application (0 = première)
  var settingsFrom = null;      // adresse d'où l'on est arrivé sur les Réglages
  var settingsIdx = -1;         // position de l'entrée « Réglages »
  var settingsPushed = false;   // l'entrée « Réglages » a été ajoutée juste après la vue précédente

  function parse(hash) {
    var none = { locationId: null, itemId: null, query: null, settings: false };
    var m = /^#\/([losr])(?:\/([^\/?#]*))?(?=[\/?#]|$)/.exec(hash || '');
    if (!m) { return none; }
    if (m[1] === 'r') { return { locationId: null, itemId: null, query: null, settings: true }; }
    var raw = m[2] || '';
    var id;
    try { id = decodeURIComponent(raw); } catch (err) { id = raw; }
    if (m[1] === 's') { return { locationId: null, itemId: null, query: id, settings: false }; }
    if (!id) { return none; }
    return m[1] === 'o'
      ? { locationId: null, itemId: id, query: null, settings: false }
      : { locationId: id, itemId: null, query: null, settings: false };
  }

  function href(locationId) {
    return locationId ? '#/l/' + encodeURIComponent(locationId) : '#/';
  }

  function itemHref(itemId) {
    return '#/o/' + encodeURIComponent(itemId);
  }

  function settingsHref() { return '#/r'; }

  function searchHref(query) {
    return '#/s/' + encodeURIComponent(query || '');
  }

  function stateIndex() {
    var s = window.history.state;
    return (s && typeof s.i === 'number') ? s.i : null;
  }

  function markEntry() {
    try { window.history.replaceState({ i: index }, ''); } catch (err) { /* sans suite */ }
  }

  // Met à jour la recherche : la première frappe ajoute une entrée d'historique,
  // les suivantes la remplacent (le bouton Retour revient à l'écran précédent).
  function search(query) {
    var h = searchHref(query);
    if (route.query !== null) {
      window.history.replaceState({ i: index }, '', h);
    } else {
      window.location.hash = h;
    }
    onHashChange();          // immédiat : l'événement « hashchange » arrive plus tard, parfois après la frappe suivante
  }

  function navigate(locationId) {
    window.location.hash = href(locationId);
  }

  function current() { return route; }

  // Adresse vers laquelle « Retour » mène quand il n'y a rien avant dans l'historique (null = nulle part).
  function fallbackHash() {
    if (route.itemId) {
      var it = R.store.getItem(route.itemId);
      return it ? href(it.locationId) : '#/';
    }
    if (route.locationId) {
      var loc = R.store.getLocation(route.locationId);
      return href(loc ? loc.parentId : null);
    }
    if (route.query !== null || route.settings) { return '#/'; }
    return null;
  }

  function canBack() { return index > 0 || fallbackHash() !== null; }

  // Bouton Retour de l'application : entrée précédente de l'historique, sinon niveau supérieur.
  function back() {
    if (index > 0) { window.history.back(); return true; }
    var f = fallbackHash();
    if (f) { window.location.hash = f; return true; }
    return false;
  }

  // Ferme les Réglages et revient à la vue d'où l'on venait.
  function closeSettings() {
    if (!route.settings) { return; }
    if (settingsPushed && index === settingsIdx && index > 0) { window.history.back(); return; }
    window.location.hash = (settingsFrom && settingsFrom.indexOf('#/r') !== 0) ? settingsFrom : '#/';
  }

  function onHashChange() {
    if (window.location.hash === lastHash) { return; }
    var previousHash = lastHash;
    var previousRoute = route;
    lastHash = window.location.hash;
    var si = stateIndex();
    var pushed = false;
    if (si === null) { index += 1; pushed = true; markEntry(); } else { index = si; }
    route = parse(window.location.hash);
    if (route.settings && !previousRoute.settings) {
      settingsFrom = previousHash || '#/';
      settingsIdx = index;
      settingsPushed = pushed;
    }
    R.events.emit('route:changed', route);
  }

  function init() {
    lastHash = window.location.hash;
    var si = stateIndex();
    if (si === null) { index = 0; markEntry(); } else { index = si; }
    route = parse(window.location.hash);
    if (route.settings) { settingsFrom = '#/'; settingsIdx = index; settingsPushed = false; }
    window.addEventListener('hashchange', onHashChange);
  }

  R.ns('ui').router = {
    init: init, href: href, itemHref: itemHref, searchHref: searchHref, settingsHref: settingsHref,
    navigate: navigate, search: search, current: current,
    canBack: canBack, back: back, closeSettings: closeSettings
  };
})();
