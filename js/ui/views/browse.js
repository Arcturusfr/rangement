/*
  js/ui/views/browse.js — Application « Rangement »
  Version : V010
  Horodatage : 2026-10-26 15:33 (heure de Paris)
  Résumé : nombre d'objets (total, sous-emplacements compris) à droite de chaque emplacement de l'arborescence large.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;
  var container = null;
  var expanded = {};        // id → true : emplacements dépliés (en mémoire, repliés à chaque ouverture)
  var lastHighlight;        // dernier élément surligné (undefined = jamais rendu)
  var mode = 'wide';        // 'wide' (libellés) | 'mini' (rail sans libellés)

  // Emplacement à surligner : celui de la route, ou celui de l'objet affiché.
  function highlightedId() {
    var route = R.ui.router.current();
    if (route.itemId) {
      var item = R.store.getItem(route.itemId);
      return item ? item.locationId : null;
    }
    return route.locationId;
  }

  // ---------- état ----------

  function loadMode() {
    try {
      var ui = JSON.parse(R.storage.getAux('ui') || '{}');
      if (ui && ui.tree === 'mini') { mode = 'mini'; }
    } catch (err) { /* préférence illisible : arborescence large */ }
  }

  function setMode(next) {
    mode = next;
    R.storage.setAux('ui', JSON.stringify({ tree: mode }));
    document.documentElement.setAttribute('data-tree', mode);
    render();
  }

  function hasKids(id) { return R.store.childLocations(id).length > 0; }

  function allExpanded() {
    return R.store.locations().every(function (l) { return !hasKids(l.id) || expanded[l.id]; });
  }

  function expandAncestors(id) {
    R.store.pathOf(id).slice(0, -1).forEach(function (l) { expanded[l.id] = true; });
  }

  // Met à jour sur place (sans reconstruire, pour l'animation) l'état ouvert / fermé de chaque nœud.
  function syncOpen() {
    if (mode === 'mini') { render(); return; }
    container.querySelectorAll('.tree-node').forEach(function (node) {
      var id = node.getAttribute('data-id');
      var isOpen = !!expanded[id];
      node.setAttribute('data-open', isOpen ? 'true' : 'false');
      var t = node.querySelector(':scope > .tree-row > .tree-toggle');
      if (t) { setToggle(t, isOpen, R.store.getLocation(id) ? R.store.getLocation(id).name : ''); }
    });
    updateRootToggle();
  }

  function toggle(id) { expanded[id] = !expanded[id]; syncOpen(); }

  function expandAll() {
    R.store.locations().forEach(function (l) { if (hasKids(l.id)) { expanded[l.id] = true; } });
    syncOpen();
  }

  function collapseAll() { expanded = {}; syncOpen(); }

  // ---------- affichage ----------

  function setToggle(btn, isOpen, name) {
    btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    btn.setAttribute('aria-label', (isOpen ? 'Replier \u00ab ' : 'Déplier \u00ab ') + name + ' \u00bb');
  }

  function updateRootToggle() {
    var t = document.getElementById('tree-root-toggle');
    if (!t) { return; }
    var all = allExpanded();
    t.setAttribute('aria-expanded', all ? 'true' : 'false');
    t.setAttribute('aria-label', all ? 'Tout replier' : 'Tout déplier');
    t.setAttribute('title', all ? 'Tout replier' : 'Tout déplier');
  }

  // Nombre d'objets contenus (sous-emplacements compris) ; rien si zéro.
  function countBadge(id) {
    var n = R.store.countIn(id).items;
    return n ? el('span', { class: 'tree-count', title: R.ui.dom.plural(n, 'objet', 'objets') }, [String(n)]) : null;
  }

  function renderNode(loc, depth, currentId) {
    var kids = R.store.childLocations(loc.id);
    var isOpen = !!expanded[loc.id];
    var toggleNode;
    if (kids.length) {
      toggleNode = el('button', { class: 'tree-toggle', type: 'button', onclick: function () { toggle(loc.id); } });
      setToggle(toggleNode, isOpen, loc.name);
    } else {
      toggleNode = el('span', { class: 'tree-toggle tree-toggle--none', 'aria-hidden': 'true' });
    }
    var parts = [el('div', { class: 'tree-row' }, [
      toggleNode,
      el('a', {
        class: 'tree-link',
        href: R.ui.router.href(loc.id),
        'data-level': R.models.levelOf(depth),
        'aria-current': loc.id === currentId ? 'page' : null
      }, [loc.name]),
      countBadge(loc.id)
    ])];
    if (kids.length) {
      parts.push(el('div', { class: 'tree-children' }, [
        el('ul', { class: 'tree' }, kids.map(function (k) { return renderNode(k, depth + 1, currentId); }))
      ]));
    }
    return el('li', { class: 'tree-node', 'data-id': loc.id, 'data-open': isOpen ? 'true' : 'false' }, parts);
  }

  function renderWide(currentId, rootCurrent) {
    var rootToggle = el('button', { class: 'tree-toggle', id: 'tree-root-toggle', type: 'button', onclick: function () {
      if (allExpanded()) { collapseAll(); } else { expandAll(); }
    } });
    var shrink = el('button', {
      class: 'tree-shrink', id: 'tree-shrink', type: 'button', 'aria-label': 'Réduire l\u2019arborescence',
      title: 'Réduire l\u2019arborescence', onclick: function () { setMode('mini'); }
    }, ['\u00AB']);
    container.appendChild(el('div', { class: 'tree-head' }, [
      rootToggle,
      el('a', { class: 'tree-root', href: R.ui.router.href(null), 'aria-current': rootCurrent ? 'page' : null }, [R.models.rootLabel()]),
      shrink
    ]));
    var kids = R.store.childLocations(null);
    if (kids.length) {
      container.appendChild(el('ul', { class: 'tree' }, kids.map(function (k) { return renderNode(k, 0, currentId); })));
    } else {
      rootToggle.disabled = true;
    }
    updateRootToggle();
  }

  function renderMini(currentId, rootCurrent) {
    var rail = R.ui.views.treerail.create({
      isOpen: function (id) { return !!expanded[id]; },
      toggle: toggle,
      currentId: currentId,
      rootCurrent: rootCurrent
    });
    var grow = el('button', {
      class: 'tree-shrink', id: 'tree-grow', type: 'button', 'aria-label': 'Agrandir l\u2019arborescence',
      title: 'Agrandir l\u2019arborescence', onclick: function () { setMode('wide'); }
    }, ['\u00BB']);
    container.appendChild(el('div', { class: 'tree-head tree-head--mini' }, [grow, rail.head]));
    container.appendChild(rail.body);
  }

  function render() {
    R.ui.views.treerail.close();
    var currentId = highlightedId();
    var r = R.ui.router.current();
    var searching = r.query !== null || r.settings;
    // L'élément surligné doit rester visible : ses parents s'ouvrent quand il change.
    if (currentId !== lastHighlight) {
      if (currentId) { expandAncestors(currentId); }
      lastHighlight = currentId;
    }
    var rootCurrent = !(currentId || searching);
    R.ui.dom.clear(container);
    if (mode === 'mini') { renderMini(currentId, rootCurrent); } else { renderWide(currentId, rootCurrent); }
  }

  function mount(node) {
    container = node;
    loadMode();
    document.documentElement.setAttribute('data-tree', mode);
    render();
    R.events.on('store:changed', render);
    R.events.on('route:changed', render);
  }

  R.ns('ui.views').browse = { mount: mount, expandAll: expandAll, collapseAll: collapseAll, setMode: setMode, mode: function () { return mode; } };
})();
