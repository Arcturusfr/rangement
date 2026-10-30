<!--
  roadmap-et-avancement.md — Application « Rangement »
  Version : V011
  Horodatage : 2026-10-30 00:22 (heure de Paris)
  Résumé : jalon 7 : grille de placement des meubles (V011).
-->

# Roadmap et avancement — Rangement `V011`

> Dernière mise à jour : 30/10/2026 00:22 (Paris) — **V011**

## État actuel

- **Jalon 6 bis validé** (V009). **Jalon 7** livré en V010, testé sur Z Fold et iPad : correct pour les meubles simples ; deux retours (débordement au-delà de 6 emplacements sur Z Fold ; meuble complexe impossible à reproduire).
- **V011** : la vue graphique d'un meuble repose sur une **grille** (colonnes, lignes, bandes au-dessus et en dessous du meuble) ; chaque sous-emplacement a une place et une taille en cases, déplaçables et redimensionnables ; les cases ne débordent plus du cadre et les libellés sont tronqués dans leur case ; les réglages de la V010 sont convertis.
- Tests Playwright/Chromium : **739 tests, 0 échec** (62 jalon 1, 73 jalon 2, 131 jalon 3, 73 jalon 4, 137 jalon 5, 52 jalon 6, 139 jalon 6 bis, 72 jalon 7).
- En attente : **validation de la V011 par l'utilisateur** (voir `ToDo_Utilisateur.md`), en particulier sur le « Meuble living ».

### (historique) État à la V010

- Jalon 7 livré : commutateur Liste / Vue graphique, meuble en rectangle avec pieds, sous-emplacements avec nombre d'objets et niveau, détail des niveaux inférieurs, nombre d'objets dans l'arborescence (placement automatique ; 722 tests).

### (historique) État à la V009

- Jalon 6 bis livré : arborescence repliable et rail, en-têtes figés, duplication, Retour, flèches de niveau, saisie interdite, pastille de sauvegarde, code couleur.

### (historique) État à la V008

