/*
  js/ui/views/searchbar.js — Application « Rangement »
  Version : V009
  Horodatage : 2026-10-25 16:10 (heure de Paris)
  Résumé : bouton Retour de l'application et icône de loupe devant le champ ; sinon inchangé.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;
  var input = null;
  var backButton = null;

  // Le champ reflète la recherche de la route ; hors recherche il est vide.
  function sync() {
    var q = R.ui.router.current().query;
    var wanted = q === null ? '' : q;
    if (input.value !== wanted) { input.value = wanted; }
    backButton.disabled = !R.ui.router.canBack();
  }

  function magnifier() {
    var ns = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('class', 'searchbar-icon');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');
    var circle = document.createElementNS(ns, 'circle');
    circle.setAttribute('cx', '10'); circle.setAttribute('cy', '10'); circle.setAttribute('r', '6.5');
    var handle = document.createElementNS(ns, 'path');
    handle.setAttribute('d', 'M15 15l6 6');
    [circle, handle].forEach(function (n) {
      n.setAttribute('fill', 'none'); n.setAttribute('stroke', 'currentColor');
      n.setAttribute('stroke-width', '2.4'); n.setAttribute('stroke-linecap', 'round');
      svg.appendChild(n);
    });
    return svg;
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
    backButton = el('button', {
      class: 'button button--secondary', id: 'app-back', type: 'button',
      onclick: function () { R.ui.router.back(); }
    }, ['\u2190 Retour']);
    var form = el('form', { class: 'searchbar-form', role: 'search', novalidate: true, onsubmit: function (event) {
      event.preventDefault();
      input.blur();            // referme le clavier sur mobile
    } }, [
      backButton,
      el('div', { class: 'searchbar-field' }, [
        el('label', { class: 'visually-hidden', 'for': 'search-input' }, ['Rechercher']),
        magnifier(),
        input
      ])
    ]);
    input.addEventListener('input', function () { R.ui.router.search(input.value); });
    root.appendChild(form);
    R.events.on('route:changed', sync);
    sync();
  }

  R.ns('ui.views').searchbar = { mount: mount };
})();
