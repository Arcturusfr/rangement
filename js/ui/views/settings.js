/*
  js/ui/views/settings.js — Application « Rangement »
  Version : V008
  Horodatage : 2026-10-25 00:52 (heure de Paris)
  Résumé : section « Application hors ligne » : mise à jour sur accord, recherche de mise à jour, vider le cache, installer (jalon 6).
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;
  var plural = R.ui.dom.plural;

  var flash = null;   // { text } : confirmation affichée en haut de l'écran, effacée dès qu'on le quitte

  var checking = null;   // résultat de la dernière recherche de mise à jour : { text }

  R.events.on('route:changed', function () { flash = null; checking = null; });

  function btn(label, variant, onclick, attrs) {
    return el('button', Object.assign({ class: 'button' + (variant ? ' button--' + variant : ''), type: 'button', onclick: onclick }, attrs || {}), [label]);
  }

  function section(title, nodes) {
    return el('section', { class: 'section' }, [el('h3', { class: 'section-title' }, [title])].concat(nodes));
  }

  function dateLabel(iso) {
    var d = new Date(iso);
    if (isNaN(d.getTime())) { return 'date inconnue'; }
    try { return d.toLocaleString('fr-FR', { dateStyle: 'long', timeStyle: 'short' }); }
    catch (err) { return d.toLocaleString('fr-FR'); }
  }

  function countsLabel(c) {
    return plural(c.locations, 'emplacement', 'emplacements') + ' et ' + plural(c.items, 'objet', 'objets');
  }

  // ---------- export ----------

  function doExport() {
    var B = R.features.backup;
    var out = B.prepareExport();
    var url = URL.createObjectURL(new Blob([out.text], { type: 'application/json' }));
    var link = el('a', { href: url, download: out.filename, hidden: true });
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(function () { URL.revokeObjectURL(url); }, 10000);
    flash = { text: 'Sauvegarde exportée : \u00ab ' + out.filename + ' \u00bb (' + countsLabel(out.counts) +
      '). Rangez ce fichier ailleurs que sur cet appareil.' };
    B.markExported();     // met aussi l'écran à jour
  }

  // ---------- import ----------

  function askImport(fileName, text) {
    var B = R.features.backup;
    var parsed = B.parse(text);
    if (!parsed.ok) {
      R.ui.components.dialog.alert({ title: 'Importation impossible', message: parsed.error });
      return;
    }
    var current = B.status().counts;
    var empty = !current.locations && !current.items;
    var message = '\u00ab ' + fileName + ' \u00bb contient ' + countsLabel(parsed.counts) +
      (parsed.exportedAt ? ' (sauvegarde du ' + dateLabel(parsed.exportedAt) + ')' : '') + '. ' +
      (empty
        ? 'Votre logement est vide : il sera rempli avec ces données.'
        : 'Vos données actuelles (' + countsLabel(current) + ') seront remplacées. Une copie de sécurité sera conservée : vous pourrez annuler l\u2019importation depuis cet écran.');
    R.ui.components.dialog.confirm({
      title: 'Importer cette sauvegarde ?',
      message: message,
      confirmLabel: empty ? 'Importer' : 'Remplacer mes données',
      danger: !empty,
      onConfirm: function () {
        flash = { text: 'Importation terminée : ' + countsLabel(parsed.counts) + '.' };
        var res = B.importData(parsed.data);
        if (!res.ok) { flash = null; }
        return res;
      }
    });
  }

  function onFileChosen(input) {
    var file = input.files && input.files[0];
    if (!file) { return; }
    var reader = new FileReader();
    reader.onload = function () {
      input.value = '';
      askImport(file.name, String(reader.result));
    };
    reader.onerror = function () {
      input.value = '';
      R.ui.components.dialog.alert({ title: 'Importation impossible', message: 'Ce fichier n\u2019a pas pu être lu.' });
    };
    reader.readAsText(file);
  }

  function askUndo(info) {
    R.ui.components.dialog.confirm({
      title: 'Annuler la dernière importation ?',
      message: 'Vos données reviendront à l\u2019état d\u2019avant l\u2019importation du ' + dateLabel(info.savedAt) +
        ' (' + countsLabel(info.counts) + '). Les données actuelles seront remplacées.',
      confirmLabel: 'Restaurer',
      danger: true,
      onConfirm: function () {
        flash = { text: 'Données restaurées : ' + countsLabel(info.counts) + '.' };
        var res = R.features.backup.undoImport();
        if (!res.ok) { flash = null; }
        return res;
      }
    });
  }

  // ---------- application hors ligne (PWA) ----------

  function askClearCache() {
    R.ui.components.dialog.confirm({
      title: 'Vider le cache de l\u2019application ?',
      message: 'Les fichiers de l\u2019application mis en cache sur cet appareil seront supprimés, puis l\u2019application se rechargera. ' +
        'Vos données (emplacements, objets) ne sont pas touchées. Une connexion est nécessaire pour la recharger.',
      confirmLabel: 'Vider le cache',
      danger: true,
      onConfirm: function () { R.pwa.clearCache(); return { ok: true }; }
    });
  }

  function onCheckUpdate() {
    checking = { text: 'Recherche d\u2019une nouvelle version\u2026' };
    R.events.emit('pwa:changed', {});
    R.pwa.checkUpdate().then(function (res) {
      checking = { text: !res.ok ? 'Recherche impossible pour l\u2019instant (hors connexion ?).'
        : (res.updateReady ? 'Une nouvelle version est prête.' : 'Vous utilisez la dernière version.') };
      R.events.emit('pwa:changed', {});
    });
  }

  function pwaSection() {
    var p = R.pwa.status();
    var nodes = [];
    if (!p.supported) {
      nodes.push(el('p', { class: 'hint' }, ['Le mode hors ligne n\u2019est pas disponible dans ce contexte (il nécessite une adresse https:// ou localhost, pas un fichier ouvert directement).']));
      return section('Application hors ligne', nodes);
    }
    if (p.error) {
      nodes.push(el('p', { class: 'note-box note-box--warn' }, ['Le mode hors ligne n\u2019a pas pu être activé : ' + p.error]));
    } else if (p.updateReady) {
      nodes.push(el('p', { class: 'note-box note-box--warn', role: 'status' }, ['Une nouvelle version de l\u2019application est prête. Elle sera utilisée après la mise à jour (l\u2019écran se rechargera ; vos données ne changent pas).']));
    } else if (p.cacheName) {
      nodes.push(el('p', null, ['L\u2019application est disponible hors ligne. Cache actif : ' + p.cacheName + '.']));
    } else {
      nodes.push(el('p', { class: 'hint' }, ['Le mode hors ligne s\u2019active au premier chargement ; rouvrez l\u2019application dans un instant.']));
    }
    if (checking) { nodes.push(el('p', { class: 'hint', role: 'status' }, [checking.text])); }
    if (p.standalone) { nodes.push(el('p', { class: 'hint' }, ['Application installée sur cet appareil.'])); }

    var buttons = [];
    if (p.updateReady) { buttons.push(btn('Mettre à jour', '', function () { R.pwa.applyUpdate(); }, { id: 'update-button' })); }
    if (p.canInstall) { buttons.push(btn('Installer l\u2019application', '', function () { R.pwa.promptInstall(); }, { id: 'install-button' })); }
    buttons.push(btn('Rechercher une mise à jour', 'secondary', onCheckUpdate, { id: 'check-update-button' }));
    buttons.push(btn('Vider le cache de l\u2019application', 'secondary', askClearCache, { id: 'clear-cache-button' }));
    nodes.push(el('div', { class: 'toolbar' }, buttons));
    return section('Application hors ligne', nodes);
  }

  // ---------- écran ----------

  function statusNote(st) {
    if (!st.counts.locations && !st.counts.items) {
      return el('p', { class: 'hint' }, ['Aucune donnée à sauvegarder pour l\u2019instant.']);
    }
    if (!st.lastExportAt) {
      return el('p', { class: 'note-box note-box--warn' }, ['Aucune sauvegarde n\u2019a encore été exportée depuis cet appareil.']);
    }
    var when = 'Dernière sauvegarde : ' + dateLabel(st.lastExportAt) + '. ';
    return st.dirty
      ? el('p', { class: 'note-box note-box--warn' }, [when + 'Des modifications ont été faites depuis : pensez à exporter une nouvelle sauvegarde.'])
      : el('p', { class: 'note-box note-box--ok' }, [when + 'Aucune modification depuis.']);
  }

  // Renvoie le contenu du volet de détail pour les réglages.
  function create() {
    var B = R.features.backup;
    var st = B.status();
    var undo = B.undoInfo();
    var hasData = st.counts.locations > 0 || st.counts.items > 0;

    var input = el('input', { type: 'file', id: 'import-file', accept: '.json,application/json', hidden: true });
    input.addEventListener('change', function () { onFileChosen(input); });

    var nodes = [
      el('header', { class: 'detail-head' }, [
        el('h2', { class: 'detail-title' }, ['Réglages']),
        el('p', { class: 'detail-meta' }, ['Sauvegarde et restauration de vos données'])
      ])
    ];
    if (flash) { nodes.push(el('p', { class: 'note-box note-box--ok', role: 'status' }, [flash.text])); }

    nodes.push(section('Sauvegarde', [
      el('p', null, ['Votre logement contient ' + countsLabel(st.counts) + '.']),
      statusNote(st),
      el('p', { class: 'hint' }, ['Les données restent sur cet appareil (dans ce navigateur). Exportez-les régulièrement vers un fichier JSON que vous conserverez ailleurs.']),
      el('div', { class: 'toolbar' }, [
        btn('Exporter une sauvegarde', '', doExport, { id: 'export-button', disabled: hasData ? null : true })
      ])
    ]));

    var restoreButtons = [btn('Importer une sauvegarde\u2026', 'secondary', function () { input.click(); }, { id: 'import-button' })];
    if (undo) { restoreButtons.push(btn('Annuler la dernière importation', 'secondary', function () { askUndo(undo); }, { id: 'undo-button' })); }
    nodes.push(section('Restauration', [
      el('p', { class: 'hint' }, ['Importer une sauvegarde remplace toutes les données actuelles. Une copie de sécurité est conservée pour pouvoir annuler.']),
      el('div', { class: 'toolbar' }, restoreButtons),
      input
    ]));

    nodes.push(pwaSection());

    nodes.push(section('À propos', [
      el('p', null, ['Version de l\u2019application : ' + R.config.version]),
      el('p', null, ['Format des données : ' + R.config.schemaVersion]),
      el('p', null, [R.storage.isPersistent()
        ? 'Stockage : sur cet appareil, conservé après fermeture.'
        : 'Stockage : indisponible, les données ne sont pas conservées après fermeture.'])
    ]));

    nodes.push(el('p', null, [el('a', { class: 'button button--secondary', href: R.ui.router.href(null) }, ['Retour au logement'])]));
    return el('div', { class: 'settings' }, nodes);
  }

  R.ns('ui.views').settings = { create: create };
})();
