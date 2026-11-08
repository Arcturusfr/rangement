# tests/test_jalon9_2.py — Application « Rangement »
# Version : V017
# Horodatage : 2026-11-08 01:30 (heure de Paris)
# Résumé : V017 : le bandeau de niveau navigue réellement ; scénario « focus » réécrit.
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon9_2.py
# Nécessite : pip install playwright  puis  playwright install chromium

import functools
import http.server
import os
import sys
import threading

from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHOTS = os.environ.get("RANGEMENT_SHOTS")
results = []
F = "Rangement.features.furniture"
COMMANDS = ["Placer et dimensionner", "Ajouter un objet ici", "Ajouter un emplacement ici", "Modifier", "Déplacer", "Dupliquer", "Supprimer"]


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (("  -> " + str(detail)) if (detail and not cond) else ""))


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def start_server():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=ROOT))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def js(page, expr):
    return page.evaluate(expr)


def stored(page):
    return page.evaluate("JSON.parse(localStorage.getItem('rangement.data'))")


def start(browser, base, w=884, h=1100, errors=None):
    ctx = browser.new_context(viewport={"width": w, "height": h})
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if errors is not None and m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)) if errors is not None else None)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector("#pane-detail .list")
    return ctx, page


def plan(page):
    page.get_by_role("button", name="Plan", exact=True).click()
    page.wait_for_selector(".furn-body[data-fit]")
    page.wait_for_timeout(150)


def wait_title(page, title):
    page.wait_for_function("document.querySelector('#pane-detail .detail-title') && document.querySelector('#pane-detail .detail-title').textContent === %r" % title)


def loc_id(page, name):
    return js(page, "Rangement.store.locations().filter(function(l){return l.name===%r;})[0].id" % name)


def geo(page, name):
    return js(page, "Rangement.store.getLocation(%r).geometry" % loc_id(page, name))


def cell(page, name):
    return page.locator(".furn-cell", has_text=name)


def menu(page):
    return page.locator(".ctx-menu")


def tap(page, name):
    cell(page, name).locator(".furn-open").click()
    page.wait_for_selector(".ctx-menu")


def choose(page, label):
    menu(page).get_by_role("button", name=label, exact=True).click()


def dlg(page):
    return page.locator("dialog.dialog[open]")


def closed(page):
    page.wait_for_selector("dialog.dialog[open]", state="detached")


def items_of(page):
    return page.locator(".ctx-menu .ctx-item").all_inner_texts()


def valid(page):
    return js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok")


def in_screen(page, sel, w, h):
    b = page.locator(sel).bounding_box()
    return b is not None and b["x"] >= 0 and b["y"] >= 0 and b["x"] + b["width"] <= w + 1 and b["y"] + b["height"] <= h + 1, b


def info(page):
    """Texte de l'info-bulle ℹ️ de l'en-tête (V016)."""
    page.locator("#info-toggle").click()
    page.wait_for_selector(".bubble")
    txt = page.locator(".bubble").inner_text()
    page.keyboard.press("Escape")
    return txt


