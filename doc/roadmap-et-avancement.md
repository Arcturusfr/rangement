<!--
  roadmap-et-avancement.md — Application « Rangement »
  Version : V023b
  Horodatage : 2026-11-27 01:20 (heure de Paris)
  Résumé : V023b : meubles non « Haut » entièrement visibles à l'écran ; jalon 14 (pieds) ; V024 = ouvertures dans les pièces ; catégories à repenser.
-->

# Roadmap et avancement — Rangement `V023b`

> Dernière mise à jour : 27/11/2026 01:20 (Paris) — **V023b**

## État actuel

- **V022 et V022a validées.** **Jalon 14 livré (V023, corrigé en V023a puis V023b)** : pieds des meubles. *V023b : V023a testée sans bug, mais les « Très grands » pieds étaient beaucoup trop grands à l'écran (corps du meuble trop haut). Tout meuble dont les proportions ne sont pas « Haut » doit désormais **tenir entièrement à l'écran** ; le corps est aplati si besoin (acceptable pour les tables).* *V023a : sur retour de l'utilisateur (emplacements bien visibles entre les pieds, écrans plié et déplié), les « Grands » passent à la moitié de la hauteur **totale** (pieds = hauteur du cadre) et un choix « Très grands » (75 % de la hauteur totale, pour les tables sans tiroirs) est ajouté.*
  - Liste **« Pieds : Sans / Petits / Grands / Très grands »** dans les réglages de la grille d'un meuble (et d'un niveau plus bas dessiné comme un meuble).
  - **Grands pieds** : pieds = hauteur du cadre (donc moitié de la hauteur totale, pieds compris) ; **très grands** : 75 % de la hauteur totale (3 × le cadre) ; la bande **« Dessous » se place entre les deux pieds** (les emplacements qu'on y met s'y dessinent). Si la bande est plus haute, les pieds s'allongent. On peut toujours ajouter emplacements (cases libres de la bande ou du plateau, menu « Actions ») et objets.
  - **Meubles entièrement visibles (V023b)** : proportions Carré / Large / Très large → le cadre (bandes et pieds compris) tient dans le volet de détail ; corps aplati jusqu'à 64 px par ligne, ou 40 px avec de grands pieds (lignes < 60 px : nom et nombre d'objets sur une ligne) ; « Haut » inchangé.
  - `feet` passe de booléen à `'petits'` / `'grands'` / `'tres-grands'` ; l'ancien « Avec » (`true`) est **lu comme « Petits »** (aucune migration de fichier nécessaire, sauvegardes anciennes comprises).
  - Tests Playwright/Chromium : **1397 tests** (jalons 1 à 13 : 1308 ; **89 pour la V023b, `test_jalon14.py`**), 0 échec. Seul `test_jalon9_2.py` a été adapté (`feet == 'petits'` au lieu de `True`) ; les tests des jalons 7, 8, 9, 9.3 bis et 10 relancés sans changement.
  - En attente : **validation de la V023 par l'utilisateur** (voir `ToDo_Utilisateur.md`) ; puis **V024** (ouvertures dans les pièces : portes, etc. — questions de cadrage à trancher dans la conversation de la V024). Les **catégories** (à la place des mots-clés) sont remises à plus tard : l'utilisateur s'oriente vers une solution différente et plus complète, sur laquelle il réfléchit encore.

### (historique) État à la V022a

