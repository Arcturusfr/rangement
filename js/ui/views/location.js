/*
  js/ui/views/location.js — Application « Rangement »
  Version : V003
  Horodatage : 2026-10-22 21:39 (heure de Paris)
  Résumé : création — volet principal : contenu d'un emplacement (lecture seule).
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;
  var plural = R.ui.dom.plural;
  var container = null;

  function countChips(id) {
    var n = R.store.countIn(id);
    var chips = [];
    if (n.locations) { chips.push(plural(n.locations, 'emplacement', 'emplacements')); }
    if (n.items) { chips.push(plural(n.items, 'objet', 'objets')); }
    return chips.length ? chips : ['Vide'];
  }

  function locationRows(parentId) {
    return R.store.childLocations(parentId).map(function (loc) {
      var label = R.models.kindLabel(loc.kind);
      return {
        title: loc.name,
        href: R.ui.router.href(loc.id),
        kind: loc.kind,
        subtitle: loc.note ? label + ' — ' + loc.note : label,
        chips: countChips(loc.id)
      };
    });
  }

  function itemRows(locationId) {
    return R.store.itemsIn(locationId).map(function (it) {
      var chips = [];
      if (it.quantity !== 1) { chips.push('\u00d7 ' + it.quantity); }
      return { title: it.name, subtitle: it.note, chips: chips.concat(it.tags) };
    });
  }

  function section(title, listNode) {
    return el('section', { class: 'section' }, [el('h3', { class: 'section-title' }, [title]), listNode]);
  }

  function renderEmptyApp() {
    return el('div', { class: 'empty' }, [
      el('h2', null, ['Aucun emplacement pour l\u2019instant']),
      el('p', null, ['Chargez les données de démonstration pour explorer l\u2019application : quatre rangements d\u2019exemple (chambre, séjour, entrée).']),
      el('button', {
        class: 'button',
        type: 'button',
        onclick: function () { R.features.demo.load(); }
      }, ['Charger les données de démonstration'])
    ]);
  }

  function renderNotFound() {
    return el('div', { class: 'empty' }, [
      el('h2', null, ['Emplacement introuvable']),
      el('p', null, ['Cet emplacement n\u2019existe plus ou le lien est incorrect.']),
      el('a', { class: 'button', href: R.ui.router.href(null) }, ['Retour au logement'])
    ]);
  }

  function render() {
    R.ui.dom.clear(container);

    if (!R.store.locations().length) {
      container.appendChild(renderEmptyApp());
      return;
    }

    var id = R.ui.router.current().locationId;
    var loc = id ? R.store.getLocation(id) : null;
    if (id && !loc) {
      container.appendChild(renderNotFound());
      return;
    }

    if (loc) { container.appendChild(R.ui.components.breadcrumb.create(R.store.pathOf(id))); }

    var parentId = loc ? loc.id : null;
    var heading = [el('h2', { class: 'detail-title' }, [loc ? loc.name : 'Logement'])];
    if (loc) {
      heading.push(el('p', { class: 'detail-meta' }, [
        R.models.kindLabel(loc.kind) + (loc.note ? ' — ' + loc.note : '')
      ]));
    }
    container.appendChild(el('header', { class: 'detail-head', 'data-kind': loc ? loc.kind : null }, heading));

    var kids = locationRows(parentId);
    var items = loc ? itemRows(loc.id) : [];

    if (kids.length) {
      container.appendChild(section(loc ? 'Emplacements à l\u2019intérieur' : 'Pièces', R.ui.components.list.create(kids)));
    }
    if (items.length) {
      container.appendChild(section('Objets rangés ici', R.ui.components.list.create(items)));
    }
    if (!kids.length && !items.length) {
      container.appendChild(el('p', { class: 'hint' }, ['Cet emplacement est vide.']));
    }
  }

  function mount(node) {
    container = node;
    render();
    R.events.on('store:changed', render);
    R.events.on('route:changed', function () { render(); container.scrollTop = 0; });
  }

  R.ns('ui.views').location = { mount: mount };
})();
