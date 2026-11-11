/*
  js/ui/views/location.js — Application « Rangement »
  Version : V018
  Horodatage : 2026-11-10 21:05 (heure de Paris)
  Résumé : V018 : boutons flottants Liste / Plan et Agrandir ; vue graphique par défaut.
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

  var LEVEL_NAMES = ['Pièce', 'Emplacement', 'Sous-emplacement', 'Sous-sous-emplacement'];

  function levelName(depth) { return LEVEL_NAMES[depth] || ('Niveau ' + (depth + 1)); }

  // Commandes du menu déroulant « Actions ».
  function actions(loc, depth) {
    var A = R.ui.views.locationActions;
    if (!loc) { return [{ label: 'Ajouter une pièce', run: function () { A.openCreate(null); } }]; }
    return [
      { label: 'Ajouter un objet ici', run: function () { R.ui.views.itemActions.openCreate(loc.id); } },
      { label: 'Ajouter un emplacement ici', run: function () { A.openCreate(loc.id); } },
      { label: 'Modifier', run: function () { A.openEdit(loc.id); } },
      { label: 'D\u00e9placer', run: function () { A.openMove(loc.id); } },
      { label: 'Dupliquer', run: function () { A.openDuplicate(loc.id); } },
      { label: 'Supprimer', danger: true, run: function () { A.askDelete(loc.id); } }
    ];
  }

  // Texte de l'info-bulle ℹ️ : niveau, nombre d'emplacements et d'objets (et note).
  function infoLines(loc, depth) {
    var lines = [];
    if (!loc) {
      var rooms = R.store.childLocations(null).length;
      lines.push('Niveau 0 \u2014 le logement');
      lines.push(rooms ? plural(rooms, 'pièce', 'pièces') + ' (niveau 1)' : 'Aucune pièce');
      lines.push('Au total : ' + plural(R.store.locations().length, 'emplacement', 'emplacements') + ' et ' + plural(R.store.items().length, 'objet', 'objets'));
      return lines;
    }
    var subs = R.store.childLocations(loc.id).length;
    var total = R.store.countIn(loc.id);
    var word = depth === 0 ? ['emplacement', 'emplacements'] : ['sous-emplacement', 'sous-emplacements'];
    lines.push('Niveau ' + (depth + 1) + ' \u2014 ' + levelName(depth));
    lines.push(subs ? plural(subs, word[0], word[1]) + ' (niveau ' + (depth + 2) + ')' : 'Aucun ' + word[0]);
    lines.push('Objets rangés directement ici : ' + R.store.itemsIn(loc.id).length);
    if (total.locations > subs || total.items > R.store.itemsIn(loc.id).length) {
      lines.push('Contenu total : ' + plural(total.locations, 'emplacement', 'emplacements') + ' et ' + plural(total.items, 'objet', 'objets') + ' (tous niveaux)');
    }
    if (loc.note) { lines.push('Note : ' + loc.note); }
    return lines;
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
    var top = container.scrollTop;
    renderView();
    container.scrollTop = top;
  }

  function renderView() {
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
    var V = R.ui.views.furniture;
    var planScope = (!loc || depth === 0);                                      // logement ou pièce : un plan
    var furnScope = !!loc && R.features.furniture.hasGraphic(loc.id);          // meuble ou niveau plus bas avec sous-emplacements : vue graphique
    var planGraphic = planScope && V.mode('plan') === 'graphic';
    var anyGraphic = planGraphic || (furnScope && V.mode() === 'graphic');
    var floatSwitch = planScope ? V.switcher('plan') : (furnScope ? V.switcher() : null);
    var floats = [];
    if (floatSwitch) { floats.push(floatSwitch); }
    if (planGraphic) { floats.push(V.zoomButton()); }
    var bar = R.ui.components.detailbar.create({
      ref: loc ? { type: 'location', id: loc.id } : { type: 'root' },
      path: loc ? R.store.pathOf(id) : [],
      title: loc ? loc.name : R.models.rootLabel(),
      level: loc ? R.models.levelOf(depth) : 'racine',
      kind: loc ? R.models.kindLabel(loc.kind) : null,
      info: infoLines(loc, depth),
      actions: actions(loc, depth),
      floats: floats,
      floatReserve: !!floatSwitch && !anyGraphic      // en liste, de la place est réservée sous l'en-tête ; sur un plan, les boutons le recouvrent
    });
    container.appendChild(bar.head);

    if (planScope && V.mode('plan') === 'graphic') {
      container.appendChild(V.createPlan(loc ? loc.id : null));
      return;
    }
    if (furnScope && V.mode() === 'graphic') {
      container.appendChild(V.create(loc.id));
      return;
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
