/*
  js/ui/components/list.js — Application « Rangement »
  Version : V009
  Horodatage : 2026-10-25 16:10 (heure de Paris)
  Résumé : niveau de couleur (row.level) à la place du type ; lignes « grisées » conservées.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;

  // rows : [{ title, href?, level?, subtitle?, chips?: string[], muted?: boolean }]
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
      return el('li', { class: 'list-item' + (row.muted ? ' list-item--muted' : ''), 'data-level': row.level || null }, [inner]);
    });
    return el('ul', { class: 'list' }, items);
  }

  R.ns('ui.components').list = { create: create };
})();
