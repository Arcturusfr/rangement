# tests/test_jalon9.py — Application « Rangement »
# Version : V014
# Horodatage : 2026-11-02 22:47 (heure de Paris)
# Résumé : création — tests Playwright/Chromium du jalon 9, étape 1 (plan ajusté à l'écran, bouton Agrandir, tuiles compactes, plan d'une pièce).
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon9.py
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


def settle(page, mode="fit"):
    page.wait_for_function("document.querySelector('.furn-body').dataset.fit === %r" % mode)
    page.wait_for_timeout(120)


def body(page):
    return page.locator(".furn-body").bounding_box()


def cell_size(page):
    return js(page, "(function(){var c=document.querySelector('.furn-body .furn-cell').getBoundingClientRect(); return [c.width, c.height];})()")


def inside(page):
    return js(page, """(function(){var b=document.querySelector('.furn-body').getBoundingClientRect(); var bad=[];
      document.querySelectorAll('.furn-body .furn-cell').forEach(function(c){var r=c.getBoundingClientRect();
        if(r.left<b.left-1||r.right>b.right+1||r.top<b.top-1||r.bottom>b.bottom+1){bad.push('case '+c.textContent.slice(0,20));}
        c.querySelectorAll('.furn-name').forEach(function(n){var q=n.getBoundingClientRect();
          if(q.left<r.left-1||q.right>r.right+1||q.bottom>r.bottom+1||q.top<r.top-1){bad.push('libellé '+n.textContent.slice(0,20));}});});
      return bad;})()""")


def frame_scrolls(page):
    return js(page, "(function(){var f=document.querySelector('.furn-frame--plan'); return f.scrollWidth > f.clientWidth + 1;})()")


