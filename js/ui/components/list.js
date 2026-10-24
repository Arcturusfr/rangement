/*
  js/ui/components/list.js — Application « Rangement »
  Version : V003
  Horodatage : 2026-10-24 13:10 (heure de Paris)
  Résumé : lignes « grisées » (row.muted) pour les objets de quantité nulle.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;

  // rows : [{ title, href?, kind?, subtitle?, chips?: string[], muted?: boolean }]
  function create(rows) {
    var items = rows.map(function (row) {
      var body = [
        el('span', { class: 'list-title' }, [row.title]),
        row.subtitle ? el('span', { class: 'list-sub' }, [row.subtitle]) : null,
        row.chips && row.chips.length
          ? el('span', { class: 'list-chips' }, row.chips.map(function (c) { return el('span', { class: 'chip' }, [c]); }))
          : null
      ];
      var inner = row.href
        ? el('a', { class: 'list-row', href: row.href }, body)
        : el('div', { class: 'list-row' }, body);
      return el('li', { class: 'list-item' + (row.muted ? ' list-item--muted' : ''), 'data-kind': row.kind || null }, [inner]);
    });
    return el('ul', { class: 'list' }, items);
  }

  R.ns('ui.components').list = { create: create };
})();
