# tests/test_jalon9_4.py — Application « Rangement »
# Version : V018b
# Horodatage : 2026-11-13 02:25 (heure de Paris)
# Résumé : V018b : le serveur de test ignore les connexions coupées par le navigateur (WinError 10053 sous Windows) ; parcours inchangés.
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon9_4.py
# Nécessite : pip install playwright  puis  playwright install chromium

import functools
import http.server
import os
import sys
import threading

from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (("  -> " + str(detail)) if (detail and not cond) else ""))


class QuietServer(http.server.ThreadingHTTPServer):
    """Serveur de test : une connexion coupée par le navigateur en cours d'envoi (WinError 10053 sous Windows,
    changement de page, fermeture du contexte) n'est pas une erreur ; on n'affiche plus sa trace."""

    def handle_error(self, request, client_address):
        if isinstance(sys.exc_info()[1], ConnectionError):
            return
        super().handle_error(request, client_address)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def js(page, expr):
    return page.evaluate(expr)


def start(browser, base, w, h, errors):
    ctx = browser.new_context(viewport={"width": w, "height": h})     # volontairement sans réglages préalables : on teste les valeurs par défaut
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector("#pane-detail .furn-view")
    page.wait_for_selector(".furn-body[data-fit]")
    page.wait_for_timeout(200)
    return ctx, page


def loc_id(page, name):
    return js(page, "Rangement.store.locations().filter(function(l){return l.name===%r;})[0].id" % name)


def goto(page, base, name):
    page.goto(base + "#/l/" + loc_id(page, name))
    page.wait_for_function("document.querySelector('#pane-detail .detail-title') && document.querySelector('#pane-detail .detail-title').textContent === %r" % name)
    page.wait_for_timeout(150)


def label(page):
    return " ".join(page.locator("#view-toggle").inner_text().split())


