/*
  js/ui/components/breadcrumb.js — Application « Rangement »
  Version : V003
  Horodatage : 2026-10-22 21:39 (heure de Paris)
  Résumé : création — fil d'Ariane (Logement › Pièce › Meuble › Tiroir).
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;

  // `path` : emplacements de la racine jusqu'à l'emplacement courant (inclus).
  function create(path) {
    var crumbs = [];
    var atRoot = path.length === 0;

    crumbs.push(el('li', null, [
      atRoot
        ? el('span', { 'aria-current': 'page' }, ['Logement'])
        : el('a', { href: R.ui.router.href(null) }, ['Logement'])
    ]));

    path.forEach(function (loc, i) {
      var last = i === path.length - 1;
      crumbs.push(el('li', null, [
        last
          ? el('span', { 'aria-current': 'page' }, [loc.name])
          : el('a', { href: R.ui.router.href(loc.id) }, [loc.name])
      ]));
    });

    return el('nav', { class: 'breadcrumb', 'aria-label': 'Fil d\u2019Ariane' }, [el('ol', null, crumbs)]);
  }

  R.ns('ui.components').breadcrumb = { create: create };
})();