- **V022 testée : « le reste est très bien »**, une seule remarque. **V022a (correctif)** : le **pictogramme** du bouton réduire / élargir le volet d'arborescence (dessin détaillé) est **bleu #043BB2** et **agrandi** (38 px) pour remplir le bouton ; le bouton lui-même n'est plus coloré (en V022, j'avais colorié le bouton et laissé le dessin petit : malentendu). Tests : **1308**, 0 échec (`test_jalon13.py` adapté : 45 tests). En attente : validation de la V022a (voir `ToDo_Utilisateur.md`) ; puis **V023** (pieds « Petits / Grands») et **V024** (catégories, questions en attente de réponse).

### (historique) État à la V022

- **V021 validée.** **Jalon 13 livré (V022)**, premier lot de la liste d'évolutions de l'utilisateur :
  - **Focus** : plus de carré de surbrillance au toucher sur les boutons (l'anneau reste pour le clavier) ; survol réservé à la souris.
  - **Boutons du détail** : un seul conteneur (écran déplié) avec un fin filet transparent entre les deux groupes ; flèches ▲ ▼ **circulaires**.
  - **Volet d'arborescence** : bouton réduire / élargir **bleu #043BB2**, aussi haut que « Logement » (dans le rail : toute la largeur).
  - **Icône « Actions »** : éclair plein dans un carré (SVG de l'utilisateur, corrigé).
  - **Pictogrammes des menus** (Actions, menu d'une case, case libre, objet) : Ouvrir, Ajouter pièce / emplacement, Ajouter objet, Régler la grille, Déplacer, Dupliquer, Supprimer (corbeille), plus les existants.
  - **Marge** de 16 px sous le contenu (barre des tâches du téléphone) : *à valider sur le Z Fold*.
  - Tests Playwright/Chromium : **1306 tests** (jalons 1 à 12 : 1263 ; **43 pour la V022, `test_jalon13.py`**), 0 échec ; aucun ancien test modifié. Sous forte charge (tests lancés en parallèle), un test long peut expirer ; relancé seul, il passe.
  - **Lotissement convenu pour la suite** : **V023** = pieds des meubles « Petits / Grands » (« Grands » = moitié de la hauteur, bande « Dessous » entre les pieds) ; **V024** (éventuellement V025) = « Catégories » à la place des mots-clés (liste déroulante modifiable, « Divers » par défaut) — questions à trancher avant : une ou plusieurs catégories par objet, où modifier la liste, sort des objets d'une catégorie supprimée, saisie libre.
  - En attente : **validation de la V022 par l'utilisateur** (voir `ToDo_Utilisateur.md`).

### (historique) État à la V021

- **V020 validée** (aucun bug ; absence du bouton d'arborescence sur les écrans Recherche et Réglages, et fermeture du volet d'arborescence sur écran replié par un appui à côté, validées). **Jalon 12 livré (V021)**, d'après les demandes de l'utilisateur sur les pictogrammes des boutons :
  - **Boutons de l'en-tête** (Retour, loupe, engrenage) : fond transparent, pictogramme et cercle blancs ; **couleurs inversées** quand la loupe ou l'engrenage est enfoncé.
  - **Pictogramme de l'arborescence** redessiné (père en haut à gauche, fils alignés verticalement dessous), d'après le dessin de l'utilisateur.
  - **Volet d'arborescence 10 % plus étroit** sur écran déplié (288 px au plus) ; écran replié inchangé.
  - **« Actions »** remplacé par un pictogramme (**proposition de Claude : trois points verticaux**, à valider) ; nom accessible conservé.
  - **Pictogrammes élargir / réduire le volet** : « agrandir » d'après le dessin de l'utilisateur ; « réduire » = **proposition de Claude** (séparation plus à gauche, barres plus courtes, chevron vers la gauche), à valider.
  - Tests Playwright/Chromium : **1263 tests** (jalons 1 à 11 : 1235 ; **28 pour la V021, `test_jalon12.py`**), 0 échec. Les tests existants n'ont pas eu besoin d'être modifiés. Remarque : lancés tous en parallèle, quelques tests longs (jalons 2, 3, 5) peuvent être interrompus par la charge ; relancés seuls, ils passent.
  - En attente : **validation de la V021 par l'utilisateur** (voir `ToDo_Utilisateur.md`).

### (historique) État à la V020

- **V019 validée** (« fonctionne correctement »). **Jalon 11 livré (V020, validé en V021)**, d'après les retours de l'utilisateur sur la V019 :
  - **Couleur** : niveau 0 (logement) et bandeau d'en-tête de l'application en `#043BB2` ; `theme-color` et manifeste alignés.
  - **En-tête de l'application** : Retour, loupe et engrenage en **pictogrammes** (plus de libellé « Réglages » ni « Arborescence »). **Recherche masquée** par défaut, ouverte par la loupe (à gauche de l'engrenage).
  - **Cases libres invisibles en consultation** : un appui long dans le plan choisit la case libre la plus proche et ouvre son menu ; elles apparaissent en pointillés en mode « Modifier le plan ».
  - **Mode « Modifier le plan »** : le texte d'explication est derrière un bouton **« ? »** (pop-up).
  - **Boutons regroupés** dans l'en-tête du détail : groupe **arborescence** (afficher / masquer, ▲ ▼) et groupe **commandes** (Actions, Liste / Plan, Agrandir, Modifier, « ? »).
  - **Arborescence (solution proposée par Claude, à valider)** : deux commandes distinctes à icônes explicites — afficher / masquer (bouton de groupe) et largeur rail ↔ libellés (pictogrammes « élargir » / « réduire » dans le volet, à la place des chevrons) ; le bouton à trois états disparaît. **Rail** : flèche de dépliement devant la racine. **Écran replié** : bouton d'affichage / masquage ; le volet (avec libellés, sans rail) recouvre partiellement l'écran.
  - Tests Playwright/Chromium : **1235 tests** (jalons 1 à 10 : 1192 ; **43 pour la V020, `test_jalon11.py`**), 0 échec. Tests des jalons 4, 6, 6 bis, 9.4 et 10 adaptés ; tous les tests ouvrent la recherche au chargement (le champ est masqué par défaut). Remarque : sous forte charge (nombreux tests en parallèle), un test peut expirer ; relancé seul, il passe.
  - En attente : **validation de la V020 par l'utilisateur** (voir `ToDo_Utilisateur.md`).

### (historique) État à la V019

- **V018 validée** (aucun bug de fonctionnement ; V018a et V018b étaient des correctifs de tests). **Jalon 10 livré (V019)**, d'après les retours de l'utilisateur sur la V018 :
  - **Boutons d'affichage** : les trois boutons (Liste / Plan, Agrandir, **Modifier le plan**) sont des **pictogrammes** alignés à droite dans l'en-tête figé, sous ▲ ▼ et « Actions » ; ils ne recouvrent plus le coin du plan. Pictogrammes fournis par l'utilisateur (`Pictogrammes.html`) : module `js/ui/icons.js` ; engrenage devant « Réglages », crayon dans les menus, pictogrammes au centre des pavés de flèches.
  - **Navigation dans le plan** : appui simple = ouvrir ; **appui long** = menu contextuel (« Ouvrir » écrit comme les autres commandes) ; clic droit / touche Menu = appui long. **Bouton « + » supprimé** : un appui long sur une **case libre** ouvre un menu (créer un emplacement **à cette place**, régler la grille) ; « Régler la grille… » aussi dans le menu « Actions » et le mode modification.
  - **Mode « Modifier le plan »** (bouton de l'en-tête, enfoncé quand actif) : sélection d'une case par appui simple, pavés de flèches, « Grille… », « Terminer ».
  - **Bandeaux** : en-tête et recherche sur **une seule ligne** (écran déplié) ; en-tête du détail resserré ; le plan 7 × 10 tient dans l'écran déplié avec des cases d'au moins 48 px, y compris arborescence masquée.
  - **Arborescence** : rail remis à chaque démarrage (états non mémorisés).
  - Au passage : le cadre d'un meuble ne dépasse plus la largeur de l'écran replié (cas d'un meuble à beaucoup de lignes).
  - Tests Playwright/Chromium : **1181 tests** (jalons 1 à 9.4 : 1121 ; **60 pour la V019, `test_jalon10.py`**), 0 échec. Les tests des jalons 6 bis, 7, 8, 9, 9.2, 9.3, 9.3 bis et 9.4 ont été adaptés (menu à l'appui long, pictogrammes, boutons de l'en-tête, rail au démarrage). Remarque : sous forte charge (nombreux tests lancés en parallèle), un test peut expirer ; relancé seul, il passe.
  - En attente : **validation de la V019 par l'utilisateur** (voir `ToDo_Utilisateur.md`). Reste à faire plus tard : « respiration » du contour des cases libres en placement ; pictogrammes dans d'autres boutons si souhaité.

### (historique) État à la V018b

- **V018b (correctif des tests, aucun changement de code de l'application)** : sur le PC Windows, les tests affichaient des traces `ConnectionAbortedError: [WinError 10053]` (le navigateur coupe une connexion pendant que le petit serveur de test envoie un fichier) alors que tous les tests passaient (`test_jalon6bis.py` : 133 tests, 0 échec). Le serveur de test de chacun des 14 `test_jalon*.py` ignore désormais ces coupures (classe `QuietServer`). Un timeout isolé a été observé hier sur le même PC (`test_jalon6bis.py`, sous-test `dwellingName`, V018) ; il ne s'est pas reproduit en V018a. À surveiller : s'il revient, regarder si le bandeau d'erreur de démarrage s'affiche. Tests : toujours **1103**, 0 échec sous Chromium/Linux (tous les jalons relancés en V018b). **V018 reste en attente de validation par l'utilisateur.**
- **V018a (correctif des tests, aucun changement de code de l'application)** : l'utilisateur a lancé les tests sur son PC Windows. `test_jalon5.py` plantait à la création d'un fichier temporaire nommé `<img …>.json` (caractères interdits sous Windows) : le fichier est désormais passé en mémoire à Playwright (même vérification de sécurité sur tous les systèmes) et la sortie console est forcée en UTF-8. Les caractères `≥`, `≤`, `ℹ️` des libellés de test ne s'affichent correctement dans une console Windows que si Python est lancé en UTF-8 (`PYTHONUTF8=1`) ; les autres jalons n'ont pas été modifiés. Tests : toujours **1103**, 0 échec sous Chromium/Linux (`test_jalon5.py` : 137, `test_jalon6.py` : 52 relancés en V018a). **V018 reste en attente de validation par l'utilisateur.**
- **V017 validée** (aucun bug ; seuil de masquage du bandeau à 85 px et bandeau à 44 px conservés). **Étape 9.4 livrée (V018)** : l'application s'ouvre sur le **plan** (vue graphique par défaut à tous les niveaux, plan ajusté à l'écran) ; **bouton flottant unique Liste / Plan** dont le libellé indique l'action (`➔ Liste`, `➔ Plan`, `➔ Vue graphique`) ; **bouton flottant Agrandir / Ajuster à l'écran** à icône SVG, en haut à droite du plan ; **arborescence à trois états** (large, rail par défaut, masquée) avec un bouton « Arborescence » dans l'en-tête.
- Tests Playwright/Chromium : **1103 tests** (jalons 1 à 9.3 : 1071 ; **32 pour la V018, `test_jalon9_4.py`**), 0 échec. Les anciens tests partent de la vue Liste et de l'arborescence large (nouveaux défauts) et ont été adaptés au bouton flottant.
- Les deux `furniture.js` de la V017 (fonction et vue) ont été fournis par l'utilisateur : la V018 repose sur ses vraies versions ; `js/features/furniture.js` n'a **pas** changé.
- En attente : **validation de la V018 par l'utilisateur** (voir `ToDo_Utilisateur.md`). Ensuite : pictogrammes SVG dans les boutons, « respiration » des cases libres en placement.

### (historique) État à la V017

- **Jalon 9.3 (V016) validé** (info-bulle, boutons Liste / Plan, écran replié : convenables). **V017 livrée, préalable à l'étape 9.4** : l'utilisateur a signalé une ambiguïté (le bandeau à droite d'une case et la commande « Ouvrir » menaient à deux situations différentes ; petites pièces difficiles à toucher). **Navigation unique** : le bandeau de niveau ouvre réellement l'emplacement, comme « Ouvrir » (plus de niveau dessiné dans le plan du parent, plus de texte de rappel ni de « Remonter… ») ; le bandeau est **masqué sur les cases de moins de 85 px** (toute la case ouvre le menu) et pendant le placement ; la **Vue graphique** est proposée à tout niveau qui a des sous-emplacements (plus seulement aux meubles).
- Tests Playwright/Chromium : **1071 tests** (62 + 73 + 131 + 73 + 137 + 52 + 133 + 89 jalons 1 à 7, 78 jalon 8, 43 jalon 9.1, 89 jalon 9.2, 63 jalon 9.3, **48 V017 (`test_jalon9_3bis.py`)**), 0 échec. Tests des jalons 7, 8 et 9.2 adaptés (le bandeau navigue).
- En attente : **validation de la V017 par l'utilisateur** (voir `ToDo_Utilisateur.md`), puis étape 9.4 (plan en vue d'accueil ; remarques de l'utilisateur à venir).

### (historique) État à la V016

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
| V017 (préalable au 9.4) | **Validé par l'utilisateur** : une seule façon d'entrer dans un niveau (le bandeau de niveau équivaut à « Ouvrir » ; on supprime le niveau dessiné dans le plan du parent et ses accessoires) ; bandeau masqué sur les petites tuiles ; Vue graphique étendue à tous les niveaux qui ont des sous-emplacements. *(Hypothèses de Claude, à valider à l'usage :)* seuil de masquage du bandeau = case de moins de 85 px de large ; bandeau absent pendant le placement ; un meuble garde toujours son commutateur Liste / Vue graphique, un niveau plus bas ne l'a que s'il a des sous-emplacements ; un niveau plus bas se dessine comme un meuble ; le choix Liste / Vue graphique reste commun à tous ces niveaux. |
| Jalon 14 (V023) | **Demandé par l'utilisateur** : possibilité de pieds plus grands aux meubles. **Convenu** : « Petits » (comme avant) / « Grands » ; « Grands » = moitié de la hauteur **totale** (pieds compris, donc pieds = hauteur du cadre), **« Très grands » = 75 %** de la hauteur totale (tables sans tiroirs), bande « Dessous » entre les pieds ; V023a corrige la première version (moitié du cadre seulement) ; **V023b** : tout meuble non « Haut » tient entièrement à l'écran (corps aplati si besoin ; 64 px par ligne au minimum, 40 px avec de grands pieds). *(Choix de Claude, à valider :)* l'ancien « Avec » devient « Petits » (lecture, pas de réécriture du fichier) ; pieds de 20 px de large (16 px pour les petits), aux deux extrémités sous le cadre, avec 6 % de marge ; la zone des pieds s'allonge si la bande « Dessous » est plus haute que la moitié ; les colonnes de la bande « Dessous » se répartissent sur la largeur entre les pieds (plus étroites que celles du meuble) ; un plan (logement, pièce) n'a pas de pieds. |
| Jalon 13 (V022) | **Demandé / validé par l'utilisateur** : liste d'évolutions lotie en V022 (interface), V023 (pieds), V024 (catégories) ; pictogrammes aussi pour « Ouvrir » et les « Ajouter… ». *(Choix de Claude, à valider :)* focus clavier conservé ; filet de 2 px entre les deux groupes, fusion seulement sur écran déplié ; bouton du volet = fond bleu, pictogramme blanc ; « Supprimer » = corbeille (rouge « danger ») ; « Ouvrir » = flèche entrant dans un cadre ; « Ajouter pièce / emplacement » = plan avec un « + » ; marge sous le plan de 16 px. |
| Jalon 12 (V021) | **Demandé par l'utilisateur** : boutons de l'en-tête transparents (pictogramme et cercle blancs), couleurs inversées quand loupe / engrenage sont enfoncés ; pictogramme de l'arborescence redessiné (fils alignés sous le père) ; volet d'arborescence 10 % plus étroit sur écran déplié ; « Actions » remplacé par un pictogramme ; pictogrammes plus explicites, alternés, pour élargir / réduire le volet. *(Hypothèses de Claude, à valider :)* « Actions » = trois points verticaux ; pictogramme « réduire » = pendant du dessin « agrandir » (chevron vers la gauche, séparation et barres plus courtes) ; largeur de volet = 288 px (320 × 0,9), minimum 216 px ; bouton « Actions » enfoncé (couleur d'accent) pendant que son menu est ouvert ; engrenage inversé tant que les Réglages sont ouverts. |
| Jalon 11 (V020) | **Demandé / validé par l'utilisateur (V020 validée)** : cases libres masquées en consultation (appui long = case la plus proche + menu) ; couleur `#043BB2` pour le niveau 0 et le bandeau d'en-tête ; « Réglages » en engrenage seul ; « Arborescence » en pictogramme ; boutons regroupés (arborescence / autres) ; texte d'aide du mode modification derrière un « ? » ; champ de recherche masqué + loupe à gauche de l'engrenage ; flèche de dépliement dans le rail ; bouton d'affichage du volet sur écran replié (sans rail, volet recouvrant). *(Solution de Claude, à valider :)* le bouton à trois états est remplacé par « afficher / masquer » (bouton de groupe) + « largeur » (bouton du volet, icônes élargir / réduire) ; ce bouton d'arborescence est dans l'en-tête du détail (absent des écrans Recherche et Réglages) ; le bouton Retour sort du formulaire de recherche et va dans l'en-tête ; refermer la recherche pendant une recherche revient à l'écran précédent ; le volet recouvrant se ferme par le voile, Échap ou le choix d'un élément ; les groupes sont deux « pilules » teintées alignées à droite ; le texte d'aide s'affiche en info-bulle ; aide « ? » visible seulement en modification. |
| Jalon 10 (V019) | **Demandé / validé par l'utilisateur** : trois boutons d'affichage en pictogrammes **alignés à droite** (pas en haut à gauche) ; rail remis au démarrage ; bandeaux à réduire (en-tête et recherche fusionnés sur l'écran déplié) ; appui simple = ouvrir, appui long = menu contextuel avec « Ouvrir » écrit comme les autres ; bouton pour le mode modification du plan ; bouton « + » supprimé à condition qu'un appui long sur une case libre ouvre le menu (créer un emplacement, modifier la grille). *(Hypothèses de Claude, à valider à l'usage :)* les trois boutons sont dans l'en-tête figé, sous ▲ ▼ et « Actions » (et non flottants sur le plan) ; appui long ≈ 450 ms avec vibration brève, clic droit / touche Menu équivalents ; un appui simple sur une case libre ne fait rien ; le menu d'une case libre propose aussi « Ajouter un objet ici » (hors logement) ; « Régler la grille… » aussi dans le menu « Actions » en vue graphique ; « Placer et dimensionner » conservé dans le menu d'une case comme raccourci vers le mode modification ; l'indicateur de niveau reste affiché mais n'est plus un bouton ; engrenage devant « Réglages » (le mot reste) ; en mode modification un appui long ouvre quand même le menu. |
| Jalon 9.4 (V018) | **Demandé / validé par l'utilisateur** : l'application s'ouvre sur le plan du logement (qui tient dans l'écran) ; zones de l'écran déplié : en-tête et recherche figés pleine largeur, navigation figée au-dessus du plan, arborescence figée à gauche ; **Agrandir / Ajuster** = bouton flottant à icône explicite en haut à droite du plan ; **Liste / Plan** = un seul bouton flottant dont le libellé indique l'action (éventuellement précédé de ➔) ; valable pour logement, pièces et meubles ; **arborescence à 3 états** (large, rail, masquée). *(Hypothèses de Claude, à valider à l'usage :)* rail par défaut ; bouton « Arborescence » dans l'en-tête qui fait défiler les trois états ; bouton Liste / Plan en haut à gauche sous l'en-tête figé, Agrandir à droite (sur un plan seulement) ; les boutons recouvrent le coin du plan, en liste de la place leur est réservée ; vue graphique par défaut aussi pour meubles et niveaux plus bas ; boutons de 44 px à fond sombre semi-opaque. |
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

### Jalon 9 — Interface centrée sur les plans 🟦 (étapes 1, 2 et 3 livrées, V014, V015 et V016 ; V017 = préalable à l'étape 4)
- ✅ 9.1 Plan ajusté à l'écran (largeur et hauteur), bouton « Agrandir », tuiles compactes, plan d'une pièce (commutateur Liste / Plan sur une pièce)
- ✅ 9.2 Menu contextuel près de l'élément touché (« Ouvrir » en tête, commandes du menu « Actions » de l'élément, pavés de flèches intégrés et masquables) + bouton « + » flottant pour créer au niveau du plan (V015)
- ✅ 9.3 Pictogramme ℹ️ et info-bulle, menu « Actions » déroulant, libellé de catégorie et Liste / Plan dans l'en-tête figé (V016)
- ⬜ 9.4 Plan comme vue d'accueil ; place de la liste et de l'arborescence ; affichage des objets dans le plan
- ⬜ Validation sur GitHub Pages et sur le Z Fold (utilisateur)

### V017 — Navigation unique et Vue graphique à tous les niveaux ✅ (livrée, validation utilisateur en attente)
- ✅ Le bandeau de niveau d'une case ouvre l'emplacement (comme « Ouvrir ») ; `focus`, texte de rappel et « Remonter… » supprimés
- ✅ Bandeau masqué sur les cases de moins de 85 px et pendant le placement
- ✅ Vue graphique proposée à tout niveau ayant des sous-emplacements (`hasGraphic`)
- ⬜ Validation sur GitHub Pages et sur le Z Fold (utilisateur)

### Jalon 9.4 — Plan en vue d'accueil ✅ (livré en V018, validé)
- ✅ Vue graphique par défaut (logement, pièces, meubles) ; plan ajusté à l'écran
- ✅ Bouton flottant unique Liste / Plan (libellé = action, avec ➔) ; bouton flottant Agrandir / Ajuster (icône SVG) en haut à droite du plan
- ✅ Arborescence : large, rail (défaut), masquée ; bouton d'en-tête
- ✅ Validation sur GitHub Pages et sur le Z Fold (utilisateur) : aucun bug ; améliorations ergonomiques → jalon 10
- ⬜ *(plus tard)* « respiration » du contour des cases libres en placement

### Jalon 14 — Pieds des meubles ✅ (livré en V023, validation utilisateur en attente)
- ✅ Liste « Pieds : Sans / Petits / Grands / Très grands » ; grands = pieds de la hauteur du cadre (moitié de la hauteur totale), très grands = 75 % ; bande « Dessous » entre les pieds ; ancien « Avec » lu comme « Petits »
- ⬜ Validation sur GitHub Pages et sur le Z Fold (utilisateur)
- ⬜ V024 : ouvertures dans les pièces (voir « État actuel »)

### Jalon 13 — Ajustements d'interface ✅ (livré en V022, validé)
- ✅ Focus sans carré ; conteneur unique des boutons du détail ; flèches circulaires
- ✅ Bouton du volet bleu et aussi haut que « Logement » ; icône « Actions » ; pictogrammes des menus ; marge sous le plan
- ✅ Validation par l'utilisateur (V022 puis V022a)

### Jalon 12 — Pictogrammes des commandes ✅ (livré en V021, validé)
- ✅ Boutons de l'en-tête transparents, couleurs inversées quand enfoncés
- ✅ Pictogramme de l'arborescence redessiné ; volet d'arborescence 10 % plus étroit (écran déplié)
- ✅ « Actions » en pictogramme ; pictogrammes élargir / réduire le volet
- ⬜ Validation sur GitHub Pages et sur le Z Fold (utilisateur)

### Jalon 11 — Épure de l'interface ✅ (livré en V020, validé)
- ✅ Couleur `#043BB2` (niveau 0, bandeau d'en-tête, thème)
- ✅ En-tête en pictogrammes (Retour, loupe, engrenage) ; recherche masquée
- ✅ Groupes de boutons ; aide « ? » du mode modification ; cases libres invisibles en consultation
- ✅ Arborescence : afficher / masquer + largeur (icônes explicites), flèche dans le rail, volet recouvrant sur écran replié
- ✅ Validation sur GitHub Pages et sur le Z Fold (utilisateur) : aucun bug

### Jalon 10 — Ergonomie des plans ✅ (livré en V019, validé)
- ✅ Pictogrammes SVG (`icons.js`) et boutons d'affichage alignés à droite dans l'en-tête figé (Liste / Plan, Agrandir, Modifier le plan)
- ✅ Appui simple = ouvrir, appui long = menu contextuel (`longpress.js`) ; cases libres avec menu (créer un emplacement à cette place, régler la grille) ; bouton « + » supprimé
- ✅ Mode « Modifier le plan » (bouton enfoncé, sélection par appui simple, pavés de flèches)
- ✅ En-tête et recherche sur une ligne (écran déplié), en-tête du détail resserré ; plan 7 × 10 entier dans l'écran
- ✅ Rail remis à chaque démarrage
- ✅ Validation sur GitHub Pages et sur le Z Fold (utilisateur) : fonctionne correctement ; améliorations → jalon 11

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
| V017 | 08/11/2026 01:30 | Jalon 9.3 validé ; préalable au 9.4 : navigation unique depuis les plans, bandeau masqué sur les cases étroites, Vue graphique à tous les niveaux (48 tests dédiés, 1071 au total) |
| V018 | 10/11/2026 21:05 | V017 validée ; étape 9.4 livrée : plan en vue d'accueil, boutons flottants Liste / Plan et Agrandir, arborescence à trois états (32 tests dédiés, 1103 au total) |
| V018a | 12/11/2026 21:50 | Correctif des tests sous Windows (`test_jalon5.py`, sortie UTF-8) ; aucun changement de code de l'application (1103 tests au total) |
| V018b | 13/11/2026 02:25 | Serveur de test silencieux sur les connexions coupées (14 fichiers de tests) ; aucun changement de code de l'application (1103 tests au total) |
| V019 | 17/11/2026 07:12 | V018 validée ; jalon 10 livré : pictogrammes, appui simple / long, cases libres, mode « Modifier le plan », bandeaux resserrés, rail au démarrage (60 tests dédiés, 1181 au total) |
| V020 | 20/11/2026 22:57 | V019 validée ; jalon 11 livré : couleur #043BB2, en-tête en pictogrammes, recherche masquée, groupes de boutons, aide « ? », cases libres invisibles, volet d'arborescence (43 tests dédiés, 1235 au total) |
| V021 | 24/11/2026 01:46 | V020 validée ; jalon 12 livré : pictogrammes des commandes (en-tête transparent / inversé, arborescence, « Actions », élargir / réduire), volet d'arborescence 10 % plus étroit (28 tests dédiés, 1263 au total) |
| V022 | 25/11/2026 22:35 | V021 validée ; jalon 13 livré : ajustements d'interface (focus, conteneur unique, flèches rondes, bouton du volet, icône « Actions », pictogrammes des menus, marge sous le plan ; 43 tests dédiés, 1306 au total) |
| V022a | 26/11/2026 02:45 | Correctif : pictogramme du volet d'arborescence bleu et agrandi (1308 tests au total) |
| V023 | 27/11/2026 00:35 | V022 / V022a validées ; jalon 14 livré : pieds « Sans / Petits / Grands » (43 tests dédiés, 1351 au total) |
| V023a | 27/11/2026 00:50 | Correctif jalon 14 : grands pieds = moitié de la hauteur totale (pieds compris) ; choix « Très grands » (75 %) ; 62 tests dédiés, 1370 au total |
| V023b | 27/11/2026 01:20 | Correctif jalon 14 : meubles non « Haut » entièrement visibles à l'écran (corps aplati) ; 89 tests dédiés, 1397 au total |
