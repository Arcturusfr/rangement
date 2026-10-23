<!--
  ToDo_Utilisateur.md — Application « Rangement »
  Version : V004
  Horodatage : 2026-10-23 11:37 (heure de Paris)
  Résumé : jalon 2 livré — fichiers à enregistrer, tests à faire, questions ; base Contexte à mettre à jour.
-->

# ToDo Utilisateur — Rangement `V004`

> Dernière mise à jour : 23/10/2026 11:37 (Paris) — **V004**

## Fait

- [x] Relire `ARCHITECTURE.md` et valider l'arborescence d'emplacements
- [x] Répondre aux questions ouvertes de la V001
- [x] Fournir des exemples réels de rangement
- [x] Préciser la consigne tronquée (déplacée dans la base « Instructions » du Projet)
- [x] Répondre aux 2 questions de la V002 (recherche sans accents/casse ; suppression refusée si non vide)
- [x] Valider le jalon 1 (aperçu QEdit, Chrome sur le Z Fold) et trouver la cause de l'écran vide (sous-dossiers manquants)

## À faire maintenant

- [ ] **Enregistrer les fichiers de la V004** en respectant les dossiers (voir `ARCHITECTURE.md` §2).
  - **Nouveaux** : `js/features/locations.js`, `js/ui/components/form.js`, `js/ui/components/dialog.js`, `js/ui/views/location-actions.js`, `tests/test_jalon2.py`.
  - **Remplacés** : `index.html`, `css/components.css`, `js/config.js`, `js/main.js`, `js/core/models.js`, `js/ui/views/location.js`, `tests/test_jalon1.py` et les trois `.md`.
  - **Inchangés** (ne pas y toucher) : `css/base.css`, `css/layout.css`, `js/core/events.js`, `ids.js`, `storage.js`, `store.js`, `js/features/demo.js`, `js/ui/dom.js`, `router.js`, `layout.js`, `js/ui/components/breadcrumb.js`, `list.js`, `js/ui/views/browse.js`.
- [ ] **Vérifier que la version affichée est `V004`** (si c'est encore `V003a`, vider le cache ou attendre 1 à 2 minutes après l'envoi sur GitHub).
- [ ] **Mettre à jour la base `Contexte` du Projet** avec tous les fichiers V004 (la base contenait encore des fichiers V003 : `index.html`, `config.js`, `main.js` et les `.md`).
- [ ] **Tester sur le Z Fold (Chrome) et dans l'aperçu QEdit** :
  1. Si l'appli contient des données de démonstration, ajouter un emplacement dans « Séjour » (bouton « Ajouter un emplacement ici ») ; le modifier ; le déplacer dans une autre pièce.
  2. Essayer de supprimer un emplacement qui contient un objet (message de refus attendu), puis de supprimer un emplacement vide (confirmation attendue).
  3. Recharger la page : les modifications doivent être conservées.
  4. Écran externe replié : vérifier que les boutons et les formulaires restent faciles à toucher.
- [ ] **Répondre aux 2 questions ouvertes** de `roadmap-et-avancement.md` (noms identiques ; saisie des objets).
- [ ] **Relire `ARCHITECTURE.md` V004**, surtout §5 (API et règles de gestion des emplacements) et §6 (règles du service worker).

## À faire avant la première livraison de code (Jalon 1)

- [ ] **Créer le dépôt GitHub public** (ex. `rangement`) et activer GitHub Pages sur la branche principale.
- [ ] **Ajouter dans ce dépôt** les trois fichiers `.md` (à la racine).
- [ ] **Retenir l'adresse du site** (`https://<ton-compte>.github.io/rangement/`) : les données du `localStorage` sont liées à cette adresse.

## À faire avant le Jalon 6 (PWA)

- [ ] **Fournir ou valider une icône** pour l'application (sinon je générerai une icône simple en SVG/PNG).
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
