/*
  js/ui/views/furniture.js — Application « Rangement »
  Version : V010
  Horodatage : 2026-10-26 15:33 (heure de Paris)
  Résumé : création — vue graphique d'un meuble (rectangle, pieds, sous-emplacements, nombre d'objets, détail des niveaux inférieurs) et commutateur Liste / Vue graphique.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;
  var plural = R.ui.dom.plural;

  var LEVEL_NAMES = ['Pièce', 'Emplacement', 'Sous-emplacement', 'Sous-sous-emplacement'];
  var editing = false;   // réglages de disposition affichés
  var focus = {};        // identifiant du meuble → identifiant du niveau inférieur actuellement dessiné
  var uid = 0;

  function levelName(depth) { return LEVEL_NAMES[depth] || ('Niveau ' + (depth + 1)); }

  // ---------- mode d'affichage (mémorisé sur l'appareil) ----------

  function mode() { return R.storage.getAux('view') === 'graphic' ? 'graphic' : 'list'; }

  function setMode(next) {
    if (next === mode()) { return; }
    R.storage.setAux('view', next);
    R.events.emit('view:changed', {});
  }

  function switcher() {
    var current = mode();
    function b(label, value) {
      return el('button', {
        class: 'button button--secondary view-switch-btn', type: 'button', 'aria-pressed': current === value ? 'true' : 'false',
        onclick: function () { setMode(value); }
      }, [label]);
    }
    return el('div', { class: 'view-switch', role: 'group', 'aria-label': 'Mode d\u2019affichage' }, [b('Liste', 'list'), b('Vue graphique', 'graphic')]);
  }

  // ---------- dessin ----------

  function control(label, node) {
    return el('label', { class: 'furn-ctl' }, [el('span', null, [label]), node]);
  }

  function select(options, value, onchange) {
    var s = el('select', null, options.map(function (o) { return el('option', { value: String(o.value) }, [o.label]); }));
    s.value = String(value);
    s.addEventListener('change', function () { onchange(s.value); });
    return s;
  }

  function nearestRatio(r) {
    var best = R.features.furniture.ratios[0];
    R.features.furniture.ratios.forEach(function (o) { if (Math.abs(o.value - r) < Math.abs(best.value - r)) { best = o; } });
    return best.value;
  }

  function controls(shownId) {
    var F = R.features.furniture;
    var g = F.get(shownId);
    var feet = el('input', { type: 'checkbox', checked: g.feet ? true : null });
    feet.addEventListener('change', function () { F.set(shownId, { feet: feet.checked }); });
    return el('div', { class: 'furn-controls' }, [
      control('Proportions', select(F.ratios, nearestRatio(g.ratio), function (v) { F.set(shownId, { ratio: Number(v) }); })),
      control('Colonnes', select([{ value: 0, label: 'Auto' }, { value: 1, label: '1' }, { value: 2, label: '2' }, { value: 3, label: '3' }, { value: 4, label: '4' }],
        g.cols, function (v) { F.set(shownId, { cols: Number(v) }); })),
      control('Pieds', feet)
    ]);
  }

  function cell(wrap, furnId, k, depth) {
    var F = R.features.furniture;
    var kidDepth = depth + 1;
    var n = R.store.countIn(k.id);
    var subs = R.store.childLocations(k.id).length;
    var kind = R.models.kindLabel(k.kind);
    var parts = [el('a', { class: 'furn-open', href: R.ui.router.href(k.id) }, [
      el('span', { class: 'furn-name' }, [k.name]),
      el('span', { class: 'furn-count' }, [plural(n.items, 'objet', 'objets')]),
      el('span', { class: 'furn-kind' }, ['Niveau ' + (kidDepth + 1) + ', ' + kind.toLowerCase()])
    ])];
    if (subs) {
      parts.push(el('button', {
        class: 'furn-more', type: 'button',
        'aria-label': 'Voir les ' + plural(subs, 'sous-emplacement', 'sous-emplacements') + ' de \u00ab ' + k.name + ' \u00bb (niveau ' + (kidDepth + 2) + ')',
        onclick: function () { focus[furnId] = k.id; draw(wrap, furnId); }
      }, [el('span', { class: 'furn-nest', 'aria-hidden': 'true' }), String(subs)]));
    }
    if (editing) {
      parts.push(el('div', { class: 'furn-edit' }, [
        el('button', { class: 'furn-tool', type: 'button', 'aria-label': 'Décaler \u00ab ' + k.name + ' \u00bb vers le début', onclick: function () { F.shift(k.id, -1); } }, ['\u25C0']),
        el('button', { class: 'furn-tool', type: 'button', 'aria-label': 'Décaler \u00ab ' + k.name + ' \u00bb vers la fin', onclick: function () { F.shift(k.id, 1); } }, ['\u25B6']),
        el('button', { class: 'furn-tool', type: 'button', 'aria-label': (F.span(k) === 2 ? 'Rétrécir' : 'Élargir') + ' \u00ab ' + k.name + ' \u00bb', onclick: function () { F.toggleSpan(k.id); } }, ['\u2194'])
      ]));
    }
    var node = el('div', { class: 'furn-cell', 'data-level': R.models.levelOf(kidDepth), 'data-span': String(F.span(k)) }, parts);
    return node;
  }

  function draw(wrap, furnId) {
    var F = R.features.furniture;
    R.ui.dom.clear(wrap);
    var shownId = focus[furnId];
    if (!shownId || !R.store.getLocation(shownId) || !R.store.pathOf(shownId).some(function (p) { return p.id === furnId; })) { shownId = furnId; }
    var loc = R.store.getLocation(shownId);
    var depth = R.store.depthOf(shownId);
    var level = R.models.levelOf(depth);
    var kids = F.ordered(shownId);
    var g = F.get(shownId);

    var caption = 'Niveau ' + (depth + 1) + ' \u2014 ' + levelName(depth) + ' \u00ab ' + loc.name + ' \u00bb' + (kids.length
      ? ' : ses ' + plural(kids.length, 'sous-emplacement', 'sous-emplacements') + ' (niveau ' + (depth + 2) + ') sont dessinés ci-dessous.'
      : ' : aucun sous-emplacement.');
    wrap.appendChild(el('p', { class: 'furn-caption', 'data-level': level }, [caption]));

    var bar = [];
    if (shownId !== furnId) {
      var up = loc.parentId;
      bar.push(el('button', {
        class: 'button button--secondary', type: 'button',
        onclick: function () { if (up === furnId) { delete focus[furnId]; } else { focus[furnId] = up; } draw(wrap, furnId); }
      }, ['\u2190 Remonter au niveau ' + depth]));
    }
    bar.push(el('button', {
      class: 'button button--secondary', type: 'button', 'aria-pressed': editing ? 'true' : 'false',
      onclick: function () { editing = !editing; draw(wrap, furnId); }
    }, [editing ? 'Terminer l\u2019ajustement' : 'Ajuster la disposition']));
    wrap.appendChild(el('div', { class: 'furn-bar' }, bar));
    if (editing) { wrap.appendChild(controls(shownId)); }

    var grid = el('div', { class: 'furn-grid' });
    if (kids.length) {
      grid.style.gridTemplateColumns = 'repeat(' + F.columns(shownId, kids.length) + ', minmax(0, 1fr))';
      kids.forEach(function (k) { grid.appendChild(cell(wrap, furnId, k, depth)); });
    } else {
      grid.appendChild(el('p', { class: 'furn-empty' }, ['Aucun sous-emplacement : les objets sont rangés directement ici.']));
    }
    var body = el('div', { class: 'furn-body', 'data-level': level }, [grid]);
    body.style.aspectRatio = String(g.ratio);
    var frame = [body];
    if (g.feet) { frame.push(el('div', { class: 'furn-feet', 'data-level': level }, [el('span', { class: 'furn-foot' }), el('span', { class: 'furn-foot' })])); }
    wrap.appendChild(el('div', { class: 'furn-frame' }, frame));

    var items = R.store.itemsIn(shownId);
    if (items.length) {
      wrap.appendChild(el('section', { class: 'section' }, [
        el('h3', { class: 'section-title' }, ['Objets rangés dans \u00ab ' + loc.name + ' \u00bb (niveau ' + (depth + 1) + ') : ' + items.length]),
        R.ui.components.list.create(items.map(function (it) {
          return {
            title: it.name, href: R.ui.router.itemHref(it.id), level: it.quantity === 0 ? 'zero' : 'objet', muted: it.quantity === 0,
            chips: (it.quantity !== 1 ? ['\u00d7 ' + R.features.items.formatQuantity(it.quantity)] : []).concat(it.tags)
          };
        }))
      ]));
    }
  }

  // Vue graphique du meuble `furnId` (emplacement de premier niveau).
  function create(furnId) {
    uid += 1;
    var wrap = el('div', { class: 'furn-view', id: 'furn-view-' + uid });
    draw(wrap, furnId);
    return wrap;
  }

  R.ns('ui.views').furniture = { create: create, switcher: switcher, mode: mode, setMode: setMode };
})();
