<!--
  ARCHITECTURE.md — Application « Rangement »
  Version : V004
  Horodatage : 2026-10-23 11:37 (heure de Paris)
  Résumé : jalon 2 livré — gestion des emplacements : nouveaux fichiers (locations, form, dialog, location-actions), API, tests.
-->

# ARCHITECTURE — Rangement `V004`

> Dernière mise à jour : 23/10/2026 11:37 (Paris) — **V004**
> Statut : **jalon 2 livré** (création, modification, déplacement, suppression d'emplacements). Les fichiers marqués *(à venir)* ne sont pas encore créés.

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
├── manifest.webmanifest       Manifeste PWA (nom, icônes, couleurs, affichage) (à venir, jalon 6)
├── sw.js                      Service worker (cache hors ligne, versionné) (à venir, jalon 6)
├── icons/                     Icônes PWA (192, 512, maskable) (à venir, jalon 6)
├── ARCHITECTURE.md            Ce fichier
├── roadmap-et-avancement.md   Avancement et prochaines étapes
├── ToDo_Utilisateur.md        Tâches à la charge de l'utilisateur
├── tests/
│   ├── test_jalon1.py         Tests Playwright/Chromium : squelette, stockage, mise en page, diagnostic
│   └── test_jalon2.py         Tests Playwright/Chromium : gestion des emplacements
├── css/
│   ├── base.css               Variables (couleurs, espacements), reset, typographie
│   ├── layout.css             Mise en page : 1 volet / 2 volets, en-tête, navigation
│   └── components.css         Boutons, listes, formulaires, fil d'Ariane, dialogues
└── js/
    ├── config.js              Crée `window.Rangement` ; version, constantes, clé de stockage
    ├── core/
    │   ├── ids.js             Génération d'identifiants uniques
    │   ├── models.js          Définition/validation des objets (Emplacement, Objet)
    │   ├── storage.js         Lecture/écriture persistante (localStorage)
    │   ├── store.js           État en mémoire + notification des changements
    │   └── events.js          Mini bus d'événements
    ├── features/
    │   ├── demo.js            Données de démonstration (provisoire)
    │   ├── locations.js       Créer/modifier/déplacer/supprimer des emplacements, avec garde-fous
    │   ├── items.js           Créer/modifier/déplacer/supprimer des objets (à venir, jalon 3)
    │   ├── search.js          Recherche (nom, tags, chemin complet) (à venir, jalon 4)
    │   └── backup.js          Export / import JSON (à venir, jalon 5)
    ├── ui/
    │   ├── dom.js             Aides de construction du DOM (texte toujours échappé)
    │   ├── router.js          Navigation interne (hash `#/...`)
    │   ├── layout.js          Bascule 1 volet / 2 volets selon la largeur
    │   ├── components/
    │   │   ├── breadcrumb.js  Fil d'Ariane (Pièce › Meuble › Tiroir)
    │   │   ├── list.js        Liste générique
    │   │   ├── form.js        Champs de formulaire (texte, zone de texte, liste) et lecture des valeurs
    │   │   └── dialog.js      Dialogues : formulaire, confirmation, message
    │   └── views/
    │       ├── home.js        Accueil : recherche + accès rapide (à venir, jalon 4)
    │       ├── browse.js      Volet gauche : arborescence des emplacements
    │       ├── location-actions.js  Dialogues d'action : ajouter, modifier, déplacer, supprimer un emplacement
    │       ├── location.js    Volet principal : contenu d'un emplacement + barre d'actions
    │       ├── item.js        Fiche d'un objet (à venir, jalon 3)
    │       └── settings.js    Export/import, version, réglages PWA (à venir, jalons 5-6)
    ├── pwa.js                 Enregistrement du service worker + gestion des mises à jour (à venir, jalon 6)
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
  "appVersion": "V004",
  "locations": [],
  "items": []
}
```

`schemaVersion` permet de migrer les données si le modèle évolue.

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

Les dépendances vont toujours du bas vers le haut ; un fichier ne peut utiliser que ce qui est chargé avant lui. Ordre effectif en V004 :

1. `js/config.js` (crée `window.Rangement`, l'aide `Rangement.ns('a.b')` et `Rangement.config`)
2. `js/core/events.js`, `ids.js`, `models.js`, `storage.js`, `store.js`
3. `js/features/demo.js`, `locations.js` *(puis, aux jalons suivants : `items.js`, `search.js`, `backup.js`)*
4. `js/ui/dom.js`, `js/ui/router.js`, `js/ui/components/breadcrumb.js`, `list.js`, `form.js`, `dialog.js`
5. `js/ui/layout.js`
6. `js/ui/views/browse.js`, `location-actions.js`, `location.js` *(puis les autres vues)*
7. `js/pwa.js` *(jalon 6)*
8. `js/main.js` (dernier : démarre l'application)

Chaque fichier suit le même patron : une fonction auto-exécutée (IIFE) qui lit `window.Rangement`, ajoute son module et n'expose rien d'autre. Les appels entre modules d'un même niveau (ex. un composant qui appelle le routeur) se font à l'exécution, pas au chargement, ce qui évite les dépendances d'ordre fragiles.

### API principale (V004)

| Module | Rôle |
|---|---|
| `Rangement.store.init()` | Charge les données ; si elles sont illisibles ou incohérentes, les met de côté (`rangement.data.corrupt`) et démarre à vide |
| `Rangement.store.update(fn)` | Applique `fn` à une **copie** des données ; la copie n'est adoptée (et sauvegardée) que si elle reste cohérente. Renvoie `{ ok, errors }` |
| `Rangement.store.replaceAll(data)` | Remplace tout le contenu (import, démo) après validation |
| `Rangement.store.childLocations / itemsIn / pathOf / countIn` | Lecture : enfants, objets, chemin complet, comptage récursif |
| `Rangement.models.validateData(data)` | Contrôle : ids uniques, parents existants, pas de boucle, objets rattachés à un emplacement valide |
| `Rangement.models.normalizeText(texte)` | Minuscules sans accents ; sert aux comparaisons de noms (et à la recherche, jalon 4) |
| `Rangement.features.locations.create / update / move / remove` | Gestion des emplacements. Renvoient `{ ok }` ou `{ ok: false, error }` (message en français, affiché tel quel) |
| `Rangement.features.locations.parentChoices(id)` | Destinations possibles pour un déplacement (tout sauf l'emplacement et son contenu) |
| `Rangement.ui.components.dialog.form / confirm / alert` | Dialogues modaux (`<dialog>`), retour du focus à la fermeture |
| `Rangement.events` | `store:changed`, `store:error`, `route:changed`, `layout:changed` |

Si `localStorage` est indisponible, `storage.js` bascule en mémoire et l'appli affiche un avertissement.

### Règles de gestion des emplacements (V004)

- Le **nom est obligatoire** ; il est rogné des espaces.
- Deux emplacements **frères** (même parent) ne peuvent pas porter le même nom, sans tenir compte de la casse ni des accents. Deux « Commode » dans des pièces différentes sont autorisés.
- Un emplacement **ne peut pas être déplacé** dans lui-même ni dans son propre contenu.
- La **suppression est refusée** tant que l'emplacement contient des emplacements ou des objets ; sinon une confirmation est demandée.
- À la création : type **Pièce** par défaut à la racine, **Autre** par défaut ailleurs.

### 5.1 Diagnostic de démarrage

Un petit script **en ligne** dans `index.html` (donc indépendant des fichiers `.js`) affiche à l'écran, dans un bandeau rouge, tout fichier introuvable et toute erreur JavaScript. Au démarrage, `main.js` vérifie en plus que chaque module attendu est présent et nomme le fichier manquant (tableau `REQUIRED`). Quand un fichier est ajouté à l'application, il faut l'ajouter à ce tableau (c'est fait pour `locations.js`, `form.js`, `dialog.js` et `location-actions.js`).

## 6. PWA et service worker (règles strictes)

Le service worker est une source classique de bugs (ancienne version qui reste en cache). Règles :

- **Cache versionné** : nom du cache = `rangement-Vxxx`. La version est la même que celle de l'appli.
- **Pré-cache explicite** : la liste des fichiers mis en cache est écrite en dur dans `sw.js` et mise à jour à chaque livraison.
- **Nettoyage à l'activation** : tous les caches dont le nom ≠ cache courant sont supprimés.
- **Mise à jour contrôlée** : une nouvelle version s'installe en arrière-plan mais **n'est activée qu'avec l'accord de l'utilisateur** (bouton « Mettre à jour » affiché par `pwa.js`) ; pas de `skipWaiting` automatique.
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

## 9. Historique

| Version | Date (Paris) | Changement |
|---|---|---|
| V001 | 22/10/2026 16:10 | Création du document |
| V002 | 22/10/2026 16:46 | Scripts classiques + espace de noms ; PWA et règles du service worker ; photos exclues ; exemples réels |
| V003 | 22/10/2026 21:39 | Jalon 1 : arborescence réelle, ordre de chargement effectif, API du store, tests |
| V003a | 23/10/2026 00:27 | Diagnostic de démarrage (fichiers manquants, erreurs JS affichés à l'écran) |
| V004 | 23/10/2026 11:37 | Jalon 2 : gestion des emplacements (créer, modifier, déplacer, supprimer), dialogues, règles de gestion |
