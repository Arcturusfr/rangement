/*
  js/ui/views/furniture.js — Application « Rangement »
  Version : V013
  Horodatage : 2026-11-01 12:00 (heure de Paris)
  Résumé : plan du logement : la même grille dessine les pièces (createPlan, commutateur Liste / Plan, réglages colonnes et lignes), mode d'ajustement réinitialisé au changement d'écran.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;
  var plural = R.ui.dom.plural;

  var LEVEL_NAMES = ['Pièce', 'Emplacement', 'Sous-emplacement', 'Sous-sous-emplacement'];
  var ZONE_LABELS = { top: 'Au-dessus du meuble', body: 'Dans le meuble', bottom: 'En dessous du meuble' };
  var PLAN_COL = 72;      // largeur minimale d'une colonne du plan (px) : au-delà, le plan défile horizontalement dans son cadre
  var ROW_MIN = 64;       // hauteur minimale d'une ligne du meuble (px) : le cadre grandit plutôt que de laisser déborder
  var BAND_ROW = 56;      // hauteur d'une ligne d'une bande (px)
  var editing = false;    // réglages de disposition affichés
  var selected = null;    // emplacement sélectionné (mode ajustement)
  var message = null;     // refus à afficher une fois
  var focus = {};         // identifiant du meuble → niveau inférieur actuellement dessiné
  var uid = 0;

  // Libellé d'une zone ; dans le plan du logement il n'y a qu'une zone : le plan.
  function zoneLabel(zone, atRoot) { return atRoot ? 'Dans le plan' : ZONE_LABELS[zone]; }

  function levelName(depth) { return LEVEL_NAMES[depth] || ('Niveau ' + (depth + 1)); }

  // ---------- mode d'affichage (mémorisé sur l'appareil) ----------

  // scope 'plan' : choix propre au logement (clé annexe `planview`) ; sinon celui des meubles (clé `view`).
  function viewKey(scope) { return scope === 'plan' ? 'planview' : 'view'; }

  function mode(scope) { return R.storage.getAux(viewKey(scope)) === 'graphic' ? 'graphic' : 'list'; }

  function setMode(next, scope) {
    if (next === mode(scope)) { return; }
    R.storage.setAux(viewKey(scope), next);
    R.events.emit('view:changed', {});
  }

  function switcher(scope) {
    var current = mode(scope);
    function b(label, value) {
      return el('button', {
        class: 'button button--secondary view-switch-btn', type: 'button', 'aria-pressed': current === value ? 'true' : 'false',
        onclick: function () { setMode(value, scope); }
      }, [label]);
    }
    return el('div', { class: 'view-switch', role: 'group', 'aria-label': 'Mode d\u2019affichage' }, [b('Liste', 'list'), b(scope === 'plan' ? 'Plan' : 'Vue graphique', 'graphic')]);
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
    var L = F.limitsFor(shownId);
    if (F.isRoot(shownId)) {
      var gridRoot = function (key) { return function (v) { var p = {}; p[key] = Number(v); run(redraw, F.setGrid(shownId, p)); }; };
      return el('div', { class: 'furn-controls' }, [
        control('Colonnes', select(range(1, L.cols, lay.C), lay.C, gridRoot('cols'))),
        control('Lignes', select(range(1, L.rows, lay.L), lay.L, gridRoot('rows')))
      ]);
    }
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

  // Pavé de quatre flèches (sans libellé visible : le nom accessible est dans aria-label).
  function pad(name, center, keys) {
    var nodes = keys.map(function (k) {
      return el('button', { class: 'furn-pad-btn furn-pad-' + k.dir, type: 'button', 'aria-label': k.label, title: k.label, onclick: k.run }, [k.glyph]);
    });
    nodes.push(el('span', { class: 'furn-pad-mid', 'aria-hidden': 'true' }, [center]));
    return el('div', { class: 'furn-pad', role: 'group', 'aria-label': name }, nodes);
  }

  function selectionPanel(c, lay, redraw, atRoot) {
    var F = R.features.furniture;
    var loc = R.store.getLocation(c.id);
    function k(dir, glyph, label, fn) { return { dir: dir, glyph: glyph, label: label, run: function () { run(redraw, fn()); } }; }
    return el('div', { class: 'furn-sel', role: 'group', 'aria-label': 'Emplacement sélectionné' }, [
      el('p', { class: 'furn-sel-text' }, ['Sélection : \u00ab ' + loc.name + ' \u00bb \u2014 ' + zoneLabel(c.zone, atRoot).toLowerCase() + ', colonne ' + (c.col + 1) + ', ligne ' + (c.row + 1) + ', taille ' + c.w + ' \u00d7 ' + c.h + ' (cases).']),
      pad('Déplacer', '\u271B', [
        k('up', '\u25B2', 'Décaler vers le haut', function () { return F.move(c.id, 0, -1); }),
        k('left', '\u25C0', 'Décaler à gauche', function () { return F.move(c.id, -1, 0); }),
        k('right', '\u25B6', 'Décaler à droite', function () { return F.move(c.id, 1, 0); }),
        k('down', '\u25BC', 'Décaler vers le bas', function () { return F.move(c.id, 0, 1); })
      ]),
      pad('Taille', '\u25AD', [
        k('up', '+', 'Hauteur +', function () { return F.resize(c.id, 0, 1); }),
        k('left', '\u2212', 'Largeur \u2212', function () { return F.resize(c.id, -1, 0); }),
        k('right', '+', 'Largeur +', function () { return F.resize(c.id, 1, 0); }),
        k('down', '\u2212', 'Hauteur \u2212', function () { return F.resize(c.id, 0, -1); })
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
    var pane = wrap.closest ? wrap.closest('.pane') : null;     // le défilement ne doit pas remonter à chaque action
    var scrollTop = pane ? pane.scrollTop : 0;
    R.ui.dom.clear(wrap);
    var rootMode = F.isRoot(furnId);          // plan du logement : les pièces sont les cases
    var shownId = focus[furnId];
    if (!shownId || !R.store.getLocation(shownId) || (!rootMode && !R.store.pathOf(shownId).some(function (p) { return p.id === furnId; }))) { shownId = furnId; }
    var atRoot = F.isRoot(shownId);
    var loc = atRoot ? null : R.store.getLocation(shownId);
    var depth = atRoot ? -1 : R.store.depthOf(shownId);
    var level = atRoot ? 'racine' : R.models.levelOf(depth);
    var lay = F.layout(shownId);
    var g = F.get(shownId);
    var sel = editing ? lay.cells.filter(function (c) { return c.id === selected; })[0] : null;
    var kidsCount = lay.cells.length;

    wrap.appendChild(el('p', { class: 'furn-caption', 'data-level': level }, [atRoot
      ? 'Plan du logement' + (kidsCount ? ' : ses ' + plural(kidsCount, 'pièce', 'pièces') + ' (niveau 1) sont dessinées ci-dessous.' : ' : aucune pièce.')
      : 'Niveau ' + (depth + 1) + ' \u2014 ' + levelName(depth) + ' \u00ab ' + loc.name + ' \u00bb' + (kidsCount
        ? ' : ses ' + plural(kidsCount, 'sous-emplacement', 'sous-emplacements') + ' (niveau ' + (depth + 2) + ') sont dessinés ci-dessous.'
        : ' : aucun sous-emplacement.')]));

    var bar = [];
    if (shownId !== furnId) {
      var up = loc.parentId;
      bar.push(el('button', {
        class: 'button button--secondary', type: 'button',
        onclick: function () { if (up === furnId || (rootMode && !up)) { delete focus[furnId]; } else { focus[furnId] = up; } selected = null; redraw(); }
      }, [rootMode && depth === 0 ? '\u2190 Remonter au plan du logement' : '\u2190 Remonter au niveau ' + depth]));
    }
    bar.push(el('button', {
      class: 'button button--secondary', type: 'button', 'aria-pressed': editing ? 'true' : 'false',
      onclick: function () { editing = !editing; selected = null; message = null; redraw(); }
    }, [editing ? 'Terminer l\u2019ajustement' : (atRoot ? 'Ajuster le plan' : 'Ajuster la disposition')]));
    wrap.appendChild(el('div', { class: 'furn-bar' }, bar));
    if (editing) { wrap.appendChild(controls(shownId, lay, redraw)); }
    if (message) { wrap.appendChild(el('p', { class: 'form-error furn-msg', role: 'status' }, [message])); message = null; }
    if (!sel && editing && kidsCount) { wrap.appendChild(el('p', { class: 'hint' }, [atRoot ? 'Touchez une pièce pour la sélectionner, puis déplacez-la ou changez sa taille ; une case libre y place la pièce sélectionnée.' : 'Touchez un emplacement pour le sélectionner, puis déplacez-le ou changez sa taille ; une case libre y place l\u2019emplacement sélectionné.'])); }

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
                class: 'furn-slot', type: 'button', 'aria-label': 'Case libre : colonne ' + (col + 1) + ', ligne ' + (row + 1) + ' (' + zoneLabel(zone, atRoot).toLowerCase() + ')',
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
      return el('div', { class: 'furn-band', 'data-zone': zone }, [el('p', { class: 'furn-band-label' }, [zoneLabel(zone, atRoot)]), zoneGrid(zone, rows)]);
    }

    var frame = [];
    if (lay.T) { frame.push(band('top', lay.T)); }
    var bodyContent = (!kidsCount && !editing)
      ? el('p', { class: 'furn-empty' }, [atRoot ? 'Aucune pièce à dessiner.' : 'Aucun sous-emplacement : les objets sont rangés directement ici.'])
      : zoneGrid('body', lay.L);
    var body = el('div', { class: 'furn-body', 'data-level': level }, [bodyContent]);
    if (atRoot) {         // plan : cases à peu près carrées, le cadre défile horizontalement si les colonnes sont nombreuses
      body.style.aspectRatio = lay.C + ' / ' + lay.L;
      body.style.minWidth = (lay.C * PLAN_COL) + 'px';
    } else {
      body.style.aspectRatio = String(g.ratio);
    }
    body.style.minHeight = (lay.L * ROW_MIN) + 'px';
    frame.push(body);
    if (g.feet) { frame.push(el('div', { class: 'furn-feet', 'data-level': level }, [el('span', { class: 'furn-foot' }), el('span', { class: 'furn-foot' })])); }
    if (lay.B) { frame.push(band('bottom', lay.B)); }
    wrap.appendChild(el('div', { class: 'furn-frame' + (atRoot ? ' furn-frame--plan' : '') }, frame));
    if (sel) { wrap.appendChild(selectionPanel(sel, lay, redraw, atRoot)); }

    var items = atRoot ? [] : R.store.itemsIn(shownId);
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
    if (pane) { pane.scrollTop = scrollTop; }
  }

  // Vue graphique du meuble `furnId` (emplacement de premier niveau).
  function create(furnId) {
    uid += 1;
    var wrap = el('div', { class: 'furn-view', id: 'furn-view-' + uid });
    draw(wrap, furnId);
    return wrap;
  }

  // Plan du logement : la même grille, où les cases sont les pièces.
  function createPlan() { return create(R.features.furniture.ROOT); }

  // Un changement d'écran referme l'ajustement (il ne doit pas suivre d'un meuble ou d'un plan à l'autre).
  R.events.on('route:changed', function () { editing = false; selected = null; message = null; });

  R.ns('ui.views').furniture = { create: create, createPlan: createPlan, switcher: switcher, mode: mode, setMode: setMode };
})();
