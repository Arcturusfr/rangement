<!--
  roadmap-et-avancement.md — Application « Rangement »
  Version : V004
  Horodatage : 2026-10-23 11:37 (heure de Paris)
  Résumé : jalon 1 validé ; jalon 2 livré (gestion des emplacements) ; décisions et questions pour le jalon 3.
-->

# Roadmap et avancement — Rangement `V004`

> Dernière mise à jour : 23/10/2026 11:37 (Paris) — **V004**

## État actuel

- **Jalon 1 validé** par l'utilisateur (QEdit, Chrome ; l'écran vide initial venait de sous-dossiers manquants sur GitHub, d'où le diagnostic de démarrage ajouté en V003a).
- **Jalon 2 livré** (V004) : créer, modifier, déplacer et supprimer des emplacements, avec écran de démarrage, dialogues et garde-fous.
- Tests Playwright/Chromium : **135 tests, 0 échec** (62 pour les jalons 1 et diagnostic, 73 pour le jalon 2), en `http://` et en `file://`.
- En attente : **validation du jalon 2 par l'utilisateur** (QEdit, Chrome sur le Z Fold ; voir `ToDo_Utilisateur.md`).
- Prochaine étape : **Jalon 3** (gestion des objets).

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
| Noms identiques | *(hypothèse de Claude, à confirmer)* refusés entre emplacements **frères**, sans tenir compte de la casse ni des accents |

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

### Jalon 2 — Gestion des emplacements ✅ (livré en V004, validation utilisateur en attente)
- ✅ Créer / modifier (nom, type, note) / supprimer un emplacement
- ✅ Navigation dans l'arborescence avec fil d'Ariane
- ✅ Déplacer un emplacement (changer de parent), jamais dans lui-même ni dans son contenu
- ✅ Refuser la suppression d'un emplacement non vide (message explicite)
- ✅ Formulaires et dialogues (`form.js`, `dialog.js`) ; vrai écran de démarrage (le chargement des données de démonstration reste proposé quand l'application est vide)
- ⬜ Validation sur l'aperçu QEdit et sur le Z Fold (utilisateur)

### Jalon 3 — Gestion des objets
- ⬜ Créer / modifier / supprimer un objet
- ⬜ Déplacer un objet d'un emplacement à un autre
- ⬜ Quantité, tags, note

### Jalon 4 — Recherche
- ⬜ Recherche par nom / tag, résultat avec chemin complet (« Séjour › Meuble living › Tiroir bas gauche »)
- ⬜ Accès rapide depuis l'accueil

### Jalon 5 — Sauvegarde
- ⬜ Export / import JSON (avec contrôle de `schemaVersion`)
- ⬜ Écran de réglages

### Jalon 6 — PWA hors ligne
- ⬜ `manifest.webmanifest` et icônes
- ⬜ `sw.js` versionné, pré-cache explicite, nettoyage des anciens caches
- ⬜ `pwa.js` : mise à jour sur accord de l'utilisateur, bouton « Vider le cache »
- ⬜ Tests Playwright : installation, usage hors ligne, mise à jour de version

### Jalon 7 — Premières visualisations *(plus tard)*
- ⬜ Vue schématique d'une pièce en SVG, générée à partir des données
- ⬜ Mise en évidence d'un emplacement depuis une recherche

### Jalon 8 — Plan du logement *(plus tard)*
- ⬜ Plan SVG complet du logement
- ⬜ Outil simple de construction/modification du plan

### Idées reportées
- QR codes / étiquettes imprimables par boîte
- Photos (impliquerait IndexedDB)

## Questions ouvertes

1. **Noms identiques** : refuser deux emplacements de même nom au même endroit (hypothèse actuelle) te convient-il ? *(on peut aussi les autoriser)*
2. **Objets (jalon 3)** : à la saisie d'un objet, quantité à 1 par défaut et mots-clés saisis séparés par des virgules (ex. `optique, nature`) : OK ?

## Historique des versions

| Version | Date (Paris) | Changement |
|---|---|---|
| V001 | 22/10/2026 16:10 | Création du document |
| V002 | 22/10/2026 16:46 | Cadrage validé, décisions consignées, jalons PWA ajoutés |
| V003 | 22/10/2026 21:39 | Jalon 1 livré (code + 57 tests) ; décisions recherche/suppression ; jalon 2 en cours |
| V003a | 23/10/2026 00:27 | Écran vide signalé par l'utilisateur ; diagnostic de démarrage ajouté (62 tests) |
| V004 | 23/10/2026 11:37 | Jalon 1 validé ; jalon 2 livré (73 tests dédiés, 135 au total) |
