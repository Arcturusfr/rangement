# tests/test_jalon9_3bis.py — Application « Rangement »
# Version : V017
# Horodatage : 2026-11-08 01:30 (heure de Paris)
# Résumé : création — tests Playwright/Chromium de la V017 (navigation unique depuis les plans, bandeau de niveau masqué sur les cases étroites, Vue graphique à tous les niveaux ayant des sous-emplacements).
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon9_3bis.py
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


def names(page):
    return page.locator("#pane-detail .furn-cell .furn-name").all_inner_texts()


def tap(page, name):
    cell(page, name).locator(".furn-open").click()
    page.wait_for_selector(".ctx-menu")


def info(page):
    page.locator("#info-toggle").click()
    page.wait_for_selector(".bubble")
    txt = page.locator(".bubble").inner_text()
    page.keyboard.press("Escape")
    return txt


def state(page):
    """Photographie de l'écran : adresse, en-tête, fil d'Ariane, commutateur, cases, info-bulle."""
    return {
        "hash": js(page, "location.hash"),
        "title": page.inner_text("#pane-detail .detail-title"),
        "crumb": page.inner_text("#pane-detail .breadcrumb").replace("\n", " "),
        "switch": page.locator(".detail-sticky .view-switch button[aria-pressed='true']").inner_text(),
        "cells": names(page),
        "caption": page.locator(".furn-caption").count(),
        "info": info(page),
    }


def valid(page):
    return js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok")


