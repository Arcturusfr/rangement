/*
  js/ui/views/item-actions.js — Application « Rangement »
  Version : V006
  Horodatage : 2026-10-24 13:10 (heure de Paris)
  Résumé : quantité : nombre entier (clavier numérique) ; indication « 0 si épuisé ».
*/
(function () {
  'use strict';

  var R = window.Rangement;

  var QTY_HINT = 'Nombre entier ; 0 si l\u2019objet est épuisé.';
  var TAGS_HINT = 'Séparés par des virgules, par exemple : optique, nature.';

  // Ajoute un objet dans l'emplacement `locationId`.
  function openCreate(locationId) {
    var loc = R.store.getLocation(locationId);
    if (!loc) { return; }
    R.ui.components.dialog.form({
      title: 'Nouvel objet dans \u00ab ' + loc.name + ' \u00bb',
      fields: [
        { name: 'name', label: 'Nom', maxlength: 80 },
        { name: 'quantity', label: 'Quantité', value: '1', inputmode: 'numeric', maxlength: 7, hint: QTY_HINT },
        { name: 'tags', label: 'Mots-clés (facultatif)', hint: TAGS_HINT },
        { name: 'note', label: 'Note (facultatif)', type: 'textarea' }
      ],
      submitLabel: 'Ajouter',
      onSubmit: function (v) {
        return R.features.items.create({
          name: v.name, quantity: v.quantity, tags: v.tags, note: v.note, locationId: locationId
        });
      }
    });
  }

  function openEdit(id) {
    var item = R.store.getItem(id);
    if (!item) { return; }
    R.ui.components.dialog.form({
      title: 'Modifier \u00ab ' + item.name + ' \u00bb',
      fields: [
        { name: 'name', label: 'Nom', value: item.name, maxlength: 80 },
        { name: 'quantity', label: 'Quantité', value: R.features.items.formatQuantity(item.quantity), inputmode: 'numeric', maxlength: 7, hint: QTY_HINT },
        { name: 'tags', label: 'Mots-clés (facultatif)', value: item.tags.join(', '), hint: TAGS_HINT },
        { name: 'note', label: 'Note (facultatif)', type: 'textarea', value: item.note }
      ],
      submitLabel: 'Enregistrer',
      onSubmit: function (v) {
        return R.features.items.update(id, { name: v.name, quantity: v.quantity, tags: v.tags, note: v.note });
      }
    });
  }

  function openMove(id) {
    var item = R.store.getItem(id);
    if (!item) { return; }
    R.ui.components.dialog.form({
      title: 'Déplacer \u00ab ' + item.name + ' \u00bb',
      fields: [{
        name: 'location',
        label: 'Nouvel emplacement',
        type: 'select',
        options: R.features.items.locationChoices(),
        value: item.locationId
      }],
      submitLabel: 'Déplacer',
      onSubmit: function (v) { return R.features.items.move(id, v.location); }
    });
  }

  function askDelete(id) {
    var item = R.store.getItem(id);
    if (!item) { return; }
    R.ui.components.dialog.confirm({
      title: 'Supprimer cet objet ?',
      message: '\u00ab ' + item.name + ' \u00bb sera supprimé définitivement.',
      confirmLabel: 'Supprimer',
      danger: true,
      onConfirm: function () {
        var locationId = item.locationId;
        var res = R.features.items.remove(id);
        if (res.ok) { R.ui.router.navigate(locationId); }
        return res;
      }
    });
  }

  R.ns('ui.views').itemActions = {
    openCreate: openCreate,
    openEdit: openEdit,
    openMove: openMove,
    askDelete: askDelete
  };
})();
