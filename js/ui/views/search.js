/*
  js/ui/views/search.js — Application « Rangement »
  Version : V009
  Horodatage : 2026-10-25 16:10 (heure de Paris)
  Résumé : niveaux de couleur des résultats (objet, épuisé, pièce, emplacement, sous-emplacement).
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;
  var plural = R.ui.dom.plural;

  function pathLabel(path) {
    return path.map(function (p) { return p.name; }).join(' \u203a ');
  }

  function itemRow(hit) {
    var it = hit.item;
    var chips = [];
    if (it.quantity !== 1) { chips.push('\u00d7 ' + R.features.items.formatQuantity(it.quantity)); }
    return {
      title: it.name,
      href: R.ui.router.itemHref(it.id),
      subtitle: pathLabel(hit.path),
      level: it.quantity === 0 ? 'zero' : 'objet',
      chips: chips.concat(it.tags),
      muted: it.quantity === 0
    };
  }

  function locationRow(hit) {
    var loc = hit.location;
    var parents = hit.path.slice(0, -1);
    var label = R.models.kindLabel(loc.kind);
    return {
      title: loc.name,
      href: R.ui.router.href(loc.id),
      level: R.models.levelOf(hit.path.length - 1),
      subtitle: parents.length ? label + ' \u2014 ' + pathLabel(parents) : label
    };
  }

  function section(title, rows) {
    return el('section', { class: 'section' }, [
      el('h3', { class: 'section-title' }, [title]),
      R.ui.components.list.create(rows)
    ]);
  }

  // Renvoie le contenu du volet de détail pour la recherche `query`.
  function create(query) {
    var res = R.features.search.search(query);
    var total = res.items.length + res.locations.length;
    var nodes = [el('header', { class: 'detail-head' }, [el('h2', { class: 'detail-title' }, ['Recherche'])])];

    if (!res.terms.length) {
      nodes.push(el('p', { class: 'hint' }, ['Saisissez un nom d\u2019objet, un mot-clé ou un emplacement dans le champ de recherche.']));
    } else if (!total) {
      nodes.push(el('p', { class: 'detail-meta' }, ['Aucun résultat pour \u00ab ' + query.trim() + ' \u00bb.']));
      nodes.push(el('p', { class: 'hint' }, ['La recherche ignore la casse et les accents, mais pas les fautes de frappe. Avec plusieurs mots, tous doivent être trouvés.']));
    } else {
      nodes[0].appendChild(el('p', { class: 'detail-meta' }, [plural(total, 'résultat', 'résultats') + ' pour \u00ab ' + query.trim() + ' \u00bb']));
      if (res.items.length) { nodes.push(section('Objets (' + res.items.length + ')', res.items.map(itemRow))); }
      if (res.locations.length) { nodes.push(section('Emplacements (' + res.locations.length + ')', res.locations.map(locationRow))); }
    }
    return el('div', { class: 'search-results' }, nodes);
  }

  R.ns('ui.views').search = { create: create };
})();
