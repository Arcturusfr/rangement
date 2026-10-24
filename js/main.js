/*
  js/main.js — Application « Rangement »
  Version : V006
  Horodatage : 2026-10-24 13:10 (heure de Paris)
  Résumé : modules de recherche ajoutés ; champ de recherche monté (jalon 4).
*/
(function () {
  'use strict';

  var R = window.Rangement;

  // Modules attendus et fichier qui doit les fournir (voir ARCHITECTURE.md §5).
  var REQUIRED = [
    ['events', 'js/core/events.js'],
    ['ids', 'js/core/ids.js'],
    ['models', 'js/core/models.js'],
    ['storage', 'js/core/storage.js'],
    ['store', 'js/core/store.js'],
    ['features.demo', 'js/features/demo.js'],
    ['features.locations', 'js/features/locations.js'],
    ['features.items', 'js/features/items.js'],
    ['features.search', 'js/features/search.js'],
    ['ui.dom', 'js/ui/dom.js'],
    ['ui.router', 'js/ui/router.js'],
    ['ui.components.breadcrumb', 'js/ui/components/breadcrumb.js'],
    ['ui.components.list', 'js/ui/components/list.js'],
    ['ui.components.form', 'js/ui/components/form.js'],
    ['ui.components.dialog', 'js/ui/components/dialog.js'],
    ['ui.layout', 'js/ui/layout.js'],
    ['ui.views.browse', 'js/ui/views/browse.js'],
    ['ui.views.locationActions', 'js/ui/views/location-actions.js'],
    ['ui.views.itemActions', 'js/ui/views/item-actions.js'],
    ['ui.views.item', 'js/ui/views/item.js'],
    ['ui.views.search', 'js/ui/views/search.js'],
    ['ui.views.searchbar', 'js/ui/views/searchbar.js'],
    ['ui.views.location', 'js/ui/views/location.js']
  ];

  function resolve(path) {
    var node = R;
    var keys = path.split('.');
    for (var i = 0; i < keys.length; i++) {
      node = node && node[keys[i]];
    }
    return node;
  }

  function missingFiles() {
    return REQUIRED.filter(function (m) { return !resolve(m[0]); }).map(function (m) { return m[1]; });
  }

  function report(message) {
    if (window.__rangementBoot) { window.__rangementBoot.add(message); }
  }

  function showStatus(messages) {
    var bar = document.getElementById('status');
    R.ui.dom.clear(bar);
    messages.forEach(function (m) { bar.appendChild(R.ui.dom.el('p', null, [m])); });
    bar.hidden = messages.length === 0;
  }

  function start() {
    document.title = R.config.appName + ' ' + R.config.version;
    document.getElementById('app-version').textContent = R.config.version;

    var missing = missingFiles();
    if (missing.length) {
      report('Fichiers manquants ou illisibles : ' + missing.join(', ') + '. Vérifiez qu\u2019ils sont bien dans le dépôt, à ce chemin exact.');
      return;
    }

    R.store.init();
    R.ui.router.init();
    R.ui.layout.init();

    R.ui.views.searchbar.mount(document.getElementById('searchbar'));
    R.ui.views.browse.mount(document.getElementById('pane-tree'));
    R.ui.views.location.mount(document.getElementById('pane-detail'));

    var messages = R.store.notices();
    showStatus(messages);
    R.events.on('store:error', function (e) { messages.push(e.message); showStatus(messages); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
