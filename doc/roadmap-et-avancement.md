<!--
  roadmap-et-avancement.md — Application « Rangement »
  Version : V016
  Horodatage : 2026-11-06 12:00 (heure de Paris)
  Résumé : jalon 9 (interface centrée sur les plans), étapes 1 à 3 livrées (V016 : ℹ️, Actions déroulant, en-tête figé enrichi).
-->

# Roadmap et avancement — Rangement `V016`

> Dernière mise à jour : 06/11/2026 12:00 (Paris) — **V016**

## État actuel

- **Jalon 9.2 (V015) validé.** **Étape 9.3 livrée (V016)** : pictogramme **ℹ️** juste après le nom de l'élément affiché (aussi sur la fiche d'un objet) avec info-bulle (niveau, nombre d'emplacements et d'objets, note) ; le **texte de rappel sous « Liste / Plan » a disparu** ; menu **« Actions » déroulant** ; **libellé de catégorie** à la suite du nom (tronqué avec chevron rotatif si besoin) ; **Liste / Plan** dans l'en-tête figé, sous les flèches et « Actions », sans allonger le bandeau.
- Tests Playwright/Chromium : **1020 tests** (62 + 73 + 131 + 73 + 137 + 52 + 133 + 88 jalons 1 à 7, 77 jalon 8, 43 jalon 9.1, 88 jalon 9.2, **63 jalon 9.3**), 0 échec. Les tests des jalons 2, 3, 6 bis, 7, 8, 9 et 9.2 ont été adaptés (commandes passées par le menu « Actions », légende du plan remplacée par l'info-bulle ; 6 vérifications de la barre repliable et des boutons « Ajouter » colorés supprimées en 6 bis).
- En attente : **validation de la V016 par l'utilisateur** (voir `ToDo_Utilisateur.md`).

### (historique) État à la V015a

- **Jalons 8 et 9.1 (V014) validés.** **Étape 9.2 livrée (V015)** : un appui sur une case d'un plan ouvre un **menu contextuel** près d'elle (« Ouvrir » en tête, plus grand et en gras, puis Placer et dimensionner, Ajouter un objet / un emplacement, Modifier, Déplacer, Dupliquer, Supprimer) ; **bouton « + » flottant** (ajouter une pièce / un objet / un emplacement au niveau affiché, régler la grille) ; **pavés de flèches** intégrés au placement, avec « Grille… » et « Terminer » ; le menu « Ajuster » a disparu (réglages de grille en boîte de dialogue).
- Tests Playwright/Chromium : **958 tests** (62 + 73 + 131 + 73 + 137 + 52 + 139 + 87 jalons 1 à 7, 77 jalon 8, 43 jalon 9.1, **84 jalon 9.2**), 0 échec.
- En attente : **validation de la V015 par l'utilisateur** (voir `ToDo_Utilisateur.md`).

### (historique) État à la V014

- **Jalon 8 apprécié** (grille et rendu visuel : très satisfait). **Réorientation décidée** : faire des plans l'élément principal de l'interface (**jalon 9**). **Étape 1 livrée (V014)** : plan ajusté à l'écran (largeur, et hauteur autant que possible), bouton « Agrandir » (taille réelle), tuiles compactes, plan d'une pièce directement ajustable (commutateur Liste / Plan sur une pièce).
- Tests Playwright/Chromium : **875 tests** (62 + 73 + 131 + 73 + 137 + 52 + 139 + 87 jalons 1 à 7, **78 jalon 8, 43 jalon 9**), 0 échec.
- En attente : **validation de la V014 par l'utilisateur** (voir `ToDo_Utilisateur.md`).

### (historique) État à la V013

- **Jalon 7 validé** (V012 testée : fluide). **Jalon 8 livré** (V013) : **plan du logement** — à la racine, un commutateur « Liste / Plan » ; les pièces sont des tuiles collées sur la grille des meubles (déplacement, taille en cases, échange, cases libres, colonnes et lignes jusqu'à 20), nombre d'objets sur chaque pièce, icône pour voir les meubles d'une pièce.
- Tests Playwright/Chromium : **830 tests** (62 jalon 1, 73 jalon 2, 131 jalon 3, 73 jalon 4, 137 jalon 5, 52 jalon 6, 139 jalon 6 bis, 87 jalon 7, **76 jalon 8**), 0 échec.
- En attente : **validation de la V013 par l'utilisateur** (voir `ToDo_Utilisateur.md`).

### (historique) État à la V012

- **Jalon 6 bis validé** (V009). **Jalon 7** : V010 (vue graphique), V011 (grille de placement, bandes dessus / dessous) ; V011 testée sur Z Fold : fonctionne bien et fluide, trois améliorations demandées.
- **V012** : déplacer un emplacement sur une case occupée **échange** les deux emplacements ; la page **ne remonte plus** en haut à chaque action ; les commandes d'ajustement sont **deux pavés de quatre flèches** sans libellé (déplacer, taille), **fixés en bas de l'écran**.
- Tests Playwright/Chromium : **754 tests, 0 échec** (62 jalon 1, 73 jalon 2, 131 jalon 3, 73 jalon 4, 137 jalon 5, 52 jalon 6, 139 jalon 6 bis, 87 jalon 7).
- En attente : **validation de la V012 par l'utilisateur** (voir `ToDo_Utilisateur.md`).

### (historique) État à la V011

- Grille de placement : colonnes, lignes, bandes au-dessus et en dessous, places et tailles en cases, correction du débordement ; réglages de la V010 convertis (739 tests).

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
| Jalon 7 (V010 / V011) | **Validé** : vue graphique des meubles uniquement (pas de plan de pièce pour l'instant) ; géométrie dans `geometry` ; commutateur Liste / Vue graphique ; niveau rappelé à chaque affichage ; nombre d'objets sur les cases. **V011 (demandé par l'utilisateur)** : grille de cases remplie automatiquement, nombre de cases modifiable, emplacements déplaçables et redimensionnables en cases (flèches, pas de glisser-déposer), **deux bandes** au-dessus et en dessous du meuble. *(Hypothèses de Claude, à valider à l'usage :)* liste par défaut, choix mémorisé ; dessin en HTML/CSS ; places figées dès la première modification ; **V012 (demandé par l'utilisateur)** : échange de deux emplacements en cas de déplacement sur une case occupée, pavés de flèches (déplacer, taille) fixés en bas de l'écran ; *hypothèses de Claude :* l'échange est refusé si plusieurs emplacements sont sur le chemin ou si l'autre ne tient pas à la place libérée ; 6 colonnes, 8 lignes et 3 lignes par bande au maximum ; nombre d'objets de l'arborescence = total sous-niveaux compris, masqué si zéro. |
| Jalon 8 (V013) | **Validé** : pièces en **tuiles collées** (pas de murs, portes ni fenêtres pour l'instant), réutilisation de la grille des meubles, pièces = rectangles de cases (pas de formes en L), nom + nombre d'objets sur chaque case, grille jusqu'à 20 × 20, places automatiques puis figées, disposition des meubles dans une pièce = jalon 8 bis à part. *(Hypothèses de Claude, à valider à l'usage :)* liste par défaut, choix Liste / Plan mémorisé séparément de celui des meubles ; 2 / 3 / 4 colonnes automatiques selon le nombre de pièces ; plan stocké dans l'enveloppe (`plan`), facultatif ; cadre à défilement horizontal si beaucoup de colonnes ; l'icône d'une tuile ouvre les meubles de la pièce sur la même grille (première version du jalon 8 bis). |
| Jalon 9 (V014 →) | **Validé** : les plans deviennent l'élément principal ; tout tient sur l'écran déplié (plan **et** menus), le plan peut être agrandi ; navigation fluide et intuitive. Dimensions réelles de l'utilisateur : logement en **7 colonnes × 10 lignes**, plus grande pièce en 6 × 8 ; libellés absents ou tronqués sur les très petites pièces : sans gêne. **Geste** : un appui sur un élément ouvre un **menu contextuel près de lui**, dont la première commande, plus grande et en gras, est **« Ouvrir »** (quasi un double appui) ; pas d'appui long. **Création au niveau du plan** (nouvelle pièce, etc.) : bouton **« + » flottant** (pas de menu contextuel possible hors d'un élément). **Flèches** déplacer / taille : intégrées au menu contextuel, toujours visibles pendant l'édition, masquables à la fin, sans trop cacher le plan. **Pictogrammes ℹ️** : ouvrent des infobulles pour alléger l'interface (contenu à définir à l'usage : mode d'emploi contextuel, précisions sur un élément). Le menu « Ajuster » disparaîtra de lui-même. Découpage validé : 9.1 plan ajusté à l'écran ; 9.2 menu contextuel (+ bouton « + », flèches intégrées) ; 9.3 infobulles ℹ️ ; 9.4 plan en vue d'accueil ; les tests de chaque étape affineront les suivantes. *(Hypothèses de Claude, à valider :)* 9.1 : cases jamais sous 28 px (le cadre défile alors), la hauteur ne les réduit pas sous 48 px (la page défile alors), « compactes » sous 60 px, 72 px minimum en taille réelle ; le choix Liste / Plan est commun au logement et aux pièces ; liste par défaut jusqu'à l'étape 9.4. |
| Jalon 9.3 (V016) | **Demandé / validé par l'utilisateur** : ℹ️ juste après le nom (y compris fiche d'objet) avec info-bulle reprenant niveau, nombre d'emplacements et d'objets ; menu « Actions » conservé mais déroulant ; libellé de catégorie dans l'en-tête figé à la suite du nom (tronqué + chevron rotatif → bulle) ; Liste / Plan sous les flèches et « Actions » sans augmenter la hauteur du bandeau. *(Hypothèses de Claude, à valider à l'usage :)* le texte de rappel du plan ne reste que dans un niveau inférieur dessiné ; la note d'un emplacement passe dans l'info-bulle ; libellé « Objet » sur une fiche ; boutons du commutateur de 32 px de haut (zone d'appui étendue) ; en-tête en deux colonnes (en écran replié : fil d'Ariane sur toute la largeur, titre un peu plus petit) ; les boutons « Ajouter… » du menu ne sont plus colorés. |
| Jalon 9.2 (V015) | *(Hypothèses de Claude, à valider à l'usage :)* commandes du menu dans l'ordre Ouvrir, Placer et dimensionner, Ajouter un objet ici, Ajouter un emplacement ici, Modifier, Déplacer, Dupliquer, Supprimer ; la case n'est plus un lien (tout passe par « Ouvrir ») ; **« Placer et dimensionner »** remplace « Ajuster » : il sélectionne la case et affiche les pavés de flèches, avec « Grille… » et « Terminer » ; le « + » est caché pendant le placement ; les réglages de grille (colonnes, lignes ; pour un meuble proportions, dessus, dessous, pieds) sont dans une boîte de dialogue ouverte par « + » › « Régler la grille… » ; le menu est aussi proposé dans la vue graphique d'un meuble et de ses niveaux ; le « + » agit sur le niveau affiché. |
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

### Jalon 8 — Plan du logement ✅ (livré en V013, validation utilisateur en attente)
- ✅ Commutateur Liste / Plan à la racine ; pièces en tuiles sur la grille (déplacer, taille, échange, cases libres, colonnes et lignes)
- ✅ Nombre d'objets sur chaque pièce, icône pour voir les meubles d'une pièce, `plan` conservé dans les données, l'export, l'import et l'annulation d'import
- ⬜ Validation sur GitHub Pages et sur le Z Fold (utilisateur)
- ⬜ *(plus tard, si utile)* portes et fenêtres ; formes de pièces non rectangulaires

### Jalon 9 — Interface centrée sur les plans 🟦 (étapes 1, 2 et 3 livrées, V014, V015 et V016)
- ✅ 9.1 Plan ajusté à l'écran (largeur et hauteur), bouton « Agrandir », tuiles compactes, plan d'une pièce (commutateur Liste / Plan sur une pièce)
- ✅ 9.2 Menu contextuel près de l'élément touché (« Ouvrir » en tête, commandes du menu « Actions » de l'élément, pavés de flèches intégrés et masquables) + bouton « + » flottant pour créer au niveau du plan (V015)
- ✅ 9.3 Pictogramme ℹ️ et info-bulle, menu « Actions » déroulant, libellé de catégorie et Liste / Plan dans l'en-tête figé (V016)
- ⬜ 9.4 Plan comme vue d'accueil ; place de la liste et de l'arborescence ; affichage des objets dans le plan
- ⬜ Validation sur GitHub Pages et sur le Z Fold (utilisateur)

### Jalon 8 bis — Disposition des meubles dans une pièce *(en grande partie couvert par le jalon 9)*
- ⬜ Vue d'une pièce avec ses meubles posés sur la grille (première version déjà accessible par l'icône d'une tuile du plan)
- ⬜ Mise en évidence d'un emplacement depuis une recherche

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
| V012 | 31/10/2026 14:31 | Jalon 7 : échange d'emplacements, pavés de flèches, défilement conservé (87 tests dédiés, 754 au total) |
| V013 | 01/11/2026 12:00 | Jalon 7 validé ; jalon 8 livré (plan du logement, 76 tests dédiés, 830 au total) |
| V014 | 02/11/2026 22:47 | Jalon 9 : réorientation vers les plans décidée ; étape 1 livrée (plan ajusté à l'écran, plan d'une pièce ; 43 tests dédiés, 875 au total) |
| V015 | 05/11/2026 02:30 | Jalons 8 et 9.1 validés ; étape 9.2 livrée (menu contextuel, bouton « + », grille en boîte de dialogue ; 84 tests dédiés, 958 au total) |
| V015a | 05/11/2026 | Correctif : niveau inférieur du plan oublié au changement d'écran (88 tests dédiés au 9.2, 962 au total) |
| V016 | 06/11/2026 12:00 | Jalon 9.2 validé ; étape 9.3 livrée (ℹ️, Actions déroulant, en-tête figé enrichi ; 63 tests dédiés, 1020 au total) |
