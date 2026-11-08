/*
  js/features/search.js — Application « Rangement »
  Version : V006
  Horodatage : 2026-10-24 13:10 (heure de Paris)
  Résumé : création — recherche d'objets et d'emplacements (casse et accents ignorés, tous les mots requis).
*/
(function () {
  'use strict';

  var R = window.Rangement;

  // Poids d'une correspondance selon le champ où le mot est trouvé.
  var W_NAME = 4, W_TAGS = 3, W_NOTE = 2, W_PATH = 1;

  function norm(value) { return R.models.normalizeText(value); }

  function terms(query) { return norm(query).split(/\s+/).filter(Boolean); }

  function names(locs) { return locs.map(function (l) { return l.name; }).join(' '); }

  // Chaque mot doit se trouver dans au moins un champ ; le score cumule le meilleur poids de chaque mot.
  // Renvoie 0 si un mot n'est trouvé nulle part.
  function score(ts, fields) {
    var total = 0;
    for (var i = 0; i < ts.length; i++) {
      var best = 0;
      for (var j = 0; j < fields.length; j++) {
        if (fields[j].text.indexOf(ts[i]) !== -1 && fields[j].weight > best) { best = fields[j].weight; }
      }
      if (!best) { return 0; }
      total += best;
    }
    return total;
  }

  function byScoreThenName(a, b) {
    if (b.score !== a.score) { return b.score - a.score; }
    return a.name.localeCompare(b.name, 'fr', { sensitivity: 'base', numeric: true });
  }

  // Renvoie { terms, items: [{ item, path, score, name }], locations: [{ location, path, score, name }] }
  // `path` : emplacements de la racine jusqu'à l'emplacement de l'objet (ou jusqu'à l'emplacement trouvé, inclus).
  function search(query) {
    var ts = terms(query);
    var out = { terms: ts, items: [], locations: [] };
    if (!ts.length) { return out; }

    R.store.items().forEach(function (it) {
      var path = R.store.pathOf(it.locationId);
      var s = score(ts, [
        { text: norm(it.name), weight: W_NAME },
        { text: norm((it.tags || []).join('\n')), weight: W_TAGS },
        { text: norm(it.note), weight: W_NOTE },
        { text: norm(names(path)), weight: W_PATH }
      ]);
      if (s) { out.items.push({ item: it, path: path, score: s, name: it.name }); }
    });

    R.store.locations().forEach(function (loc) {
      var path = R.store.pathOf(loc.id);
      var s = score(ts, [
        { text: norm(loc.name), weight: W_NAME },
        { text: norm(loc.note), weight: W_NOTE },
        { text: norm(names(path.slice(0, -1))), weight: W_PATH }
      ]);
      if (s) { out.locations.push({ location: loc, path: path, score: s, name: loc.name }); }
    });

    out.items.sort(byScoreThenName);
    out.locations.sort(byScoreThenName);
    return out;
  }

  R.ns('features').search = { search: search, terms: terms };
})();
