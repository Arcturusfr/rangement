/*
  js/ui/views/location.js — Application « Rangement »
  Version : V004
  Horodatage : 2026-10-23 11:34 (heure de Paris)
  Résumé : actions sur les emplacements (ajouter, modifier, déplacer, supprimer) ; vrai écran de démarrage.
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
        subtitle: loc.note ? label + ' \u2014 ' + loc.note : label,
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

  function btn(label, variant, onclick) {
    return el('button', { class: 'button' + (variant ? ' button--' + variant : ''), type: 'button', onclick: onclick }, [label]);
  }

  function toolbar(loc) {
    var A = R.ui.views.locationActions;
    var buttons = loc
      ? [
          btn('Ajouter un emplacement ici', '', function () { A.openCreate(loc.id); }),
          btn('Modifier', 'secondary', function () { A.openEdit(loc.id); }),
          btn('Déplacer', 'secondary', function () { A.openMove(loc.id); }),
          btn('Supprimer', 'danger-outline', function () { A.askDelete(loc.id); })
        ]
      : [btn('Ajouter une pièce', '', function () { A.openCreate(null); })];
    return el('div', { class: 'toolbar', role: 'group', 'aria-label': 'Actions' }, buttons);
  }

  function renderStart() {
    var A = R.ui.views.locationActions;
    return el('div', { class: 'empty' }, [
      el('h2', null, ['Bienvenue dans Rangement']),
      el('p', null, ['Commencez par créer une pièce (par exemple \u00ab Séjour \u00bb), puis ajoutez-y des meubles, des tiroirs ou des boîtes.']),
      el('div', { class: 'toolbar' }, [
        btn('Créer ma première pièce', '', function () { A.openCreate(null); }),
        btn('Charger les données de démonstration', 'secondary', function () { R.features.demo.load(); })
      ])
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
      container.appendChild(renderStart());
      return;
    }

    var id = R.ui.router.current().locationId;
    var loc = id ? R.store.getLocation(id) : null;
    if (id && !loc) {
      container.appendChild(renderNotFound());
      return;
    }

    if (loc) { container.appendChild(R.ui.components.breadcrumb.create(R.store.pathOf(id))); }

    var heading = [el('h2', { class: 'detail-title' }, [loc ? loc.name : 'Logement'])];
    if (loc) {
      heading.push(el('p', { class: 'detail-meta' }, [
        R.models.kindLabel(loc.kind) + (loc.note ? ' \u2014 ' + loc.note : '')
      ]));
    }
    container.appendChild(el('header', { class: 'detail-head', 'data-kind': loc ? loc.kind : null }, heading));
    container.appendChild(toolbar(loc));

    var kids = locationRows(loc ? loc.id : null);
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