def scenario_menu(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    plan(page)
    check("menu | aucun menu au départ, plus de bouton « Ajuster »", menu(page).count() == 0 and page.get_by_role("button", name="Ajuster le plan").count() == 0)
    check("menu | une case est un bouton (plus un lien)", page.locator("a.furn-open").count() == 0 and page.locator("button.furn-open").count() == 3)
    start_hash = js(page, "location.hash")
    tap(page, "Séjour")
    check("menu | un appui ouvre un menu près de la case", menu(page).is_visible() and "Séjour" in menu(page).inner_text())
    check("menu | nom du parent rappelé (le logement)", "Logement" in menu(page).locator(".ctx-path").inner_text())
    check("menu | la navigation n'a pas eu lieu", js(page, "location.hash") == start_hash)
    primary = menu(page).locator(".ctx-primary")
    check("menu | « Ouvrir » en premier", primary.inner_text() == "Ouvrir" and menu(page).locator("button").first.inner_text() == "Ouvrir")
    check("menu | « Ouvrir » a le focus", js(page, "document.activeElement.textContent") == "Ouvrir")
    pb = primary.bounding_box()
    ib = menu(page).locator(".ctx-item").first.bounding_box()
    check("menu | « Ouvrir » plus grand et en gras", pb["height"] > ib["height"] and pb["height"] >= 52 and int(primary.evaluate("e => getComputedStyle(e).fontWeight")) >= 700, (pb, ib))
    check("menu | les commandes de l'élément, dans l'ordre", items_of(page) == COMMANDS, items_of(page))
    check("menu | case marquée pendant que le menu est ouvert", cell(page, "Séjour").evaluate("e => e.classList.contains('has-menu')"))
    cb, mb = cell(page, "Séjour").bounding_box(), menu(page).bounding_box()
    near = (0 <= mb["y"] - (cb["y"] + cb["height"]) <= 8) or (mb["y"] + mb["height"] <= cb["y"] + 1)
    check("menu | placé juste sous (ou au-dessus de) la case, dans l'écran", near and mb["x"] >= 0 and mb["x"] + mb["width"] <= 885 and mb["y"] + mb["height"] <= 1101, (cb, mb))
    check("menu | commandes ≥ 44 px", all(menu(page).locator("button").nth(i).bounding_box()["height"] >= 43 for i in range(menu(page).locator("button").count())))
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j9-2-menu-deplie.png"))
    page.keyboard.press("Escape")
    check("menu | Échap referme et rend le focus à la case", menu(page).count() == 0 and js(page, "document.activeElement.className") == "furn-open" and not cell(page, "Séjour").evaluate("e => e.classList.contains('has-menu')"))
    tap(page, "Séjour")
    page.mouse.click(5, 5)
    check("menu | un appui ailleurs referme sans rien déclencher", menu(page).count() == 0 and js(page, "location.hash") == start_hash)
    tap(page, "Séjour")
    js(page, "location.hash = '#/r'")
    page.wait_for_selector("#pane-detail .settings")
    check("menu | un changement d'écran referme le menu", menu(page).count() == 0)
    page.go_back()
    page.wait_for_selector(".furn-body[data-fit]")
    tap(page, "Séjour")
    choose(page, "Ouvrir")
    wait_title(page, "Séjour")
    check("menu | « Ouvrir » ouvre l'emplacement et referme le menu", menu(page).count() == 0 and page.inner_text("#pane-detail .detail-title") == "Séjour")
    check("menu | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_commands(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    plan(page)
    n_items = len(stored(page)["items"])

    # Modifier
    tap(page, "Entrée")
    choose(page, "Modifier")
    d = dlg(page)
    check("commandes | Modifier : boîte d'édition, menu refermé", "Modifier" in d.inner_text() and menu(page).count() == 0)
    d.get_by_label("Nom").fill("Hall")
    d.get_by_role("button", name="Enregistrer").click()
    closed(page)
    page.wait_for_selector(".furn-cell:has-text('Hall')")
    check("commandes | Modifier : le plan est à jour", cell(page, "Hall").count() == 1 and cell(page, "Entrée").count() == 0)

    # Ajouter un objet
    tap(page, "Séjour")
    choose(page, "Ajouter un objet ici")
    d = dlg(page)
    check("commandes | Ajouter un objet : dans la pièce touchée", "Nouvel objet dans \u00ab Séjour \u00bb" in d.inner_text(), d.inner_text())
    d.get_by_label("Nom").fill("Lampe")
    d.get_by_role("button", name="Ajouter", exact=True).click()
    closed(page)
    page.wait_for_function("document.querySelector('.furn-cell:nth-child(3)') !== null")
    check("commandes | Ajouter un objet : compteur de la pièce à jour (3 objets)", "3 objets" in cell(page, "Séjour").inner_text() and len(stored(page)["items"]) == n_items + 1, cell(page, "Séjour").inner_text())

    # Ajouter un emplacement
    tap(page, "Hall")
    choose(page, "Ajouter un emplacement ici")
    d = dlg(page)
    check("commandes | Ajouter un emplacement : dans la pièce touchée", "Nouvel emplacement dans \u00ab Hall \u00bb" in d.inner_text(), d.inner_text())
    d.get_by_label("Nom").fill("Étagère entrée")
    d.get_by_role("button", name="Ajouter", exact=True).click()
    closed(page)
    page.wait_for_selector(".furn-cell:has-text('Hall') .furn-more")
    check("commandes | Ajouter un emplacement : l'icône de niveau apparaît (2 sous-emplacements)", cell(page, "Hall").locator(".furn-more").inner_text().strip() == "2")

    # Dupliquer : on arrive sur la copie
    tap(page, "Chambre à coucher")
    choose(page, "Dupliquer")
    d = dlg(page)
    check("commandes | Dupliquer : préremplie avec le nom de la case", d.get_by_label("Nom de la copie").input_value() == "Chambre à coucher")
    d.get_by_label("Nom de la copie").fill("Chambre bis")
    d.get_by_role("button", name="Dupliquer", exact=True).click()
    closed(page)
    wait_title(page, "Chambre bis")
    check("commandes | Dupliquer : on arrive sur la copie", True)
    page.goto(base + "#/")
    page.wait_for_selector(".furn-body[data-fit]")

    # Déplacer (changer de parent) : la boîte propose la racine et les autres emplacements
    tap(page, "Chambre bis")
    choose(page, "Déplacer")
    d = dlg(page)
    options = d.get_by_label("Nouvel emplacement parent").locator("option").all_inner_texts()
    check("commandes | Déplacer : propose les autres emplacements", "Logement (racine)" in options and "Séjour" in options and not any("Chambre bis" in o for o in options), options)
    d.get_by_role("button", name="Annuler").click()
    closed(page)

    # Supprimer : refusé si non vide ; accepté si vide
    tap(page, "Séjour")
    choose(page, "Supprimer")
    d = dlg(page)
    check("commandes | Supprimer : refusé quand la pièce contient quelque chose", "Suppression impossible" in d.inner_text(), d.inner_text())
    d.get_by_role("button", name="OK").click()
    closed(page)
    tap(page, "Chambre bis")
    choose(page, "Supprimer")
    d = dlg(page)
    check("commandes | Supprimer : confirmation pour une pièce vide", "Supprimer cet emplacement" in d.inner_text())
    d.get_by_role("button", name="Supprimer", exact=True).click()
    closed(page)
    page.wait_for_function("document.querySelectorAll('.furn-cell').length === 3")
    check("commandes | Supprimer : la case disparaît du plan, on reste sur le plan", cell(page, "Chambre bis").count() == 0 and page.locator(".furn-view").count() == 1)
    check("commandes | données valides", valid(page))
    check("commandes | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_place(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    plan(page)
    check("placement | le bouton « + » est là hors placement", page.locator("#plan-add").is_visible())
    tap(page, "Entrée")
    choose(page, "Placer et dimensionner")
    page.wait_for_selector(".furn-sel")
    check("placement | la case est sélectionnée, pavés de flèches visibles", "Entrée" in page.inner_text(".furn-sel-text") and page.locator(".furn-pad-btn").count() == 8)
    check("placement | mode placement exposé", page.locator(".furn-view").get_attribute("data-editing") == "true")
    check("placement | « Grille… » et « Terminer » dans le pavé", page.locator(".furn-sel").get_by_role("button", name="Grille…").is_visible() and page.locator(".furn-sel").get_by_role("button", name="Terminer").is_visible())
    check("placement | « + » masqué pendant le placement", page.locator("#plan-add").count() == 0)
    check("placement | cases libres affichées", page.locator(".furn-slot").count() == 1)
    before = js(page, "%s.layout(%s.ROOT).cells.filter(function(c){return c.id==='%s';})[0]" % (F, F, loc_id(page, "Entrée")))
    page.get_by_role("button", name="Décaler vers le bas", exact=True).click()
    page.wait_for_function("Rangement.store.getLocation('%s').geometry && Rangement.store.getLocation('%s').geometry.row === 1" % (loc_id(page, "Entrée"), loc_id(page, "Entrée")))
    after = geo(page, "Entrée")
    check("placement | une flèche déplace la case d'une ligne", after["row"] == before["row"] + 1 and after["col"] == before["col"], (before, after))
    page.get_by_role("button", name="Largeur +", exact=True).click()
    page.wait_for_timeout(150)
    check("placement | message de refus ou agrandissement, jamais d'erreur", valid(page))
    page.locator(".furn-cell", has_text="Séjour").locator(".furn-open").click()
    check("placement | un appui sur une autre case la sélectionne (pas de menu)", menu(page).count() == 0 and "Séjour" in page.inner_text(".furn-sel-text"))
    page.locator(".furn-sel").get_by_role("button", name="Terminer").click()
    page.wait_for_function("document.querySelectorAll('.furn-sel').length === 0")
    check("placement | Terminer masque le pavé, les cases rouvrent le menu", page.locator(".furn-slot").count() == 0 and page.locator("#plan-add").is_visible() and page.locator(".furn-view").get_attribute("data-editing") == "false")
    tap(page, "Séjour")
    check("placement | le menu s'ouvre de nouveau", menu(page).is_visible())
    page.keyboard.press("Escape")

    # placement : changement d'écran → fin du placement
    tap(page, "Séjour")
    choose(page, "Placer et dimensionner")
    page.wait_for_selector(".furn-sel")
    js(page, "location.hash = '#/l/%s'" % loc_id(page, "Séjour"))
    wait_title(page, "Séjour")
    page.goto(base + "#/")
    page.wait_for_selector(".furn-body[data-fit]")
    check("placement | un changement d'écran referme le placement", page.locator(".furn-sel").count() == 0 and page.locator("#plan-add").count() == 1)

    # Grille… depuis le pavé
    tap(page, "Séjour")
    choose(page, "Placer et dimensionner")
    page.wait_for_selector(".furn-sel")
    page.locator(".furn-sel").get_by_role("button", name="Grille…").click()
    d = dlg(page)
    check("placement | « Grille… » ouvre les réglages de la grille", "Grille de" in d.inner_text() and d.get_by_label("Colonnes").count() == 1)
    d.get_by_role("button", name="Annuler").click()
    closed(page)
    check("placement | annuler garde le placement en cours", page.locator(".furn-sel").count() == 1)
    check("placement | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_plus(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    check("plus | pas de « + » en mode liste", page.locator("#plan-add").count() == 0)
    plan(page)
    add = page.locator("#plan-add")
    b = add.bounding_box()
    check("plus | bouton rond flottant ≥ 44 px, dans l'écran, en bas à droite", b["width"] >= 44 and b["height"] >= 44 and b["x"] + b["width"] <= 884 and b["y"] + b["height"] <= 1100 and b["x"] > 600 and b["y"] > 800, b)
    check("plus | nom accessible", add.get_attribute("aria-label") == "Ajouter ou régler ici")
    add.click()
    page.wait_for_selector(".ctx-menu")
    check("plus | à la racine : ajouter une pièce, régler la grille", items_of(page) == ["Ajouter une pièce", "Régler la grille…"] and menu(page).locator(".ctx-primary").count() == 0, items_of(page))
    mb = menu(page).bounding_box()
    check("plus | menu dans l'écran, au-dessus du bouton", mb["y"] >= 0 and mb["y"] + mb["height"] <= b["y"] + 1 and mb["x"] + mb["width"] <= 885, (mb, b))
    choose(page, "Ajouter une pièce")
    d = dlg(page)
    check("plus | nouvelle pièce", "Nouvelle pièce" in d.inner_text())
    d.get_by_label("Nom").fill("Garage")
    d.get_by_role("button", name="Ajouter", exact=True).click()
    closed(page)
    page.wait_for_selector(".furn-cell:has-text('Garage')")
    check("plus | la pièce apparaît dans la première case libre", cell(page, "Garage").count() == 1 and page.locator(".furn-cell").count() == 4)

    # une pièce : objet, emplacement, grille
    sej = loc_id(page, "Séjour")
    page.goto(base + "#/l/" + sej)
    wait_title(page, "Séjour")
    page.wait_for_selector(".furn-body[data-fit]")
    page.locator("#plan-add").click()
    page.wait_for_selector(".ctx-menu")
    check("plus | dans une pièce : objet, emplacement, grille", items_of(page) == ["Ajouter un objet ici", "Ajouter un emplacement ici", "Régler la grille…"] and "Séjour" in menu(page).inner_text(), items_of(page))
    choose(page, "Ajouter un emplacement ici")
    d = dlg(page)
    check("plus | l'emplacement est créé dans la pièce affichée", "Nouvel emplacement dans \u00ab Séjour \u00bb" in d.inner_text())
    d.get_by_role("button", name="Annuler").click()
    closed(page)

    # grille d'une pièce
    page.locator("#plan-add").click()
    choose(page, "Régler la grille…")
    d = dlg(page)
    check("grille | pièce : colonnes et lignes seulement", d.get_by_label("Colonnes").count() == 1 and d.get_by_label("Lignes").count() == 1 and d.get_by_label("Dessus").count() == 0 and d.get_by_label("Pieds").count() == 0)
    check("grille | choix de colonnes jusqu'à 20", d.get_by_label("Colonnes").locator("option").count() == 20)
    d.get_by_label("Colonnes").select_option("4")
    d.get_by_label("Lignes").select_option("3")
    d.get_by_role("button", name="Appliquer").click()
    closed(page)
    g = geo(page, "Séjour")
    check("grille | grille de la pièce enregistrée, sa place dans le logement intacte", g["cols"] == 4 and g["rows"] == 3, g)
    check("grille | le plan est redessiné (4 × 3)", js(page, "%s.layout('%s')" % (F, sej))["C"] == 4 and js(page, "%s.layout('%s')" % (F, sej))["L"] == 3)

    # grille du logement : refus clair, rien ne change
    page.goto(base + "#/")
    page.wait_for_selector(".furn-body[data-fit]")
    page.locator("#plan-add").click()
    choose(page, "Régler la grille…")
    d = dlg(page)
    d.get_by_label("Colonnes").select_option("1")
    d.get_by_label("Lignes").select_option("1")
    d.get_by_role("button", name="Appliquer").click()
    check("grille | réduction refusée : message clair, boîte conservée", "déplacez-les" in d.inner_text() and d.is_visible())
    d.get_by_role("button", name="Annuler").click()
    closed(page)
    check("grille | rien n'a changé après un refus", js(page, "Rangement.store.plan()") is None)
    page.locator("#plan-add").click()
    choose(page, "Régler la grille…")
    d = dlg(page)
    check("grille | valeurs actuelles préremplies", d.get_by_label("Colonnes").input_value() == "2" and d.get_by_label("Lignes").input_value() == "2")
    d.get_by_role("button", name="Appliquer").click()
    closed(page)
    check("grille | appliquer sans changement : rien n'est figé", js(page, "Rangement.store.plan()") is None)
    page.locator("#plan-add").click()
    choose(page, "Régler la grille…")
    dlg(page).get_by_label("Colonnes").select_option("7")
    dlg(page).get_by_label("Lignes").select_option("10")
    dlg(page).get_by_role("button", name="Appliquer").click()
    closed(page)
    page.wait_for_function("Rangement.store.plan() && Rangement.store.plan().cols === 7")
    check("grille | 7 × 10 enregistré dans le plan", js(page, "Rangement.store.plan()") == {"cols": 7, "rows": 10})
    check("grille | données valides", valid(page))

    # meuble : réglages complets
    mv = loc_id(page, "Meuble living")
    page.goto(base + "#/l/" + mv)
    wait_title(page, "Meuble living")
    page.get_by_role("button", name="Vue graphique").click()
    page.wait_for_selector(".furn-view")
    check("plus | meuble : « + » aussi", page.locator("#plan-add").is_visible())
    page.locator("#plan-add").click()
    choose(page, "Régler la grille…")
    d = dlg(page)
    check("grille | meuble : proportions, dessus, dessous et pieds en plus", all(d.get_by_label(n).count() == 1 for n in ("Colonnes", "Lignes", "Proportions", "Dessus", "Dessous", "Pieds")))
    d.get_by_label("Pieds").select_option("1")
    d.get_by_label("Proportions").select_option(label="Carré")
    d.get_by_label("Dessus").select_option("1")
    d.get_by_role("button", name="Appliquer").click()
    closed(page)
    g = geo(page, "Meuble living")
    check("grille | meuble : pieds, proportions et bande enregistrés", g.get("feet") is True and g.get("ratio") == 1 and g.get("top") == 1, g)
    check("grille | meuble : bande et pieds dessinés", page.locator(".furn-band[data-zone='top']").count() == 1 and page.locator(".furn-feet").count() == 1)

    # niveau inférieur : le « + » travaille sur le niveau affiché
    js(page, "Rangement.features.locations.create({name:'Boîte', kind:'boite', parentId:'%s'})" % loc_id(page, "Tiroir bas gauche"))
    cell(page, "Tiroir bas gauche").locator(".furn-more").click()
    wait_title(page, "Tiroir bas gauche")
    page.wait_for_selector(".furn-view")
    page.locator("#plan-add").click()
    page.wait_for_selector(".ctx-menu")
    check("plus | niveau inférieur ouvert (Vue graphique) : le menu concerne l'emplacement affiché", "Tiroir bas gauche" in menu(page).inner_text(), menu(page).inner_text())
    page.keyboard.press("Escape")
    check("plus | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_focus(browser, base):
    """V017 : le bandeau de niveau navigue réellement ; rien n'est « dessiné dans le parent »."""
    errors = []
    ctx, page = start(browser, base, errors=errors)
    plan(page)
    cell(page, "Séjour").locator(".furn-more").click()
    wait_title(page, "Séjour")
    page.wait_for_selector(".furn-body[data-fit]")
    txt = info(page)
    check("niveau | le bandeau ouvre la pièce : adresse, en-tête, ℹ️", js(page, "location.hash") == "#/l/" + loc_id(page, "Séjour") and "Niveau 1" in txt and page.locator(".furn-caption").count() == 0, txt)
    check("niveau | les meubles de la pièce sont dessinés", page.locator(".furn-cell .furn-name").all_inner_texts() == ["Meuble living"])
    cell(page, "Meuble living").locator(".furn-more").click()
    wait_title(page, "Meuble living")
    check("niveau | le bandeau du meuble ouvre le meuble", "Niveau 2" in info(page))
    page.goto(base + "#/")
    page.wait_for_selector(".furn-body[data-fit]")
    check("niveau | retour au logement : plan complet, rien d'ouvert avant", page.locator(".furn-cell .furn-name").all_inner_texts() == ["Chambre à coucher", "Entrée", "Séjour"])
    check("niveau | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_narrow(browser, base):
    errors = []
    ctx, page = start(browser, base, 390, 844, errors)
    js(page, "Rangement.features.locations.create({name:'<img src=x onerror=window.__xss=1>', kind:'piece'})")
    plan(page)
    tap(page, "<img")
    ok, b = in_screen(page, ".ctx-menu", 390, 844)
    check("replié | menu dans l'écran", ok, b)
    check("replié | commandes ≥ 44 px", all(menu(page).locator("button").nth(i).bounding_box()["height"] >= 43 for i in range(menu(page).locator("button").count())))
    check("replié | nom hostile affiché comme texte", menu(page).locator("img").count() == 0 and "<img src=x" in menu(page).inner_text() and page.evaluate("window.__xss") is None)
    check("replié | pas de défilement horizontal", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j9-2-menu-replie.png"))
    page.keyboard.press("Escape")
    # case du bas à droite : le menu reste dans l'écran
    names = page.locator(".furn-cell .furn-name").all_inner_texts()
    last = names[-1]
    cell(page, last).locator(".furn-open").click()
    page.wait_for_selector(".ctx-menu")
    ok, b = in_screen(page, ".ctx-menu", 390, 844)
    check("replié | case en bas du plan : menu dans l'écran", ok, b)
    page.keyboard.press("Escape")
    add_ok, b = in_screen(page, "#plan-add", 390, 844)
    check("replié | « + » dans l'écran, ≥ 44 px", add_ok and b["width"] >= 44, b)
    page.locator("#plan-add").click()
    page.wait_for_selector(".ctx-menu")
    ok, b = in_screen(page, ".ctx-menu", 390, 844)
    check("replié | menu du « + » dans l'écran", ok, b)
    page.keyboard.press("Escape")

    # placement : les pavés tiennent dans l'écran et le plan reste visible
    tap(page, "Séjour")
    choose(page, "Placer et dimensionner")
    page.wait_for_selector(".furn-sel")
    page.wait_for_timeout(250)
    ok, b = in_screen(page, ".furn-sel", 390, 844)
    check("replié | pavés de flèches dans l'écran", ok, b)
    pads = page.locator(".furn-pad-btn")
    check("replié | 8 flèches ≥ 44 px", pads.count() == 8 and all(pads.nth(i).bounding_box()["height"] >= 43 and pads.nth(i).bounding_box()["width"] >= 43 for i in range(8)))
    btns = page.locator(".furn-sel-btns .button")
    check("replié | « Grille… » et « Terminer » ≥ 44 px", btns.count() == 2 and all(btns.nth(i).bounding_box()["height"] >= 43 for i in range(2)))
    plan_box, sel_box = page.locator(".furn-body").bounding_box(), page.locator(".furn-sel").bounding_box()
    check("replié | le plan reste en grande partie visible au-dessus du pavé", plan_box["y"] + min(plan_box["height"], 150) <= sel_box["y"], (plan_box, sel_box))
    check("replié | pas de défilement horizontal en placement", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j9-2-placement-replie.png"))
    page.locator(".furn-sel").get_by_role("button", name="Terminer").click()
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()


def main():
    server = start_server()
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        scenario_menu(browser, base)
        scenario_commands(browser, base)
        scenario_place(browser, base)
        scenario_plus(browser, base)
        scenario_focus(browser, base)
        scenario_narrow(browser, base)
        browser.close()
    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
