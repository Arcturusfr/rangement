<!--
  ToDo_Utilisateur.md — Application « Rangement »
  Version : V006
  Horodatage : 2026-10-24 13:10 (heure de Paris)
  Résumé : jalon 4 livré — fichiers à enregistrer, tests de la recherche et des nouvelles règles des objets ; base Contexte à mettre à jour.
-->

# ToDo Utilisateur — Rangement `V006`

> Dernière mise à jour : 24/10/2026 13:10 (Paris) — **V006**

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

## À faire maintenant

- [ ] **Enregistrer les fichiers de la V006** en respectant les dossiers (voir `ARCHITECTURE.md` §2).
  - **Nouveaux** : `js/features/search.js`, `js/ui/views/search.js`, `js/ui/views/searchbar.js`, `tests/test_jalon4.py`.
  - **Remplacés** : `index.html`, `css/components.css`, `js/config.js`, `js/main.js`, `js/features/items.js`, `js/ui/router.js`, `js/ui/components/list.js`, `js/ui/views/browse.js`, `js/ui/views/item-actions.js`, `js/ui/views/item.js`, `js/ui/views/location.js`, `tests/test_jalon3.py` et les trois `.md`.
  - **Inchangés** (ne pas y toucher) : `css/base.css`, `css/layout.css`, `js/core/` (tous les fichiers), `js/features/demo.js`, `locations.js`, `js/ui/dom.js`, `layout.js`, `js/ui/components/breadcrumb.js`, `form.js`, `dialog.js`, `js/ui/views/location-actions.js`, `tests/test_jalon1.py`, `tests/test_jalon2.py`.
- [ ] **Vérifier que la version affichée est `V006`** (si c'est encore `V005`, vider le cache ou attendre 1 à 2 minutes après l'envoi sur GitHub).
- [ ] **Mettre à jour la base `Contexte` du Projet** avec tous les fichiers V006 (les fichiers V005 remplacés ci-dessus ne doivent pas rester).
- [ ] **Tester sur le Z Fold (Chrome) et dans l'aperçu QEdit** :
  1. Un champ de recherche est visible sous l'en-tête. Taper `piles` : « Piles neuves » apparaît avec son chemin complet ; taper `ELECTRICITE` (sans accent, en majuscules) : même résultat.
  2. Taper `jumelles optique` (deux mots) : un résultat ; `jumelles piles` : « Aucun résultat ».
  3. Taper `séjour` : les objets rangés dans le séjour, puis les emplacements correspondants.
  4. Toucher un résultat : la fiche (ou l'emplacement) s'ouvre ; le bouton Retour ramène aux résultats, champ rempli.
  5. Après une saisie, un seul appui sur Retour doit ramener à l'écran d'où vous êtes parti.
  6. Écran externe replié : champ facile à toucher, résultats lisibles, pas de défilement horizontal.
  7. **Règles des objets** : essayer d'ajouter un 2ᵉ objet de même nom dans un emplacement (refus attendu avec explication) ; saisir une quantité `2,5` (refus attendu) ; mettre une quantité à `0` : le cadre de l'objet doit apparaître grisé (liste, fiche et résultats de recherche).
- [ ] **Si des objets enregistrés ont une quantité décimale** (créés pendant vos essais de la V005) : les corriger en nombre entier (le formulaire de modification vous le demandera).
- [ ] **Relire `ARCHITECTURE.md` V006**, surtout §5 (règles de la recherche et règles de gestion des objets).
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
