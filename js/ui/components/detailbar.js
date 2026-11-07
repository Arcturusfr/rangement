/*
  js/ui/components/detailbar.js — Application « Rangement »
  Version : V016
  Horodatage : 2026-11-06 12:00 (heure de Paris)
  Résumé : jalon 9.3 — en-tête figé : nom + ℹ️ (info-bulle) + libellé de catégorie (chevron si tronqué) ; flèches de niveau et « Actions » (menu déroulant) ; commutateur Liste / Plan dessous, sans bande supplémentaire.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;

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

  // Libellé de catégorie à la suite du nom : tronqué si la place manque, avec un chevron qui ouvre une bulle avec le libellé complet.
  function kindNode(kind, level) {
    var text = el('span', { class: 'detail-kind-text' }, [kind]);
    var more = el('button', {
      class: 'kind-more', type: 'button', hidden: true, 'aria-haspopup': 'dialog', 'aria-expanded': 'false',
      'aria-label': 'Afficher le libellé complet : ' + kind, title: kind
    }, [el('span', { class: 'kind-chev', 'aria-hidden': 'true' }, ['\u25BE'])]);
    more.addEventListener('click', function () {
      R.ui.components.bubble.toggle({ anchor: more, lines: [kind], level: level, label: 'Libellé complet' });
    });
    var node = el('span', { class: 'detail-kind' }, [text, more]);

    function refresh() {
      if (!text.isConnected) { return; }
      more.hidden = true;                                   // on mesure sans le chevron : s'il n'y a pas de troncature, il reste caché
      more.hidden = !(text.scrollWidth > text.clientWidth + 1);
    }
    function schedule() {
      refresh();
      if (window.requestAnimationFrame) { window.requestAnimationFrame(function () { refresh(); window.requestAnimationFrame(refresh); }); }
    }
    function onResize() {
      if (!text.isConnected) { window.removeEventListener('resize', onResize); return; }
      refresh();
    }
    window.addEventListener('resize', onResize);
    node._refresh = schedule;
    return node;
  }

  // opts : { ref, path, currentLabel?, currentLevel?, title, level, depleted?, kind?, info?: string[], actions?: [{ label, run, danger? }], switcher?: Node }
  // Renvoie { head } : l'en-tête, figé en haut du volet.
  function create(opts) {
    remember(opts.ref);

    var tools = [
      arrow('\u25B2', 'Niveau supérieur', upTarget(opts.ref)),
      arrow('\u25BC', 'Niveau inférieur', downTarget(opts.ref))
    ];
    if (opts.actions && opts.actions.length) {
      var toggle = el('button', {
        class: 'button button--secondary button--toggle', type: 'button', id: 'manage-toggle', 'aria-haspopup': 'true'
      }, ['Actions', el('span', { 'aria-hidden': 'true' }, ['\u25BE'])]);
      toggle.addEventListener('click', function () {
        R.ui.components.contextmenu.open({
          anchor: toggle, title: opts.title, subtitle: 'Actions', label: 'Actions', level: opts.level, items: opts.actions
        });
      });
      tools.push(toggle);
    }

    var row = [el('h2', { class: 'detail-title' }, [opts.title])];
    if (opts.info && opts.info.length) {
      var infoBtn = el('button', {
        class: 'info-btn', type: 'button', id: 'info-toggle', 'aria-haspopup': 'dialog', 'aria-expanded': 'false',
        'aria-label': 'Informations sur \u00ab ' + opts.title + ' \u00bb', title: 'Informations'
      }, [el('span', { class: 'info-glyph', 'aria-hidden': 'true' }, ['i'])]);
      infoBtn.addEventListener('click', function () {
        R.ui.components.bubble.toggle({ anchor: infoBtn, title: opts.title, lines: opts.info, level: opts.level, label: 'Informations' });
      });
      row.push(infoBtn);
    }
    var kind = opts.kind ? kindNode(opts.kind, opts.level) : null;
    if (kind) { row.push(kind); }

    var left = [];
    if (opts.path.length || opts.currentLabel) {
      left.push(R.ui.components.breadcrumb.create(opts.path, opts.currentLabel, opts.currentLevel));
    }
    left.push(el('div', { class: 'detail-titlerow' + (opts.depleted ? ' detail-head--depleted' : '') }, row));

    var right = [el('div', { class: 'detail-bar-tools-row' }, tools)];
    if (opts.switcher) { right.push(opts.switcher); }

    var header = el('header', { class: 'detail-bar', 'data-level': opts.level }, [
      el('div', { class: 'detail-bar-left' }, left),
      el('div', { class: 'detail-bar-tools' }, right)
    ]);
    var head = el('div', { class: 'detail-sticky' }, [header]);
    if (kind) { kind._refresh(); }
    return { head: head };
  }

  R.ns('ui.components').detailbar = { create: create };
})();
