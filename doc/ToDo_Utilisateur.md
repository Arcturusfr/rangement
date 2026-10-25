<!--
  ToDo_Utilisateur.md — Application « Rangement »
  Version : V009
  Horodatage : 2026-10-25 16:10 (heure de Paris)
  Résumé : jalon 6 bis livré — fichiers à enregistrer et tests à faire.
-->

# ToDo Utilisateur — Rangement `V009`

> Dernière mise à jour : 25/10/2026 16:10 (Paris) — **V009**

## Fait

- [x] Valider le jalon 6 (PWA hors ligne) et décider de la pastille de sauvegarde

- [x] Relire `ARCHITECTURE.md` et valider l'arborescence d'emplacements
- [x] Répondre aux questions ouvertes de la V001
- [x] Fournir des exemples réels de rangement
- [x] Préciser la consigne tronquée (déplacée dans la base « Instructions » du Projet)
- [x] Répondre aux 2 questions de la V002 (recherche sans accents/casse ; suppression refusée si non vide)
- [x] Valider le jalon 1 (aperçu QEdit, Chrome sur le Z Fold) et trouver la cause de l'écran vide (sous-dossiers manquants)
- [x] Valider le jalon 2 (gestion des emplacements) : aucun bug
- [x] Répondre aux 2 questions ouvertes de la V004 (noms identiques d'emplacements refusés entre frères ; objets : quantité à 1 par défaut, mots-clés séparés par des virgules)
- [x] Valider le jalon 3 (gestion des objets) : parfait
- [x] Répondre aux 2 questions ouvertes de la V005 (noms d'objets uniques par emplacement ; quantités entières, 0 accepté et grisé)
- [x] Générer les icônes PWA 192 et 512 px (à joindre à la conversation du Jalon 6)
- [x] Mettre à jour la base `Contexte` avec les fichiers V005
- [x] Enregistrer les fichiers de la V006 et mettre à jour la base `Contexte`
- [x] Valider le jalon 5 (sauvegarde) : aucun bug de fonctionnement
- [x] Joindre les icônes PWA à la conversation du Jalon 6
- [x] Valider le jalon 4 (recherche) : testé longuement sur GitHub, aucun bug ; améliorations ergonomiques notées pour le jalon 6 bis

## À faire maintenant

- [ ] **Enregistrer les fichiers de la V009** (archive `V009.zip` : `gestion_fichiers.py` les range ; liste complète dans `liste_fichiers_V009.txt`).
  - **Nouveaux** : `js/ui/components/detailbar.js`, `js/ui/views/treerail.js`, `tests/test_jalon6bis.py`.
  - **Remplacés** : `index.html`, `sw.js` (**à la racine**, pas dans `js/`), `css/base.css`, `css/layout.css`, `css/components.css`, `js/config.js`, `js/main.js`, `js/core/models.js`, `js/core/store.js`, `js/features/locations.js`, `js/features/items.js`, `js/features/backup.js`, `js/ui/router.js`, `js/ui/components/breadcrumb.js`, `list.js`, `form.js`, `dialog.js`, `js/ui/views/browse.js`, `location-actions.js`, `item-actions.js`, `item.js`, `location.js`, `search.js` (vue), `searchbar.js`, `tests/test_jalon2.py`, `test_jalon3.py`, `test_jalon6.py` et les trois `.md`.
  - **Inchangés** : tout le reste (dont `js/ui/layout.js`, `manifest.webmanifest`, `icons/`).
- [ ] **Vérifier que la version affichée est `V009`** (sinon, Réglages › « Rechercher une mise à jour » puis « Mettre à jour »).
- [ ] **Mettre à jour la base `Contexte`** avec les fichiers V009 (supprimer les versions remplacées).
- [ ] **Tester le Jalon 6 bis** : arborescence (replier / déplier, « Logement » figé, rail et infobulle Ok / Annuler sur le Z Fold déplié) ; détail (en-tête figé, bouton « Actions ») ; duplication ; Retour et flèches ▲ ▼ ; Réglages refermés par leur bouton ; quantité décimale (message, blocage, Annuler) ; pastille orange avant « Réglages » ; couleurs ; écran replié.
- [ ] **Répondre** : les choix de la roadmap (« Hypothèses de Claude ») vous conviennent-ils (flèche ▼, contenu copié, mémorisation) ? Autres évolutions ?

### (historique) À faire à la V008

- [ ] **Enregistrer les fichiers de la V008** (archive `V008.zip` : le script `gestion_fichiers.py` les range dans leurs dossiers ; la liste complète est dans `liste_fichiers_V008.txt`).
  - **Nouveaux** : `manifest.webmanifest`, `sw.js` (à la racine), `js/pwa.js`, `icons/` (4 PNG), `tests/test_jalon6.py`.
  - **Remplacés** : `index.html`, `css/components.css`, `js/config.js`, `js/main.js`, `js/ui/views/settings.js`, `js/ui/views/location.js` et les trois `.md`.
  - **Inchangés** : tout le reste.
- [ ] **Vérifier que la version affichée est `V008`** (si c'est encore `V007`, attendre 1 à 2 minutes après l'envoi sur GitHub, puis Réglages › « Rechercher une mise à jour »).
- [ ] **Mettre à jour la base `Contexte` du Projet** avec les fichiers V008 (les fichiers V007 remplacés ne doivent pas rester). Les icônes PNG n'ont pas besoin d'y être.
- [ ] **Tester le Jalon 6** (sur l'adresse GitHub Pages, en https) :
  1. Ouvrir le site, laisser charger, aller dans Réglages : la section « Application hors ligne » indique « Cache actif : rangement-V008 ».
  2. **Mode avion** : couper les données et le Wi-Fi, rouvrir l'application (navigateur ou icône installée) : elle doit s'ouvrir avec toutes vos données, et la recherche doit fonctionner.
  3. **Installer** sur le Z Fold : menu du navigateur › « Installer l'application » / « Ajouter à l'écran d'accueil » (ou bouton « Installer l'application » des Réglages s'il apparaît). Vérifier l'icône (les versions maskable sont découpées en rond/carré arrondi : dites-moi si le rendu vous gêne) et l'ouverture en plein écran, écran déplié et replié.
  4. **Mise à jour** : à la prochaine livraison, après envoi sur GitHub, ouvrir l'application : une pastille ● doit apparaître sur « Réglages » ; Réglages › « Mettre à jour » recharge l'application avec la nouvelle version, données intactes.
  5. « Vider le cache de l'application » : confirmation, rechargement, données intactes.
  6. Aperçu QEdit (`file://`) : Réglages indique que le mode hors ligne n'est pas disponible ; l'application fonctionne normalement.
- [ ] **Exporter une sauvegarde** de vos vraies données avant d'installer (précaution habituelle).
- [ ] **Poursuivre la liste des évolutions ergonomiques** (Jalon 6 bis) et la transmettre au lancement de cette étape ; répondre à la **question ouverte** (rappel de sauvegarde) de `roadmap-et-avancement.md`.

## À faire avant la première livraison de code (Jalon 1)

- [ ] **Créer le dépôt GitHub public** (ex. `rangement`) et activer GitHub Pages sur la branche principale.
- [ ] **Ajouter dans ce dépôt** les trois fichiers `.md` (à la racine).
- [ ] **Retenir l'adresse du site** (`https://<ton-compte>.github.io/rangement/`) : les données du `localStorage` sont liées à cette adresse.

## À faire de façon récurrente

- [ ] À chaque livraison : enregistrer **tous** les fichiers fournis (remplacer les anciens) et vérifier que le numéro de version affiché dans l'appli correspond (la version de `sw.js` suit celle de l'application).
- [ ] Après saisie de données importantes : **exporter une sauvegarde JSON** (à partir du Jalon 5) et la ranger hors de l'appareil.
- [ ] Après une mise à jour de l'appli installée : accepter la mise à jour proposée (bouton « Mettre à jour ») et vérifier la version affichée.

## Historique des versions

| Version | Date (Paris) | Changement |
|---|---|---|
| V001 | 22/10/2026 16:10 | Création du document |
| V002 | 22/10/2026 16:46 | Tâches V001 cochées, nouvelles tâches (GitHub, PWA), 2 questions |
| V003 | 22/10/2026 21:39 | Jalon 1 livré : tâches de test (QEdit, Z Fold) et d'installation des fichiers |
| V003a | 23/10/2026 00:27 | Procédure de diagnostic de l'écran vide ; 4 fichiers à remplacer |
| V004 | 23/10/2026 11:37 | Jalon 2 livré : fichiers à enregistrer, tests, base Contexte à mettre à jour |
| V005 | 23/10/2026 23:50 | Jalon 3 livré : fichiers à enregistrer, tests de la gestion des objets, base Contexte à mettre à jour |
| V006 | 24/10/2026 13:10 | Jalon 4 livré : fichiers à enregistrer, tests de la recherche et des règles des objets, base Contexte à mettre à jour |
| V007 | 24/10/2026 22:30 | Jalon 5 livré : fichiers à enregistrer, première sauvegarde des données, tests de l'export / import, base Contexte à mettre à jour |
| V008 | 25/10/2026 00:52 | Jalon 6 livré : fichiers à enregistrer, tests de la PWA (hors ligne, installation, mise à jour), base Contexte à mettre à jour |
| V009 | 25/10/2026 16:10 | Jalon 6 bis livré : fichiers à enregistrer, tests des évolutions ergonomiques, base Contexte à mettre à jour |