- **Jalon 5 validé** par l'utilisateur : aucun bug de fonctionnement.
- **Jalon 6 livré** (V008) : **PWA hors ligne** — `manifest.webmanifest`, icônes (192/512, any et maskable), `sw.js` (pré-cache explicite versionné `rangement-V008`, cache d'abord, nettoyage des anciens caches, **mise à jour uniquement sur accord**), `js/pwa.js`, section « Application hors ligne » dans Réglages (mise à jour, recherche de mise à jour, vider le cache, installer), pastille ● sur « Réglages » quand une mise à jour attend.
- Tests Playwright/Chromium : **528 tests, 0 échec** (62 jalon 1 et diagnostic, 73 jalon 2, 131 jalon 3, 73 jalon 4, 137 jalon 5, 52 jalon 6), en `http://` et en `file://` pour les parcours principaux.
- En attente : **validation du jalon 6 par l'utilisateur** (GitHub Pages, installation sur le Z Fold, usage en mode avion ; voir `ToDo_Utilisateur.md`).
- Prochaine étape : **Jalon 6 bis** (évolutions ergonomiques) — la liste est à fournir par l'utilisateur.

## Décisions prises

| Sujet | Décision |
|---|---|
| Arborescence | Pièce › meuble › tiroir › boîte, profondeur libre (validée) |
| Photos | Pas pour l'instant ; stockage en `localStorage` |
| QR codes / étiquettes | Bonne idée, **reporté** |
| Objets | Suivi **individuel** de chaque objet |
| Hors ligne / installation | **PWA : oui**, avec gestion stricte du service worker |
| Multi-appareils | Sauvegarde **manuelle** par JSON, pas de synchronisation |
| JavaScript | **Pas de modules ES** ; `<script>` classiques dans le bon ordre, espace de noms `window.Rangement` |
| Recherche | Insensible à la casse et aux accents, **sans** tolérance aux fautes de frappe |
| Suppression d'un emplacement | **Refusée** tant qu'il contient des objets ou des sous-emplacements |
| Type d'emplacement | Choisi dans une liste (Pièce, Meuble, Tiroir, Étagère, Boîte, Autre) ; **Pièce** par défaut à la racine, **Autre** ailleurs |
| Noms identiques (emplacements) | **Validé** : refusés entre emplacements **frères** (même parent), sans tenir compte de la casse ni des accents ; deux « Commode » dans des pièces différentes restent possibles |
| Saisie d'un objet | **Validé** : quantité à **1** par défaut ; mots-clés saisis **séparés par des virgules** (ex. `optique, nature`) |
| Objets | Toujours rangés dans un emplacement (jamais directement à la racine) ; fiche individuelle par objet |
| Noms identiques (objets) | **Validé** : refusés dans un même emplacement (casse et accents ignorés) ; pour des objets identiques, utiliser la quantité ou un suffixe numérique (« sac à dos 1 », « sac à dos 2 ») ; autorisés dans des emplacements différents |
| Quantité | **Validé** : nombre **entier** (pas de décimales pour l'instant, à revoir à l'usage) ; **0 accepté** (objet épuisé mais référencé) ; objet de quantité 0 **grisé** (fond et texte) |
| Recherche (règles) | Champ permanent sous l'en-tête ; tous les mots requis ; champs : nom > mots-clés > note > chemin ; objets puis emplacements |
| Sauvegarde (V007) | Export en fichier JSON horodaté (`rangement-AAAA-MM-JJ-HHMM.json`) ; import **par remplacement** (pas de fusion) après analyse complète du fichier et confirmation ; copie de sécurité automatique avant chaque import, annulable depuis les Réglages ; fichier invalide = refus sans rien modifier. *(Proposé par Claude, à valider à l'usage.)* |
| Icônes PWA | Fournies par l'utilisateur et intégrées en V008 (`icons/`) ; les mêmes images servent aux versions `any` et `maskable` |
| Jalon 6 bis (V009) | Niveaux de couleur par profondeur (pièce / premier ordre / sous-emplacement / objet / épuisé). *(Hypothèses de Claude, à valider à l'usage :)* flèche ▼ = dernier enfant visité sinon premier ; duplication d'un emplacement : choix du contenu copié (seul par défaut) ; on arrive sur la copie ; l'état déplié de l'arborescence n'est pas mémorisé, la largeur (rail) l'est ; pastille orange = données jamais exportées ou modifiées depuis. |
| Jalon 7 (V010 / V011) | **Validé** : vue graphique des meubles uniquement (pas de plan de pièce pour l'instant) ; géométrie dans `geometry` ; commutateur Liste / Vue graphique ; niveau rappelé à chaque affichage ; nombre d'objets sur les cases. **V011 (demandé par l'utilisateur)** : grille de cases remplie automatiquement, nombre de cases modifiable, emplacements déplaçables et redimensionnables en cases (flèches, pas de glisser-déposer), **deux bandes** au-dessus et en dessous du meuble. *(Hypothèses de Claude, à valider à l'usage :)* liste par défaut, choix mémorisé ; dessin en HTML/CSS ; places figées dès la première modification ; refus (sans échange automatique) d'un déplacement sur une case occupée ; 6 colonnes, 8 lignes et 3 lignes par bande au maximum ; nombre d'objets de l'arborescence = total sous-niveaux compris, masqué si zéro. |
| PWA (V008) | Pré-cache explicite versionné ; **mise à jour sur accord** (jamais de `skipWaiting` automatique) ; bouton « Vider le cache » (données intactes) ; pas de service worker en `file://`. *(Règles de ARCHITECTURE.md §5, §6.)* |

## Jalons

Légende : ⬜ à faire · 🟦 en cours · ✅ terminé

### Jalon 0 — Cadrage ✅
- ✅ Avis sur le projet et choix techniques généraux
- ✅ Architecture et modèle de données validés
- ✅ Questions ouvertes tranchées

### Jalon 1 — Squelette et stockage ✅ (livré en V003, validé)
- ✅ `index.html`, CSS de base, numéro de version affiché dans l'en-tête
- ✅ `js/config.js` + modules `core/` : identifiants, modèles, stockage, store, événements
- ✅ Mise en page responsive (2 volets déplié / 1 volet replié)
- ✅ Jeu de données de démonstration (les 4 exemples réels) pour tester
- ✅ Tests Playwright de base (chargement, absence d'erreur console, persistance, données corrompues, stockage indisponible, protection contre l'injection HTML)
- ✅ Diagnostic de démarrage (V003a) : fichiers manquants et erreurs JS affichés à l'écran
- ✅ Validation sur l'aperçu QEdit et sur le Z Fold (utilisateur)

### Jalon 2 — Gestion des emplacements ✅ (livré en V004, validé)
- ✅ Créer / modifier (nom, type, note) / supprimer un emplacement
- ✅ Navigation dans l'arborescence avec fil d'Ariane
- ✅ Déplacer un emplacement (changer de parent), jamais dans lui-même ni dans son contenu
- ✅ Refuser la suppression d'un emplacement non vide (message explicite)
- ✅ Formulaires et dialogues (`form.js`, `dialog.js`) ; vrai écran de démarrage (le chargement des données de démonstration reste proposé quand l'application est vide)
- ✅ Validation sur l'aperçu QEdit et sur le Z Fold (utilisateur)

### Jalon 3 — Gestion des objets ✅ (livré en V005, validé ; règles précisées en V006)
- ✅ Créer / modifier / supprimer un objet (suppression avec confirmation)
- ✅ Déplacer un objet d'un emplacement à un autre (chemin complet affiché dans la liste)
- ✅ Quantité (1 par défaut), mots-clés séparés par des virgules, note
- ✅ Fiche d'un objet (`#/o/<id>`) : fil d'Ariane, emplacement, quantité, mots-clés, note, actions
- ✅ Les lignes d'objets de la liste d'un emplacement ouvrent la fiche
- ✅ Validation sur l'aperçu QEdit et sur le Z Fold (utilisateur)
- ✅ V006 : noms d'objets uniques par emplacement, quantité entière, objets de quantité 0 grisés

### Jalon 4 — Recherche ✅ (livré en V006, validé)
- ✅ Recherche par nom, mots-clés, note et chemin ; casse et accents ignorés, sans tolérance aux fautes ; tous les mots requis
- ✅ Résultats avec chemin complet (« Séjour › Meuble living › Tiroir bas gauche »), classés par pertinence ; objets puis emplacements
- ✅ Accès rapide : champ de recherche permanent sous l'en-tête (écrans déplié et replié), route `#/s/<texte>`, lien direct et bouton Retour gérés
- ✅ Validation sur les fichiers hébergés sur GitHub avec de nombreuses données (utilisateur) : aucun bug

### Jalon 5 — Sauvegarde ✅ (livré en V007, validé)
- ✅ Export JSON horodaté, import avec contrôles et confirmation, copie de sécurité annulable, écran Réglages, suivi de la dernière sauvegarde
- ✅ Validation par l'utilisateur : aucun bug de fonctionnement

### Jalon 6 — PWA hors ligne ✅ (livré en V008, validation utilisateur en attente)
- ✅ `manifest.webmanifest` et icônes (4 PNG)
- ✅ `sw.js` versionné, pré-cache explicite, nettoyage des anciens caches
- ✅ `pwa.js` : mise à jour sur accord de l'utilisateur, bouton « Vider le cache », installation
- ✅ Tests Playwright : pré-cache complet, usage hors ligne, mise à jour de version, vidage du cache, `file://`, écran replié
- ⬜ Validation sur GitHub Pages, installation sur le Z Fold, mode avion, mise à jour réelle V008 → suivante (utilisateur)

### Jalon 6 bis — Évolutions ergonomiques ✅ (livré en V009, validation utilisateur en attente)
Étape intermédiaire ajoutée à la demande de l'utilisateur, qui consigne la liste des évolutions au fur et à mesure de ses tests.
- ✅ Arborescence repliable, ligne « Logement » figée (+ variable de précision), rail réductible avec infobulle Ok / Annuler
- ✅ Détail : fil d'Ariane et titre figés, bouton replier la gestion
- ✅ Duplication d'un emplacement ou d'un objet (nom ou destination à changer)
- ✅ Loupe, bouton Retour, flèches de niveau, fermeture des Réglages par leur bouton
- ✅ Saisie interdite : message au changement de champ, blocage jusqu'à correction, sortie par Annuler / Retour
- ✅ Pastille de sauvegarde près de « Réglages »
- ✅ Code couleur par niveau, boutons « Ajouter… » colorés, gris pour quantité 0
- ⬜ Validation sur GitHub Pages et sur le Z Fold (utilisateur)

### Jalon 7 — Premières visualisations ✅ (livré en V010, validation utilisateur en attente)
- ✅ Vue graphique d'un meuble : rectangle, pieds, sous-emplacements, nombre d'objets, détail des niveaux inférieurs
- ✅ V011 : grille (colonnes, lignes), places et tailles en cases, bandes au-dessus et en dessous, correction du débordement
- ✅ Nombre d'objets dans l'arborescence
- ⬜ Validation sur GitHub Pages et sur le Z Fold (utilisateur)
- ⬜ *(plus tard)* Mise en évidence d'un emplacement depuis une recherche ; vue d'une pièce

### Jalon 8 — Plan du logement *(plus tard)*
- ⬜ Plan SVG complet du logement
- ⬜ Outil simple de construction/modification du plan

### Idées reportées
- QR codes / étiquettes imprimables par boîte
- Photos (impliquerait IndexedDB)

## Questions ouvertes

1. *(aucune pour l'instant — la pastille de rappel de sauvegarde est traitée en V009.)*

## Historique des versions

| Version | Date (Paris) | Changement |
|---|---|---|
| V001 | 22/10/2026 16:10 | Création du document |
| V002 | 22/10/2026 16:46 | Cadrage validé, décisions consignées, jalons PWA ajoutés |
| V003 | 22/10/2026 21:39 | Jalon 1 livré (code + 57 tests) ; décisions recherche/suppression ; jalon 2 en cours |
| V003a | 23/10/2026 00:27 | Écran vide signalé par l'utilisateur ; diagnostic de démarrage ajouté (62 tests) |
| V004 | 23/10/2026 11:37 | Jalon 1 validé ; jalon 2 livré (73 tests dédiés, 135 au total) |
| V005 | 23/10/2026 23:50 | Jalon 2 validé ; jalon 3 livré (116 tests dédiés, 251 au total) |
| V006 | 24/10/2026 13:10 | Jalon 3 validé, règles des objets précisées ; jalon 4 livré (recherche) ; jalon 6 bis ajouté (339 tests au total) |
| V007 | 24/10/2026 22:30 | Jalon 4 validé ; jalon 5 livré (sauvegarde : export / import JSON, Réglages, 137 tests dédiés, 476 au total) |
| V008 | 25/10/2026 00:52 | Jalon 5 validé ; jalon 6 livré (PWA hors ligne, 52 tests dédiés, 528 au total) |
| V009 | 25/10/2026 16:10 | Jalon 6 validé ; jalon 6 bis livré (139 tests dédiés, 667 au total) |
| V010 | 26/10/2026 15:33 | Jalon 6 bis validé ; jalon 7 livré (55 tests dédiés, 722 au total) |
| V011 | 30/10/2026 00:22 | Jalon 7 : grille de placement des meubles (72 tests dédiés, 739 au total) |
