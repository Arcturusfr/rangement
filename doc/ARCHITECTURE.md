<!--
  ARCHITECTURE.md — Application « Rangement »
  Version : V009
  Horodatage : 2026-10-25 16:10 (heure de Paris)
  Résumé : jalon 6 bis livré — règles V009, nouveaux modules (detailbar, treerail), API.
-->

# ARCHITECTURE — Rangement `V009`

> Dernière mise à jour : 25/10/2026 16:10 (Paris) — **V009**
> Statut : **jalon 6 bis livré** (évolutions ergonomiques). Le jalon 6 (PWA hors ligne) est validé. Les fichiers marqués *(à venir)* ne sont pas encore créés.

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
│   └── test_jalon6bis.py      Tests Playwright/Chromium : évolutions ergonomiques (arborescence, rail, en-têtes figés, duplication, Retour, flèches, saisie interdite, pastille, couleurs)
├── css/
│   ├── base.css               Variables (couleurs, espacements), reset, typographie
│   ├── layout.css             Mise en page : 1 volet / 2 volets, en-tête, navigation
│   └── components.css         Boutons, listes, formulaires, fil d'Ariane, dialogues
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
    │   └── backup.js          Export / import JSON, copie de sécurité avant import (annulable), suivi de la dernière sauvegarde
    ├── ui/
    │   ├── dom.js             Aides de construction du DOM (texte toujours échappé)
    │   ├── router.js          Navigation interne (hash `#/...`)
    │   ├── layout.js          Bascule 1 volet / 2 volets selon la largeur
    │   ├── components/
    │   │   ├── breadcrumb.js  Fil d'Ariane (Pièce › Meuble › Tiroir)
    │   │   ├── list.js        Liste générique
    │   │   ├── form.js        Champs de formulaire (texte, zone de texte, liste), validation champ par champ et lecture des valeurs
    │   │   ├── dialog.js      Dialogues : formulaire (avec blocage de saisie interdite), confirmation, message
    │   │   └── detailbar.js   En-tête figé du volet de détail : fil d'Ariane, titre, flèches de niveau, bouton « Actions » (gestion repliable)
    │   └── views/
    │       ├── browse.js      Volet gauche : arborescence repliable, ligne « Logement » figée, bascule large / rail
    │       ├── treerail.js    Arborescence minimale (rail sans libellés) et infobulle Ok / Annuler
    │       ├── location-actions.js  Dialogues d'action : ajouter, modifier, déplacer, supprimer un emplacement
    │       ├── item-actions.js  Dialogues d'action : ajouter, modifier, déplacer, supprimer un objet
    │       ├── location.js    Volet principal : contenu d'un emplacement + barre d'actions ; affiche aussi la fiche d'un objet
    │       ├── item.js        Fiche d'un objet (emplacement, quantité, mots-clés, note, actions)
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
  "items": []
}
```

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
3. `js/features/demo.js`, `locations.js`, `items.js`, `search.js`, `backup.js`
4. `js/ui/dom.js`, `js/ui/router.js`, `js/ui/components/breadcrumb.js`, `list.js`, `form.js`, `dialog.js`, `detailbar.js`
5. `js/ui/layout.js`
6. `js/ui/views/treerail.js`, `browse.js`, `location-actions.js`, `item-actions.js`, `item.js`, `search.js`, `searchbar.js`, `settings.js`, `location.js`
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
| `Rangement.events` | `store:changed`, `store:error`, `route:changed`, `layout:changed`, `backup:changed`, `pwa:changed` |

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

### 5.1 Diagnostic de démarrage

Un petit script **en ligne** dans `index.html` (donc indépendant des fichiers `.js`) affiche à l'écran, dans un bandeau rouge, tout fichier introuvable et toute erreur JavaScript. Au démarrage, `main.js` vérifie en plus que chaque module attendu est présent et nomme le fichier manquant (tableau `REQUIRED`). Quand un fichier est ajouté à l'application, il faut l'ajouter à ce tableau (c'est fait pour `locations.js`, `form.js`, `dialog.js`, `location-actions.js`, `items.js`, `item-actions.js`, `item.js`, `search.js` (fonction et vue), `searchbar.js`, `backup.js`, `settings.js`, `pwa.js`, `detailbar.js` et `treerail.js`).

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
