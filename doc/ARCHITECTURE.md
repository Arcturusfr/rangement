<!--
  ARCHITECTURE.md — Application « Rangement »
  Version : V023b
  Horodatage : 2026-11-27 01:20 (heure de Paris)
  Résumé : V023b (jalon 14) : un meuble dont les proportions ne sont pas « Haut » tient entièrement à l'écran (corps aplati si besoin) ; pieds Sans / Petits / Grands / Très grands. V022 / V022a validées.
-->

# ARCHITECTURE — Rangement `V023b`

> Dernière mise à jour : 27/11/2026 01:20 (Paris) — **V023b** (jalon 14 : pieds « petits / grands / très grands » ; **V022 et V022a validées**)
> Statut : **jalon 14 livré (V023)** : liste « Pieds » = Sans / Petits / Grands / Très grands ; grands pieds = moitié de la hauteur totale (pieds compris, donc pieds = cadre), très grands = 75 % ; la bande « Dessous » se place entre les pieds. Jalon 13 (V022) : plus de carré de surbrillance au toucher sur les boutons ; boutons du détail (écran déplié) réunis dans **un seul conteneur** à fin filet transparent ; flèches de niveau **circulaires** ; bouton réduire / élargir le volet **bleu #043BB2** et aussi haut que « Logement » ; nouvelle icône « Actions » (éclair dans un carré) ; **pictogrammes devant les commandes des menus** ; marge de 16 px de plus sous le contenu (barre des tâches du téléphone). Jalons 1 à 12 livrés et validés.

## 1. Principes directeurs

1. **Application 100 % statique** : HTML + CSS + JavaScript « vanilla », sans build, sans framework, sans serveur. Compatible GitHub Pages.
2. **Fichier racine** : `index.html` (obligatoire pour l'hébergement).
3. **Découpage fin** : un fichier = une responsabilité. Pas de fichier de plus de ~300 lignes sauf exception justifiée.
4. **Scripts classiques, pas de modules ES** : les fichiers JS sont chargés par des balises `<script>` ordinaires, **dans un ordre précis** défini dans `index.html` (voir §5). Pour éviter les variables globales en vrac, chaque fichier s'enregistre dans **un seul espace de noms global : `window.Rangement`** (ex. `Rangement.store`, `Rangement.ui.views.browse`).
5. **Données locales** : tout est stocké dans le `localStorage` de l'appareil. Aucune donnée personnelle n'est dans le dépôt GitHub public. Sauvegarde/restauration **manuelle** par export/import JSON ; **pas de synchronisation** entre appareils.
6. **Séparation stricte** : données (`core`) ≠ logique métier (`features`) ≠ affichage (`ui`). L'affichage n'écrit jamais directement dans le stockage.
7. **Prévu pour le graphique** : le modèle réserve dès le départ un champ `geometry` optionnel pour brancher plus tard le plan SVG sans migration lourde.
8. **Responsive Z Fold** : conçu d'abord pour l'écran déplié (affichage en 2 volets), avec repli en 1 volet pour l'écran externe.
9. **PWA hors ligne, service worker maîtrisé** : voir §6.

## 2. Arborescence

```
/ (racine du dépôt)
├── index.html                 Point d'entrée, charge CSS et JS (ordre important)
├── manifest.webmanifest       Manifeste PWA (nom, icônes, couleurs, affichage)
├── sw.js                      Service worker (pré-cache explicite, versionné, cache d'abord)
├── icons/                     Icônes PWA : icon-192x192, icon-512x512, maskable-icon-192x192, maskable-icon-512x512 (.png)
├── ARCHITECTURE.md            Ce fichier
├── roadmap-et-avancement.md   Avancement et prochaines étapes
├── ToDo_Utilisateur.md        Tâches à la charge de l'utilisateur
├── tests/
│   ├── test_jalon1.py         Tests Playwright/Chromium : squelette, stockage, mise en page, diagnostic
│   ├── test_jalon2.py         Tests Playwright/Chromium : gestion des emplacements
│   ├── test_jalon3.py         Tests Playwright/Chromium : gestion des objets
│   ├── test_jalon4.py         Tests Playwright/Chromium : recherche
│   ├── test_jalon5.py         Tests Playwright/Chromium : sauvegarde (export, import, annulation, réglages)
│   ├── test_jalon6.py         Tests Playwright/Chromium : PWA (manifeste, pré-cache, hors ligne, mise à jour, vidage du cache)
│   ├── test_jalon7.py         Tests Playwright/Chromium : vue graphique des meubles (disposition, niveaux, nombre d'objets dans l'arborescence)
│   ├── test_jalon9.py         Tests Playwright/Chromium : plan ajusté à l'écran, taille réelle, tuiles compactes, plan d'une pièce
│   ├── test_jalon9_2.py       Tests Playwright/Chromium : menu contextuel d'une case, bouton « + », réglage de la grille, placement (pavés de flèches)
│   ├── test_jalon9_3.py       Tests Playwright/Chromium : ℹ️ et info-bulle, libellé de catégorie tronqué + chevron, menu déroulant « Actions », Liste / Plan dans l'en-tête figé
│   ├── test_jalon9_3bis.py    Tests Playwright/Chromium (V017) : bandeau de niveau = « Ouvrir », bandeau masqué sur les cases étroites, Vue graphique à tous les niveaux
│   ├── test_jalon9_4.py       Tests Playwright/Chromium (V018) : plan en vue d'accueil, boutons flottants Liste / Plan et Agrandir, arborescence à trois états
│   ├── test_jalon14.py        Tests Playwright/Chromium (V023) : pieds Sans / Petits / Grands / Très grands, migration de l'ancienne valeur « avec », bande « Dessous » entre les grands pieds, ajout d'emplacements et d'objets, redimensionnement
│   ├── test_jalon13.py        Tests Playwright/Chromium (V022) : focus, conteneur unique des boutons du détail, flèches circulaires, bouton du volet, icône « Actions », pictogrammes des menus, marge sous le plan
│   ├── test_jalon12.py        Tests Playwright/Chromium (V021) : boutons de l'en-tête transparents / inversés, pictogramme arborescence, « Actions » en pictogramme, largeur du volet, pictogrammes élargir / réduire
│   ├── test_jalon11.py        Tests Playwright/Chromium (V020) : couleur #043BB2, recherche masquée + loupe, Réglages en pictogramme, groupes de boutons, aide « ? », cases libres invisibles (appui long = case la plus proche), volet d'arborescence sur écran replié
│   ├── test_jalon10.py        Tests Playwright/Chromium (V019) : pictogrammes, appui simple / long, mode « Modifier le plan », en-tête et recherche regroupés, rail au démarrage, cases libres
│   ├── test_jalon8.py         Tests Playwright/Chromium : plan du logement (pièces sur la grille, ajustement, sauvegarde, cadre défilant)
│   └── test_jalon6bis.py      Tests Playwright/Chromium : évolutions ergonomiques (arborescence, rail, en-têtes figés, duplication, Retour, flèches, saisie interdite, pastille, couleurs)
├── css/
│   ├── base.css               Variables (couleurs, espacements), reset, typographie
│   ├── layout.css             Mise en page : 1 volet / 2 volets, en-tête, navigation
│   ├── components.css         Boutons, listes, formulaires, fil d'Ariane, dialogues
│   └── furniture.css          Vue graphique d'un meuble, cases et cases libres, nombre d'objets de l'arborescence ; menu contextuel (`.ctx-*`)
└── js/
    ├── config.js              Crée `window.Rangement` ; version, constantes, clé de stockage
    ├── core/
    │   ├── ids.js             Génération d'identifiants uniques
    │   ├── models.js          Définition/validation des objets (Emplacement, Objet)
    │   ├── storage.js         Lecture/écriture persistante (localStorage) + clés annexes (copie de sécurité, suivi des sauvegardes)
    │   ├── store.js           État en mémoire + notification des changements
    │   └── events.js          Mini bus d'événements
    ├── features/
    │   ├── demo.js            Données de démonstration (provisoire)
    │   ├── locations.js       Créer/modifier/déplacer/supprimer des emplacements, avec garde-fous
    │   ├── items.js           Créer/modifier/déplacer/supprimer des objets (quantité, mots-clés, note)
    │   ├── search.js          Recherche d'objets et d'emplacements (nom, mots-clés, note, chemin), classée par pertinence
    │   ├── furniture.js       Grille d'un meuble **ou du plan du logement** (colonnes, lignes, bandes dessus / dessous pour un meuble, proportions, pieds `false` | `'petits'` | `'grands'` | `'tres-grands'`) et place de chaque sous-emplacement / pièce en cases (`geometry`) ; identifiant spécial `ROOT` = le logement ; `isPlanLike(id)` = le logement ou une pièce (cases carrées, une seule zone) ; `hasGraphic(id)` = Vue graphique proposée (un meuble, ou tout niveau plus bas qui a des sous-emplacements)
    │   └── backup.js          Export / import JSON, copie de sécurité avant import (annulable), suivi de la dernière sauvegarde
    ├── ui/
    │   ├── dom.js             Aides de construction du DOM (texte toujours échappé)
    │   ├── icons.js           Pictogrammes SVG filaires (`Rangement.ui.icons.create(nom, taille)`) : list, plan, settings, edit-text, edit-plan, move-cell, enlarge-cell, zoom-in, zoom-out, tree, search, help, arrow-left, expand-h, collapse-h, actions, open, add-place, add-item, grid, move-to, duplicate, delete
    │   ├── router.js          Navigation interne (hash `#/...`)
    │   ├── layout.js          Bascule 1 volet / 2 volets selon la largeur
    │   ├── components/
    │   │   ├── breadcrumb.js  Fil d'Ariane (Pièce › Meuble › Tiroir)
    │   │   ├── list.js        Liste générique
    │   │   ├── form.js        Champs de formulaire (texte, zone de texte, liste), validation champ par champ et lecture des valeurs
    │   │   ├── dialog.js      Dialogues : formulaire (avec blocage de saisie interdite), confirmation, message
    │   │   ├── detailbar.js   En-tête figé du volet de détail (deux colonnes) : fil d'Ariane, nom, ℹ️, libellé de catégorie (chevron si tronqué) ; flèches de niveau, menu déroulant « Actions » (bouton-pictogramme depuis la V021) et, sous eux, les boutons-pictogrammes d'affichage (`views` : Liste / Plan, Agrandir, Modifier le plan)
    │   │   ├── bubble.js      Info-bulle ouverte près d'un bouton (ℹ️, chevron du libellé) ; fermée par Échap, un appui ailleurs ou un changement d'écran
    │   │   ├── longpress.js   Appui simple / appui long (≈ 450 ms) sur un élément ; clic droit et touche Menu = appui long ; le clic qui suit un appui long est ignoré ; option `filter(event)`
    │   │   └── contextmenu.js Menu contextuel ouvert près d'un élément : commande principale « Ouvrir » (plus grande), puis les autres commandes ; fermé par Échap, un appui ailleurs ou un changement d'écran
    │   └── views/
    │       ├── browse.js      Volet gauche : arborescence repliable, ligne « Logement » figée, bascule large / rail
    │       ├── treerail.js    Arborescence minimale (rail sans libellés) et infobulle Ok / Annuler
    │       ├── location-actions.js  Dialogues d'action : ajouter, modifier, déplacer, supprimer un emplacement
    │       ├── item-actions.js  Dialogues d'action : ajouter, modifier, déplacer, supprimer un objet
    │       ├── location.js    Volet principal : contenu d'un emplacement + barre d'actions ; affiche aussi la fiche d'un objet
    │       ├── item.js        Fiche d'un objet (emplacement, quantité, mots-clés, note, actions)
    │       ├── furniture.js   Vue graphique d'un meuble ou d'un niveau plus bas sur grille (cases, bandes, sélection ; le bandeau de niveau d'une case ouvre l'emplacement) et du plan du logement ou d'une pièce (`createPlan(id)`, ajusté à l'écran par `fit()`) ; commutateurs Liste / Vue graphique (meubles) et Liste / Plan (logement)
    │       ├── searchbar.js   Champ de recherche permanent sous l'en-tête (synchronisé avec la route)
    │       ├── search.js      Résultats de recherche : objets puis emplacements, avec chemin complet
    │       └── settings.js    Écran Réglages (`#/r`) : export, import, annulation d'import, application hors ligne (mise à jour, cache, installation), à propos
    ├── pwa.js                 Enregistrement du service worker, mise à jour sur accord, vidage du cache, invite d'installation
    └── main.js                Démarrage : init stockage, routeur, premier rendu
