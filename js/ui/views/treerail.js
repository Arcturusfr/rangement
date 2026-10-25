/*
  js/ui/views/treerail.js — Application « Rangement »
  Version : V009
  Horodatage : 2026-10-25 16:10 (heure de Paris)
  Résumé : création — arborescence minimale (rail sans libellés) et infobulle Ok / Annuler d'un élément.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;
  var open = null;   // { backdrop, box, anchor, onKey }

  function close(restoreFocus) {
    if (!open) { return; }
    var o = open;
    open = null;
    document.removeEventListener('keydown', o.onKey, true);
    if (o.backdrop.parentNode) { o.backdrop.parentNode.removeChild(o.backdrop); }
    if (o.box.parentNode) { o.box.parentNode.removeChild(o.box); }
    if (restoreFocus && o.anchor && document.contains(o.anchor)) { o.anchor.focus(); }
  }

  // info : { id (null = racine), name, path, level, href }
  function openFlyout(info, anchor) {
    close(false);
    var okButton = el('button', {
      class: 'button', type: 'button', 'data-level': info.level,
      onclick: function () { close(false); window.location.hash = info.href; }
    }, ['Ok']);
    var box = el('div', { class: 'tree-flyout', role: 'group', 'aria-label': 'Sélection : ' + info.name, 'data-level': info.level }, [
      info.path ? el('p', { class: 'tree-flyout-path' }, [info.path]) : null,
      el('p', { class: 'tree-flyout-name' }, [info.name]),
      el('div', { class: 'tree-flyout-actions' }, [
        el('button', { class: 'button button--secondary', type: 'button', onclick: function () { close(true); } }, ['Annuler']),
        okButton
      ])
    ]);
    var backdrop = el('div', { class: 'tree-flyout-backdrop', onclick: function () { close(true); } });
    var onKey = function (event) { if (event.key === 'Escape') { event.stopPropagation(); close(true); } };
    document.addEventListener('keydown', onKey, true);
    document.body.appendChild(backdrop);
    document.body.appendChild(box);
    open = { backdrop: backdrop, box: box, anchor: anchor, onKey: onKey };

    // Le libellé se déploie à partir de l'élément, par-dessus la partie gauche du volet de détail.
    var rect = anchor.getBoundingClientRect();
    var top = Math.min(rect.top, window.innerHeight - box.offsetHeight - 8);
    box.style.left = Math.max(0, rect.left) + 'px';
    box.style.top = Math.max(8, top) + 'px';
    okButton.focus();
  }

  function dot() { return el('span', { class: 'mini-dot', 'aria-hidden': 'true' }); }

  function squareFor(info, current) {
    var btn = el('button', {
      class: 'tree-mini-item', type: 'button', 'data-level': info.level,
      'aria-label': info.name, title: info.name, 'aria-haspopup': 'true',
      'aria-current': current ? 'page' : null
    }, [dot()]);
    btn.addEventListener('click', function () { openFlyout(info, btn); });
    return btn;
  }

  function pathOf(id) {
    return R.store.pathOf(id).slice(0, -1).map(function (p) { return p.name; }).join(' \u203a ');
  }

  // api : { isOpen(id), toggle(id), currentId, rootCurrent }
  // Renvoie { head, body } : la racine (figée) et la liste des emplacements visibles.
  function create(api) {
    var rootInfo = { id: null, name: R.models.rootLabel(), path: '', level: 'racine', href: R.ui.router.href(null) };
    var head = squareFor(rootInfo, api.rootCurrent);

    var list = el('ul', { class: 'tree-mini' });
    function addRows(parentId, depth) {
      R.store.childLocations(parentId).forEach(function (loc) {
        var kids = R.store.childLocations(loc.id);
        var expanded = api.isOpen(loc.id);
        var info = { id: loc.id, name: loc.name, path: pathOf(loc.id), level: R.models.levelOf(depth), href: R.ui.router.href(loc.id) };
        var toggle = kids.length
          ? el('button', {
              class: 'tree-toggle', type: 'button', 'aria-expanded': expanded ? 'true' : 'false',
              'aria-label': (expanded ? 'Replier \u00ab ' : 'Déplier \u00ab ') + loc.name + ' \u00bb',
              onclick: function () { api.toggle(loc.id); }
            })
          : el('span', { class: 'tree-mini-spacer', 'aria-hidden': 'true' });
        list.appendChild(el('li', { class: 'mini-row', 'data-depth': String(Math.min(depth, 4)) }, [
          toggle, squareFor(info, loc.id === api.currentId)
        ]));
        if (kids.length && expanded) { addRows(loc.id, depth + 1); }
      });
    }
    addRows(null, 0);
    return { head: head, body: list };
  }

  R.ns('ui.views').treerail = { create: create, close: function () { close(false); } };
})();
