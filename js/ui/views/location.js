/*
  js/ui/views/location.js — Application « Rangement »
  Version : V010
  Horodatage : 2026-10-26 15:33 (heure de Paris)
  Résumé : jalon 7 : commutateur Liste / Vue graphique pour les meubles (emplacements de premier niveau).
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
    var level = R.models.levelOf(parentId ? R.store.depthOf(parentId) + 1 : 0);
    return R.store.childLocations(parentId).map(function (loc) {
      var label = R.models.kindLabel(loc.kind);
      return {
        title: loc.name,
        href: R.ui.router.href(loc.id),
        level: level,
        subtitle: loc.note ? label + ' \u2014 ' + loc.note : label,
        chips: countChips(loc.id)
      };
    });
  }

  function itemRows(locationId) {
    return R.store.itemsIn(locationId).map(function (it) {
      var chips = [];
      if (it.quantity !== 1) { chips.push('\u00d7 ' + R.features.items.formatQuantity(it.quantity)); }
      return {
        title: it.name,
        href: R.ui.router.itemHref(it.id),
        subtitle: it.note,
        level: it.quantity === 0 ? 'zero' : 'objet',
        chips: chips.concat(it.tags),
        muted: it.quantity === 0
      };
    });
  }

  function section(title, listNode) {
    return el('section', { class: 'section' }, [el('h3', { class: 'section-title' }, [title]), listNode]);
  }

  function btn(label, variant, onclick, level) {
    return el('button', { class: 'button' + (variant ? ' button--' + variant : ''), type: 'button', 'data-level': level || null, onclick: onclick }, [label]);
  }

  function toolbar(loc, depth) {
    var A = R.ui.views.locationActions;
    var buttons = loc
      ? [
          btn('Ajouter un objet ici', '', function () { R.ui.views.itemActions.openCreate(loc.id); }, 'objet'),
          btn('Ajouter un emplacement ici', '', function () { A.openCreate(loc.id); }, R.models.levelOf(depth + 1)),
          btn('Modifier', 'secondary', function () { A.openEdit(loc.id); }),
          btn('Déplacer', 'secondary', function () { A.openMove(loc.id); }),
          btn('Dupliquer', 'secondary', function () { A.openDuplicate(loc.id); }),
          btn('Supprimer', 'danger-outline', function () { A.askDelete(loc.id); })
        ]
      : [btn('Ajouter une pièce', '', function () { A.openCreate(null); }, 'piece')];
    return el('div', { class: 'toolbar', role: 'group', 'aria-label': 'Actions' }, buttons);
  }

  function renderStart() {
    var A = R.ui.views.locationActions;
    return el('div', { class: 'empty' }, [
      el('h2', null, ['Bienvenue dans Rangement']),
      el('p', null, ['Commencez par créer une pièce (par exemple \u00ab Séjour \u00bb), puis ajoutez-y des meubles, des tiroirs ou des boîtes.']),
      el('div', { class: 'toolbar' }, [
        btn('Créer ma première pièce', '', function () { A.openCreate(null); }, 'piece'),
        btn('Charger les données de démonstration', 'secondary', function () { R.features.demo.load(); }),
        el('a', { class: 'button button--secondary', href: R.ui.router.settingsHref() }, ['Importer une sauvegarde'])
      ])
    ]);
  }

  function renderNotFound(title, message) {
    return el('div', { class: 'empty' }, [
      el('h2', null, [title]),
      el('p', null, [message]),
      el('a', { class: 'button', href: R.ui.router.href(null) }, ['Retour au logement'])
    ]);
  }

  function render() {
    R.ui.dom.clear(container);

    var route = R.ui.router.current();

    if (route.settings) {
      container.appendChild(R.ui.views.settings.create());
      return;
    }

    if (!R.store.locations().length) {
      container.appendChild(renderStart());
      return;
    }

    if (route.query !== null) {
      container.appendChild(R.ui.views.search.create(route.query));
      return;
    }

    if (route.itemId) {
      var item = R.store.getItem(route.itemId);
      container.appendChild(item
        ? R.ui.views.item.create(item)
        : renderNotFound('Objet introuvable', 'Cet objet n\u2019existe plus ou le lien est incorrect.'));
      return;
    }

    var id = route.locationId;
    var loc = id ? R.store.getLocation(id) : null;
    if (id && !loc) {
      container.appendChild(renderNotFound('Emplacement introuvable', 'Cet emplacement n\u2019existe plus ou le lien est incorrect.'));
      return;
    }

    var depth = loc ? R.store.depthOf(loc.id) : -1;
    var bar = R.ui.components.detailbar.create({
      ref: loc ? { type: 'location', id: loc.id } : { type: 'root' },
      path: loc ? R.store.pathOf(id) : [],
      title: loc ? loc.name : R.models.rootLabel(),
      level: loc ? R.models.levelOf(depth) : 'racine',
      toolbar: toolbar(loc, depth)
    });
    container.appendChild(bar.head);
    if (loc) {
      container.appendChild(el('p', { class: 'detail-meta' }, [
        R.models.kindLabel(loc.kind) + (loc.note ? ' \u2014 ' + loc.note : '')
      ]));
    }
    container.appendChild(bar.manage);

    if (loc && R.features.furniture.isFurniture(loc.id)) {
      container.appendChild(R.ui.views.furniture.switcher());
      if (R.ui.views.furniture.mode() === 'graphic') {
        container.appendChild(R.ui.views.furniture.create(loc.id));
        return;
      }
    }

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
    R.events.on('backup:changed', render);
    R.events.on('view:changed', render);
    R.events.on('pwa:changed', function () { if (R.ui.router.current().settings) { render(); } });
    R.events.on('route:changed', function () { render(); container.scrollTop = 0; });
  }

  R.ns('ui.views').location = { mount: mount };
})();
