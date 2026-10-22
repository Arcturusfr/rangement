/*
  js/ui/router.js — Application « Rangement »
  Version : V003
  Horodatage : 2026-10-22 21:39 (heure de Paris)
  Résumé : création — navigation par hash (#/ et #/l/<id>).
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var route = { locationId: null };

  function parse(hash) {
    var m = /^#\/l\/([^\/?#]+)/.exec(hash || '');
    return { locationId: m ? decodeURIComponent(m[1]) : null };
  }

  function href(locationId) {
    return locationId ? '#/l/' + encodeURIComponent(locationId) : '#/';
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

  R.ns('ui').router = { init: init, href: href, navigate: navigate, current: current };
})();