def scenario_fit(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1100, errors)
    js(page, "%s.setGrid(%s.ROOT,{cols:7, rows:10})" % (F, F))
    plan(page)
    settle(page)
    check("ajusté | 7 × 10 : le plan tient en largeur, sans défilement", not frame_scrolls(page) and js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    w, h = cell_size(page)
    check("ajusté | cases carrées", abs(w - h) <= 2, (w, h))
    b = body(page)
    check("ajusté | cadre dans le volet de détail", b["x"] >= 0 and b["x"] + b["width"] <= 884 + 1, b)
    check("ajusté | taille de case raisonnable (≥ 28 px)", w >= 28, w)
    check("ajusté | tout dans le cadre", inside(page) == [], inside(page))
    check("ajusté | attribut de mode exposé", page.locator(".furn-body").get_attribute("data-fit") == "fit")
    bottom = b["y"] + b["height"]
    check("ajusté | tient en hauteur ou cases au plus bas à 48 px", bottom <= 1100 + 1 or w <= 49, (bottom, w))

    # redimensionnement : écran replié
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_function("document.documentElement.dataset.panes === '1'")
    page.wait_for_timeout(300)
    b2 = body(page)
    check("ajusté | écran replié : toujours sans défilement du cadre", not frame_scrolls(page) and b2["x"] >= 0 and b2["x"] + b2["width"] <= 391, b2)
    w2, h2 = cell_size(page)
    check("ajusté | écran replié : cases plus petites, toujours carrées", w2 < w and abs(w2 - h2) <= 2, (w, w2, h2))
    check("ajusté | écran replié : tuiles compactes", js(page, "document.querySelector('.furn-body').classList.contains('furn-compact')"))
    check("ajusté | tuiles compactes : le mot « objets » et le niveau sont masqués", js(page, "getComputedStyle(document.querySelector('.furn-count-word')).display") == "none")
    check("ajusté | écran replié : tout dans le cadre", inside(page) == [], inside(page))
    page.set_viewport_size({"width": 884, "height": 1100})
    page.wait_for_function("document.documentElement.dataset.panes === '2'")
    page.wait_for_timeout(300)
    w3, _ = cell_size(page)
    check("ajusté | retour à l'écran déplié : cases agrandies de nouveau", w3 > w2, (w2, w3))

    # taille réelle
    page.get_by_role("button", name="Agrandir").click()
    settle(page, "real")
    check("réel | bouton enfoncé et libellé inversé", page.locator("#plan-zoom").get_attribute("aria-pressed") == "true" and page.locator("#plan-zoom").inner_text() == "Ajuster à l’écran")
    wr, hr = cell_size(page)
    check("réel | cases d'au moins 72 px, le cadre défile", wr >= 71 and frame_scrolls(page), (wr, hr))
    check("réel | pas de tuiles compactes", not js(page, "document.querySelector('.furn-body').classList.contains('furn-compact')"))
    check("réel | la page ne défile pas horizontalement", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    check("réel | tout dans le cadre", inside(page) == [], inside(page))
    page.reload()
    page.wait_for_selector(".furn-body[data-fit]")
    settle(page, "real")
    check("réel | choix conservé après rechargement", page.locator("#plan-zoom").get_attribute("aria-pressed") == "true")
    page.get_by_role("button", name="Ajuster à l’écran").click()
    settle(page)
    check("réel | retour à l'affichage ajusté", not frame_scrolls(page) and page.locator("#plan-zoom").get_attribute("aria-pressed") == "false")
    check("ajusté | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_height(browser, base):
    """La barre d'actions qui se replie rend de la hauteur au plan."""
    errors = []
    ctx, page = start(browser, base, 884, 700, errors)
    js(page, "%s.setGrid(%s.ROOT,{cols:3, rows:10})" % (F, F))
    plan(page)
    settle(page)
    w1, _ = cell_size(page)
    page.locator("#manage-toggle").click()
    page.wait_for_timeout(500)
    w2, _ = cell_size(page)
    check("hauteur | replier « Actions » libère de la place : cases plus grandes", w2 >= w1, (w1, w2))
    check("hauteur | cases jamais sous 48 px à cause de la hauteur", w1 >= 47 and w2 >= 47, (w1, w2))
    page.locator("#manage-toggle").click()
    page.wait_for_timeout(500)
    check("hauteur | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_editing(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1100, errors)
    plan(page)
    settle(page)
    page.get_by_role("button", name="Ajuster le plan").click()
    page.locator(".furn-cell", has_text="Séjour").locator(".furn-open").click()
    page.wait_for_selector(".furn-sel")
    page.wait_for_timeout(200)
    check("ajusté | avec la sélection, le plan et les pavés de flèches tiennent dans l'écran", js(page, "(function(){var s=document.querySelector('.furn-sel').getBoundingClientRect(); return s.bottom <= window.innerHeight + 1;})()") and inside(page) == [])
    check("ajusté | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_room(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1100, errors)
    sej = js(page, "Rangement.store.locations().filter(function(l){return l.name==='Séjour';})[0].id")
    page.goto(base + "#/l/" + sej)
    page.wait_for_function("document.querySelector('#pane-detail .detail-title').textContent === 'Séjour'")
    check("pièce | commutateur Liste / Plan sur une pièce", page.get_by_role("button", name="Plan", exact=True).count() == 1 and page.get_by_role("button", name="Liste", exact=True).get_attribute("aria-pressed") == "true")
    check("pièce | liste par défaut inchangée", "Meuble living" in page.inner_text("#pane-detail .list"))
    page.get_by_role("button", name="Plan", exact=True).click()
    page.wait_for_selector(".furn-body[data-fit]")
    settle(page)
    names = page.locator(".furn-cell .furn-name").all_inner_texts()
    check("pièce | les meubles de la pièce sont dessinés", names == ["Meuble living"], names)
    cap = page.inner_text(".furn-caption")
    check("pièce | niveau rappelé", "Niveau 1" in cap and "Pièce" in cap and "Séjour" in cap and "niveau 2" in cap, cap)
    w, h = cell_size(page)
    check("pièce | cases carrées, ajustées à l'écran", abs(w - h) <= 2 and not frame_scrolls(page), (w, h))
    check("pièce | pas de bandes, de pieds ni de proportions", page.locator(".furn-band, .furn-feet").count() == 0)
    # le choix Liste / Plan est commun au logement et aux pièces
    page.goto(base + "#/")
    page.wait_for_selector(".furn-body[data-fit]")
    check("pièce | le choix du plan est commun au logement et aux pièces", page.get_by_role("button", name="Plan", exact=True).get_attribute("aria-pressed") == "true")
    page.goto(base + "#/l/" + sej)
    page.wait_for_selector(".furn-body[data-fit]")
    page.get_by_role("button", name="Ajuster le plan").click()
    check("pièce | ajustement direct : colonnes et lignes seulement", page.get_by_label("Colonnes").count() == 1 and page.get_by_label("Dessus").count() == 0 and page.get_by_label("Proportions").count() == 0)
    before = js(page, "Rangement.store.getLocation('%s').geometry" % sej) or {}
    page.get_by_label("Colonnes").select_option("3")
    page.wait_for_function("Rangement.features.furniture.get('%s').cols === 3" % sej)
    page.get_by_label("Lignes").select_option("2")
    page.wait_for_function("Rangement.features.furniture.get('%s').rows === 2" % sej)
    g = js(page, "Rangement.store.getLocation('%s').geometry" % sej)
    check("pièce | grille de la pièce enregistrée sans toucher à sa place dans le logement", g["cols"] == 3 and g["rows"] == 2 and g.get("top") == 0 and g.get("bottom") == 0 and all(g.get(k) == before.get(k) for k in before), (before, g))
    mid = page.locator(".furn-cell", has_text="Meuble living")
    mid.locator(".furn-open").click()
    page.wait_for_selector(".furn-sel")
    page.get_by_role("button", name="Largeur +", exact=True).click()
    page.wait_for_function("Rangement.store.locations().filter(function(l){return l.name==='Meuble living';})[0].geometry.w === 2")
    check("pièce | le meuble se redimensionne dans le plan de la pièce", True)
    check("pièce | données valides", js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok"))
    # un meuble, lui, garde sa vue d'origine
    mv = js(page, "Rangement.store.locations().filter(function(l){return l.name==='Meuble living';})[0].id")
    page.goto(base + "#/l/" + mv)
    page.wait_for_function("document.querySelector('#pane-detail .detail-title').textContent === 'Meuble living'")
    check("pièce | un meuble garde son commutateur « Vue graphique »", page.get_by_role("button", name="Vue graphique", exact=True).count() == 1 and page.get_by_role("button", name="Plan", exact=True).count() == 0)
    check("pièce | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_misc(browser, base):
    errors = []
    ctx, page = start(browser, base, 390, 844, errors)
    plan(page)
    settle(page)
    check("replié | bouton Agrandir ≥ 44 px et dans l'écran", all(b["height"] >= 44 and b["x"] >= 0 and b["x"] + b["width"] <= 390 for b in [page.locator("#plan-zoom").bounding_box()]))
    check("replié | plan ajusté sans défilement", not frame_scrolls(page) and js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    js(page, "Rangement.features.locations.create({name:'<img src=x onerror=window.__xss=1>', kind:'piece'})")
    page.wait_for_timeout(200)
    check("sécurité | nom hostile : texte brut dans une tuile compacte", page.locator(".furn-view img").count() == 0 and page.evaluate("window.__xss") is None)
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j9-replie-plan.png"), full_page=True)
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()


def main():
    server = start_server()
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        scenario_fit(browser, base)
        scenario_height(browser, base)
        scenario_editing(browser, base)
        scenario_room(browser, base)
        scenario_misc(browser, base)
        browser.close()
    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
