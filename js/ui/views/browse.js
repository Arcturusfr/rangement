/*
  js/ui/views/browse.js — Application « Rangement »
  Version : V005
  Horodatage : 2026-10-23 23:50 (heure de Paris)
  Résumé : quand une fiche d'objet est affichée, son emplacement est surligné dans l'arborescence.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;
  var container = null;

  // Emplacement à surligner : celui de la route, ou celui de l'objet affiché.
  function highlightedId() {
    var route = R.ui.router.current();
    if (route.itemId) {
      var item = R.store.getItem(route.itemId);
      return item ? item.locationId : null;
    }
    return route.locationId;
  }

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
    var currentId = highlightedId();
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
