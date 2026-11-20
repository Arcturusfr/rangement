# tests/test_jalon11.py — Application « Rangement »
# Version : V020
# Horodatage : 2026-11-20 22:57 (heure de Paris)
# Résumé : jalon 11 (V020) : couleur #043BB2, recherche masquée + loupe, Réglages en pictogramme, groupes de boutons, aide « ? », cases libres invisibles (appui long = case la plus proche), volet d'arborescence.
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon11.py
# Nécessite : pip install playwright  puis  playwright install chromium

import functools
import http.server
import os
import sys
import threading

from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BRAND = "rgb(4, 59, 178)"
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


def start(browser, base, w, h, errors):
    ctx = browser.new_context(viewport={"width": w, "height": h})     # sans réglage préalable : valeurs par défaut
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


def longpress_at(page, x, y, ms=650):
    page.mouse.move(x, y)
    page.mouse.down()
    page.wait_for_timeout(ms)
    page.mouse.up()


def box(page, sel):
    return page.locator(sel).bounding_box()


def css(page, sel, prop, pseudo=None):
    return js(page, "getComputedStyle(document.querySelector(%r)%s)[%r]" % (sel, (", %r" % pseudo) if pseudo else "", prop))


def scenario_header(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1000, errors)
    check("couleur | bandeau d'en-tête de l'application en #043BB2", css(page, ".app-top", "backgroundColor") == BRAND, css(page, ".app-top", "backgroundColor"))
    check("couleur | niveau 0 : cadre du plan du logement", css(page, ".furn-body", "borderTopColor") == BRAND, css(page, ".furn-body", "borderTopColor"))
    check("couleur | niveau 0 : titre « Logement »", css(page, ".detail-title", "color") == BRAND)
    check("couleur | niveau 0 : pastille de la racine dans le rail", css(page, "#pane-tree .tree-mini-item .mini-dot", "borderTopColor") == BRAND or css(page, "#pane-tree .tree-mini-item .mini-dot", "backgroundColor") == BRAND)
    check("couleur | ancienne couleur sombre abandonnée pour le bandeau", css(page, ".app-top", "backgroundColor") != "rgb(22, 34, 42)")
    check("manifeste | couleur du thème alignée", js(page, "document.querySelector('meta[name=theme-color]').content") == "#043BB2")

    check("Réglages | engrenage seul, nom accessible conservé", page.locator("#app-settings svg").count() == 1 and page.get_attribute("#app-settings", "aria-label").startswith("Réglages") and box(page, "#app-settings")["width"] <= 46)
    check("Arborescence | plus de libellé dans l'en-tête de l'application", "Arborescence" not in page.inner_text(".app-top") and page.locator("#tree-cycle").count() == 0)

    # recherche masquée
    sb = page.locator("#search-toggle")
    check("recherche | champ masqué par défaut, loupe à gauche de l'engrenage", not page.is_visible("#search-input") and sb.locator("svg").count() == 1 and box(page, "#search-toggle")["x"] < box(page, "#app-settings")["x"] and sb.get_attribute("aria-expanded") == "false")
    sb.click()
    check("recherche | la loupe affiche le champ et lui donne le focus", page.is_visible("#search-input") and js(page, "document.activeElement.id") == "search-input" and page.locator("#search-toggle").get_attribute("aria-expanded") == "true")
    page.fill("#search-input", "piles")
    page.wait_for_selector("#pane-detail .search-results")
    check("recherche | la saisie lance la recherche", "Piles neuves" in page.inner_text("#pane-detail .search-results"))
    page.locator("#search-toggle").click()
    page.wait_for_selector("#pane-detail .furn-view")
    check("recherche | refermer le champ pendant une recherche revient à l'écran précédent", not page.is_visible("#search-input") and js(page, "location.hash") in ("#/", ""))
    page.goto(base + "#/s/piles")
    page.reload()
    page.wait_for_selector("#pane-detail .search-results")
    check("recherche | un lien de recherche affiche le champ, prérempli", page.is_visible("#search-input") and page.input_value("#search-input") == "piles")
    page.goto(base + "#/")

    # Retour dans l'en-tête
    check("Retour | pictogramme dans l'en-tête, à gauche du nom, indépendant de la recherche", page.locator("#app-back svg").count() == 1 and box(page, "#app-back")["x"] < box(page, ".app-name")["x"])
    check("Retour | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_groups(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1000, errors)
    g = page.locator(".detail-group")
    check("groupes | deux groupes de boutons dans l'en-tête du détail", g.count() == 2, g.count())
    tree, cmd = g.nth(0), g.nth(1)
    check("groupes | arborescence : afficher/masquer + flèches de niveau", tree.locator("#tree-toggle").count() == 1 and tree.locator("[aria-label='Niveau supérieur']").count() == 1 and tree.locator("[aria-label='Niveau inférieur']").count() == 1 and tree.locator("#manage-toggle").count() == 0)
    check("groupes | commandes : Actions + Liste/Plan + Agrandir + Modifier", all(cmd.locator(s).count() == 1 for s in ("#manage-toggle", "#view-toggle", "#plan-zoom", "#plan-edit")) and cmd.locator("#tree-toggle").count() == 0)
    bt, bc = tree.bounding_box(), cmd.bounding_box()
    check("groupes | groupes distincts, alignés à droite (arborescence au-dessus des commandes)", bc["y"] >= bt["y"] + bt["height"] - 1 and abs((bt["x"] + bt["width"]) - (bc["x"] + bc["width"])) <= 2, (bt, bc))
    check("groupes | hauteur de l'en-tête du détail ≤ 112 px", box(page, ".detail-sticky")["height"] <= 112, box(page, ".detail-sticky"))
    page.get_by_role("button", name="Liste", exact=True).click()
    page.wait_for_selector("#pane-detail .list")
    check("groupes | en liste : « Actions » et Liste/Plan seuls dans le groupe des commandes", page.locator(".detail-group").nth(1).locator("#plan-edit").count() == 0 and page.locator(".detail-group").nth(1).locator("#manage-toggle").count() == 1)
    check("groupes | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_slots_and_help(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1000, errors)
    F = "Rangement.features.furniture"
    js(page, "%s.setGrid(%s.ROOT,{cols:3, rows:3})" % (F, F))
    page.wait_for_function("Rangement.store.plan() && Rangement.store.plan().cols === 3")
    page.wait_for_timeout(300)
    check("consultation | les cases libres existent mais sont invisibles", page.locator(".furn-slot").count() == 6 and css(page, ".furn-slot", "borderTopColor") == "rgba(0, 0, 0, 0)", css(page, ".furn-slot", "borderTopColor"))
    check("consultation | aucun texte d'explication sous le plan", page.locator(".furn-view .hint").count() == 0 and page.locator("#plan-help").count() == 0)
    body = box(page, ".furn-body")
    rows = [box(page, ".furn-slot >> nth=%d" % i) for i in range(6)]
    lowest = max(r["y"] + r["height"] / 2 for r in rows)
    # appui long dans la marge gauche du cadre, à la hauteur de la 3e ligne : la case libre la plus proche (colonne 1, ligne 3)
    longpress_at(page, body["x"] + 3, lowest)
    page.wait_for_selector(".ctx-menu")
    txt = page.locator(".ctx-menu").inner_text()
    check("consultation | un appui long hors case choisit la case libre la plus proche et ouvre son menu", "Case libre" in txt and "colonne 1, ligne 3" in txt and "Ajouter une pièce ici" in txt, txt)
    page.keyboard.press("Escape")
    # appui long près du coin bas droit
    longpress_at(page, body["x"] + body["width"] - 3, body["y"] + body["height"] - 3)
    page.wait_for_selector(".ctx-menu")
    check("consultation | coin bas droit : colonne 3, ligne 3", "colonne 3, ligne 3" in page.locator(".ctx-menu").inner_text())
    page.keyboard.press("Escape")
    # un appui long sur une case existante garde son menu
    c = box(page, ".furn-cell >> nth=0")
    longpress_at(page, c["x"] + c["width"] / 2, c["y"] + c["height"] / 2)
    page.wait_for_selector(".ctx-menu")
    check("consultation | un appui long sur une case ouvre le menu de la case", page.locator(".ctx-menu .ctx-item").first.inner_text() == "Ouvrir")
    page.keyboard.press("Escape")
    # création à la case la plus proche
    longpress_at(page, body["x"] + 3, lowest)
    page.wait_for_selector(".ctx-menu")
    page.locator(".ctx-menu").get_by_role("button", name="Ajouter une pièce ici", exact=True).click()
    d = page.locator("dialog.dialog[open]")
    d.get_by_label("Nom").fill("Garage")
    d.get_by_role("button", name="Ajouter", exact=True).click()
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    g = js(page, "Rangement.store.locations().filter(function(l){return l.name==='Garage';})[0].geometry")
    check("consultation | la pièce est créée à la case choisie (colonne 1, ligne 3)", g["col"] == 0 and g["row"] == 2, g)

    # mode modification : cases visibles, aide dans une pop-up
    page.locator("#plan-edit").click()
    page.wait_for_selector(".furn-view[data-editing='true']")
    check("modification | les cases libres sont dessinées", css(page, ".furn-slot", "borderTopColor") != "rgba(0, 0, 0, 0)")
    check("modification | le texte d'explication n'est plus affiché", page.locator(".furn-view .hint").count() == 0)
    h = page.locator("#plan-help")
    check("modification | bouton « ? » dans le groupe des commandes, à côté de « Modifier le plan »", h.count() == 1 and h.locator("svg").count() == 1 and page.locator(".detail-group").nth(1).locator("#plan-help").count() == 1)
    h.click()
    page.wait_for_selector(".bubble")
    check("modification | le « ? » ouvre l'explication dans une pop-up", "Touchez une case" in page.locator(".bubble").inner_text() and "appui long" in page.locator(".bubble").inner_text())
    page.keyboard.press("Escape")
    check("modification | Échap referme la pop-up", page.locator(".bubble").count() == 0)
    page.locator("#plan-edit").click()
    page.wait_for_selector(".furn-view[data-editing='false']")
    check("modification | le « ? » disparaît hors modification", page.locator("#plan-help").count() == 0)
    check("consultation | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_tree_buttons(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1000, errors)
    check("rail | flèche de dépliement devant la racine", page.locator("#pane-tree .tree-head--mini #tree-root-toggle").count() == 1)
    ctx.close()
    errors = []
    ctx, page = start(browser, base, 390, 844, errors)
    t = page.locator("#tree-toggle")
    check("replié | le bouton d'arborescence est dans le groupe d'arborescence, avec ▲ ▼", t.is_visible() and page.locator(".detail-group").nth(0).locator("#tree-toggle").count() == 1)
    check("replié | le volet est masqué au départ", not page.is_visible("#pane-tree") and page.get_attribute("html", "data-tree-open") == "false")
    t.click()
    page.wait_for_selector("#pane-tree", state="visible")
    check("replié | le volet recouvre l'écran (largeur ≤ 85 %), libellés visibles, sans rail", box(page, "#pane-tree")["width"] <= 390 * 0.86 and page.locator("#pane-tree .tree-link").count() == 3 + 5 and page.locator("#tree-grow").count() == 0)
    check("replié | le bouton est enfoncé quand le volet est affiché", page.locator("#tree-toggle").get_attribute("aria-pressed") == "true")
    page.locator("#tree-scrim").click(position={"x": 370, "y": 300})
    page.wait_for_selector("#pane-tree", state="hidden")
    check("replié | un appui à côté du volet (voile) le masque", not page.is_visible("#pane-tree") and page.locator("#tree-toggle").get_attribute("aria-pressed") == "false")
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
        scenario_groups(browser, base)
        scenario_slots_and_help(browser, base)
        scenario_tree_buttons(browser, base)
        browser.close()
    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
