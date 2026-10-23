/*
  js/ui/router.js — Application « Rangement »
  Version : V005
  Horodatage : 2026-10-23 23:50 (heure de Paris)
  Résumé : ajout de la route d'un objet (#/o/<id>) ; current() renvoie { locationId, itemId }.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var route = { locationId: null, itemId: null };

  function parse(hash) {
    var m = /^#\/([lo])\/([^\/?#]+)/.exec(hash || '');
    if (!m) { return { locationId: null, itemId: null }; }
    var id = decodeURIComponent(m[2]);
    return m[1] === 'o' ? { locationId: null, itemId: id } : { locationId: id, itemId: null };
  }

  function href(locationId) {
    return locationId ? '#/l/' + encodeURIComponent(locationId) : '#/';
  }

  function itemHref(itemId) {
    return '#/o/' + encodeURIComponent(itemId);
  }

  function navigate(locationId) {
    window.location.hash = href(locationId);
  }

  function current() { return route; }

  function onHashChange() {
    route = parse(window.location.hash);
    R.events.emit('route:changed', route);
  }

  function init() {
    route = parse(window.location.hash);
    window.addEventListener('hashchange', onHashChange);
  }

  R.ns('ui').router = { init: init, href: href, itemHref: itemHref, navigate: navigate, current: current };
})();
