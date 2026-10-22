/*
  js/features/demo.js — Application « Rangement »
  Version : V003
  Horodatage : 2026-10-22 21:39 (heure de Paris)
  Résumé : création — jeu de données de démonstration (les 4 exemples réels).
*/
(function () {
  'use strict';

  var R = window.Rangement;

  function build() {
    var data = R.models.emptyData();

    function loc(name, kind, parent, note) {
      var l = R.models.newLocation({ name: name, kind: kind, parentId: parent ? parent.id : null, note: note });
      data.locations.push(l);
      return l;
    }
    function item(name, where, tags, note) {
      data.items.push(R.models.newItem({ name: name, locationId: where.id, tags: tags, note: note }));
    }

    var chambre = loc('Chambre à coucher', 'piece');
    var commodeChambre = loc('Commode', 'meuble', chambre);
    item('Polos d\u2019été', commodeChambre, ['vêtements']);

    var sejour = loc('Séjour', 'piece');
    var living = loc('Meuble living', 'meuble', sejour);
    var tiroirPiles = loc('Tiroir bas gauche', 'tiroir', living);
    var grandTiroir = loc('Grand tiroir du bas', 'tiroir', living);
    item('Piles neuves', tiroirPiles, ['électricité']);
    item('Jumelles Nikon', grandTiroir, ['optique', 'nature']);

    var entree = loc('Entrée', 'piece');
    var commodeEntree = loc('Commode', 'meuble', entree);
    item('Objets divers à trier', commodeEntree, ['tri'], 'À répartir dans de vrais emplacements.');

    return data;
  }

  function load() {
    return R.store.replaceAll(build());
  }

  R.ns('features').demo = { build: build, load: load };
})();
