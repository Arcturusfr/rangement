/*
  js/ui/views/location-actions.js — Application « Rangement »
  Version : V009
  Horodatage : 2026-10-25 16:10 (heure de Paris)
  Résumé : duplication d'un emplacement ; bouton de validation coloré selon le niveau créé.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var plural = R.ui.dom.plural;

  function kindOptions() {
    return R.config.kinds.map(function (k) { return { value: k.id, label: k.label }; });
  }

  // Ajoute un emplacement dans `parentId` (null = nouvelle pièce à la racine).
  function openCreate(parentId) {
    var parent = parentId ? R.store.getLocation(parentId) : null;
    R.ui.components.dialog.form({
      title: parent ? 'Nouvel emplacement dans \u00ab ' + parent.name + ' \u00bb' : 'Nouvelle pièce',
      fields: [
        { name: 'name', label: 'Nom', maxlength: 80 },
        { name: 'kind', label: 'Type', type: 'select', options: kindOptions(), value: parent ? 'autre' : 'piece' },
        { name: 'note', label: 'Note (facultatif)', type: 'textarea' }
      ],
      submitLabel: 'Ajouter',
      submitLevel: R.models.levelOf(parent ? R.store.depthOf(parent.id) + 1 : 0),
      onSubmit: function (v) {
        return R.features.locations.create({ name: v.name, kind: v.kind, note: v.note, parentId: parentId });
      }
    });
  }

  function openEdit(id) {
    var loc = R.store.getLocation(id);
    if (!loc) { return; }
    R.ui.components.dialog.form({
      title: 'Modifier \u00ab ' + loc.name + ' \u00bb',
      fields: [
        { name: 'name', label: 'Nom', value: loc.name, maxlength: 80 },
        { name: 'kind', label: 'Type', type: 'select', options: kindOptions(), value: loc.kind },
        { name: 'note', label: 'Note (facultatif)', type: 'textarea', value: loc.note }
      ],
      submitLabel: 'Enregistrer',
      onSubmit: function (v) {
        return R.features.locations.update(id, { name: v.name, kind: v.kind, note: v.note });
      }
    });
  }

  function openMove(id) {
    var loc = R.store.getLocation(id);
    if (!loc) { return; }
    R.ui.components.dialog.form({
      title: 'Déplacer \u00ab ' + loc.name + ' \u00bb',
      fields: [{
        name: 'parent',
        label: 'Nouvel emplacement parent',
        type: 'select',
        options: R.features.locations.parentChoices(id),
        value: loc.parentId || '',
        hint: 'Le contenu de cet emplacement le suit.'
      }],
      submitLabel: 'Déplacer',
      onSubmit: function (v) { return R.features.locations.move(id, v.parent || null); }
    });
  }

  var CONTENT_CHOICES = [
    { value: 'none', label: 'Cet emplacement seul (vide)' },
    { value: 'structure', label: 'Avec ses sous-emplacements (sans les objets)' },
    { value: 'all', label: 'Avec tout son contenu (sous-emplacements et objets)' }
  ];

  // Duplique un emplacement : il faut changer le nom ou choisir un autre emplacement parent.
  function openDuplicate(id) {
    var loc = R.store.getLocation(id);
    if (!loc) { return; }
    var n = R.store.countIn(id);
    var fields = [
      { name: 'name', label: 'Nom de la copie', value: loc.name, maxlength: 80 },
      {
        name: 'parent',
        label: 'Emplacement parent de la copie',
        type: 'select',
        options: R.features.locations.parentChoices(id),
        value: loc.parentId || '',
        hint: 'Modifiez le nom ou choisissez un autre emplacement.'
      }
    ];
    if (n.locations || n.items) {
      fields.push({ name: 'content', label: 'Contenu à copier', type: 'select', options: CONTENT_CHOICES, value: 'none' });
    }
    R.ui.components.dialog.form({
      title: 'Dupliquer \u00ab ' + loc.name + ' \u00bb',
      fields: fields,
      submitLabel: 'Dupliquer',
      selectFirst: true,
      onSubmit: function (v) {
        var res = R.features.locations.duplicate(id, { name: v.name, parentId: v.parent || null, content: v.content });
        if (res.ok) { R.ui.router.navigate(res.location.id); }
        return res;
      }
    });
  }

  function askDelete(id) {
    var loc = R.store.getLocation(id);
    if (!loc) { return; }
    var n = R.store.countIn(id);

    if (n.locations || n.items) {
      var parts = [];
      if (n.locations) { parts.push(plural(n.locations, 'emplacement', 'emplacements')); }
      if (n.items) { parts.push(plural(n.items, 'objet', 'objets')); }
      R.ui.components.dialog.alert({
        title: 'Suppression impossible',
        message: '\u00ab ' + loc.name + ' \u00bb contient encore ' + parts.join(' et ') +
          '. Déplacez ou supprimez ce contenu avant de supprimer cet emplacement.'
      });
      return;
    }

    R.ui.components.dialog.confirm({
      title: 'Supprimer cet emplacement ?',
      message: '\u00ab ' + loc.name + ' \u00bb est vide. La suppression est définitive.',
      confirmLabel: 'Supprimer',
      danger: true,
      onConfirm: function () {
        var parentId = loc.parentId;
        var res = R.features.locations.remove(id);
        if (res.ok) { R.ui.router.navigate(parentId); }
        return res;
      }
    });
  }

  R.ns('ui.views').locationActions = {
    openCreate: openCreate,
    openEdit: openEdit,
    openMove: openMove,
    openDuplicate: openDuplicate,
    askDelete: askDelete
  };
})();
