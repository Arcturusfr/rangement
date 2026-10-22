/*
  js/ui/views/browse.js — Application « Rangement »
  Version : V003
  Horodatage : 2026-10-22 21:39 (heure de Paris)
  Résumé : création — volet gauche : arborescence complète des emplacements.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;
  var container = null;

  function renderLevel(parentId, currentId) {
    var kids = R.store.childLocations(parentId);
    if (!kids.length) { return null; }
    return el('ul', { class: 'tree' }, kids.map(function (loc) {
      return el('li', null, [
        el('a', {
          class: 'tree-link',
          href: R.ui.router.href(loc.id),
          'data-kind': loc.kind,
          'aria-current': loc.id === currentId ? 'page' : null
        }, [loc.name]),
        renderLevel(loc.id, currentId)
      ]);
    }));
  }

  function render() {
    var currentId = R.ui.router.current().locationId;
    R.ui.dom.clear(container);
    container.appendChild(el('h2', { class: 'pane-title' }, ['Arborescence']));
    container.appendChild(el('a', {
      class: 'tree-root',
      href: R.ui.router.href(null),
      'aria-current': currentId ? null : 'page'
    }, ['Logement']));
    var tree = renderLevel(null, currentId);
    if (tree) { container.appendChild(tree); }
  }

  function mount(node) {
    container = node;
    render();
    R.events.on('store:changed', render);
    R.events.on('route:changed', render);
  }

  R.ns('ui.views').browse = { mount: mount };
})();
