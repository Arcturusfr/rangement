/*
  js/ui/views/furniture.js — Application « Rangement »
  Version : V011
  Horodatage : 2026-10-30 00:22 (heure de Paris)
  Résumé : vue graphique sur grille (cases, tailles en cases, bandes au-dessus / en dessous), sélection et déplacement d'un emplacement, débordements corrigés.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;
  var plural = R.ui.dom.plural;

  var LEVEL_NAMES = ['Pièce', 'Emplacement', 'Sous-emplacement', 'Sous-sous-emplacement'];
  var ZONE_LABELS = { top: 'Au-dessus du meuble', body: 'Dans le meuble', bottom: 'En dessous du meuble' };
  var ROW_MIN = 64;       // hauteur minimale d'une ligne du meuble (px) : le cadre grandit plutôt que de laisser déborder
  var BAND_ROW = 56;      // hauteur d'une ligne d'une bande (px)
  var editing = false;    // réglages de disposition affichés
  var selected = null;    // emplacement sélectionné (mode ajustement)
  var message = null;     // refus à afficher une fois
  var focus = {};         // identifiant du meuble → niveau inférieur actuellement dessiné
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

  // ---------- réglages ----------

  function control(label, node) { return el('label', { class: 'furn-ctl' }, [el('span', null, [label]), node]); }

  function select(options, value, onchange) {
    var s = el('select', null, options.map(function (o) { return el('option', { value: String(o.value) }, [o.label]); }));
    s.value = String(value);
    s.addEventListener('change', function () { onchange(s.value); });
    return s;
  }

  function range(min, max, current) {
    var out = [];
    for (var i = min; i <= max; i++) { out.push({ value: i, label: String(i) }); }
    if (current > max) { out.push({ value: current, label: String(current) }); }
    return out;
  }

  function nearestRatio(r) {
    var best = R.features.furniture.ratios[0];
    R.features.furniture.ratios.forEach(function (o) { if (Math.abs(o.value - r) < Math.abs(best.value - r)) { best = o; } });
    return best.value;
  }

  // Exécute une action sur la grille ; un refus s'affiche, un succès redessine par l'événement `store:changed`.
  function run(redraw, res) {
    if (!res.ok) { message = res.error; redraw(); }
  }

  function controls(shownId, lay, redraw) {
    var F = R.features.furniture;
    var g = F.get(shownId);
    var L = F.limits;
    var feet = el('input', { type: 'checkbox', checked: g.feet ? true : null });
    feet.addEventListener('change', function () { run(redraw, F.set(shownId, { feet: feet.checked })); });
    function grid(key) { return function (v) { var p = {}; p[key] = Number(v); run(redraw, F.setGrid(shownId, p)); }; }
    return el('div', { class: 'furn-controls' }, [
      control('Proportions', select(F.ratios, nearestRatio(g.ratio), function (v) { run(redraw, F.set(shownId, { ratio: Number(v) })); })),
      control('Colonnes', select(range(1, L.cols, lay.C), lay.C, grid('cols'))),
      control('Lignes', select(range(1, L.rows, lay.L), lay.L, grid('rows'))),
      control('Dessus', select(range(0, L.band, lay.T), lay.T, grid('top'))),
      control('Dessous', select(range(0, L.band, lay.B), lay.B, grid('bottom'))),
      control('Pieds', feet)
    ]);
  }

  function selectionPanel(c, lay, redraw) {
    var F = R.features.furniture;
    var loc = R.store.getLocation(c.id);
    function b(label, fn) { return el('button', { class: 'button button--secondary', type: 'button', onclick: function () { run(redraw, fn()); } }, [label]); }
    return el('div', { class: 'furn-sel', role: 'group', 'aria-label': 'Emplacement sélectionné' }, [
      el('p', { class: 'furn-sel-text' }, ['Sélection : \u00ab ' + loc.name + ' \u00bb \u2014 ' + ZONE_LABELS[c.zone].toLowerCase() + ', colonne ' + (c.col + 1) + ', ligne ' + (c.row + 1) + ', taille ' + c.w + ' \u00d7 ' + c.h + ' (cases).']),
      el('div', { class: 'furn-sel-tools' }, [
        b('\u25C0 Décaler à gauche', function () { return F.move(c.id, -1, 0); }),
        b('Décaler à droite \u25B6', function () { return F.move(c.id, 1, 0); }),
        b('\u25B2 Décaler vers le haut', function () { return F.move(c.id, 0, -1); }),
        b('\u25BC Décaler vers le bas', function () { return F.move(c.id, 0, 1); }),
        b('Largeur \u2212', function () { return F.resize(c.id, -1, 0); }),
        b('Largeur +', function () { return F.resize(c.id, 1, 0); }),
        b('Hauteur \u2212', function () { return F.resize(c.id, 0, -1); }),
        b('Hauteur +', function () { return F.resize(c.id, 0, 1); })
      ])
    ]);
  }

  // ---------- dessin ----------

  function place(node, c) {
    node.style.gridColumn = (c.col + 1) + ' / span ' + c.w;
    node.style.gridRow = (c.row + 1) + ' / span ' + c.h;
  }

  function cell(wrap, furnId, c, depth, redraw) {
    var kidDepth = depth + 1;
    var k = R.store.getLocation(c.id);
    var n = R.store.countIn(k.id);
    var subs = R.store.childLocations(k.id).length;
    var isSel = editing && selected === k.id;
    var inner = [
      el('span', { class: 'furn-name' + (c.h > 1 ? ' furn-name--wrap' : '') }, [k.name]),
      el('span', { class: 'furn-count' }, [plural(n.items, 'objet', 'objets')]),
      c.w * c.h >= 2 ? el('span', { class: 'furn-kind' }, ['Niveau ' + (kidDepth + 1) + ', ' + R.models.kindLabel(k.kind).toLowerCase()]) : null
    ];
    var open = editing
      ? el('button', { class: 'furn-open', type: 'button', 'aria-pressed': isSel ? 'true' : 'false', onclick: function () { selected = k.id; redraw(); } }, inner)
      : el('a', { class: 'furn-open', href: R.ui.router.href(k.id) }, inner);
    var parts = [open];
    if (subs) {
      parts.push(el('button', {
        class: 'furn-more', type: 'button',
        'aria-label': 'Voir les ' + plural(subs, 'sous-emplacement', 'sous-emplacements') + ' de \u00ab ' + k.name + ' \u00bb (niveau ' + (kidDepth + 2) + ')',
        onclick: function () { focus[furnId] = k.id; selected = null; redraw(); }
      }, [el('span', { class: 'furn-nest', 'aria-hidden': 'true' }), String(subs)]));
    }
    var node = el('div', { class: 'furn-cell' + (isSel ? ' is-selected' : ''), 'data-level': R.models.levelOf(kidDepth), title: k.name + ' \u2014 ' + plural(n.items, 'objet', 'objets') }, parts);
    place(node, c);
    return node;
  }

  function draw(wrap, furnId) {
    var F = R.features.furniture;
    var redraw = function () { draw(wrap, furnId); };
    R.ui.dom.clear(wrap);
    var shownId = focus[furnId];
    if (!shownId || !R.store.getLocation(shownId) || !R.store.pathOf(shownId).some(function (p) { return p.id === furnId; })) { shownId = furnId; }
    var loc = R.store.getLocation(shownId);
    var depth = R.store.depthOf(shownId);
    var level = R.models.levelOf(depth);
    var lay = F.layout(shownId);
    var g = F.get(shownId);
    var sel = editing ? lay.cells.filter(function (c) { return c.id === selected; })[0] : null;
    var kidsCount = lay.cells.length;

    wrap.appendChild(el('p', { class: 'furn-caption', 'data-level': level }, ['Niveau ' + (depth + 1) + ' \u2014 ' + levelName(depth) + ' \u00ab ' + loc.name + ' \u00bb' + (kidsCount
      ? ' : ses ' + plural(kidsCount, 'sous-emplacement', 'sous-emplacements') + ' (niveau ' + (depth + 2) + ') sont dessinés ci-dessous.'
      : ' : aucun sous-emplacement.')]));

    var bar = [];
    if (shownId !== furnId) {
      var up = loc.parentId;
      bar.push(el('button', {
        class: 'button button--secondary', type: 'button',
        onclick: function () { if (up === furnId) { delete focus[furnId]; } else { focus[furnId] = up; } selected = null; redraw(); }
      }, ['\u2190 Remonter au niveau ' + depth]));
    }
    bar.push(el('button', {
      class: 'button button--secondary', type: 'button', 'aria-pressed': editing ? 'true' : 'false',
      onclick: function () { editing = !editing; selected = null; message = null; redraw(); }
    }, [editing ? 'Terminer l\u2019ajustement' : 'Ajuster la disposition']));
    wrap.appendChild(el('div', { class: 'furn-bar' }, bar));
    if (editing) { wrap.appendChild(controls(shownId, lay, redraw)); }
    if (message) { wrap.appendChild(el('p', { class: 'form-error furn-msg', role: 'status' }, [message])); message = null; }
    if (sel) { wrap.appendChild(selectionPanel(sel, lay, redraw)); }
    else if (editing && kidsCount) { wrap.appendChild(el('p', { class: 'hint' }, ['Touchez un emplacement pour le sélectionner, puis déplacez-le ou changez sa taille ; une case libre y place l\u2019emplacement sélectionné.'])); }

    var start = { top: 0, body: lay.T, bottom: lay.T + lay.L };
    function zoneGrid(zone, rows) {
      var grid = el('div', { class: 'furn-grid', 'data-zone': zone });
      grid.style.gridTemplateColumns = 'repeat(' + lay.C + ', minmax(0, 1fr))';
      grid.style.gridTemplateRows = zone === 'body' ? 'repeat(' + rows + ', minmax(0, 1fr))' : 'repeat(' + rows + ', ' + BAND_ROW + 'px)';
      var taken = {};
      lay.cells.filter(function (c) { return c.zone === zone; }).forEach(function (c) {
        for (var i = c.row; i < c.row + c.h; i++) { for (var j = c.col; j < c.col + c.w; j++) { taken[i + ',' + j] = true; } }
        grid.appendChild(cell(wrap, furnId, c, depth, redraw));
      });
      if (editing) {
        for (var r = 0; r < rows; r++) {
          for (var c0 = 0; c0 < lay.C; c0++) {
            if (taken[r + ',' + c0]) { continue; }
            (function (row, col) {
              var slot = el('button', {
                class: 'furn-slot', type: 'button', 'aria-label': 'Case libre : colonne ' + (col + 1) + ', ligne ' + (row + 1) + ' (' + ZONE_LABELS[zone].toLowerCase() + ')',
                onclick: function () {
                  if (!sel) { message = 'Sélectionnez d\u2019abord un emplacement à déplacer.'; redraw(); return; }
                  run(redraw, F.move(sel.id, col - sel.col, (start[zone] + row) - (start[sel.zone] + sel.row)));
                }
              });
              place(slot, { col: col, row: row, w: 1, h: 1 });
              grid.appendChild(slot);
            })(r, c0);
          }
        }
      }
      return grid;
    }
    function band(zone, rows) {
      return el('div', { class: 'furn-band', 'data-zone': zone }, [el('p', { class: 'furn-band-label' }, [ZONE_LABELS[zone]]), zoneGrid(zone, rows)]);
    }

    var frame = [];
    if (lay.T) { frame.push(band('top', lay.T)); }
    var bodyContent = (!kidsCount && !editing)
      ? el('p', { class: 'furn-empty' }, ['Aucun sous-emplacement : les objets sont rangés directement ici.'])
      : zoneGrid('body', lay.L);
    var body = el('div', { class: 'furn-body', 'data-level': level }, [bodyContent]);
    body.style.aspectRatio = String(g.ratio);
    body.style.minHeight = (lay.L * ROW_MIN) + 'px';
    frame.push(body);
    if (g.feet) { frame.push(el('div', { class: 'furn-feet', 'data-level': level }, [el('span', { class: 'furn-foot' }), el('span', { class: 'furn-foot' })])); }
    if (lay.B) { frame.push(band('bottom', lay.B)); }
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
