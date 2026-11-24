# tests/test_jalon12.py — Application « Rangement »
# Version : V021
# Horodatage : 2026-11-24 01:46 (heure de Paris)
# Résumé : jalon 12 (V021) : boutons de l'en-tête transparents / inversés, pictogramme arborescence, « Actions » en pictogramme, volet d'arborescence 10 % plus étroit, pictogrammes élargir / réduire.
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon12.py
# Nécessite : pip install playwright  puis  playwright install chromium

import functools
import http.server
import os
import sys
import threading

from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WHITE, BRAND, CLEAR = "rgb(255, 255, 255)", "rgb(4, 59, 178)", "rgba(0, 0, 0, 0)"
results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (("  -> " + str(detail)) if (detail and not cond) else ""))


class QuietServer(http.server.ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        if isinstance(sys.exc_info()[1], ConnectionError):
            return
        super().handle_error(request, client_address)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def js(page, expr):
    return page.evaluate(expr)


def css(page, sel, prop):
    return js(page, "getComputedStyle(document.querySelector(%r))[%r]" % (sel, prop))


def start(browser, base, w, h, errors):
    ctx = browser.new_context(viewport={"width": w, "height": h})
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector(".furn-body[data-fit]")
    page.wait_for_timeout(200)
    return ctx, page


def scenario_header(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1000, errors)
    for sel in ("#app-back", "#search-toggle", "#app-settings"):
        check("en-tête | %s : fond transparent, pictogramme et cercle blancs" % sel,
              css(page, sel, "backgroundColor") == CLEAR and css(page, sel, "color") == WHITE and "255, 255, 255" in css(page, sel, "boxShadow"),
              (css(page, sel, "backgroundColor"), css(page, sel, "color"), css(page, sel, "boxShadow")))
    page.locator("#search-toggle").click()
    page.wait_for_selector("#search-input", state="visible")
    check("en-tête | loupe enfoncée : fond blanc, pictogramme bleu", css(page, "#search-toggle", "backgroundColor") == WHITE and css(page, "#search-toggle", "color") == BRAND)
    check("en-tête | l'engrenage reste transparent", css(page, "#app-settings", "backgroundColor") == CLEAR)
    page.locator("#search-toggle").click()
    page.mouse.move(500, 600)
    page.wait_for_timeout(250)
    check("en-tête | loupe relâchée : retour au transparent", css(page, "#search-toggle", "backgroundColor") == CLEAR and css(page, "#search-toggle", "color") == WHITE)
    page.click("#app-settings")
    page.wait_for_selector("#pane-detail .settings")
    check("en-tête | Réglages ouverts : fond blanc, engrenage bleu", css(page, "#app-settings", "backgroundColor") == WHITE and css(page, "#app-settings", "color") == BRAND)
    page.click("#app-settings")
    page.wait_for_selector("#pane-detail .furn-view")
    page.mouse.move(500, 600)
    page.wait_for_timeout(250)
    check("en-tête | Réglages refermés : retour au transparent", css(page, "#app-settings", "backgroundColor") == CLEAR)
    check("en-tête | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_icons(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1000, errors)
    tree = page.locator("#tree-toggle svg")
    check("arborescence | pictogramme : 3 rectangles (père, deux fils alignés) et un tracé de liaison",
          tree.locator("rect").count() == 3 and tree.locator("path").count() == 1 and tree.locator("path").get_attribute("d") == "M6 7v12M6 12h6M6 19h6")
    xs = js(page, "Array.from(document.querySelectorAll('#tree-toggle rect')).map(function(r){return r.getAttribute('x');})")
    check("arborescence | les deux fils sont alignés verticalement sous le père (même x, décalés à droite)", xs == ["3", "12", "12"], xs)
    a = page.locator("#manage-toggle")
    check("actions | bouton-pictogramme rond, sans libellé visible", a.locator("svg").count() == 1 and a.get_attribute("aria-label") == "Actions" and a.bounding_box()["width"] >= 43 and a.bounding_box()["height"] >= 43 and "\u25BE" not in a.inner_text())
    check("actions | dans le groupe des commandes", page.locator(".detail-group").nth(1).locator("#manage-toggle").count() == 1)
    a.click()
    page.wait_for_selector(".ctx-menu")
    check("actions | menu ouvert, bouton enfoncé (couleur d'accent)", css(page, "#manage-toggle", "backgroundColor") != WHITE and page.locator("#manage-toggle.has-menu").count() == 1)
    page.keyboard.press("Escape")
    check("actions | menu refermé : bouton relâché", page.locator("#manage-toggle.has-menu").count() == 0)
    check("icônes | « actions », « expand-h » et « collapse-h » existent", all(js(page, "Rangement.ui.icons.has(%r)" % n) for n in ("actions", "expand-h", "collapse-h")))
    page.locator("#tree-grow").click()
    page.wait_for_function("document.documentElement.dataset.tree === 'wide'")
    page.wait_for_timeout(400)
    check("volet | agrandir : pictogramme « réduire » (chevron vers la gauche) dans l'arborescence large", "M18 9" in page.locator("#tree-shrink svg path").first.get_attribute("d"))
    check("volet | largeur du volet large ≈ 288 px (10 % de moins que 320)", 285 <= page.locator("#pane-tree").bounding_box()["width"] <= 290, page.locator("#pane-tree").bounding_box())
    page.locator("#tree-shrink").click()
    page.wait_for_function("document.documentElement.dataset.tree === 'mini'")
    page.wait_for_timeout(400)
    check("volet | rail : pictogramme « agrandir » (chevron vers la droite)", "M15 9" in page.locator("#tree-grow svg path").first.get_attribute("d") and page.locator("#tree-grow svg rect").count() == 4)
    check("volet | rail : largeur inchangée (76 px)", 70 <= page.locator("#pane-tree").bounding_box()["width"] <= 80)
    check("icônes | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_folded(browser, base):
    errors = []
    ctx, page = start(browser, base, 390, 844, errors)
    for sel in ("#app-back", "#search-toggle", "#app-settings"):
        check("replié | %s transparent, pictogramme blanc" % sel, css(page, sel, "backgroundColor") == CLEAR and css(page, sel, "color") == WHITE)
    b = page.locator("#manage-toggle").bounding_box()
    check("replié | « Actions » dans l'écran, ≥ 44 px", b["x"] >= 0 and b["x"] + b["width"] <= 391 and b["height"] >= 43, b)
    page.locator("#tree-toggle").click()
    page.wait_for_selector("#pane-tree", state="visible")
    check("replié | largeur du volet recouvrant inchangée (≤ 320 px, ≥ 300)", 300 <= page.locator("#pane-tree").bounding_box()["width"] <= 321, page.locator("#pane-tree").bounding_box())
    check("replié | pas de défilement horizontal", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()


def main():
    server = QuietServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=ROOT))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        scenario_header(browser, base)
        scenario_icons(browser, base)
        scenario_folded(browser, base)
        browser.close()
    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
