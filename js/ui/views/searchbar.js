/*
  js/ui/views/searchbar.js — Application « Rangement »
  Version : V020
  Horodatage : 2026-11-20 22:57 (heure de Paris)
  Résumé : V020 : champ de recherche masqué par défaut, ouvert par le bouton loupe de l'en-tête ; bouton Retour (pictogramme) dans l'en-tête.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;
  var bar = null;
  var input = null;
  var backButton = null;
  var toggleButton = null;
  var open = false;

  // Le champ reflète la recherche de la route ; hors recherche il est vide. Une recherche en cours affiche toujours le champ.
  function sync() {
    var q = R.ui.router.current().query;
    var wanted = q === null ? '' : q;
    if (q !== null && !open) { setOpen(true, true); }
    if (input.value !== wanted) { input.value = wanted; }
    backButton.disabled = !R.ui.router.canBack();
  }

  // Affiche ou masque le champ ; noFocus : sans donner le focus (clavier virtuel).
  function setOpen(next, noFocus) {
    open = !!next;
    bar.hidden = !open;
    toggleButton.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggleButton.setAttribute('title', open ? 'Masquer la recherche' : 'Rechercher');
    if (open && !noFocus) { input.focus(); }
  }

  function toggle() {
    if (open) {
      setOpen(false);
      if (R.ui.router.current().query !== null) { R.ui.router.back(); }     // quitter les résultats de recherche
    } else {
      setOpen(true);
    }
  }

  function mount(root) {
    bar = root;
    backButton = document.getElementById('app-back');
    toggleButton = document.getElementById('search-toggle');
    backButton.appendChild(R.ui.icons.create('arrow-left', 22));
    toggleButton.appendChild(R.ui.icons.create('search', 22));
    backButton.addEventListener('click', function () { R.ui.router.back(); });
    toggleButton.addEventListener('click', toggle);

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
      el('div', { class: 'searchbar-field' }, [
        el('label', { class: 'visually-hidden', 'for': 'search-input' }, ['Rechercher']),
        R.ui.icons.create('search', 20),
        input
      ])
    ]);
    form.querySelector('svg').setAttribute('class', 'searchbar-icon');
    input.addEventListener('input', function () { R.ui.router.search(input.value); });
    root.appendChild(form);
    R.events.on('route:changed', sync);
    sync();
  }

  R.ns('ui.views').searchbar = { mount: mount, setOpen: setOpen, isOpen: function () { return open; } };
})();
