/*
  js/ui/components/breadcrumb.js — Application « Rangement »
  Version : V005
  Horodatage : 2026-10-23 23:50 (heure de Paris)
  Résumé : paramètre facultatif `currentLabel` (fiche d'un objet : tous les emplacements sont des liens).
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;

  // `path` : emplacements de la racine jusqu'à l'emplacement courant (inclus).
  // `currentLabel` (facultatif) : élément courant qui n'est pas un emplacement (ex. un objet) ;
  // dans ce cas tous les emplacements de `path` sont des liens.
  function create(path, currentLabel) {
    var crumbs = [];
    var atRoot = path.length === 0 && !currentLabel;

    crumbs.push(el('li', null, [
      atRoot
        ? el('span', { 'aria-current': 'page' }, ['Logement'])
        : el('a', { href: R.ui.router.href(null) }, ['Logement'])
    ]));

    path.forEach(function (loc, i) {
      var last = i === path.length - 1 && !currentLabel;
      crumbs.push(el('li', null, [
        last
          ? el('span', { 'aria-current': 'page' }, [loc.name])
          : el('a', { href: R.ui.router.href(loc.id) }, [loc.name])
      ]));
    });

    if (currentLabel) {
      crumbs.push(el('li', null, [el('span', { 'aria-current': 'page' }, [currentLabel])]));
    }

    return el('nav', { class: 'breadcrumb', 'aria-label': 'Fil d\u2019Ariane' }, [el('ol', null, crumbs)]);
  }

  R.ns('ui.components').breadcrumb = { create: create };
})();
