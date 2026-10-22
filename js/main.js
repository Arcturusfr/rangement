/*
  js/main.js — Application « Rangement »
  Version : V003
  Horodatage : 2026-10-22 21:39 (heure de Paris)
  Résumé : création — démarrage : stockage, routeur, mise en page, vues, messages d'état.
*/
(function () {
  'use strict';

  var R = window.Rangement;

  function showStatus(messages) {
    var bar = document.getElementById('status');
    R.ui.dom.clear(bar);
    messages.forEach(function (m) { bar.appendChild(R.ui.dom.el('p', null, [m])); });
    bar.hidden = messages.length === 0;
  }

  function start() {
    document.title = R.config.appName + ' ' + R.config.version;
    document.getElementById('app-version').textContent = R.config.version;

    R.store.init();
    R.ui.router.init();
    R.ui.layout.init();

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
