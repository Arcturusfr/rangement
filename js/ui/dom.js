/*
  js/ui/dom.js — Application « Rangement »
  Version : V003
  Horodatage : 2026-10-22 21:39 (heure de Paris)
  Résumé : création — aides de construction du DOM (texte toujours échappé).
*/
(function () {
  'use strict';

  var R = window.Rangement;

  function append(parent, child) {
    if (child === null || child === undefined || child === false) { return; }
    if (Array.isArray(child)) { child.forEach(function (c) { append(parent, c); }); return; }
    parent.appendChild(typeof child === 'object' ? child : document.createTextNode(String(child)));
  }

  // el('a', { class: 'x', href: '#/' }, ['texte', autreNoeud])
  // Les chaînes sont insérées comme texte : jamais interprétées comme du HTML.
  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (key) {
      var value = attrs[key];
      if (value === null || value === undefined || value === false) { return; }
      if (key === 'class') { node.className = value; }
      else if (key.indexOf('on') === 0 && typeof value === 'function') { node.addEventListener(key.slice(2), value); }
      else { node.setAttribute(key, value === true ? '' : value); }
    });
    append(node, children);
    return node;
  }

  function clear(node) {
    while (node.firstChild) { node.removeChild(node.firstChild); }
  }

  // plural(2, 'objet', 'objets') → « 2 objets »
  function plural(n, one, many) {
    return n + ' ' + (n > 1 ? many : one);
  }

  R.ns('ui').dom = { el: el, clear: clear, plural: plural };
})();
