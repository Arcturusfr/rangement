/*
  js/ui/components/detailbar.js — Application « Rangement »
  Version : V009
  Horodatage : 2026-10-25 16:10 (heure de Paris)
  Résumé : création — en-tête figé du volet de détail (fil d'Ariane + titre), flèches de niveau, bouton replier la partie « gestion ».
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;

  var manageOpen = true;   // état de la partie « gestion » : conservé d'un écran à l'autre
  var lastDown = {};       // identifiant du parent ('' = racine) → dernier enfant affiché { type, id }

  // ref : { type: 'root' } | { type: 'location', id } | { type: 'item', id }
  function parentKey(ref) {
    if (ref.type === 'location') { var l = R.store.getLocation(ref.id); return l ? (l.parentId || '') : null; }
    if (ref.type === 'item') { var it = R.store.getItem(ref.id); return it ? it.locationId : null; }
    return null;
  }

  function remember(ref) {
    var key = parentKey(ref);
    if (key !== null) { lastDown[key] = { type: ref.type, id: ref.id }; }
  }

  function upTarget(ref) {
    if (ref.type === 'location') { var l = R.store.getLocation(ref.id); return R.ui.router.href(l ? l.parentId : null); }
    if (ref.type === 'item') { var it = R.store.getItem(ref.id); return it ? R.ui.router.href(it.locationId) : null; }
    return null;
  }

  // Niveau inférieur : le dernier enfant visité s'il existe encore, sinon le premier (emplacements, puis objets).
  function downTarget(ref) {
    if (ref.type === 'item') { return null; }
    var key = ref.type === 'root' ? '' : ref.id;
    var mem = lastDown[key];
    if (mem && mem.type === 'location') {
      var ml = R.store.getLocation(mem.id);
      if (ml && (ml.parentId || '') === key) { return R.ui.router.href(ml.id); }
    }
    if (mem && mem.type === 'item') {
      var mi = R.store.getItem(mem.id);
      if (mi && mi.locationId === key) { return R.ui.router.itemHref(mi.id); }
    }
    var kids = R.store.childLocations(key || null);
    if (kids.length) { return R.ui.router.href(kids[0].id); }
    if (ref.type === 'root') { return null; }
    var its = R.store.itemsIn(key);
    return its.length ? R.ui.router.itemHref(its[0].id) : null;
  }

  function arrow(glyph, label, target) {
    return target
      ? el('a', { class: 'button button--secondary button--icon', href: target, 'aria-label': label, title: label }, [glyph])
      : el('button', { class: 'button button--secondary button--icon', type: 'button', disabled: true, 'aria-label': label, title: label }, [glyph]);
  }

  // opts : { ref, path, currentLabel?, currentLevel?, title, level, depleted?, toolbar }
  // Renvoie { head, manage } : `head` est figé en haut du volet, `manage` contient la barre d'actions repliable.
  function create(opts) {
    remember(opts.ref);

    var toolbarId = 'manage-panel';
    var wrap = el('div', { class: 'manage', id: toolbarId, 'data-open': manageOpen ? 'true' : 'false' }, [
      el('div', { class: 'manage-inner' }, [opts.toolbar])
    ]);
    var caret = el('span', { 'aria-hidden': 'true' }, [manageOpen ? '\u25BE' : '\u25B8']);
    var toggle = el('button', {
      class: 'button button--secondary button--toggle', type: 'button',
      'aria-expanded': manageOpen ? 'true' : 'false', 'aria-controls': toolbarId, id: 'manage-toggle'
    }, ['Actions', caret]);
    toggle.addEventListener('click', function () {
      manageOpen = !manageOpen;
      wrap.setAttribute('data-open', manageOpen ? 'true' : 'false');
      toggle.setAttribute('aria-expanded', manageOpen ? 'true' : 'false');
      caret.textContent = manageOpen ? '\u25BE' : '\u25B8';
    });

    var nodes = [];
    if (opts.path.length || opts.currentLabel) {
      nodes.push(R.ui.components.breadcrumb.create(opts.path, opts.currentLabel, opts.currentLevel));
    }
    nodes.push(el('header', { class: 'detail-head detail-bar' + (opts.depleted ? ' detail-head--depleted' : ''), 'data-level': opts.level }, [
      el('h2', { class: 'detail-title' }, [opts.title]),
      el('div', { class: 'detail-bar-tools' }, [
        arrow('\u25B2', 'Niveau supérieur', upTarget(opts.ref)),
        arrow('\u25BC', 'Niveau inférieur', downTarget(opts.ref)),
        toggle
      ])
    ]));
    return { head: el('div', { class: 'detail-sticky' }, nodes), manage: wrap };
  }

  R.ns('ui.components').detailbar = { create: create };
})();
