/*
  js/ui/views/item.js — Application « Rangement »
  Version : V016
  Horodatage : 2026-11-06 12:00 (heure de Paris)
  Résumé : jalon 9.3 — ℹ️ et libellé « Objet » dans l'en-tête figé, « Actions » en menu déroulant.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;

  function section(title, content) {
    return el('section', { class: 'section' }, [el('h3', { class: 'section-title' }, [title]), content]);
  }

  // Renvoie le contenu du volet de détail pour l'objet `item`.
  function create(item) {
    var A = R.ui.views.itemActions;
    var path = R.store.pathOf(item.locationId);
    var where = path.map(function (p) { return p.name; }).join(' \u203a ');

    var depleted = item.quantity === 0;
    var bar = R.ui.components.detailbar.create({
      ref: { type: 'item', id: item.id },
      path: path,
      currentLabel: item.name,
      currentLevel: depleted ? 'zero' : 'objet',
      title: item.name,
      level: depleted ? 'zero' : 'objet',
      depleted: depleted,
      kind: 'Objet',
      info: [
        'Niveau ' + (R.store.depthOf(item.locationId) + 2) + ' \u2014 Objet',
        'Rangé dans \u00ab ' + path[path.length - 1].name + ' \u00bb (niveau ' + (R.store.depthOf(item.locationId) + 1) + ')',
        'Quantité : ' + R.features.items.formatQuantity(item.quantity) + (depleted ? ' (épuisé)' : '')
      ],
      actions: [
        { label: 'Modifier', run: function () { A.openEdit(item.id); } },
        { label: 'D\u00e9placer', run: function () { A.openMove(item.id); } },
        { label: 'Dupliquer', run: function () { A.openDuplicate(item.id); } },
        { label: 'Supprimer', danger: true, run: function () { A.askDelete(item.id); } }
      ]
    });

    var nodes = [
      bar.head,
      el('p', { class: 'detail-meta' }, ['Quantité : ' + R.features.items.formatQuantity(item.quantity) + (depleted ? ' (épuisé)' : '')]),
      section('Rangé dans', el('p', null, [
        el('a', { class: 'item-where', href: R.ui.router.href(item.locationId) }, [where])
      ]))
    ];

    if (item.tags.length) {
      nodes.push(section('Mots-clés', el('p', { class: 'list-chips' }, item.tags.map(function (t) {
        return el('span', { class: 'chip' }, [t]);
      }))));
    }
    if (item.note) {
      nodes.push(section('Note', el('p', { class: 'note-text' }, [item.note])));
    }
    return el('div', { class: 'item-detail' }, nodes);
  }

  R.ns('ui.views').item = { create: create };
})();
