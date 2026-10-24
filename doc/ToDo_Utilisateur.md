<!--
  ToDo_Utilisateur.md — Application « Rangement »
  Version : V007
  Horodatage : 2026-10-24 22:30 (heure de Paris)
  Résumé : jalon 5 livré — fichiers à enregistrer, première sauvegarde de vos données, tests de l'export / import ; base Contexte à mettre à jour.
-->

# ToDo Utilisateur — Rangement `V007`

> Dernière mise à jour : 24/10/2026 22:30 (Paris) — **V007**

## Fait

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
- [x] Valider le jalon 4 (recherche) : testé longuement sur GitHub, aucun bug ; améliorations ergonomiques notées pour le jalon 6 bis

## À faire maintenant

- [ ] **Enregistrer les fichiers de la V007** (archive `V007.zip` : le script `gestion_fichiers.py` range les fichiers dans leurs dossiers ; sinon, respecter les dossiers de `ARCHITECTURE.md` §2).
  - **Nouveaux** : `js/features/backup.js`, `js/ui/views/settings.js`, `tests/test_jalon5.py`.
  - **Remplacés** : `index.html`, `css/layout.css`, `css/components.css`, `js/config.js`, `js/main.js`, `js/core/storage.js`, `js/ui/router.js`, `js/ui/views/browse.js`, `js/ui/views/location.js` et les trois `.md`.
  - **Inchangés** (ne pas y toucher) : `css/base.css`, `js/core/` (sauf `storage.js`), `js/features/demo.js`, `locations.js`, `items.js`, `search.js`, `js/ui/dom.js`, `layout.js`, `js/ui/components/` (tous), `js/ui/views/location-actions.js`, `item-actions.js`, `item.js`, `search.js`, `searchbar.js`, `tests/test_jalon1.py` à `test_jalon4.py`.
- [ ] **Vérifier que la version affichée est `V007`** (si c'est encore `V006`, vider le cache ou attendre 1 à 2 minutes après l'envoi sur GitHub).
- [ ] **Mettre à jour la base `Contexte` du Projet** avec tous les fichiers V007 (les fichiers V006 remplacés ci-dessus ne doivent pas rester).
- [ ] **Faire tout de suite une première sauvegarde de vos vraies données** : toucher « Réglages » dans l'en-tête, puis « Exporter une sauvegarde », et ranger le fichier `rangement-….json` **hors de l'appareil** (ordinateur, cloud…).
- [ ] **Tester le Jalon 5** (GitHub, puis en local sur le téléphone, puis QEdit si souhaité) :
  1. Réglages : le nombre d'emplacements et d'objets correspond à vos données ; l'encadré indique la date de la dernière sauvegarde.
  2. Exporter : le fichier se télécharge (nom `rangement-AAAA-MM-JJ-HHMM.json`) et le message de confirmation s'affiche. Ajouter ensuite un objet puis revenir dans Réglages : l'encadré signale des modifications depuis la sauvegarde.
  3. **Aller-retour sur un autre contexte** (par exemple l'aperçu QEdit ou le test en local, dont la base est vide) : Réglages › Importer une sauvegarde › choisir le fichier exporté › vérifier que tout est retrouvé (arborescence, objets, quantités, mots-clés, recherche).
  4. **Sur une base déjà remplie, à ne faire qu'avec un export récent sous la main** : importer un fichier de sauvegarde (le résumé affiche fichier / données actuelles), confirmer, puis tester « Annuler la dernière importation » : les données d'avant doivent revenir.
  5. Essayer d'importer un fichier qui n'est pas une sauvegarde (une image, un `.txt`, un `.json` quelconque) : un message d'erreur clair doit s'afficher, sans rien modifier.
  6. Écran externe replié : lien « Réglages » facile à toucher, écran lisible, pas de défilement horizontal.
  7. Sur un logement vide (démarrage), le bouton « Importer une sauvegarde » mène aux Réglages.
- [ ] **Relire `ARCHITECTURE.md` V007**, surtout §5 (règles de la sauvegarde) et répondre à la **question ouverte** de `roadmap-et-avancement.md` (rappel de sauvegarde).
- [ ] **Si des objets enregistrés ont une quantité décimale** (créés pendant vos essais de la V005) : les corriger en nombre entier (le formulaire de modification vous le demandera) — sinon l'export les conservera tels quels.
- [ ] **Poursuivre la liste des évolutions ergonomiques** (Jalon 6 bis) au fil de vos tests : pas besoin de me la transmettre avant le lancement de cette étape.

## À faire avant la première livraison de code (Jalon 1)

- [ ] **Créer le dépôt GitHub public** (ex. `rangement`) et activer GitHub Pages sur la branche principale.
- [ ] **Ajouter dans ce dépôt** les trois fichiers `.md` (à la racine).
- [ ] **Retenir l'adresse du site** (`https://<ton-compte>.github.io/rangement/`) : les données du `localStorage` sont liées à cette adresse.

## À faire avant le Jalon 6 (PWA)

- [ ] **Joindre à la conversation du Jalon 6 les icônes PWA 192 et 512 px** déjà générées (elles ne peuvent pas être stockées dans les bases du Projet).
- [ ] **Vérifier sur le Z Fold** que l'installation « Ajouter à l'écran d'accueil » fonctionne une fois le site publié.

## À faire de façon récurrente

- [ ] À chaque livraison : enregistrer **tous** les fichiers fournis (remplacer les anciens) et vérifier que le numéro de version affiché dans l'appli correspond.
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
