/*
  js/ui/router.js — Application « Rangement »
  Version : V006
  Horodatage : 2026-10-24 13:10 (heure de Paris)
  Résumé : route de recherche (#/s/<texte>) ; current() renvoie aussi { query }.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var route = { locationId: null, itemId: null, query: null };
  var lastHash = null;   // dernière adresse traitée (évite de traiter deux fois la même)

  function parse(hash) {
    var none = { locationId: null, itemId: null, query: null };
    var m = /^#\/([los])(?:\/([^\/?#]*))?(?=[\/?#]|$)/.exec(hash || '');
    if (!m) { return none; }
    var raw = m[2] || '';
    var id;
    try { id = decodeURIComponent(raw); } catch (err) { id = raw; }
    if (m[1] === 's') { return { locationId: null, itemId: null, query: id }; }
    if (!id) { return none; }
    return m[1] === 'o'
      ? { locationId: null, itemId: id, query: null }
      : { locationId: id, itemId: null, query: null };
  }

  function href(locationId) {
    return locationId ? '#/l/' + encodeURIComponent(locationId) : '#/';
  }

  function itemHref(itemId) {
    return '#/o/' + encodeURIComponent(itemId);
  }

  function searchHref(query) {
    return '#/s/' + encodeURIComponent(query || '');
  }

  // Met à jour la recherche : la première frappe ajoute une entrée d'historique,
  // les suivantes la remplacent (le bouton Retour revient à l'écran précédent).
  function search(query) {
    var h = searchHref(query);
    if (route.query !== null) {
      window.history.replaceState(null, '', h);
    } else {
      window.location.hash = h;
    }
    onHashChange();          // immédiat : l'événement « hashchange » arrive plus tard, parfois après la frappe suivante
  }

  function navigate(locationId) {
    window.location.hash = href(locationId);
  }

  function current() { return route; }

  function onHashChange() {
    if (window.location.hash === lastHash) { return; }
    lastHash = window.location.hash;
    route = parse(window.location.hash);
    R.events.emit('route:changed', route);
  }

  function init() {
    lastHash = window.location.hash;
    route = parse(window.location.hash);
    window.addEventListener('hashchange', onHashChange);
  }

  R.ns('ui').router = {
    init: init, href: href, itemHref: itemHref, searchHref: searchHref,
    navigate: navigate, search: search, current: current
  };
})();