```

Réservé pour plus tard (non créé pour l'instant) : `js/plan/` (rendu SVG du plan), `js/editor/` (outil de construction du plan), gestion des photos, QR codes/étiquettes.

## 3. Modèle de données

Le logement est une **arborescence d'emplacements** de profondeur libre, dans laquelle on range des **objets** suivis individuellement.

### 3.1 Emplacement (`location`)

| Champ | Type | Description |
|---|---|---|
| `id` | string | Identifiant unique |
| `parentId` | string \| null | Emplacement parent (`null` = racine) |
| `name` | string | Nom affiché (ex. « Commode chambre ») |
| `kind` | string | Type libre suggéré : `piece`, `meuble`, `tiroir`, `etagere`, `boite`, `autre` |
| `note` | string | Commentaire optionnel (ex. « tiroir du bas à gauche ») |
| `geometry` | object \| null | **Réservé au futur plan SVG**. Inutilisé au départ |
| `createdAt` / `updatedAt` | ISO string | Horodatages |

### 3.2 Objet (`item`)

| Champ | Type | Description |
|---|---|---|
| `id` | string | Identifiant unique |
| `locationId` | string | Emplacement où l'objet est rangé |
| `name` | string | Nom |
| `quantity` | number | Quantité (défaut 1) |
| `tags` | string[] | Mots-clés pour la recherche |
| `note` | string | Commentaire optionnel |
| `createdAt` / `updatedAt` | ISO string | Horodatages |

### 3.3 Enveloppe de stockage

```json
{
  "schemaVersion": 1,
  "appVersion": "V007",
  "locations": [],
  "items": [],
  "plan": { "cols": 3, "rows": 2 }
}
```

`plan` est **facultatif** (V013) : colonnes et lignes de la grille du plan du logement ; absent = disposition automatique. Les pièces portent leur place dans leur propre `geometry`.

`schemaVersion` permet de migrer les données si le modèle évolue. Un fichier de sauvegarde exporté a la même forme, avec en plus `exportedAt` (date ISO de l'export).

### 3.4 Exemples de validation du modèle

| Besoin exprimé | Chemin d'emplacement | Objet |
|---|---|---|
| Polos d'été | Chambre à coucher › Commode | Polos d'été |
| Piles neuves | Séjour › Meuble living › Tiroir bas gauche | Piles neuves |
| Jumelles Nikon | Séjour › Meuble living › Grand tiroir du bas | Jumelles Nikon |
| Objets divers à trier | Entrée › Commode | Objets divers à trier |

Le modèle couvre ces cas sans adaptation. Remarque : « Objets divers à trier » est un objet « fourre-tout » ; il pourra être découpé en objets individuels au fil du tri.

## 4. Flux de données

```
Action utilisateur → ui/views → features/* → core/store → core/storage (localStorage)
                                                  │
                                                  └→ core/events → ui/views (re-rendu)
```

## 5. Ordre de chargement des scripts (`index.html`)

Les dépendances vont toujours du bas vers le haut ; un fichier ne peut utiliser que ce qui est chargé avant lui. Ordre effectif en V009 :

1. `js/config.js` (crée `window.Rangement`, l'aide `Rangement.ns('a.b')` et `Rangement.config`)
2. `js/core/events.js`, `ids.js`, `models.js`, `storage.js`, `store.js`
3. `js/features/demo.js`, `locations.js`, `items.js`, `search.js`, `backup.js`, `furniture.js`
4. `js/ui/dom.js`, `js/ui/icons.js`, `js/ui/router.js`, `js/ui/components/breadcrumb.js`, `list.js`, `form.js`, `dialog.js`, `detailbar.js`, `contextmenu.js`, `bubble.js`, `longpress.js`
5. `js/ui/layout.js`
6. `js/ui/views/treerail.js`, `browse.js`, `location-actions.js`, `item-actions.js`, `item.js`, `search.js`, `searchbar.js`, `settings.js`, `furniture.js` (vue), `location.js`
7. `js/pwa.js`
8. `js/main.js` (dernier : démarre l'application)

Chaque fichier suit le même patron : une fonction auto-exécutée (IIFE) qui lit `window.Rangement`, ajoute son module et n'expose rien d'autre. Les appels entre modules d'un même niveau (ex. un composant qui appelle le routeur) se font à l'exécution, pas au chargement, ce qui évite les dépendances d'ordre fragiles.

### API principale (V008)

| Module | Rôle |
|---|---|
| `Rangement.store.init()` | Charge les données ; si elles sont illisibles ou incohérentes, les met de côté (`rangement.data.corrupt`) et démarre à vide |
| `Rangement.store.update(fn)` | Applique `fn` à une **copie** des données ; la copie n'est adoptée (et sauvegardée) que si elle reste cohérente. Renvoie `{ ok, errors }` |
| `Rangement.store.replaceAll(data)` | Remplace tout le contenu (import, démo) après validation |
| `Rangement.storage.getAux / setAux / removeAux(nom)` | Clés annexes `rangement.data.<nom>` (`preimport`, `meta`), avec repli en mémoire comme les données |
| `Rangement.store.childLocations / itemsIn / pathOf / countIn` | Lecture : enfants, objets, chemin complet, comptage récursif |
| `Rangement.store.getLocation(id) / getItem(id)` | Lecture d'un emplacement / d'un objet par identifiant (`null` si inconnu) |
| `Rangement.models.validateData(data)` | Contrôle : ids uniques, parents existants, pas de boucle, objets rattachés à un emplacement valide |
| `Rangement.models.normalizeText(texte)` | Minuscules sans accents ; sert aux comparaisons de noms (et à la recherche, jalon 4) |
| `Rangement.features.locations.create / update / move / remove` | Gestion des emplacements. Renvoient `{ ok }` ou `{ ok: false, error }` (message en français, affiché tel quel) |
| `Rangement.features.locations.parentChoices(id)` | Destinations possibles pour un déplacement (tout sauf l'emplacement et son contenu) |
| `Rangement.features.items.create / update / move / remove` | Gestion des objets. Renvoient `{ ok }` ou `{ ok: false, error }` (message en français). `update` laisse inchangé tout champ absent (`undefined`) |
| `Rangement.features.items.locationChoices()` | Emplacements où ranger un objet, avec chemin complet (`Séjour › Meuble living`) |
| `Rangement.features.items.parseQuantity / parseTags / formatQuantity` | Lecture de la saisie : quantité (vide = 1, nombre entier, 0 accepté), mots-clés séparés par des virgules |
| `Rangement.features.search.search(texte)` | Recherche : renvoie `{ terms, items: [{ item, path, score }], locations: [{ location, path, score }] }`, triés par pertinence puis par nom |
| `Rangement.features.backup.init()` | À appeler après `store.init()` : charge le suivi des sauvegardes et marque « modifié » à chaque `store:changed` |
| `Rangement.features.backup.prepareExport() / markExported()` | Contenu et nom du fichier à télécharger (`{ filename, text, counts }`) ; enregistre la date de l'export et remet le suivi à « aucune modification » |
| `Rangement.features.backup.parse(texte)` | Analyse un fichier : `{ ok, data, counts, exportedAt }` ou `{ ok: false, error }` (message en français) |
| `Rangement.features.backup.importData(data) / undoInfo() / undoImport()` | Remplace toutes les données après mise de côté d'une copie de sécurité ; annulation de la dernière importation |
| `Rangement.features.backup.status()` | `{ lastExportAt, dirty, counts }` pour l'écran Réglages |
| `Rangement.pwa.init()` | Enregistre `sw.js` (si https/localhost ; sans effet en `file://`), écoute l'invite d'installation. Appelé par `main.js` |
| `Rangement.pwa.status()` | `{ supported, registered, cacheName, updateReady, canInstall, standalone, error }` |
| `Rangement.pwa.checkUpdate() / applyUpdate() / clearCache() / promptInstall()` | Chercher une nouvelle version ; l'activer (sur accord) ; supprimer les caches et le service worker puis recharger ; déclencher l'installation |
| `Rangement.models.levelOf(profondeur) / rootLabel()` | Niveau de couleur (`piece`, `emplacement`, `sous`) ; libellé « Logement » + précision (`Rangement.config.dwellingName`) |
| `Rangement.store.depthOf(id)` | Profondeur d'un emplacement (0 = pièce) |
| `Rangement.features.locations.duplicate(id, { name, parentId, content })` | Duplication ; `content` : `none`, `structure`, `all` |
| `Rangement.features.items.duplicate(id, { name, locationId })` / `quantityError(texte)` | Duplication d'un objet ; message d'erreur de quantité (ou `null`) |
| `Rangement.features.backup.needsBackup()` | Vrai si des données ne figurent dans aucune sauvegarde exportée (pastille) |
| `Rangement.ui.views.browse.expandAll() / collapseAll() / setMode('wide'` ou `'mini')` | Arborescence : tout déplier / replier, largeur |
| `Rangement.ui.router.back() / canBack() / closeSettings()` | Bouton Retour de l'application (historique interne, sinon niveau supérieur) ; fermeture des Réglages vers la vue d'origine |
| `Rangement.ui.router` | Routes : `#/` (logement), `#/l/<id>` (emplacement), `#/o/<id>` (fiche d'un objet), `#/s/<texte>` (recherche), `#/r` (réglages). `current()` renvoie `{ locationId, itemId, query, settings }` (`query` vaut `null` hors recherche) ; `href(id)`, `itemHref(id)`, `searchHref(texte)`, `settingsHref()`, `navigate(id)`, `search(texte)` |
| `Rangement.ui.components.dialog.form / confirm / alert` | Dialogues modaux (`<dialog>`), retour du focus à la fermeture |
| `Rangement.features.furniture.layout(id[, essai]) / get(id) / set(id, { ratio, feet }) / setGrid(id, { cols, rows, top, bottom }) / move(id, dc, dr) / resize(id, dw, dh) / isFurniture(id) / hasGraphic(id)` | Grille d'un emplacement dessiné : `layout` renvoie `{ C, L, T, B, cells: [{ id, zone, col, row, w, h }] }` (places automatiques calculées si rien n'est enregistré). `hasGraphic(id)` dit si la Vue graphique est proposée. `move`, `resize` et `setGrid` enregistrent toute la grille et renvoient `{ ok }` ou `{ ok: false, error }` (message en français). |
| `Rangement.ui.views.furniture.create(id) / createPlan([id]) / switcher(portée) / mode(portée) / setMode(m, portée)` | Vue graphique d'un meuble ; plan du logement (`createPlan`) ; commutateur Liste / Vue graphique (choix mémorisé, clé annexe `view`) ou, avec la portée `'plan'`, Liste / Plan (clé annexe `planview`) |
| `Rangement.features.furniture.ROOT` | Identifiant spécial du logement : `layout(ROOT)`, `setGrid(ROOT, { cols, rows })` ; `move` / `resize` sur une pièce travaillent sur le plan. Une seule zone (`body`), 20 colonnes et 20 lignes au plus proposées |
| `Rangement.store.plan() / Rangement.models.cleanPlan(p)` | Plan du logement `{ cols, rows }` ou `null` ; nettoyage d'un plan lu (import, stockage) |
| `Rangement.ui.components.contextmenu.open({ anchor, focusTo?, title, subtitle?, level?, primary?, items })` / `close()` / `isOpen()` | Menu contextuel placé près de `anchor` (sous, sinon au-dessus, toujours dans l'écran) ; `primary` = `{ label, run }` (grand bouton en tête), `items` = `[{ label, run, danger? }]` ; choisir une commande ferme le menu puis l'exécute ; Échap / appui ailleurs rendent le focus à `focusTo` |
| `Rangement.ui.components.detailbar.create({ ref, path, title, level, kind?, info?, actions?, views?, … })` | En-tête figé ; renvoie `{ head }`. `kind` = libellé de catégorie ; `info` = lignes de l'info-bulle ℹ️ ; `actions` = `[{ label, run, danger?, icon? }]` du menu déroulant « Actions » ; `views` = boutons-pictogrammes d'affichage : avec « Actions », ils forment le groupe des commandes ; le groupe d'arborescence (`#tree-toggle`, ▲ ▼) est ajouté par le composant |
| `Rangement.ui.components.bubble.open({ anchor, title?, lines, level? }) / toggle(cfg) / close() / isOpen()` | Info-bulle près de `anchor` (texte toujours échappé) ; Échap, un appui ailleurs, un changement d'écran ou de données la ferment |
| `Rangement.ui.views.browse.setMode('wide' \| 'mini' \| 'hidden') / setVisible(b) / toggleVisible() / isVisible() / mode()` | Arborescence : `setMode` règle la largeur et affiche le volet (`hidden` le masque) ; `setVisible` / `toggleVisible` affichent ou masquent (écran déplié : le volet ; écran replié : le volet recouvrant) ; émettent `view:changed` |
| `Rangement.ui.views.searchbar.setOpen(b, noFocus?) / isOpen()` | Affiche ou masque le champ de recherche ; une route de recherche l'affiche toujours |
| `Rangement.ui.views.furniture.helpButton(portée)` | Bouton « ? » du mode modification (`#plan-help`) : l'explication s'affiche dans une info-bulle |
| `Rangement.ui.icons.create(nom, taille?) / has(nom)` | Élément `<svg>` décoratif (`aria-hidden`, trait en `currentColor`) ; nom inconnu = SVG vide |
| `Rangement.ui.components.longpress.attach(noeud, { onShort(ev), onLong(ev), delay? })` | Appui simple = clic (Entrée au clavier compris) ; appui long = maintien ≈ 450 ms (annulé si le doigt bouge de plus de 10 px), clic droit ou touche Menu (`contextmenu`) ; vibration brève ; menu natif supprimé ; le clic qui suit un appui long est ignoré (sauf clavier, `detail` = 0) |
| `Rangement.features.furniture.pin(id)` | Enregistre la disposition actuelle (places automatiques comprises) ; appelé avant de créer un emplacement sur une case libre |
| `Rangement.features.locations.create({ …, geometry })` | `geometry` facultatif : place (zone, col, row, w, h) donnée au nouvel emplacement |
| `Rangement.ui.views.locationActions.openCreate(parentId, spot?)` | `spot` = `{ zone, col, row }` : crée l'emplacement sur cette case libre |
| `Rangement.ui.views.furniture.editButton(portée) / openGrid(id) / isEditing()` | Bouton « Modifier le plan » (`#plan-edit`, `aria-pressed`) ; boîte de réglage de la grille ; état du mode modification |
| `Rangement.events` | `view:changed`, `store:changed`, `store:error`, `route:changed`, `layout:changed`, `backup:changed`, `pwa:changed` |

Si `localStorage` est indisponible, `storage.js` bascule en mémoire et l'appli affiche un avertissement.

### Règles de gestion des emplacements (V004)

- Le **nom est obligatoire** ; il est rogné des espaces.
- Deux emplacements **frères** (même parent) ne peuvent pas porter le même nom, sans tenir compte de la casse ni des accents. Deux « Commode » dans des pièces différentes sont autorisés.
- Un emplacement **ne peut pas être déplacé** dans lui-même ni dans son propre contenu.
- La **suppression est refusée** tant que l'emplacement contient des emplacements ou des objets ; sinon une confirmation est demandée.
- À la création : type **Pièce** par défaut à la racine, **Autre** par défaut ailleurs.

### Règles de gestion des objets (V005, précisées en V006)

- Un objet est **toujours rangé dans un emplacement** (jamais directement à la racine du logement) : le bouton « Ajouter un objet ici » n'existe que dans un emplacement.
- Le **nom est obligatoire** (rogné des espaces). **Deux objets ne peuvent pas porter le même nom dans un même emplacement** (casse et accents ignorés) — *validé en V006* ; pour des objets identiques, utiliser la quantité ou un suffixe numérique (« sac à dos 1 », « sac à dos 2 »). Le même nom reste possible dans des emplacements différents ; un déplacement vers un emplacement contenant déjà ce nom est refusé.
- **Quantité** : 1 par défaut si le champ est vide ; **nombre entier** positif ou nul (pas de décimales pour l'instant, à revoir à l'usage) ; **0 accepté** (objet épuisé mais encore référencé) — *validé en V006*. Un objet de quantité 0 est affiché **grisé** (fond et texte) dans les listes et sur sa fiche (mention « épuisé »).
- **Mots-clés** : saisis séparés par des virgules (`optique, nature`) ; espaces rognés, doublons ignorés sans tenir compte de la casse ni des accents.
- Déplacer un objet : tous les emplacements sont proposés avec leur chemin complet ; l'emplacement actuel est présélectionné.
- Supprimer un objet : confirmation demandée, puis retour à l'emplacement qui le contenait.
- Un objet est affiché sur sa propre fiche (`#/o/<id>`), accessible en touchant sa ligne dans la liste d'un emplacement. Le fil d'Ariane de la fiche mène à chaque niveau de son emplacement.

### Règles de la recherche (V006)

- Le **champ de recherche est permanent** sous l'en-tête (écran déplié comme replié). Il affiche les résultats dans le volet de détail, à chaque frappe, sur la route `#/s/<texte>`.
- **Casse et accents ignorés** ; **pas de tolérance aux fautes de frappe** (décision validée) ; le texte cherché est un fragment (« pile » trouve « Piles neuves »).
- **Plusieurs mots** : tous doivent être trouvés (chacun dans au moins un champ).
- **Champs examinés** — objets : nom, mots-clés, note, chemin de l'emplacement ; emplacements : nom, note, chemin des parents. **Classement** : nom (4) > mots-clés (3) > note (2) > chemin (1), les points des mots s'additionnent ; à égalité, ordre alphabétique.
- Résultats en deux sections : **Objets** puis **Emplacements**, chaque ligne affichant le **chemin complet** (`Séjour › Meuble living › Tiroir bas gauche`). Les objets épuisés restent trouvés (grisés).
- La première frappe ajoute une entrée d'historique ; les suivantes la remplacent : le bouton Retour revient à l'écran d'où l'on est parti. Depuis une fiche, Retour restaure la recherche.

### Règles de la sauvegarde (V007)

- **Écran Réglages** (`#/r`) : lien « Réglages » dans l'en-tête (toujours visible), bouton « Importer une sauvegarde » sur l'écran de démarrage. Accessible même sans données.
- **Export** : télécharge un fichier JSON `rangement-AAAA-MM-JJ-HHMM.json` (heure de l'appareil) contenant `schemaVersion`, `appVersion`, `exportedAt`, `locations`, `items`. Désactivé tant que le logement est vide.
- **Suivi** : l'écran indique la date de la dernière sauvegarde exportée et si des modifications (ajout, changement, suppression, import) ont eu lieu depuis. Ce suivi est propre à l'appareil et au navigateur (clé annexe `meta`).
- **Import** : le fichier est analysé avant toute modification. Il est **refusé** (message explicite, données intactes) s'il est vide, trop volumineux (> ~4,5 Mo), pas du JSON, d'un `schemaVersion` différent, sans listes `locations`/`items`, ou incohérent (parent introuvable, boucle, identifiant en double, objet sans emplacement, quantité invalide). Les champs inconnus sont ignorés, les champs facultatifs absents sont complétés.
- **Confirmation** : l'import **remplace toutes les données actuelles** (pas de fusion) ; une boîte de dialogue résume le contenu du fichier et celui du logement actuel avant d'agir.
- **Copie de sécurité** : avant chaque import, les données actuelles sont mises de côté (clé annexe `preimport`, une seule copie : la plus récente). Si cette copie ne peut pas être conservée (stockage plein), l'import est refusé. Le bouton « Annuler la dernière importation » restaure cette copie, puis la supprime.
- Les noms de fichiers et les contenus importés sont toujours affichés comme du texte (jamais interprétés comme du HTML).

### Règles de la PWA (V008)

- **Manifeste** : `start_url` et `scope` relatifs (le site fonctionne sous `https://<compte>.github.io/rangement/`), affichage `standalone`, couleurs `#16222A`, 4 icônes (192 et 512 px, `any` et `maskable`). Icône Apple (`apple-touch-icon`) pour l'iPad.
- **Pré-cache** : la liste `FILES` de `sw.js` est écrite en dur ; **tout fichier ajouté à l'application doit y figurer** (le test `test_jalon6.py` vérifie que chaque fichier de `js/` et chaque ressource de `index.html` y est). L'installation est « tout ou rien ».
- **Version** : `VERSION` dans `sw.js` = version de l'application (`js/config.js`) ; cache nommé `rangement-Vxxx`. Les deux sont à changer à chaque livraison (vérifié par les tests).
- **Mise à jour** : un nouveau `sw.js` s'installe en arrière-plan et **attend** ; une pastille ● apparaît sur « Réglages » et le bouton « Mettre à jour » y est proposé. Après accord, la page se recharge. Un simple rechargement ne change pas de version.
- **Stratégie** : cache d'abord pour les fichiers de l'application ; aucune interception des autres domaines ni des requêtes non GET ; hors ligne, une navigation inconnue retombe sur `index.html`. Les données (`localStorage`) ne passent jamais par le service worker.
- **Vider le cache** (Réglages) : supprime les caches `rangement-*` et le service worker, recharge ; les données ne sont pas touchées.
- **`file://`** : pas de service worker ; Réglages l'indique. Un refus d'enregistrement n'empêche pas l'application de fonctionner.

### Règles du jalon 6 bis (V009)

- **Arborescence** : repliée à l'ouverture (seules les pièces sont visibles) ; un bouton ▸/▾ avant chaque libellé déplie ou replie (animation de 0,16 s, sans reconstruire l'arbre) ; le bouton de la ligne « Logement » déplie / replie tout. Quand l'élément affiché change, ses parents s'ouvrent. L'état déplié n'est pas conservé entre deux ouvertures.
- **Ligne « Logement » figée** en haut du volet ; le libellé = « Logement » + `Rangement.config.dwellingName` (vide pour l'instant ; prévu pour plusieurs logements).
- **Rail** (écran déplié) : le bouton « « » réduit le volet à ~76 px (choix mémorisé, clé annexe `ui`) ; chaque élément devient une pastille colorée sans libellé ; un tap ouvre une infobulle (chemin, nom, **Ok** = ouvrir le détail, **Annuler**) par-dessus le volet de droite ; un tap ailleurs (sans effet sur ce qu'il touche) ou Échap la ferme.
- **Détail** : fil d'Ariane + titre (+ flèches ▲ niveau supérieur, ▼ niveau inférieur — dernier enfant visité, sinon le premier — + bouton « Actions » qui replie la barre d'actions) restent figés ; l'état replié est conservé d'un écran à l'autre.
- **Duplication** (emplacement ou objet) : nom et destination préremplis, la copie est refusée tant qu'on ne change pas le nom **ou** la destination (règles d'unicité habituelles) ; un emplacement se copie seul, avec ses sous-emplacements, ou avec tout son contenu ; un objet reprend quantité, mots-clés et note ; on arrive sur la copie.
- **Retour** (à gauche du champ de recherche) : entrée précédente de l'historique de l'application, sinon niveau supérieur ; désactivé sur la première vue de la racine. Un second appui sur « Réglages » les referme et revient à la vue d'origine.
- **Saisie interdite** : un champ à valeur interdite (quantité décimale…) affiche son message dès qu'on le quitte et reprend le focus tant qu'il n'est pas corrigé ; Annuler, Échap et un changement de vue ferment la boîte sans rien enregistrer.
- **Pastille de sauvegarde** : point orange avant « Réglages » s'il y a des données jamais exportées ou modifiées depuis le dernier export (point jaune après = mise à jour disponible).
- **Code couleur** par niveau : pièces (vert-bleu), emplacements de premier ordre (brun), sous-emplacements (brun clair), objets (bleu), objet de quantité 0 (gris). Texte coloré quand l'élément n'est pas sélectionné, couleur de fond avec texte blanc quand il l'est ; boutons « Ajouter… » de la couleur de ce qu'ils créent.

### Règles du jalon 7 (V010, grille en V011)

- **Vue graphique** : pour les **meubles** (emplacements de premier niveau) ; *depuis la V017, aussi pour tout niveau plus bas qui a des sous-emplacements*. Un commutateur « Liste / Vue graphique » apparaît sous l'en-tête du détail ; la liste reste le mode par défaut ; le choix est mémorisé (clé annexe `view`).
- **Grille** : le meuble a `C` colonnes et `L` lignes (réglables : 1 à 6 colonnes, 1 à 8 lignes), plus une bande de `T` lignes **au-dessus** et une de `B` lignes **en dessous** (0 à 3). Chaque sous-emplacement occupe un rectangle de cases (`zone` : `top`, `body`, `bottom` ; `col`, `row`, `w`, `h`), sans chevauchement ni sortie de la grille. Un sous-emplacement ne peut pas chevaucher deux zones.
- **Remplissage automatique** : un sous-emplacement sans place enregistrée prend la première case libre du meuble (1 × 1). Dès qu'on modifie la disposition, toutes les places sont **enregistrées** et ne bougent plus ; la grille s'agrandit si besoin (rien n'est jamais caché). Les réglages de la V010 (ordre `pos`, largeur `span`) sont convertis automatiquement.
- **Réglages** (« Ajuster la disposition ») : proportions, colonnes, lignes, dessus, dessous, pieds. Un emplacement se sélectionne en le touchant ; deux **pavés de quatre flèches** sans libellé (déplacer d'une case ; taille : + / − en largeur et en hauteur) restent **fixés en bas de l'écran** pendant le défilement ; toucher une case libre y place l'emplacement. **Déplacer sur une case occupée par un seul emplacement échange les deux** (l'autre doit tenir à la place libérée). Les refus (plusieurs emplacements sur le chemin, sortie de grille, cases occupées à supprimer, chevauchement de zones) s'affichent en clair et ne changent rien.
- **Défilement** : un réglage ou un déplacement ne remonte pas la page (la position de défilement du volet est conservée quand l'affichage est redessiné ; seul un changement d'écran remonte en haut).
- **Dessin** : HTML/CSS (texte toujours échappé). Le cadre du meuble a la proportion choisie mais **grandit** si les lignes sont nombreuses (64 px minimum par ligne) ; les libellés sont tronqués dans leur case (nom complet au toucher / en infobulle), jamais débordants. Chaque case indique son nombre d'objets (sous-niveaux compris) et, si elle fait au moins deux cases, son niveau.
- **Niveaux** : une légende rappelle toujours le niveau affiché (« Niveau 2 — Emplacement « Meuble living » : ses sous-emplacements (niveau 3)… »). Une icône (carrés emboîtés + nombre) signale un sous-emplacement qui en contient d'autres. *(Depuis la V017, son appui ouvre réellement cet emplacement — voir « jalon 9, étape 3 bis » — au lieu de le dessiner dans le meuble ; plus de « Remonter au niveau N », on remonte par ▲ ou Retour.)*
- **Stockage** : dans `geometry` (`ratio`, `feet`, `cols`, `rows`, `top`, `bottom` pour l'emplacement dessiné ; `zone`, `col`, `row`, `w`, `h` pour la place d'un sous-emplacement) ; `schemaVersion` inchangé (1) ; repris par l'export / import.
- **Arborescence** : le nombre d'objets (total, sous-emplacements compris) s'affiche à droite de chaque libellé (rien s'il est nul), hors du lien.

### Règles du jalon 8 (V013)

- **Plan du logement** : à la racine, un commutateur « Liste / Plan » (choix mémorisé séparément de celui des meubles, clé annexe `planview`) ; la liste reste le mode par défaut. Les **pièces** sont des tuiles collées sur la même grille que les meubles ; **pas de murs, portes ni fenêtres** pour l'instant, pas de formes en L (une pièce = un rectangle de cases).
- **Grille** : `cols` × `rows` enregistrés dans `plan` (enveloppe de stockage), réglables de 1 à 20 ; une seule zone (pas de bandes, pas de pieds, pas de proportions) ; le cadre est à peu près carré par case, il **défile horizontalement dans son cadre** (jamais la page) quand les colonnes sont nombreuses (72 px minimum par colonne). Disposition automatique : 2 colonnes jusqu'à 4 pièces, 3 jusqu'à 9, 4 au-delà ; les places sont **figées** dès la première modification, une pièce créée ensuite prend la première case libre.
- **Ajustement** (« Ajuster le plan ») : mêmes commandes que pour un meuble (sélection, deux pavés de flèches fixés en bas, échange de deux pièces, cases libres, refus en clair) ; un changement d'écran referme l'ajustement.
- **Place d'une pièce** : dans sa `geometry` (`zone: 'body'`, `col`, `row`, `w`, `h`) ; `schemaVersion` inchangé ; reprise par l'export / import (le `plan` aussi ; une sauvegarde sans `plan` rétablit la disposition automatique ; un `plan` illisible est ignoré).
- **Niveaux** : *(V013 : l'icône sur une tuile dessinait les emplacements de la pièce dans le plan du logement ; depuis la V017 elle ouvre la pièce, qui a son propre plan.)*

### Règles du jalon 9, étape 1 (V014)

- **Orientation** : les plans (logement › pièces › meubles) deviennent l'élément principal de l'interface ; la liste et l'arborescence restent des vues secondaires (recherche, accessibilité, secours). Tout doit tenir sur l'écran déplié (plan et menus), avec possibilité d'agrandir le plan. Étapes prévues : 1 plan ajusté à l'écran (livrée) ; 2 menu contextuel (« Ouvrir » en tête, commandes de l'élément, pavés de flèches intégrés, bouton « + » flottant pour créer au niveau du plan) ; 3 pictogrammes « info » ; 4 plan en vue d'accueil.
- **Plan ajusté à l'écran** (par défaut) : `fit()` calcule la taille d'une case carrée pour que le plan tienne en largeur dans le volet et, autant que possible, en hauteur (jamais moins de 48 px à cause de la hauteur ; jamais moins de 28 px : en dessous, le cadre défile). Recalcul au redimensionnement, au changement de mise en page et quand la barre « Actions » se replie. Les cases de moins de 60 px deviennent **compactes** (nom tronqué, nombre d'objets seul, pas de niveau ; nom complet au toucher / en infobulle).
- **Taille réelle** : bouton « Agrandir » / « Ajuster à l'écran » (choix mémorisé, clé annexe `planzoom`) ; cases carrées d'au moins 72 px, le cadre défile horizontalement dans son cadre (jamais la page).
- **Plan d'une pièce** : une pièce a, comme le logement, un commutateur Liste / Plan (même choix mémorisé, clé `planview`) ; ses meubles sont posés sur la même grille (jusqu'à 20 × 20, une seule zone, ni bandes ni pieds ni proportions), ajustables directement sans passer par l'ajustement du logement. Colonnes et lignes de la pièce dans sa `geometry` (à côté de sa propre place dans le plan du logement). Un meuble et ses niveaux inférieurs gardent leur vue d'origine (bandes, proportions, pieds).

### Règles du jalon 9, étape 2 (V015)

- *(V019 : le menu s'ouvre à l'appui long ; un appui simple ouvre la case ; « Ouvrir » n'est plus en grand ; le bouton « + » est supprimé — voir « Règles du jalon 10 »)* **Menu contextuel** : dans un plan (logement, pièce) ou la vue graphique d'un meuble, une case n'est plus un lien mais un bouton ; un appui ouvre près d'elle un menu : **« Ouvrir »** (plus grand, en gras, a le focus), puis **Placer et dimensionner**, **Ajouter un objet ici**, **Ajouter un emplacement ici**, **Modifier**, **Déplacer**, **Dupliquer**, **Supprimer** (mêmes boîtes de dialogue et mêmes garde-fous que le menu « Actions »). En-tête du menu : chemin du parent et nom (colorés par niveau). Pas d'appui long. Le bandeau de niveau inférieur d'une case reste un bouton à part (V017 : il ouvre l'emplacement, comme « Ouvrir »).
- **Placement** : « Placer et dimensionner » sélectionne la case et affiche les deux pavés de flèches (déplacer / taille, échange, cases libres) fixés en bas, avec deux boutons : **Grille…** (réglages de la grille) et **Terminer** (masque le pavé). Pendant le placement, un appui sur une case la sélectionne (pas de menu) ; un changement d'écran referme le placement. Le bouton « Ajuster le plan / la disposition » et les listes de réglages en ligne **disparaissent**.
- **Bouton « + » flottant** (rond, en bas à droite de l'écran, caché pendant le placement) : menu pour agir **au niveau affiché** : à la racine « Ajouter une pièce » ; dans une pièce, un meuble ou un niveau inférieur « Ajouter un objet ici », « Ajouter un emplacement ici » ; toujours « Régler la grille… ».
- **Réglage de la grille** (boîte de dialogue, valeurs actuelles préremplies) : colonnes et lignes (1 à 20 pour un plan, 1 à 6 × 1 à 8 pour un meuble) ; pour un meuble aussi proportions, dessus, dessous (0 à 3) et pieds. Un refus (cases occupées) s'affiche dans la boîte, qui reste ouverte, rien ne change ; « Appliquer » sans changement ne fige aucune place.
- Le pavé de flèches affiche « « nom » : dans le plan, colonne N, ligne M, taille w × h. » ; la hauteur réservée au plan pendant le placement est de 230 px.

### Règles du jalon 9, étape 3 (V016)

- **ℹ️** : pictogramme juste après le nom de l'élément affiché (logement, pièce, meuble, niveaux inférieurs, fiche d'un objet ; pas sur la recherche ni les Réglages). Un appui ouvre une **info-bulle** : niveau, nombre de sous-emplacements, objets rangés directement, contenu total (tous niveaux) et note ; pour un objet : niveau, emplacement, quantité. Texte toujours affiché comme du texte.
- **Texte de rappel supprimé** sous « Liste / Plan » ; il a disparu en V017 (plus de niveau dessiné dans le plan du parent : l'en-tête décrit toujours l'emplacement affiché). La ligne « Type — note » sous le titre disparaît (le type monte dans l'en-tête, la note dans l'info-bulle).
- **Libellé de catégorie** (Pièce, Meuble, Tiroir…, « Objet » sur une fiche) à la suite du nom, sur la même ligne ; il est tronqué en premier si la place manque, et un **petit chevron rotatif** apparaît alors (seulement s'il y a troncature) pour ouvrir une bulle avec le libellé complet.
- **Menu « Actions »** : le bouton garde sa place dans l'en-tête mais ouvre un **menu déroulant** (même composant que le menu contextuel) ; la barre de boutons sous l'en-tête et la mémorisation « replié / déplié » disparaissent. Commandes : emplacement → Ajouter un objet ici, Ajouter un emplacement ici, Modifier, Déplacer, Dupliquer, Supprimer ; logement → Ajouter une pièce ; objet → Modifier, Déplacer, Dupliquer, Supprimer. Les boutons « Ajouter… » ne sont plus colorés par niveau.
- **Liste / Plan** (logement, pièces) et **Liste / Vue graphique** (meubles) sont dans l'en-tête figé, **sous les flèches de niveau et « Actions »** ; l'en-tête est en deux colonnes (fil d'Ariane + nom à gauche, commandes à droite) pour que le bandeau ne grandisse pas (à peu près la même hauteur qu'un sous-emplacement sans commutateur). Boutons du commutateur de 32 px de haut, zone d'appui étendue à ~44 px. Écran replié : le fil d'Ariane prend toute la largeur, nom et commandes dessous.

### Règles du jalon 9, étape 3 bis (V017)

- **Navigation unique** : un seul moyen d'entrer dans un niveau, la vraie navigation (`#/l/<id>`). Le **bandeau de niveau** d'une case (carrés emboîtés + nombre de sous-emplacements) fait la même chose que « Ouvrir » du menu contextuel : en-tête, fil d'Ariane, ℹ️, « Actions » et Liste / Plan sont ceux de l'emplacement ouvert. Le mode « niveau dessiné dans le plan du parent » (`focus`, texte de rappel `.furn-caption`, bouton « Remonter… ») est **supprimé** ; on remonte par ▲, le bouton Retour ou le fil d'Ariane.
- **Cases étroites** : le bandeau est **masqué quand la case fait moins de 85 px de large** (requête de conteneur CSS `@container (max-width: 84px)` sur `.furn-cell`, et classe `.furn-compact` du plan ajusté) ; toute la case ouvre alors le menu contextuel (« Ouvrir » en tête). Le nombre de sous-emplacements reste lisible dans ℹ️. Le bandeau est aussi absent pendant le placement (un appui sélectionne seulement la case).
- **Vue graphique à tous les niveaux** : `Rangement.features.furniture.hasGraphic(id)` — un meuble (toujours) ou tout emplacement plus profond qui contient des sous-emplacements. Le commutateur Liste / Vue graphique (choix mémorisé, clé annexe `view`) est alors proposé ; un niveau sans sous-emplacement n'a que la liste. Un niveau plus bas se dessine comme un meuble (proportions, dessus, dessous, pieds, grille 6 × 8 au plus) ; sa grille et les places de ses sous-emplacements sont dans les `geometry` habituelles ; un placement, un menu contextuel et le « + » y fonctionnent comme sur un meuble.

### Règles du jalon 9, étape 4 (V018)

- **Plan en vue d'accueil** : la vue graphique est la vue **par défaut** à tous les niveaux (logement, pièces : « Plan » ; meubles et niveaux plus bas avec sous-emplacements : « Vue graphique »). `Rangement.ui.views.furniture.mode(portée)` renvoie `graphic` sauf si l'utilisateur a choisi la liste (clés annexes `planview` et `view`, valeur `list`). Le plan s'ajuste à l'écran (`fit()`).
- **Zones de l'écran déplié** : en-tête (nom, Arborescence, Réglages) et bandeau de recherche pleine largeur, figés ; volet d'arborescence figé à gauche ; à droite, en-tête figé du détail (fil d'Ariane, nom, ℹ️, libellé, flèches, Actions) puis zone du plan, seule à défiler.
- *(V019 : ces boutons ne sont plus flottants mais alignés à droite dans l'en-tête, avec pictogrammes ; voir « Règles du jalon 10 »)* **Boutons flottants** (`.float-zone` dans `.detail-sticky`, sous l'en-tête figé ; `detailbar.create({ floats, floatReserve })`) : **un seul bouton Liste / Plan** à gauche, dont le libellé indique **l'action** (`➔ Liste` quand on est sur le plan, `➔ Plan` ou `➔ Vue graphique` quand on est en liste ; id `view-toggle`, `data-mode` = mode courant) ; **Agrandir / Ajuster à l'écran** à droite (`#plan-zoom`, icône SVG seule, nom accessible = l'action, `aria-pressed` = taille réelle), uniquement sur un plan (logement, pièce). Boutons de 44 px, fond sombre semi-opaque ; sur un plan ils recouvrent le coin du plan, en liste de la place est réservée (`.detail-sticky--reserve`). `furniture.switcher(portée)` et `furniture.zoomButton()` les construisent ; un appui émet `view:changed`.
- **Arborescence à trois états** : `large`, `rail` (**défaut**), `masquée` (écran déplié seulement) ; choix non mémorisé depuis la V019 (rail à chaque démarrage) ; bouton « Arborescence » dans l'en-tête (`#tree-cycle`, large › rail › masquée › large) en plus des boutons « » du volet ; `browse.cycle()`, `setMode('wide' | 'mini' | 'hidden')`. Masquée : le détail prend toute la largeur.
- **Reporté** (versions suivantes) : pictogrammes SVG dans les autres boutons, « respiration » des cases libres en placement.

### Règles du jalon 10 (V019)

- **Appui simple / appui long** sur une case d'un plan ou d'une vue graphique : un appui simple **ouvre** l'emplacement ; un **appui long** (≈ 450 ms) ouvre le **menu contextuel** : Ouvrir (écrit comme les autres commandes), Placer et dimensionner, Ajouter un objet ici, Ajouter un emplacement ici, Modifier, Déplacer, Dupliquer, Supprimer. Clic droit et touche Menu / Maj+F10 valent un appui long ; Entrée sur une case l'ouvre. Le bandeau de niveau (carrés emboîtés + nombre) n'est plus qu'un **indicateur** (toute la case ouvre) ; il reste masqué sur les cases de moins de 85 px et pendant la modification.
- **Cases libres** : toujours dessinées (pointillés fins ; plus épais en modification). Un appui simple n'y fait rien ; un **appui long** (ou Entrée au clavier) ouvre un menu : *logement* → Ajouter une pièce ici, Régler la grille… ; *pièce, meuble, niveau plus bas* → Ajouter un emplacement ici, Ajouter un objet ici, Régler la grille…. « Ajouter un emplacement / une pièce ici » **fige d'abord la disposition** (`furniture.pin`) puis crée l'emplacement **à cette case** (`geometry`, taille 1 × 1) : rien d'autre ne bouge. Un plan sans emplacement affiche ses cases libres et un texte d'aide.
- **Bouton « + » flottant supprimé.** Création : menu « Actions » de l'en-tête (ajouter un objet / emplacement / pièce au niveau affiché) ou case libre. « Régler la grille… » : menu « Actions » (en vue graphique seulement), « Grille… » du mode modification, menu d'une case libre.
- **Mode « Modifier le plan »** : bouton-pictogramme `#plan-edit` de l'en-tête (en vue graphique : plan du logement, pièce, meuble ; absent en liste), `aria-pressed` quand il est actif. Actif : le plan est entouré d'un contour en pointillés ; un appui simple **sélectionne** une case (pavés de flèches, « Grille… », « Terminer ») ; un appui sur une case libre y place la case sélectionnée ; un appui long ouvre quand même le menu. Sans sélection : « Grille… » et « Terminer » et un texte d'aide. Il se termine par le même bouton, par « Terminer », par un changement d'écran ou en passant à la liste. « Placer et dimensionner » (menu d'une case) active le mode avec la case sélectionnée.
- **Boutons d'affichage** : trois boutons ronds de 44 px, **alignés à droite dans l'en-tête figé, sous les flèches ▲ ▼ et « Actions »** (écran replié : sur une troisième ligne, à droite) — Liste / Plan (`#view-toggle`, pictogramme = vue vers laquelle on bascule), Agrandir / Ajuster à l'écran (`#plan-zoom`, plans seulement), Modifier le plan (`#plan-edit`). Le nom accessible dit l'action (texte masqué + `aria-label` + infobulle). Plus de zone flottante : **rien ne recouvre plus le plan**.
- **Bandeaux resserrés** : sur l'écran déplié, en-tête de l'application et recherche tiennent sur **une seule ligne** (`.app-top` : nom, Retour + champ, Arborescence, Réglages, version) ; écran replié : deux bandeaux superposés comme avant. L'en-tête figé du détail perd son grand remplissage haut (8 px au lieu de 24). Le cadre d'un meuble ne dépasse plus la largeur disponible (`width: 100 %`). Réserve de hauteur sous un plan : 40 px (remplissage du volet compris), pour qu'un plan qui tient dans l'écran ne fasse pas défiler.
- **Pictogrammes** (`icons.js`, SVG filaires fournis par l'utilisateur) : Liste / Plan / Modifier le plan dans l'en-tête, engrenage devant « Réglages », crayon devant « Modifier » et « Placer et dimensionner » dans les menus, « déplacer » et « agrandir » au centre des pavés de flèches, coins du bouton Agrandir / Ajuster.
- **Arborescence** : repart **toujours en rail** ; *(V020 : les trois états sont remplacés par « afficher / masquer » + « rail / libellés » ; voir « Règles du jalon 11 »)*.

### Règles du jalon 11 (V020)

- **Couleur du niveau 0** : `--brand` / `--level-racine` = `#043BB2` (logement : cadre du plan, titre, fil d'Ariane, ligne « Logement » de l'arborescence, pastille du rail) et **bandeau d'en-tête de l'application** ; `theme-color` et `theme_color` du manifeste alignés. Le texte courant garde sa couleur sombre.
- **En-tête de l'application** : Retour (`#app-back`, flèche), nom, puis à droite loupe (`#search-toggle`), engrenage « Réglages » (`#app-settings`, **sans libellé visible**, nom accessible conservé, pastilles d'état sur le pictogramme) et version. Boutons ronds de 44 px, clairs sur fond bleu ; « enfoncé » = contour blanc. Le bouton « Arborescence » à trois états **n'existe plus**.
- **Recherche** : le champ est **masqué par défaut** ; la loupe l'affiche (écran déplié : sur la ligne de l'en-tête ; écran replié : bandeau sous l'en-tête) et lui donne le focus. Une route `#/s/…` l'affiche toujours. Refermer le champ pendant une recherche revient à l'écran précédent. Le bouton Retour est indépendant du champ.
- **Deux groupes de boutons** dans l'en-tête figé du détail, alignés à droite (groupes teintés) : **arborescence** = afficher / masquer le volet (`#tree-toggle`, pictogramme, `aria-pressed`) + ▲ ▼ ; **commandes** = « Actions » + Liste / Plan, Agrandir, Modifier le plan (+ « ? » en modification).
- **Arborescence — deux commandes distinctes, chacune à icône explicite** : *afficher / masquer* le volet (bouton de groupe, écran déplié et replié) ; *largeur* rail ↔ libellés (bouton du volet, pictogrammes « élargir » / « réduire » à la place des chevrons ; écran déplié seulement). Masquer puis afficher conserve la largeur choisie ; rien n'est mémorisé (rail à chaque démarrage). **Rail** : flèche « tout déplier / replier » devant la racine, comme dans l'arborescence large. **Écran replié** : le volet (toujours avec libellés, sans rail) **recouvre partiellement l'écran** (≤ 85 % de la largeur) sur un voile ; il se ferme par un appui sur le voile, Échap ou le choix d'un élément.
- **Cases libres** : **invisibles en consultation** (elles restent dans la grille ; elles apparaissent en pointillés en mode « Modifier le plan »). Un **appui long dans le plan** (sur une case libre ou n'importe où ailleurs qu'une case) **choisit la case libre la plus proche** de l'appui et ouvre son menu (créer un emplacement / une pièce à cette place, objet, régler la grille).
- **Mode « Modifier le plan »** : le texte d'explication n'est plus affiché ; un bouton **« ? »** (`#plan-help`, dans le groupe des commandes, visible seulement en modification) l'affiche dans une pop-up.

### Règles du jalon 12 (V021)

- **Boutons de l'en-tête** (Retour, loupe, engrenage) : fond **transparent**, pictogramme et cercle (contour de 2 px) **blancs** sur le bandeau `#043BB2` ; survol = voile blanc léger. **Enfoncé** (loupe quand le champ est ouvert, engrenage quand les Réglages sont ouverts : `aria-pressed`, `aria-expanded`, `aria-current="page"`) : couleurs **inversées** — disque blanc, pictogramme bleu.
- **Pictogramme « arborescence »** (`tree`) : le père en haut à gauche, les deux fils alignés verticalement dessous (à droite), reliés par un tracé en demi-opacité.
- **« Actions »** : bouton rond de 44 px (même style que les boutons d'affichage) à pictogramme `actions` (trois points verticaux) ; `id="manage-toggle"`, nom accessible « Actions » (texte masqué + `aria-label` + infobulle) ; enfoncé (couleur d'accent, classe `has-menu`) tant que son menu est ouvert.
- **Largeur du volet d'arborescence** (écran déplié) : `minmax(216px, 288px)` (10 % de moins qu'en V020) ; le rail (76 px) et le volet recouvrant de l'écran replié (≤ 320 px, 85 % de la largeur) sont inchangés.
- **Pictogrammes du volet** : `expand-h` (rail → large) et `collapse-h` (large → rail), qui alternent : écran avec séparation du volet, petites barres d'arborescence et chevron dans le sens du changement (vers la droite pour agrandir, vers la gauche pour réduire) ; le rail est évoqué par des barres plus courtes et une séparation plus à gauche.

### Règles du jalon 13 (V022)

- **Focus** : `-webkit-tap-highlight-color: transparent` sur boutons, liens et listes ; l'anneau de focus n'apparaît qu'au clavier (`:focus-visible`) ; le survol des boutons de l'en-tête n'existe qu'avec une souris (`@media (hover: hover)`), pour qu'il ne reste pas « collé » après un appui tactile.
- **Conteneur des boutons du détail** (écran déplié) : les groupes « arborescence » et « commandes » forment **un seul bloc** de même largeur, aux bords arrondis à l'extérieur seulement (12 px) et séparé par un **filet transparent de 2 px** (`row-gap` de `.detail-bar`). Écran replié : deux groupes distincts comme avant (ils ne sont pas voisins dans la grille).
- **Flèches de niveau** (▲ ▼) : boutons ronds de 44 px (`.detail-bar .button--icon`).
- **Volet d'arborescence** : le bouton réduire / élargir (`.tree-shrink`) occupe toute la hauteur de la ligne « Logement » (40 px au moins) et, dans le rail, toute la largeur du rail ; **le pictogramme** (38 px, détaillé) est bleu `--brand` (#043BB2) et remplit le bouton, qui lui-même n'est pas coloré *(V022a ; en V022 le bouton était plein et le pictogramme trop petit)*.
- **Menus** : chaque commande peut porter un pictogramme (`icon`) : Ouvrir (`open`), Ajouter une pièce / un emplacement (`add-place`), Ajouter un objet (`add-item`), Régler la grille (`grid`), Placer et dimensionner (`move-cell`), Modifier (`edit-text`), Déplacer (`move-to`), Dupliquer (`duplicate`), Supprimer (`delete`, corbeille, rouge « danger » comme le texte). Pictogrammes dessinés en `currentColor` (les couleurs fixes des modèles ont été remplacées).
- **Icône « Actions »** : carré arrondi contenant un éclair plein (`actions`).
- **Marge sous le contenu** : `--bottom-extra` (16 px, `base.css`) ajouté au remplissage bas des volets, et `BOTTOM_EXTRA` (16, `views/furniture.js`) à la réserve de hauteur du plan ajusté. À régler si la barre des tâches masque encore le bas.

### Règles du jalon 14 (V023)

- **Pieds** : le champ `geometry.feet` d'un meuble (ou d'un niveau plus bas dessiné comme un meuble) passe de booléen à `'petits'`, `'grands'` ou `'tres-grands'` (absent / `false` = sans). L'ancienne valeur `true` (« Avec ») est **lue comme `'petits'`** (`feetOf()` dans `features/furniture.js`) et réécrite telle quelle au prochain enregistrement des réglages ; `schemaVersion` inchangé. `get(id).feet` renvoie `false`, `'petits'`, `'grands'` ou `'tres-grands'` ; un plan (logement, pièce) n'a jamais de pieds.
- **Réglage** : la boîte « Grille de … » propose « Pieds : Sans / Petits / Grands / Très grands » (valeurs `0` / `1` / `2` / `3`) avec une indication sur les grands pieds.
- **Petits pieds** : inchangés (deux petits pieds de 16 × 24 px sous le cadre ; la bande « Dessous » se place sous eux).
- **Grands pieds** : zone `.furn-legs` sous le cadre = deux pieds `.furn-foot--tall` (20 px de large, aux deux extrémités) avec, **entre eux**, la bande « Dessous » (`.furn-legs-mid`). Leur hauteur est calculée **sur la hauteur totale, pieds compris** : « Grands » = moitié de la hauteur totale, donc **pieds = hauteur du cadre** (× 1) ; « Très grands » = **75 %** de la hauteur totale, donc **3 × la hauteur du cadre** (`min-height` posée par `fitLegs()`, facteur lu dans `data-feet` dans `views/furniture.js`, recalculée à l'affichage, au redimensionnement — `ResizeObserver` sur le cadre et `refitAll()` — et à chaque redessin) ; elle grandit si la bande « Dessous » est plus haute. Création d'emplacements et d'objets toujours possible : cases libres de la bande (appui long, y compris dans le vide entre les pieds : case libre la plus proche), cases libres du plateau, menu « Actions ». Les emplacements placés dans la bande (`zone: 'bottom'`) s'y dessinent, appui long et cases libres compris. `fit()` (plans) n'est pas concerné : seuls les meubles ont des pieds.
- **Meubles entièrement visibles (V023b)** : un meuble dont les proportions ne sont **pas « Haut »** (Carré, Large, Très large) tient **entièrement dans l'écran**, bandes et pieds compris (`fitFurn()` dans `views/furniture.js`, appelée avec `fit()` / `fitLegs()` à l'affichage, au redimensionnement et quand l'en-tête figé change de hauteur). Le corps est **aplati** si besoin : jamais sous 64 px par ligne (`ROW_MIN`), sauf avec de **grands pieds** (tables) où il peut descendre à **40 px par ligne** (`FLAT_ROW`) ; sous 60 px par ligne la classe `.furn-flat` met le nom et le nombre d'objets sur une seule ligne. Les proportions des pieds sont conservées (× 1 ou × 3 du corps aplati). Si même le minimum ne tient pas (beaucoup de lignes, petit écran), la page défile comme avant. « Haut » est inchangé (hauteur = largeur / 0,7, défilement possible). Repère de test : `data-furn-fit` sur le cadre.

### 5.1 Diagnostic de démarrage

Un petit script **en ligne** dans `index.html` (donc indépendant des fichiers `.js`) affiche à l'écran, dans un bandeau rouge, tout fichier introuvable et toute erreur JavaScript. Au démarrage, `main.js` vérifie en plus que chaque module attendu est présent et nomme le fichier manquant (tableau `REQUIRED`). Quand un fichier est ajouté à l'application, il faut l'ajouter à ce tableau (c'est fait pour `icons.js`, `longpress.js`, `locations.js`, `form.js`, `dialog.js`, `location-actions.js`, `items.js`, `item-actions.js`, `item.js`, `search.js` (fonction et vue), `searchbar.js`, `backup.js`, `settings.js`, `pwa.js`, `detailbar.js`, `contextmenu.js`, `bubble.js`, `treerail.js` et `furniture.js` (fonction et vue)).

## 6. PWA et service worker (règles strictes, mises en œuvre en V008)

Le service worker est une source classique de bugs (ancienne version qui reste en cache). Règles :

- **Cache versionné** : nom du cache = `rangement-Vxxx`. La version est la même que celle de l'appli.
- **Pré-cache explicite** : la liste des fichiers mis en cache est écrite en dur dans `sw.js` et mise à jour à chaque livraison.
- **Nettoyage à l'activation** : tous les caches dont le nom ≠ cache courant sont supprimés.
- **Mise à jour contrôlée** : une nouvelle version s'installe en arrière-plan mais **n'est activée qu'avec l'accord de l'utilisateur** (bouton « Mettre à jour » affiché par `pwa.js`) ; pas de `skipWaiting` automatique (il n'est déclenché que par un message de la page après clic sur « Mettre à jour »).
- **Stratégie** : cache d'abord pour les fichiers de l'appli ; **aucune interception** des requêtes vers d'autres domaines. Les données utilisateur (`localStorage`) ne passent jamais par le service worker.
- **Ne se charge pas en `file://`** : le service worker nécessite `https://` (GitHub Pages) ou `localhost`. Dans l'aperçu QEdit, `pwa.js` détecte l'absence de support et se désactive sans erreur.
- **Visibilité** : la version du cache actif et un bouton « Vider le cache de l'application » sont dans `settings.js`.

## 7. Conventions

- **Versionnage** : numéro `Vxxx` incrémenté à chaque génération de fichiers (suffixe lettre pour modifs mineures). Affiché dans l'en-tête de l'appli (valeur lue dans `js/config.js`) et en tête des fichiers `.md`. La version doit aussi être répercutée dans `sw.js` (nom du cache).
- **En-tête de fichier** : commentaire avec horodatage (heure de Paris) + résumé court des modifications.
- **JS** : scripts classiques en IIFE, un seul espace de noms `window.Rangement`.
- **CSS** : variables CSS dans `base.css`, classes préfixées par composant, pas de style en ligne.
- **Langue** : interface et commentaires en français ; identifiants de code en anglais.
- **Livraison** : fichiers complets uniquement, testés sous Chromium (Playwright) avant livraison. Les tests (`tests/`) vérifient aussi le chargement en `file://` (cas de l'aperçu QEdit). La version attendue par les tests est lue dans `js/config.js`.
- **Tests compatibles Windows** *(V018a)* : l'utilisateur lance aussi les tests sur un PC Windows. Un test ne crée jamais sur le disque un fichier dont le nom contient `< > : " | ? *` (pour un nom hostile, passer le fichier en mémoire : `set_input_files(..., files=[{"name", "mimeType", "buffer"}])`). Les libellés de test peuvent contenir des caractères hors cp1252 (`≥`, `ℹ️`…) : lancer avec `PYTHONUTF8=1` (ou `setx PYTHONUTF8 1` une fois pour toutes) ; `test_jalon5.py` force déjà la sortie en UTF-8. Le serveur HTTP des tests (`QuietServer`, dans chaque `test_jalon*.py`) ignore les connexions que le navigateur coupe en cours d'envoi (`WinError 10053` sous Windows) : leur trace n'est plus affichée.

## 8. Points d'attention techniques

- **Persistance** : `localStorage` (limite d'environ 5 Mo par origine, largement suffisant sans photos). Si les photos sont ajoutées plus tard, il faudra passer à IndexedDB.
- **Données non partagées entre appareils** : chaque appareil a sa propre base. L'export/import JSON est le moyen de sauvegarder et de transférer.
- **Données liées à l'origine** : le `localStorage` dépend de l'adresse d'hébergement. Changer d'URL (ex. nouveau nom de dépôt) = base vide ; d'où l'importance de l'export.
- **Aperçu QEdit vs GitHub Pages** : les deux n'ont pas la même origine, donc pas les mêmes données.
- **Écran pliable** : détection par largeur (media queries), pas par modèle d'appareil.

- **Premier chargement** : le mode hors ligne n'est actif qu'après le premier chargement réussi en https. **Mise à jour déployée sur GitHub Pages** : elle peut mettre 1 à 2 minutes à être servie ; utiliser « Rechercher une mise à jour » dans Réglages.

## 9. Historique

| Version | Date (Paris) | Changement |
|---|---|---|
| V001 | 22/10/2026 16:10 | Création du document |
| V002 | 22/10/2026 16:46 | Scripts classiques + espace de noms ; PWA et règles du service worker ; photos exclues ; exemples réels |
| V003 | 22/10/2026 21:39 | Jalon 1 : arborescence réelle, ordre de chargement effectif, API du store, tests |
| V003a | 23/10/2026 00:27 | Diagnostic de démarrage (fichiers manquants, erreurs JS affichés à l'écran) |
| V004 | 23/10/2026 11:37 | Jalon 2 : gestion des emplacements (créer, modifier, déplacer, supprimer), dialogues, règles de gestion |
| V005 | 23/10/2026 23:50 | Jalon 3 : gestion des objets (créer, modifier, déplacer, supprimer), fiche d'un objet, route `#/o/<id>`, règles de gestion |
| V006 | 24/10/2026 13:10 | Jalon 4 : recherche (champ permanent, route `#/s/<texte>`, `search.js`) ; objets : noms uniques par emplacement, quantité entière, quantité 0 grisée |
| V007 | 24/10/2026 22:30 | Jalon 5 : sauvegarde (export / import JSON, copie de sécurité annulable, suivi de la dernière sauvegarde), écran Réglages (`#/r`), lien « Réglages » dans l'en-tête |
| V008 | 25/10/2026 00:52 | Jalon 6 : PWA hors ligne (`manifest.webmanifest`, `sw.js`, `js/pwa.js`, icônes), section « Application hors ligne » dans Réglages, pastille de mise à jour |
| V009 | 25/10/2026 16:10 | Jalon 6 bis : arborescence repliable et rail, en-têtes figés, duplication, bouton Retour, flèches de niveau, Réglages repliables, saisie interdite, pastille de sauvegarde, code couleur, loupe |
| V010 | 26/10/2026 15:33 | Jalon 7 : vue graphique des meubles (rectangle, pieds, sous-emplacements, détail des niveaux), disposition automatique ajustable, nombre d'objets dans l'arborescence |
| V011 | 30/10/2026 00:22 | Jalon 7 : grille de placement des meubles (cases, tailles, déplacements, bandes dessus / dessous), correction du débordement des cases et libellés |
| V012 | 31/10/2026 14:31 | Jalon 7 : échange de deux emplacements, pavés de flèches fixés en bas de l'écran, défilement conservé |
| V013 | 01/11/2026 12:00 | Jalon 8 : plan du logement (pièces en tuiles sur la grille, commutateur Liste / Plan, `plan` dans les données et la sauvegarde) |
| V014 | 02/11/2026 22:47 | Jalon 9 étape 1 : plan ajusté à l'écran (largeur et hauteur), taille réelle, tuiles compactes, plan d'une pièce |
| V015 | 05/11/2026 02:30 | Jalon 9 étape 2 : menu contextuel sur les cases (« Ouvrir » en tête), bouton « + » flottant, réglages de grille en boîte de dialogue, pavé de flèches avec « Grille… » et « Terminer » |
| V015a | 05/11/2026 | Correctif : le niveau inférieur ouvert dans un plan (icône de niveau) est oublié à chaque changement d'écran |
| V016 | 06/11/2026 12:00 | Jalon 9 étape 3 : ℹ️ et info-bulle, menu « Actions » déroulant, libellé de catégorie (chevron si tronqué) et Liste / Plan dans l'en-tête figé, texte de rappel du plan supprimé |
| V017 | 08/11/2026 01:30 | Préalable au 9.4 : navigation unique (le bandeau de niveau ouvre l'emplacement comme « Ouvrir »), bandeau masqué sur les cases étroites, Vue graphique à tous les niveaux ayant des sous-emplacements, texte de rappel du plan et « Remonter… » supprimés |
| V018 | 10/11/2026 21:05 | Jalon 9 étape 4 : plan en vue d'accueil (vue graphique par défaut), boutons flottants Liste / Plan (libellé = action) et Agrandir / Ajuster (icône SVG), arborescence à trois états (large, rail par défaut, masquée) |
| V018a | 12/11/2026 21:50 | Correctif des tests sous Windows (`test_jalon5.py` : fichier d'import au nom hostile passé en mémoire, sortie UTF-8) ; aucun changement de code de l'application |
| V018b | 13/11/2026 02:25 | Les 14 tests : le serveur de test ignore les connexions coupées par le navigateur (plus de traces `WinError 10053` sous Windows) ; aucun changement de code de l'application |
| V019 | 17/11/2026 07:12 | Jalon 10 : V018 validée ; pictogrammes SVG (`icons.js`), appui simple = ouvrir / appui long = menu (`longpress.js`), cases libres avec menu, mode « Modifier le plan », boutons d'affichage alignés à droite dans l'en-tête, bouton « + » supprimé, en-tête + recherche sur une ligne, rail au démarrage |
| V020 | 20/11/2026 22:57 | Jalon 11 : V019 validée ; couleur #043BB2, en-tête en pictogrammes (Retour, loupe, engrenage), recherche masquée, groupes de boutons (arborescence / commandes), aide « ? », cases libres invisibles (appui long = la plus proche), volet d'arborescence (afficher/masquer, largeur, rail avec flèche, volet recouvrant sur écran replié) |
| V021 | 24/11/2026 01:46 | Jalon 12 : V020 validée ; boutons de l'en-tête transparents / inversés, pictogramme arborescence redessiné, « Actions » en pictogramme, volet d'arborescence 10 % plus étroit, pictogrammes élargir / réduire |
| V022 | 25/11/2026 22:35 | Jalon 13 : V021 validée ; focus sans carré, conteneur unique des boutons du détail, flèches circulaires, bouton du volet bleu et haut, icône « Actions », pictogrammes des menus, marge sous le plan |
| V022a | 26/11/2026 02:45 | Correctif : pictogramme du volet d'arborescence bleu #043BB2 et agrandi (le bouton n'est plus coloré) |
| V023 | 27/11/2026 00:35 | Jalon 14 : V022 / V022a validées ; pieds des meubles « Sans / Petits / Grands » (grands = moitié de la hauteur, bande « Dessous » entre les pieds), ancienne valeur « avec » lue comme « petits » |
| V023a | 27/11/2026 00:50 | Correctif jalon 14 : grands pieds = hauteur du cadre (moitié de la hauteur totale, pieds compris) ; nouveau choix « Très grands » (75 %) |
| V023b | 27/11/2026 01:20 | Correctif jalon 14 : les meubles dont les proportions ne sont pas « Haut » tiennent entièrement à l'écran (corps aplati si besoin, jusqu'à 40 px par ligne avec de grands pieds) |