def scenario_home(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1100, errors)
    check("accueil | l'application s'ouvre sur le plan du logement", page.locator(".furn-view").count() == 1 and js(page, "Rangement.ui.views.furniture.mode('plan')") == "graphic")
    check("accueil | le plan tient dans l'écran", page.locator(".furn-body").bounding_box()["y"] + page.locator(".furn-body").bounding_box()["height"] <= 1100 and js(page, "document.documentElement.scrollHeight - window.innerHeight") <= 1)
    check("accueil | arborescence en rail par défaut", page.get_attribute("html", "data-tree") == "mini" and page.locator("#pane-tree .tree-mini-item").count() == 4)
    sw = page.locator("#view-toggle")
    check("liste/plan | un seul bouton flottant, libellé = action (« ➔ Liste »)", sw.count() == 1 and label(page) == "\u2794 Liste" and page.locator(".view-switch").count() == 0)
    check("liste/plan | dans la zone flottante sous l'en-tête figé, ≥ 44 px", page.locator(".detail-sticky .float-zone #view-toggle").count() == 1 and sw.bounding_box()["height"] >= 43)
    z = page.locator("#plan-zoom")
    zb = z.bounding_box()
    check("agrandir | bouton flottant à icône SVG, sans texte, en haut à droite du plan", z.locator("svg").count() == 1 and z.inner_text().strip() == "" and z.get_attribute("aria-label") == "Agrandir" and zb["x"] + zb["width"] > 884 * 0.9 - 40 and zb["height"] >= 43, zb)
    check("agrandir | plus de bouton dans la barre du plan", page.locator(".furn-bar #plan-zoom").count() == 0)
    z.click()
    page.wait_for_function("document.querySelector('.furn-body') && document.querySelector('.furn-body').dataset.fit === 'real'")
    check("agrandir | taille réelle : icône et nom accessible inversés", page.locator("#plan-zoom").get_attribute("aria-label") == "Ajuster à l’écran" and page.locator("#plan-zoom").get_attribute("aria-pressed") == "true")
    page.locator("#plan-zoom").click()
    page.wait_for_function("document.querySelector('.furn-body') && document.querySelector('.furn-body').dataset.fit === 'fit'")
    check("agrandir | retour à l'affichage ajusté", page.locator("#plan-zoom").get_attribute("aria-label") == "Agrandir")
    sw.click()
    page.wait_for_selector("#pane-detail .list")
    check("liste/plan | bouton : passe à la liste, le libellé devient « ➔ Plan »", label(page) == "\u2794 Plan" and page.locator(".furn-view").count() == 0 and page.locator("#plan-zoom").count() == 0)
    first = page.locator("#pane-detail .list-item").first.bounding_box()
    sb = page.locator("#view-toggle").bounding_box()
    check("liste/plan | en liste, le bouton ne recouvre pas la première ligne", first["y"] >= sb["y"] + sb["height"] - 1, (first, sb))
    page.reload()
    page.wait_for_selector("#pane-detail .list")
    check("liste/plan | choix conservé après rechargement", label(page) == "\u2794 Plan")
    page.locator("#view-toggle").click()
    page.wait_for_selector(".furn-body[data-fit]")
    check("liste/plan | retour au plan", label(page) == "\u2794 Liste")
    check("accueil | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_levels(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1100, errors)
    goto(page, base, "Séjour")
    check("pièce | plan par défaut, mêmes boutons flottants", page.locator(".furn-view").count() == 1 and label(page) == "\u2794 Liste" and page.locator("#plan-zoom").count() == 1)
    goto(page, base, "Meuble living")
    check("meuble | vue graphique par défaut, bouton Liste, pas d'Agrandir", page.locator(".furn-view").count() == 1 and label(page) == "\u2794 Liste" and page.locator("#plan-zoom").count() == 0)
    page.locator("#view-toggle").click()
    page.wait_for_selector("#pane-detail .list")
    check("meuble | en liste, le bouton propose « ➔ Vue graphique »", label(page) == "\u2794 Vue graphique")
    goto(page, base, "Tiroir bas gauche")
    check("niveau sans sous-emplacement | pas de bouton flottant", page.locator("#view-toggle").count() == 0)
    check("niveaux | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_tree(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1100, errors)
    c = page.locator("#tree-cycle")
    check("arbo | bouton d'en-tête visible, état annoncé", c.is_visible() and "réduite" in c.get_attribute("aria-label"))
    w_mini = page.locator("#pane-detail").bounding_box()["width"]
    c.click()
    page.wait_for_function("document.documentElement.dataset.tree === 'hidden'")
    page.wait_for_timeout(250)
    check("arbo | 2e appui : volet masqué, détail sur toute la largeur", not page.is_visible("#pane-tree") and page.locator("#pane-detail").bounding_box()["width"] > w_mini + 60 and "masquée" in c.get_attribute("aria-label"))
    page.reload()
    page.wait_for_selector("#pane-detail .furn-view")
    check("arbo | état masqué conservé après rechargement", page.get_attribute("html", "data-tree") == "hidden" and not page.is_visible("#pane-tree"))
    page.locator("#tree-cycle").click()
    page.wait_for_function("document.documentElement.dataset.tree === 'wide'")
    check("arbo | 3e appui : arborescence large avec libellés", page.locator("#pane-tree .tree-link").count() == 3 + 5 and page.is_visible("#pane-tree"))
    page.locator("#tree-cycle").click()
    page.wait_for_function("document.documentElement.dataset.tree === 'mini'")
    check("arbo | 4e appui : retour au rail", page.locator("#pane-tree .tree-mini-item").count() == 4)
    page.locator("#tree-grow").click()
    page.wait_for_function("document.documentElement.dataset.tree === 'wide'")
    check("arbo | les boutons « » du volet fonctionnent toujours", page.locator("#pane-tree .tree-link").count() == 8)
    check("arbo | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_narrow(browser, base):
    errors = []
    ctx, page = start(browser, base, 390, 844, errors)
    check("replié | bouton d'arborescence masqué (un seul volet)", not page.is_visible("#tree-cycle"))
    for sel in ("#view-toggle", "#plan-zoom"):
        b = page.locator(sel).bounding_box()
        check("replié | %s ≥ 44 px et dans l'écran" % sel, b["height"] >= 43 and b["x"] >= 0 and b["x"] + b["width"] <= 391, b)
    check("replié | pas de défilement horizontal", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    check("replié | plan dans l'écran", page.locator(".furn-body").bounding_box()["x"] >= 0 and page.locator(".furn-body").bounding_box()["x"] + page.locator(".furn-body").bounding_box()["width"] <= 391)
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()


def main():
    server = QuietServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=ROOT))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        scenario_home(browser, base)
        scenario_levels(browser, base)
        scenario_tree(browser, base)
        scenario_narrow(browser, base)
        browser.close()
    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
