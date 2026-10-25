/*
  js/ui/components/breadcrumb.js — Application « Rangement »
  Version : V009
  Horodatage : 2026-10-25 16:10 (heure de Paris)
  Résumé : niveaux de couleur par élément, libellé de racine avec précision, paramètre currentLevel.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;

  // `path` : emplacements de la racine jusqu'à l'emplacement courant (inclus).
  // `currentLabel` (facultatif) : élément courant qui n'est pas un emplacement (ex. un objet) ;
  // dans ce cas tous les emplacements de `path` sont des liens ; `currentLevel` en donne le niveau de couleur.
  function create(path, currentLabel, currentLevel) {
    var crumbs = [];
    var atRoot = path.length === 0 && !currentLabel;

    crumbs.push(el('li', { 'data-level': 'racine' }, [
      atRoot
        ? el('span', { 'aria-current': 'page' }, [R.models.rootLabel()])
        : el('a', { href: R.ui.router.href(null) }, [R.models.rootLabel()])
    ]));

    path.forEach(function (loc, i) {
      var last = i === path.length - 1 && !currentLabel;
      crumbs.push(el('li', { 'data-level': R.models.levelOf(i) }, [
        last
          ? el('span', { 'aria-current': 'page' }, [loc.name])
          : el('a', { href: R.ui.router.href(loc.id) }, [loc.name])
      ]));
    });

    if (currentLabel) {
      crumbs.push(el('li', { 'data-level': currentLevel || 'objet' }, [el('span', { 'aria-current': 'page' }, [currentLabel])]));
    }

    return el('nav', { class: 'breadcrumb', 'aria-label': 'Fil d\u2019Ariane' }, [el('ol', null, crumbs)]);
  }

  R.ns('ui.components').breadcrumb = { create: create };
})();
