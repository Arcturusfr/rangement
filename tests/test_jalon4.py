# tests/test_jalon4.py — Application « Rangement »
# Version : V006
# Horodatage : 2026-10-24 13:10 (heure de Paris)
# Résumé : création — tests Playwright/Chromium du jalon 4 (recherche d'objets et d'emplacements).
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon4.py
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


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (("  -> " + str(detail)) if (detail and not cond) else ""))


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def start_server():
    handler = functools.partial(QuietHandler, directory=ROOT)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def new_page(browser, width, height, errors):
    ctx = browser.new_context(viewport={"width": width, "height": height})
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    return ctx, page


def load_demo(page):
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector("#pane-detail .list")


def search_box(page):
    return page.locator("#search-input")


def type_query(page, text):
    box = search_box(page)
    box.click()
    box.fill("")
    box.press_sequentially(text)


def results_text(page):
    return page.inner_text("#pane-detail .search-results")


def rows(page, section):
    sec = page.locator("#pane-detail .search-results .section", has=page.locator("h3", has_text=section))
    return sec.locator(".list-item")


def js(page, expr):
    return page.evaluate(expr)


def scenario_flow(browser, base, label):
    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    check(label + " | champ de recherche présent dès le départ", search_box(page).count() == 1 and page.is_visible("#search-input"))
    check(label + " | champ de recherche : étiquette accessible", page.get_by_label("Rechercher").count() == 1)
    load_demo(page)

    # Une seule entrée d'historique pour toute la saisie
    type_query(page, "piles")
    page.wait_for_function("document.querySelector('#pane-detail .detail-title').textContent === 'Recherche'")
    check(label + " | la saisie ouvre la recherche (#/s/piles)", page.evaluate("location.hash") == "#/s/piles", page.evaluate("location.hash"))
    r = rows(page, "Objets")
    check(label + " | « piles » : 1 objet trouvé", r.count() == 1 and "Piles neuves" in r.first.inner_text(), results_text(page))
    check(label + " | résultat : chemin complet affiché", "Séjour \u203a Meuble living \u203a Tiroir bas gauche" in r.first.inner_text(), r.first.inner_text())
    check(label + " | nombre de résultats annoncé", "1 résultat" in page.inner_text("#pane-detail .detail-meta"), page.inner_text("#pane-detail .detail-meta"))
    check(label + " | arborescence : rien de surligné pendant la recherche", page.locator("#pane-tree [aria-current='page']").count() == 0)

    # Casse et accents ignorés ; mots-clés ; plusieurs mots
    type_query(page, "ELECTRICITE")
    check(label + " | mot-clé trouvé sans accents ni casse", "Piles neuves" in results_text(page), results_text(page))
    type_query(page, "nature")
    check(label + " | mot-clé « nature » → Jumelles Nikon", rows(page, "Objets").count() == 1 and "Jumelles Nikon" in results_text(page))
    type_query(page, "jumelles optique")
    check(label + " | plusieurs mots : tous requis (trouvé)", rows(page, "Objets").count() == 1)
    type_query(page, "jumelles piles")
    check(label + " | plusieurs mots : tous requis (non trouvé)", "Aucun résultat" in results_text(page), results_text(page))
    type_query(page, "jumlles")
    check(label + " | pas de tolérance aux fautes de frappe", "Aucun résultat" in results_text(page))
    type_query(page, "NiKoN")
    check(label + " | casse ignorée dans le nom", "Jumelles Nikon" in results_text(page))
    type_query(page, "   ")
    check(label + " | requête vide : message d'aide", "Saisissez" in results_text(page) and page.locator("#pane-detail .list").count() == 0)

    # Recherche par chemin + emplacements
    type_query(page, "séjour")
    check(label + " | « séjour » : objets rangés dans le séjour", rows(page, "Objets").count() == 2, results_text(page))
    locs = rows(page, "Emplacements")
    check(label + " | « séjour » : emplacements trouvés (la pièce et son contenu)", locs.count() == 4, results_text(page))
    check(label + " | emplacement : nom propre en premier", "Séjour" in locs.first.locator(".list-title").inner_text())
    type_query(page, "tiroir bas")
    txt = results_text(page)
    check(label + " | « tiroir bas » : les 2 tiroirs et leurs 2 objets", rows(page, "Emplacements").count() == 2 and rows(page, "Objets").count() == 2 and "4 résultats" in page.inner_text("#pane-detail .detail-meta"), txt)

    # Ouvrir un résultat, puis Retour
    type_query(page, "jumelles")
    page.locator("#pane-detail .search-results .list-row", has_text="Jumelles Nikon").click()
    page.wait_for_selector("#pane-detail .item-detail")
    check(label + " | un objet trouvé ouvre sa fiche", page.inner_text("#pane-detail .detail-title") == "Jumelles Nikon")
    check(label + " | champ vidé hors recherche", search_box(page).input_value() == "")
    page.go_back()
    page.wait_for_selector("#pane-detail .search-results")
    check(label + " | Retour : résultats et champ restaurés", search_box(page).input_value() == "jumelles" and "Jumelles Nikon" in results_text(page), search_box(page).input_value())

    # Un emplacement trouvé ouvre l'emplacement
    type_query(page, "meuble living")
    rows(page, "Emplacements").locator(".list-row").first.click()
    page.wait_for_function("document.querySelector('#pane-detail .detail-title').textContent === 'Meuble living'")
    check(label + " | un emplacement trouvé ouvre l'emplacement", page.locator("#pane-tree [aria-current='page']").inner_text().strip() == "Meuble living")

    # Historique : toute la saisie = une entrée
    page.goto(base + "#/")
    page.wait_for_selector("#pane-detail .list")
    type_query(page, "pile")
    page.wait_for_selector("#pane-detail .search-results")
    page.go_back()
    page.wait_for_function("location.hash === '#/' || location.hash === ''")
    check(label + " | Retour après une saisie : revient à l'écran précédent", page.locator("#pane-detail .search-results").count() == 0 and search_box(page).input_value() == "")

    # Lien direct et rechargement
    page.goto(base + "#/s/piles")
    page.reload()
    page.wait_for_selector("#pane-detail .search-results")
    check(label + " | lien direct : champ prérempli et résultats", search_box(page).input_value() == "piles" and "Piles neuves" in results_text(page))

    # Touche Entrée : referme le clavier, garde les résultats
    search_box(page).click()
    search_box(page).press("Enter")
    check(label + " | Entrée : le champ perd le focus, résultats conservés", page.evaluate("document.activeElement.id") != "search-input" and "Piles neuves" in results_text(page))

    # Effacer le champ
    search_box(page).fill("")
    check(label + " | champ effacé : message d'aide", "Saisissez" in results_text(page))

    # Texte hostile
    type_query(page, "<b>x</b>")
    check(label + " | requête hostile affichée comme texte", page.locator("#pane-detail .search-results b").count() == 0 and "<b>x</b>" in results_text(page), results_text(page))
    page.goto(base + "#/s/%E0%A4%A")      # séquence % invalide : ne doit pas planter
    page.wait_for_selector("#pane-detail .search-results")
    check(label + " | adresse mal encodée tolérée", True)

    check(label + " | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_logic(browser, base):
    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    load_demo(page)
    S = "Rangement.features.search"

    check("logique | requête vide : aucun résultat", js(page, "(function(){var r=%s.search('  ');return r.items.length+r.locations.length;})()" % S) == 0)
    check("logique | mots normalisés", js(page, "%s.terms('  ÉLECTRICITÉ   Piles ')" % S) == ["electricite", "piles"])

    # Classement : nom > mot-clé > note > chemin
    loc = js(page, "Rangement.store.locations().filter(function(l){return l.name==='Grand tiroir du bas';})[0].id")
    F = "Rangement.features.items"
    js(page, "%s.create({name:'Alpha', locationId:'%s', tags:'zeta'})" % (F, loc))
    js(page, "%s.create({name:'Zeta', locationId:'%s'})" % (F, loc))
    js(page, "%s.create({name:'Beta', locationId:'%s', note:'voir zeta'})" % (F, loc))
    order = js(page, "%s.search('zeta').items.map(function(h){return h.item.name;})" % S)
    check("logique | classement : nom, puis mot-clé, puis note", order == ["Zeta", "Alpha", "Beta"], order)

    # Objet épuisé : grisé dans les résultats
    js(page, "%s.create({name:'Colle', locationId:'%s', quantity:'0'})" % (F, loc))
    page.goto(base + "#/s/colle")
    page.wait_for_selector("#pane-detail .search-results")
    check("logique | objet épuisé grisé dans les résultats", page.locator("#pane-detail .list-item--muted").count() == 1)

    # Texte hostile dans les données
    js(page, "%s.create({name:'<img src=x onerror=window.__xss=1>', locationId:'%s', tags:'<b>gras</b>'})" % (F, loc))
    type_query(page, "img")
    check("sécurité | objet hostile trouvé et affiché comme texte", "<img src=x" in results_text(page) and page.locator("#pane-detail .search-results img, #pane-detail .search-results b").count() == 0)
    check("sécurité | aucun script exécuté", page.evaluate("window.__xss") is None)

    # Les modifications se répercutent sur les résultats ouverts
    page.goto(base + "#/s/zeta")
    page.wait_for_selector("#pane-detail .search-results")
    n = rows(page, "Objets").count()
    js(page, "Rangement.features.items.remove(Rangement.features.search.search('zeta').items[0].item.id)")
    page.wait_for_function("document.querySelectorAll('#pane-detail .search-results .section')[0].querySelectorAll('.list-item').length === %d" % (n - 1))
    check("logique | suppression : résultats mis à jour", rows(page, "Objets").count() == n - 1, rows(page, "Objets").count())

    # Base vide : l'écran de démarrage prime
    check("logique | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_narrow(browser, base):
    errors = []
    ctx, page = new_page(browser, 390, 844, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    load_demo(page)
    check("replié | 1 volet", page.get_attribute("html", "data-panes") == "1")
    box = search_box(page).bounding_box()
    check("replié | champ de recherche ≥ 44 px et dans l'écran", box["height"] >= 44 and box["x"] >= 0 and box["x"] + box["width"] <= 390, box)
    type_query(page, "tiroir")
    page.wait_for_selector("#pane-detail .search-results")
    overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    check("replié | résultats : pas de défilement horizontal", overflow <= 0, overflow)
    check("replié | résultats visibles", page.is_visible("#pane-detail .search-results") and not page.is_visible("#pane-tree"))
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j4-replie-recherche.png"))
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()

    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    load_demo(page)
    type_query(page, "séjour")
    page.wait_for_selector("#pane-detail .search-results")
    check("déplié | arborescence et résultats côte à côte", page.is_visible("#pane-tree") and page.is_visible("#pane-detail .search-results"))
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j4-deplie-recherche.png"))
    check("déplié | aucune erreur console", not errors, errors)
    ctx.close()


def main():
    server = start_server()
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    file_url = "file://" + os.path.join(ROOT, "index.html")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        scenario_flow(browser, base, "http")
        scenario_flow(browser, file_url, "file")
        scenario_logic(browser, base)
        scenario_narrow(browser, base)
        browser.close()

    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
