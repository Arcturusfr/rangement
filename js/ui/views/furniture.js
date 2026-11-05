/*
  js/ui/views/furniture.js — Application « Rangement »
  Version : V015a
  Horodatage : 2026-11-05 02:30 (heure de Paris)
  Résumé : correctif : le niveau inférieur ouvert (icône de niveau) est oublié à chaque changement d'écran. Jalon 9.2 — un appui sur une case ouvre un menu contextuel (« Ouvrir » en tête, puis les commandes de l'élément) ; bouton « + » flottant (créer, régler la grille) ; réglages de grille dans une boîte de dialogue ; pavés de flèches avec « Grille… » et « Terminer » (le bouton « Ajuster » disparaît).
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;
  var plural = R.ui.dom.plural;

  var LEVEL_NAMES = ['Pièce', 'Emplacement', 'Sous-emplacement', 'Sous-sous-emplacement'];
  var ZONE_LABELS = { top: 'Au-dessus du meuble', body: 'Dans le meuble', bottom: 'En dessous du meuble' };
  var MIN_CELL = 28;      // taille minimale d'une case du plan ajusté (px) : en dessous, le cadre défile plutôt que de rétrécir encore
  var FIT_CELL = 48;      // la hauteur de l'écran ne réduit pas les cases en dessous de cette taille (la page défile alors)
  var COMPACT = 60;       // en dessous de cette taille de case (px), les tuiles n'affichent plus que l'essentiel
  var REAL_CELL = 72;     // taille minimale d'une case en « taille réelle » (px)
  var PLAN_COL = 72;      // largeur minimale d'une colonne du plan (px) : au-delà, le plan défile horizontalement dans son cadre
  var ROW_MIN = 64;       // hauteur minimale d'une ligne du meuble (px) : le cadre grandit plutôt que de laisser déborder
  var BAND_ROW = 56;      // hauteur d'une ligne d'une bande (px)
  var editing = false;    // réglages de disposition affichés
  var selected = null;    // emplacement sélectionné (mode ajustement)
  var message = null;     // refus à afficher une fois
  var focus = {};         // identifiant du meuble → niveau inférieur actuellement dessiné
  var uid = 0;

  // Plan « taille réelle » (défilement) ou « ajusté à l'écran » (choix mémorisé sur l'appareil).
  function zoomReal() { return R.storage.getAux('planzoom') === 'real'; }

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

  // Réglages de la grille de `shownId` (boîte de dialogue) : colonnes et lignes ; pour un meuble, aussi proportions, dessus, dessous et pieds.
  function openGrid(shownId) {
    var F = R.features.furniture;
    var lay = F.layout(shownId);
    var g = F.get(shownId);
    var L = F.limitsFor(shownId);
    var planLike = F.isPlanLike(shownId);
    var loc = F.isRoot(shownId) ? null : R.store.getLocation(shownId);
    var fields = [
      { name: 'cols', label: 'Colonnes', type: 'select', options: range(1, L.cols, lay.C), value: lay.C },
      { name: 'rows', label: 'Lignes', type: 'select', options: range(1, L.rows, lay.L), value: lay.L }
    ];
    if (!planLike) {
      fields.push(
        { name: 'ratio', label: 'Proportions', type: 'select', options: F.ratios, value: nearestRatio(g.ratio) },
        { name: 'top', label: 'Dessus', type: 'select', options: range(0, L.band, lay.T), value: lay.T },
        { name: 'bottom', label: 'Dessous', type: 'select', options: range(0, L.band, lay.B), value: lay.B },
        { name: 'feet', label: 'Pieds', type: 'select', options: [{ value: '0', label: 'Sans' }, { value: '1', label: 'Avec' }], value: g.feet ? '1' : '0' }
      );
    }
    R.ui.components.dialog.form({
      title: 'Grille de \u00ab ' + (loc ? loc.name : R.models.rootLabel()) + ' \u00bb',
      fields: fields,
      submitLabel: 'Appliquer',
      onSubmit: function (v) {
        var patch = { cols: Number(v.cols), rows: Number(v.rows) };
        if (!planLike) { patch.top = Number(v.top); patch.bottom = Number(v.bottom); }
        var changed = patch.cols !== lay.C || patch.rows !== lay.L || (!planLike && (patch.top !== lay.T || patch.bottom !== lay.B));
        var res = changed ? F.setGrid(shownId, patch) : { ok: true };
        if (res.ok && !planLike) { res = F.set(shownId, { ratio: Number(v.ratio), feet: v.feet === '1' }); }
        return res;
      }
    });
  }

  // Menu contextuel d'une case : « Ouvrir » en tête, puis les commandes de l'élément (celles du menu « Actions »).
  function openCellMenu(anchor, opener, k, redraw) {
    var A = R.ui.views.locationActions;
    var parents = R.store.pathOf(k.id).slice(0, -1).map(function (p) { return p.name; }).join(' \u203a ');
    R.ui.components.contextmenu.open({
      anchor: anchor, focusTo: opener, title: k.name, subtitle: parents || R.models.rootLabel(),
      level: R.models.levelOf(R.store.depthOf(k.id)),
      primary: { label: 'Ouvrir', run: function () { R.ui.router.navigate(k.id); } },
      items: [
        { label: 'Placer et dimensionner', run: function () { editing = true; selected = k.id; message = null; redraw(); } },
        { label: 'Ajouter un objet ici', run: function () { R.ui.views.itemActions.openCreate(k.id); } },
        { label: 'Ajouter un emplacement ici', run: function () { A.openCreate(k.id); } },
        { label: 'Modifier', run: function () { A.openEdit(k.id); } },
        { label: 'D\u00e9placer', run: function () { A.openMove(k.id); } },
        { label: 'Dupliquer', run: function () { A.openDuplicate(k.id); } },
        { label: 'Supprimer', danger: true, run: function () { A.askDelete(k.id); } }
      ]
    });
  }

  // Menu du bouton « + » : créer au niveau du plan affiché, ou régler sa grille.
  function openAddMenu(anchor, shownId) {
    var F = R.features.furniture;
    var A = R.ui.views.locationActions;
    var atRoot = F.isRoot(shownId);
    var loc = atRoot ? null : R.store.getLocation(shownId);
    var items = atRoot
      ? [{ label: 'Ajouter une pi\u00e8ce', run: function () { A.openCreate(null); } }]
      : [
          { label: 'Ajouter un objet ici', run: function () { R.ui.views.itemActions.openCreate(shownId); } },
          { label: 'Ajouter un emplacement ici', run: function () { A.openCreate(shownId); } }
        ];
    items.push({ label: 'R\u00e9gler la grille\u2026', run: function () { openGrid(shownId); } });
    R.ui.components.contextmenu.open({
      anchor: anchor, title: loc ? loc.name : R.models.rootLabel(), subtitle: 'Ajouter ou r\u00e9gler ici',
      label: 'Ajouter ou r\u00e9gler', level: loc ? R.models.levelOf(R.store.depthOf(shownId)) : 'racine', items: items
    });
  }

  // Pavé de quatre flèches (sans libellé visible : le nom accessible est dans aria-label).
  function pad(name, center, keys) {
    var nodes = keys.map(function (k) {
      return el('button', { class: 'furn-pad-btn furn-pad-' + k.dir, type: 'button', 'aria-label': k.label, title: k.label, onclick: k.run }, [k.glyph]);
    });
    nodes.push(el('span', { class: 'furn-pad-mid', 'aria-hidden': 'true' }, [center]));
    return el('div', { class: 'furn-pad', role: 'group', 'aria-label': name }, nodes);
  }

  function selectionPanel(c, lay, redraw, atRoot, shownId) {
    var F = R.features.furniture;
    var loc = R.store.getLocation(c.id);
    function k(dir, glyph, label, fn) { return { dir: dir, glyph: glyph, label: label, run: function () { run(redraw, fn()); } }; }
    return el('div', { class: 'furn-sel', role: 'group', 'aria-label': 'Emplacement sélectionné' }, [
      el('div', { class: 'furn-sel-head' }, [
        el('p', { class: 'furn-sel-text' }, ['\u00ab ' + loc.name + ' \u00bb : ' + zoneLabel(c.zone, atRoot).toLowerCase() + ', colonne ' + (c.col + 1) + ', ligne ' + (c.row + 1) + ', taille ' + c.w + ' \u00d7 ' + c.h + '.']),
        el('div', { class: 'furn-sel-btns' }, [
          el('button', { class: 'button button--secondary', type: 'button', onclick: function () { openGrid(shownId); } }, ['Grille\u2026']),
          el('button', { class: 'button', type: 'button', id: 'plan-done', onclick: function () { endEditing(redraw); } }, ['Terminer'])
        ])
      ]),
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

  function endEditing(redraw) { editing = false; selected = null; message = null; redraw(); }

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
      el('span', { class: 'furn-count' }, [String(n.items), el('span', { class: 'furn-count-word' }, [n.items > 1 ? ' objets' : ' objet'])]),
      c.w * c.h >= 2 ? el('span', { class: 'furn-kind' }, ['Niveau ' + (kidDepth + 1) + ', ' + R.models.kindLabel(k.kind).toLowerCase()]) : null
    ];
    var node = null;
    var open = editing
      ? el('button', { class: 'furn-open', type: 'button', 'aria-pressed': isSel ? 'true' : 'false', onclick: function () { selected = k.id; redraw(); } }, inner)
      : el('button', { class: 'furn-open', type: 'button', 'aria-haspopup': 'true', onclick: function () { openCellMenu(node, open, k, redraw); } }, inner);
    var parts = [open];
    if (subs) {
      parts.push(el('button', {
        class: 'furn-more', type: 'button',
        'aria-label': 'Voir les ' + plural(subs, 'sous-emplacement', 'sous-emplacements') + ' de \u00ab ' + k.name + ' \u00bb (niveau ' + (kidDepth + 2) + ')',
        onclick: function () { focus[furnId] = k.id; selected = null; redraw(); }
      }, [el('span', { class: 'furn-nest', 'aria-hidden': 'true' }), String(subs)]));
    }
    node = el('div', { class: 'furn-cell' + (isSel ? ' is-selected' : ''), 'data-level': R.models.levelOf(kidDepth), title: k.name + ' \u2014 ' + plural(n.items, 'objet', 'objets') }, parts);
    place(node, c);
    return node;
  }

  // ---------- plan ajusté à l'écran ----------

  // Calcule la taille d'une case pour que le plan tienne en largeur (et, autant que possible, en hauteur) dans le volet.
  function fit(wrap) {
    if (!wrap.isConnected || !wrap._plan) { return; }
    var body = wrap.querySelector('.furn-body[data-plan]');
    if (!body) { return; }
    var p = wrap._plan;
    var frame = body.parentNode;
    var pane = wrap.closest('.pane');
    var availW = frame.clientWidth;
    if (availW <= 0) { return; }
    if (p.real) {         // taille réelle : cases carrées d'au moins REAL_CELL px, le cadre défile si besoin
      var rw0 = 24 + (p.C - 1) * 8, rh0 = 24 + (p.L - 1) * 8;
      var rs = Math.max(REAL_CELL, Math.floor((availW - rw0) / p.C));
      body.style.aspectRatio = 'auto';
      body.style.minHeight = '0';
      body.style.width = (p.C * rs + rw0) + 'px';
      body.style.height = (p.L * rs + rh0) + 'px';
      body.classList.remove('furn-compact');
      body.setAttribute('data-fit', 'real');
      return;
    }
    var availH = 0;
    if (pane) {
      var top = frame.getBoundingClientRect().top - pane.getBoundingClientRect().top + pane.scrollTop;
      availH = pane.clientHeight - top - p.reserve;
    }
    var w0 = 24 + (p.C - 1) * 8;      // cadre + remplissage + espaces entre colonnes
    var h0 = 24 + (p.L - 1) * 8;
    var s = Math.min((availW - w0) / p.C, Math.max((availH - h0) / p.L, FIT_CELL));
    s = Math.floor(Math.max(s, MIN_CELL));
    body.style.aspectRatio = 'auto';
    body.style.minHeight = '0';
    body.style.width = (p.C * s + w0) + 'px';
    body.style.height = (p.L * s + h0) + 'px';
    body.classList.toggle('furn-compact', s < COMPACT);
    body.setAttribute('data-fit', 'fit');
    if (!wrap._ro && pane && window.ResizeObserver) {      // la barre d'actions qui se replie déplace le plan : on le recalcule
      wrap._ro = new window.ResizeObserver(function () { fit(wrap); });
      Array.prototype.forEach.call(pane.querySelectorAll('.manage, .detail-sticky'), function (n) { wrap._ro.observe(n); });
    }
  }

  function schedule(wrap) {
    fit(wrap);
    if (window.requestAnimationFrame) { window.requestAnimationFrame(function () { fit(wrap); window.requestAnimationFrame(function () { fit(wrap); }); }); }
  }

  function refitAll() {
    Array.prototype.forEach.call(document.querySelectorAll('.furn-view'), function (w) { fit(w); });
  }
  window.addEventListener('resize', refitAll);
  R.events.on('layout:changed', refitAll);

  function draw(wrap, furnId) {
    var F = R.features.furniture;
    var redraw = function () { draw(wrap, furnId); };
    var pane = wrap.closest ? wrap.closest('.pane') : null;     // le défilement ne doit pas remonter à chaque action
    var scrollTop = pane ? pane.scrollTop : 0;
    R.ui.dom.clear(wrap);
    wrap.setAttribute('data-editing', editing ? 'true' : 'false');
    var rootMode = F.isRoot(furnId);          // plan du logement : les pièces sont les cases
    var shownId = focus[furnId];
    if (!shownId || !R.store.getLocation(shownId) || (!rootMode && !R.store.pathOf(shownId).some(function (p) { return p.id === furnId; }))) { shownId = furnId; }
    var atRoot = F.isRoot(shownId);
    var loc = atRoot ? null : R.store.getLocation(shownId);
    var depth = atRoot ? -1 : R.store.depthOf(shownId);
    var level = atRoot ? 'racine' : R.models.levelOf(depth);
    var planLike = atRoot || depth === 0;      // logement ou pièce : dessinés comme un plan
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
    if (editing && !sel) {
      bar.push(el('button', { class: 'button', type: 'button', id: 'plan-done', onclick: function () { endEditing(redraw); } }, ['Terminer']));
    }
    if (planLike) {
      bar.push(el('button', {
        class: 'button button--secondary', type: 'button', id: 'plan-zoom', 'aria-pressed': zoomReal() ? 'true' : 'false',
        title: zoomReal() ? 'Revenir à un plan qui tient dans l\u2019écran' : 'Afficher le plan en taille réelle (défilement)',
        onclick: function () { R.storage.setAux('planzoom', zoomReal() ? 'fit' : 'real'); redraw(); }
      }, [zoomReal() ? 'Ajuster à l\u2019écran' : 'Agrandir']));
    }
    if (bar.length) { wrap.appendChild(el('div', { class: 'furn-bar' }, bar)); }
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
                class: 'furn-slot', type: 'button', 'aria-label': 'Case libre : colonne ' + (col + 1) + ', ligne ' + (row + 1) + ' (' + zoneLabel(zone, planLike).toLowerCase() + ')',
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
      return el('div', { class: 'furn-band', 'data-zone': zone }, [el('p', { class: 'furn-band-label' }, [zoneLabel(zone, planLike)]), zoneGrid(zone, rows)]);
    }

    var frame = [];
    if (lay.T) { frame.push(band('top', lay.T)); }
    var bodyContent = (!kidsCount && !editing)
      ? el('p', { class: 'furn-empty' }, [atRoot ? 'Aucune pièce à dessiner.' : 'Aucun sous-emplacement : les objets sont rangés directement ici.'])
      : zoneGrid('body', lay.L);
    var body = el('div', { class: 'furn-body', 'data-level': level }, [bodyContent]);
    if (planLike) {       // plan : cases carrées ; ajusté à l'écran par fit(), ou en taille réelle avec défilement du cadre
      body.setAttribute('data-plan', '');
      body.style.aspectRatio = lay.C + ' / ' + lay.L;
      if (zoomReal()) {
        body.style.minWidth = (lay.C * PLAN_COL) + 'px';
        body.style.minHeight = (lay.L * ROW_MIN) + 'px';
      } else {
        body.style.minHeight = (lay.L * MIN_CELL) + 'px';
      }
    } else {
      body.removeAttribute('data-plan');
      body.style.aspectRatio = String(g.ratio);
      body.style.minHeight = (lay.L * ROW_MIN) + 'px';
    }
    frame.push(body);
    if (g.feet) { frame.push(el('div', { class: 'furn-feet', 'data-level': level }, [el('span', { class: 'furn-foot' }), el('span', { class: 'furn-foot' })])); }
    if (lay.B) { frame.push(band('bottom', lay.B)); }
    wrap.appendChild(el('div', { class: 'furn-frame' + (planLike ? ' furn-frame--plan' : '') }, frame));
    if (sel) { wrap.appendChild(selectionPanel(sel, lay, redraw, planLike, shownId)); }
    if (!sel) {          // bouton « + » flottant : créer au niveau du plan affiché, régler la grille (caché pendant le placement : le pavé de flèches a « Grille… »)
      var add = el('button', {
        class: 'furn-add', id: 'plan-add', type: 'button', 'aria-haspopup': 'true',
        'aria-label': 'Ajouter ou régler ici', title: 'Ajouter ou régler ici',
        onclick: function () { openAddMenu(add, shownId); }
      }, ['+']);
      wrap.appendChild(add);
    }

    var items = atRoot ? [] : R.store.itemsIn(shownId);
    wrap._plan = planLike ? { C: lay.C, L: lay.L, real: zoomReal(), reserve: editing ? 230 : 16 } : null;
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
    schedule(wrap);
  }

  // Vue graphique du meuble `furnId` (emplacement de premier niveau).
  function create(furnId) {
    uid += 1;
    var wrap = el('div', { class: 'furn-view', id: 'furn-view-' + uid });
    draw(wrap, furnId);
    return wrap;
  }

  // Plan du logement : la même grille, où les cases sont les pièces.
  function createPlan(id) { return create(id || R.features.furniture.ROOT); }

  // Un changement d'écran referme le placement et oublie le niveau inférieur ouvert (ils ne doivent pas suivre d'un meuble ou d'un plan à l'autre).
  R.events.on('route:changed', function () { editing = false; selected = null; message = null; focus = {}; });

  R.ns('ui.views').furniture = { create: create, createPlan: createPlan, switcher: switcher, mode: mode, setMode: setMode };
})();
