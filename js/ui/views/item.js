/*
  js/ui/views/item.js — Application « Rangement »
  Version : V009
  Horodatage : 2026-10-25 16:10 (heure de Paris)
  Résumé : en-tête figé (detailbar), bouton Dupliquer, niveaux de couleur.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;

  function btn(label, variant, onclick) {
    return el('button', { class: 'button' + (variant ? ' button--' + variant : ''), type: 'button', onclick: onclick }, [label]);
  }

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
      toolbar: el('div', { class: 'toolbar', role: 'group', 'aria-label': 'Actions' }, [
        btn('Modifier', 'secondary', function () { A.openEdit(item.id); }),
        btn('Déplacer', 'secondary', function () { A.openMove(item.id); }),
        btn('Dupliquer', 'secondary', function () { A.openDuplicate(item.id); }),
        btn('Supprimer', 'danger-outline', function () { A.askDelete(item.id); })
      ])
    });

    var nodes = [
      bar.head,
      el('p', { class: 'detail-meta' }, ['Quantité : ' + R.features.items.formatQuantity(item.quantity) + (depleted ? ' (épuisé)' : '')]),
      bar.manage,
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