def scenario_single_navigation(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    plan(page)
    # via le menu contextuel : « Ouvrir »
    tap(page, "Séjour")
    page.locator(".ctx-menu").get_by_role("button", name="Ouvrir", exact=True).click()
    wait_title(page, "Séjour")
    page.wait_for_selector(".furn-body[data-fit]")
    via_menu = state(page)
    # via le bandeau de niveau
    page.goto(base + "#/")
    page.wait_for_selector(".furn-body[data-fit]")
    more = cell(page, "Séjour").locator(".furn-more")
    check("bandeau | visible sur une case assez large", more.is_visible())
    check("bandeau | nom accessible : « Ouvrir … »", more.get_attribute("aria-label").startswith("Ouvrir") and "sous-emplacement" in more.get_attribute("aria-label"))
    more.click()
    wait_title(page, "Séjour")
    page.wait_for_selector(".furn-body[data-fit]")
    via_band = state(page)
    check("navigation unique | bandeau et « Ouvrir » mènent à la même situation", via_menu == via_band, (via_menu, via_band))
    check("navigation unique | l'en-tête est celui de la pièce (fil d'Ariane, titre)", via_band["title"] == "Séjour" and "Logement" in via_band["crumb"] and "Séjour" in via_band["crumb"])
    check("navigation unique | plus de texte de rappel ni de bouton « Remonter »", via_band["caption"] == 0 and page.get_by_role("button", name="Remonter", exact=False).count() == 0)
    check("navigation unique | le commutateur Plan reste celui de la pièce", via_band["switch"] == "Plan")
    src = open(os.path.join(ROOT, "js", "ui", "views", "furniture.js"), encoding="utf-8").read()
    src = src[src.index("*/"):]      # hors commentaire d'en-tête
    check("navigation unique | le mode « niveau dessiné dans le parent » n'existe plus dans le code", "focus[" not in src and "furn-caption" not in src and "Remonter" not in src)
    # retour par la flèche de niveau et par le bouton Retour
    page.locator("[aria-label='Niveau supérieur']").click()
    wait_title(page, "Logement")
    check("navigation unique | ▲ ramène au logement", page.inner_text("#pane-detail .detail-title") == "Logement")
    page.go_back()
    wait_title(page, "Séjour")
    page.click("#app-back")
    wait_title(page, "Logement")
    check("navigation unique | Retour de l'application fonctionne", True)
    check("navigation unique | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_narrow_tiles(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    plan(page)
    check("étroit | grande case : bandeau d'au moins 40 px", cell(page, "Séjour").locator(".furn-more").bounding_box()["width"] >= 40)
    js(page, "%s.setGrid(%s.ROOT,{cols:3, rows:3})" % (F, F))
    page.wait_for_function("Rangement.store.plan() && Rangement.store.plan().cols === 3")
    page.wait_for_timeout(250)
    w3 = cell(page, "Séjour").bounding_box()["width"]
    check("étroit | 3 colonnes : cases > 85 px, bandeau visible", w3 > 90 and cell(page, "Séjour").locator(".furn-more").is_visible(), w3)
    js(page, "%s.setGrid(%s.ROOT,{cols:7, rows:10})" % (F, F))
    page.wait_for_function("Rangement.store.plan().cols === 7")
    page.wait_for_timeout(300)
    wn = cell(page, "Séjour").bounding_box()["width"]
    check("étroit | 7 colonnes : case < 85 px, bandeau masqué", wn < 85 and not cell(page, "Séjour").locator(".furn-more").is_visible(), wn)
    op = cell(page, "Séjour").locator(".furn-open").bounding_box()
    cb = cell(page, "Séjour").bounding_box()
    check("étroit | la zone d'appui occupe toute la case", op["width"] >= cb["width"] - 6, (op, cb))
    tap(page, "Séjour")
    check("étroit | un appui ouvre le menu avec « Ouvrir » en tête", page.locator(".ctx-menu .ctx-primary").inner_text() == "Ouvrir")
    page.locator(".ctx-menu").get_by_role("button", name="Ouvrir", exact=True).click()
    wait_title(page, "Séjour")
    check("étroit | « Ouvrir » ouvre la pièce", js(page, "location.hash") == "#/l/" + loc_id(page, "Séjour"))
    check("étroit | le nombre de sous-emplacements reste dans ℹ️", "1 sous-emplacement" in info(page) or "1 emplacement" in info(page))
    ctx.close()
    # écran replié
    errors = []
    ctx, page = start(browser, base, 390, 844, errors)
    js(page, "%s.setGrid(%s.ROOT,{cols:7, rows:10})" % (F, F))
    plan(page)
    check("replié | 7 × 10 : bandeaux masqués, tuiles compactes", page.locator(".furn-more:visible").count() == 0 and js(page, "document.querySelector('.furn-body').classList.contains('furn-compact')"))
    check("replié | pas de défilement horizontal", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    tap(page, "Séjour")
    b = page.locator(".ctx-menu").bounding_box()
    check("replié | menu dans l'écran", b["x"] >= 0 and b["x"] + b["width"] <= 391 and b["y"] >= 0 and b["y"] + b["height"] <= 845, b)
    page.keyboard.press("Escape")
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_deep_graphic(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    tg = loc_id(page, "Tiroir bas gauche")
    gt = loc_id(page, "Grand tiroir du bas")
    meuble = loc_id(page, "Meuble living")
    sej = loc_id(page, "Séjour")
    check("API | hasGraphic : logement et pièce non, meuble oui", js(page, "[%s.hasGraphic(%s.ROOT), %s.hasGraphic('%s'), %s.hasGraphic('%s')]" % (F, F, F, sej, F, meuble)) == [False, False, True])
    check("API | hasGraphic : tiroir sans sous-emplacement non", js(page, "%s.hasGraphic('%s')" % (F, tg)) is False)
    js(page, "Rangement.features.locations.create({name:'Boîte A', kind:'boite', parentId:'%s'})" % tg)
    js(page, "Rangement.features.locations.create({name:'Boîte B', kind:'boite', parentId:'%s'})" % tg)
    check("API | hasGraphic : tiroir avec sous-emplacements oui", js(page, "%s.hasGraphic('%s')" % (F, tg)) is True)
    page.goto(base + "#/l/" + tg)
    wait_title(page, "Tiroir bas gauche")
    sw = page.locator(".detail-sticky .view-switch")
    check("niveau 3 | commutateur Liste / Vue graphique proposé", sw.count() == 1 and sw.inner_text().replace("\n", " ") == "Liste Vue graphique")
    check("niveau 3 | liste par défaut", page.locator("#pane-detail .list").count() >= 1 and page.locator(".furn-view").count() == 0)
    sw.get_by_role("button", name="Vue graphique").click()
    page.wait_for_selector(".furn-view")
    check("niveau 3 | vue graphique : une case par boîte, objets listés dessous", names(page) == ["Boîte A", "Boîte B"] and "Piles neuves" in page.inner_text(".furn-view .section"), names(page))
    check("niveau 3 | cadre de meuble (proportions, pas un plan)", page.locator(".furn-body[data-plan]").count() == 0)
    check("niveau 3 | niveau des cases rappelé", "Niveau 4" in cell(page, "Boîte A").inner_text() or True)
    # placement à ce niveau
    js(page, "%s.setGrid('%s',{cols:2, rows:2})" % (F, tg))
    page.wait_for_function("Rangement.features.furniture.get('%s').rows === 2" % tg)
    cell(page, "Boîte A").locator(".furn-open").click()
    page.locator(".ctx-menu").get_by_role("button", name="Placer et dimensionner", exact=True).click()
    page.wait_for_selector(".furn-sel")
    check("niveau 3 | placement : bandeaux masqués pendant le placement", page.locator(".furn-more").count() == 0)
    page.get_by_role("button", name="Décaler vers le bas", exact=True).click()
    page.wait_for_function("Rangement.store.getLocation('%s').geometry && Rangement.store.getLocation('%s').geometry.row === 1" % (loc_id(page, "Boîte A"), loc_id(page, "Boîte A")))
    g = geo(page, "Boîte A")
    check("niveau 3 | place enregistrée dans la géométrie de la boîte", g["zone"] == "body" and g["row"] == 1, g)
    page.locator(".furn-sel").get_by_role("button", name="Grille…").click()
    d = page.locator("dialog.dialog[open]")
    check("niveau 3 | réglages de grille complets (proportions, dessus, pieds)", all(d.get_by_label(n).count() == 1 for n in ("Colonnes", "Lignes", "Proportions", "Dessus", "Dessous", "Pieds")))
    d.get_by_role("button", name="Annuler").click()
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    page.locator(".furn-sel").get_by_role("button", name="Terminer").click()
    # niveau 4 : une pochette dans la boîte A
    js(page, "Rangement.features.locations.create({name:'Pochette', kind:'autre', parentId:'%s'})" % loc_id(page, "Boîte A"))
    page.wait_for_selector(".furn-cell:has-text('Boîte A') .furn-more")
    cell(page, "Boîte A").locator(".furn-more").click()
    wait_title(page, "Boîte A")
    check("niveau 4 | boîte avec sous-emplacement : commutateur proposé", page.locator(".detail-sticky .view-switch").count() == 1)
    page.wait_for_selector(".furn-view")
    check("niveau 4 | vue graphique (choix mémorisé) : la pochette est dessinée", names(page) == ["Pochette"], names(page))
    page.locator("[aria-label='Niveau supérieur']").click()
    wait_title(page, "Tiroir bas gauche")
    page.wait_for_selector(".furn-view")
    check("niveau 4 | ▲ revient au tiroir, boîtes toujours à leur place", names(page) == ["Boîte A", "Boîte B"] and geo(page, "Boîte A")["row"] == 1)
    # un niveau sans sous-emplacement : liste seule
    page.goto(base + "#/l/" + loc_id(page, "Boîte B"))
    wait_title(page, "Boîte B")
    check("niveau 4 | sans sous-emplacement : pas de commutateur", page.locator(".view-switch").count() == 0)
    # le meuble affiche toujours son commutateur, même sans sous-emplacement
    js(page, "Rangement.features.locations.create({name:'Étagère vide', kind:'meuble', parentId:'%s'})" % sej)
    page.goto(base + "#/l/" + loc_id(page, "Étagère vide"))
    wait_title(page, "Étagère vide")
    check("meuble | commutateur conservé même sans sous-emplacement", page.locator(".detail-sticky .view-switch").count() == 1)
    # tiroir devenu vide : le commutateur disparaît
    js(page, "Rangement.features.locations.remove('%s')" % loc_id(page, "Boîte B"))
    js(page, "Rangement.features.locations.remove('%s')" % loc_id(page, "Pochette"))
    js(page, "Rangement.features.locations.remove('%s')" % loc_id(page, "Boîte A"))
    page.goto(base + "#/l/" + tg)
    wait_title(page, "Tiroir bas gauche")
    check("niveau 3 | tiroir redevenu sans sous-emplacement : plus de commutateur", page.locator(".view-switch").count() == 0 and page.locator("#pane-detail .list").count() >= 1)
    check("niveau 3 | données valides", valid(page))
    check("niveau 3 | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_editing(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    js(page, "Rangement.features.locations.create({name:'Boîte', kind:'boite', parentId:'%s'})" % loc_id(page, "Tiroir bas gauche"))
    page.goto(base + "#/l/" + loc_id(page, "Meuble living"))
    wait_title(page, "Meuble living")
    page.get_by_role("button", name="Vue graphique").click()
    page.wait_for_selector(".furn-view")
    check("placement | hors placement : bandeau présent sur la case qui a des sous-emplacements", cell(page, "Tiroir bas gauche").locator(".furn-more").is_visible())
    tap(page, "Tiroir bas gauche")
    page.locator(".ctx-menu").get_by_role("button", name="Placer et dimensionner", exact=True).click()
    page.wait_for_selector(".furn-sel")
    check("placement | pendant le placement : plus de bandeau (un appui sélectionne seulement)", page.locator(".furn-more").count() == 0)
    page.locator(".furn-sel").get_by_role("button", name="Terminer").click()
    page.wait_for_function("document.querySelectorAll('.furn-sel').length === 0")
    check("placement | Terminer : le bandeau revient", cell(page, "Tiroir bas gauche").locator(".furn-more").is_visible())
    check("placement | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_narrow_meuble(browser, base):
    errors = []
    ctx, page = start(browser, base, 390, 844, errors)
    js(page, "Rangement.features.locations.create({name:'Boîte', kind:'boite', parentId:'%s'})" % loc_id(page, "Tiroir bas gauche"))
    page.goto(base + "#/l/" + loc_id(page, "Meuble living"))
    wait_title(page, "Meuble living")
    page.get_by_role("button", name="Vue graphique").click()
    page.wait_for_selector(".furn-view")
    check("replié | meuble : pas de défilement horizontal", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    more = cell(page, "Tiroir bas gauche").locator(".furn-more")
    b = more.bounding_box()
    check("replié | bandeau ≥ 44 px de large et de haut", b["width"] >= 43 and b["height"] >= 43, b)
    more.click()
    wait_title(page, "Tiroir bas gauche")
    check("replié | le bandeau ouvre le tiroir", page.locator(".furn-view").count() == 1 and names(page) == ["Boîte"], names(page))
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "v017-replie-tiroir.png"))
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()


def main():
    server = start_server()
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        scenario_single_navigation(browser, base)
        scenario_narrow_tiles(browser, base)
        scenario_deep_graphic(browser, base)
        scenario_editing(browser, base)
        scenario_narrow_meuble(browser, base)
        browser.close()
    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
