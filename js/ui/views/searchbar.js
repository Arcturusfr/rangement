/*
  js/ui/views/searchbar.js — Application « Rangement »
  Version : V006
  Horodatage : 2026-10-24 13:10 (heure de Paris)
  Résumé : création — champ de recherche toujours visible sous l'en-tête, synchronisé avec la route.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;
  var input = null;

  // Le champ reflète la recherche de la route ; hors recherche il est vide.
  function sync() {
    var q = R.ui.router.current().query;
    var wanted = q === null ? '' : q;
    if (input.value !== wanted) { input.value = wanted; }
  }

  function mount(root) {
    input = el('input', {
      id: 'search-input',
      type: 'search',
      placeholder: 'Rechercher un objet, un mot-clé, un emplacement',
      autocomplete: 'off',
      autocapitalize: 'off',
      spellcheck: 'false',
      enterkeyhint: 'search'
    });
    var form = el('form', { class: 'searchbar-form', role: 'search', novalidate: true, onsubmit: function (event) {
      event.preventDefault();
      input.blur();            // referme le clavier sur mobile
    } }, [
      el('label', { class: 'visually-hidden', 'for': 'search-input' }, ['Rechercher']),
      input
    ]);
    input.addEventListener('input', function () { R.ui.router.search(input.value); });
    root.appendChild(form);
    R.events.on('route:changed', sync);
    sync();
  }

  R.ns('ui.views').searchbar = { mount: mount };
})();
