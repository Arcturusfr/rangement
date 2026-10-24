<!--
  roadmap-et-avancement.md — Application « Rangement »
  Version : V007
  Horodatage : 2026-10-24 22:30 (heure de Paris)
  Résumé : jalon 4 validé ; jalon 5 (sauvegarde : export / import JSON, Réglages) livré ; une question ouverte.
-->

# Roadmap et avancement — Rangement `V007`

> Dernière mise à jour : 24/10/2026 22:30 (Paris) — **V007**

## État actuel

- **Jalon 4 validé** par l'utilisateur (testé longuement sur les fichiers hébergés sur GitHub, avec beaucoup de données) : aucun bug de fonctionnement ; des améliorations ergonomiques ont été notées pour le jalon 6 bis.
- **Jalon 5 livré** (V007) : écran **Réglages** (`#/r`, lien dans l'en-tête), **export** JSON horodaté, **import** avec contrôles et confirmation, **copie de sécurité** automatique annulable, suivi de la dernière sauvegarde.
- Tests Playwright/Chromium : **476 tests, 0 échec** (62 pour le jalon 1 et le diagnostic, 73 pour le jalon 2, 131 pour le jalon 3, 73 pour le jalon 4, 137 pour le jalon 5), en `http://` et en `file://` pour les parcours principaux.
- En attente : **validation du jalon 5 par l'utilisateur** (GitHub, local sur téléphone, QEdit ; voir `ToDo_Utilisateur.md`). Recommandation : **exporter une première sauvegarde de vos vraies données dès la V007 installée**.
- Prochaine étape : **Jalon 6** (PWA hors ligne) — icônes 192 et 512 px à joindre à la conversation.

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
| Icônes PWA | Déjà générées (192 et 512 px) ; à **joindre à la conversation** au lancement du Jalon 6 (impossible de les stocker dans les bases du Projet) |

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

### Jalon 5 — Sauvegarde ✅ (livré en V007, validation utilisateur en attente)
- ✅ Export JSON horodaté (`schemaVersion`, `appVersion`, `exportedAt`, emplacements, objets)
- ✅ Import avec contrôle complet (format, `schemaVersion`, cohérence) et confirmation ; refus explicite sans toucher aux données
- ✅ Copie de sécurité avant import, bouton « Annuler la dernière importation »
- ✅ Écran Réglages (`#/r`) : sauvegarde, restauration, à propos (version, format, stockage) ; suivi de la dernière sauvegarde et des modifications depuis
- ✅ Accès depuis l'en-tête et depuis l'écran de démarrage (import dans un logement vide)
- ⬜ Validation sur GitHub, en local sur téléphone et dans l'aperçu QEdit (utilisateur)

### Jalon 6 — PWA hors ligne
- ⬜ `manifest.webmanifest` et icônes
- ⬜ `sw.js` versionné, pré-cache explicite, nettoyage des anciens caches
- ⬜ `pwa.js` : mise à jour sur accord de l'utilisateur, bouton « Vider le cache »
- ⬜ Tests Playwright : installation, usage hors ligne, mise à jour de version

### Jalon 6 bis — Évolutions ergonomiques ⬜
Étape intermédiaire ajoutée à la demande de l'utilisateur, qui consigne la liste des évolutions au fur et à mesure de ses tests.
- ⬜ Liste des évolutions à fournir par l'utilisateur (non encore transmise)
- ⬜ Chiffrage et regroupement en une livraison (ou deux), avec tests Playwright

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

1. **Rappel de sauvegarde** : l'écran Réglages indique si des modifications ont eu lieu depuis la dernière sauvegarde, mais l'application ne le rappelle pas ailleurs. Souhaitez-vous une pastille discrète sur le lien « Réglages » de l'en-tête quand des modifications ne sont pas sauvegardées ? *(À traiter avec les évolutions du jalon 6 bis si oui.)*

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
