# tests/test_jalon13.py — Application « Rangement »
# Version : V022a
# Horodatage : 2026-11-26 02:45 (heure de Paris)
# Résumé : jalon 13 (V022, V022a) : pas de surbrillance de focus, conteneur unique des boutons du détail, flèches circulaires, pictogramme bleu et grand dans le bouton du volet, nouvelle icône « Actions », pictogrammes des menus, marge sous le plan.
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon13.py
# Nécessite : pip install playwright  puis  playwright install chromium

import functools
import http.server
import os
import sys
import threading

from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BRAND, RED = "rgb(4, 59, 178)", "rgb(179, 38, 30)"
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


def box(page, sel):
    return page.locator(sel).bounding_box()


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


def longpress(page, locator, ms=650):
    b = locator.bounding_box()
    page.mouse.move(b["x"] + b["width"] / 2, b["y"] + b["height"] / 2)
    page.mouse.down()
    page.wait_for_timeout(ms)
    page.mouse.up()


def menu_items(page):
    return page.locator(".ctx-menu .ctx-item")


def all_have_icon(page):
    items = menu_items(page)
    return items.count() > 0 and all(items.nth(i).locator("svg").count() == 1 for i in range(items.count()))


def scenario_focus(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1000, errors)
    check("focus | pas de surbrillance de toucher sur les boutons et liens",
          css(page, "#search-toggle", "webkitTapHighlightColor") == "rgba(0, 0, 0, 0)" and css(page, "#app-settings", "webkitTapHighlightColor") == "rgba(0, 0, 0, 0)" and css(page, "#view-toggle", "webkitTapHighlightColor") == "rgba(0, 0, 0, 0)")
    page.locator("#search-toggle").click()
    page.wait_for_selector("#search-input", state="visible")
    page.locator("#search-toggle").click()
    check("focus | après un appui à la souris, aucun contour de focus sur le bouton de l'en-tête", css(page, "#search-toggle", "outlineStyle") == "none", css(page, "#search-toggle", "outlineStyle"))
    page.mouse.move(500, 700)
    page.wait_for_timeout(250)
    check("focus | le bouton relâché retrouve son fond transparent", css(page, "#search-toggle", "backgroundColor") == "rgba(0, 0, 0, 0)")
    page.locator("#search-toggle").focus()
    page.keyboard.press("Tab")
    page.keyboard.press("Shift+Tab")
    check("focus | le focus clavier reste visible (accessibilité)", js(page, "document.activeElement.id") == "search-toggle" and css(page, "#search-toggle", "outlineStyle") != "none", css(page, "#search-toggle", "outlineStyle"))
    check("focus | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_groups(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1000, errors)
    g = page.locator(".detail-group")
    t, c = g.nth(0).bounding_box(), g.nth(1).bounding_box()
    gap = c["y"] - (t["y"] + t["height"])
    check("conteneur | les deux groupes forment un seul bloc de même largeur, alignés", abs(t["x"] - c["x"]) <= 1 and abs(t["width"] - c["width"]) <= 1, (t, c))
    check("conteneur | séparation horizontale fine (1 à 4 px) et transparente", 1 <= gap <= 4, gap)
    page_bg = js(page, "getComputedStyle(document.querySelector('.detail-sticky')).backgroundColor")
    mid = js(page, """(function(){var a=document.querySelectorAll('.detail-group'); var r=a[0].getBoundingClientRect(); var q=a[1].getBoundingClientRect();
      var y=(r.bottom+q.top)/2, x=r.left+r.width/2; var e=document.elementFromPoint(x,y); return e ? e.className : null;})()""")
    check("conteneur | le filet ne contient aucun élément gris (on voit le fond de l'en-tête)", "detail-group" not in str(mid) and page_bg != "", mid)
    check("conteneur | arrondi à l'extérieur seulement",
          css(page, ".detail-group", "borderTopLeftRadius") == "12px" and css(page, ".detail-group", "borderBottomLeftRadius") == "2px", (css(page, ".detail-group", "borderTopLeftRadius"), css(page, ".detail-group", "borderBottomLeftRadius")))
    check("conteneur | même couleur de fond pour les deux groupes", js(page, "(function(){var a=document.querySelectorAll('.detail-group'); return getComputedStyle(a[0]).backgroundColor === getComputedStyle(a[1]).backgroundColor;})()"))
    up, down = box(page, "[aria-label='Niveau supérieur']"), box(page, "[aria-label='Niveau inférieur']")
    check("flèches | formes circulaires de 44 px", abs(up["width"] - up["height"]) <= 1 and up["width"] >= 43 and abs(down["width"] - down["height"]) <= 1, (up, down))
    check("flèches | rayon de bordure circulaire", float(css(page, "[aria-label='Niveau supérieur']", "borderTopLeftRadius").replace("px", "")) >= 22)
    # sans commandes (liste d'un niveau sans sous-emplacement) : le groupe seul est entièrement arrondi
    page.goto(base + "#/o/" + js(page, "Rangement.store.items()[0].id"))
    page.wait_for_selector("#pane-detail .item-detail")
    check("conteneur | fiche d'un objet : groupe d'arborescence et groupe de commandes présents", page.locator(".detail-group").count() == 2)
    check("conteneur | aucune erreur console", not errors, errors)
    ctx.close()
    errors = []
    ctx, page = start(browser, base, 390, 844, errors)
    for sel in ("[aria-label='Niveau supérieur']", "[aria-label='Niveau inférieur']"):
        b = box(page, sel)
        check("replié | %s circulaire, ≥ 44 px, dans l'écran" % sel, abs(b["width"] - b["height"]) <= 1 and b["width"] >= 43 and b["x"] + b["width"] <= 391, b)
    check("replié | pas de défilement horizontal", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_tree(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1000, errors)
    g = box(page, "#tree-grow")
    check("volet | rail : pictogramme « agrandir » bleu #043BB2, bouton non coloré", css(page, "#tree-grow", "color") == BRAND and css(page, "#tree-grow", "backgroundColor") == "rgba(0, 0, 0, 0)")
    sv = box(page, "#tree-grow svg")
    check("volet | rail : pictogramme grand (≥ 36 px), contenu dans le bouton", sv["width"] >= 36 and sv["height"] >= 36 and sv["height"] <= g["height"] + 1, (sv, g))
    check("volet | rail : bouton plus grand (≥ 60 px de large, ≥ 40 px de haut)", g["width"] >= 60 and g["height"] >= 40, g)
    page.locator("#tree-grow").click()
    page.wait_for_function("document.documentElement.dataset.tree === 'wide'")
    page.wait_for_timeout(300)
    s, r = box(page, "#tree-shrink"), box(page, ".tree-head .tree-root")
    check("volet | large : bouton « réduire » aussi haut que le cadre « Logement »", abs(s["height"] - r["height"]) <= 1 and s["height"] >= 40, (s, r))
    check("volet | large : pictogramme bleu #043BB2, bouton non coloré", css(page, "#tree-shrink", "color") == BRAND and css(page, "#tree-shrink", "backgroundColor") == "rgba(0, 0, 0, 0)")
    sv = box(page, "#tree-shrink svg")
    check("volet | large : pictogramme grand (≥ 36 px), contenu dans le bouton", sv["width"] >= 36 and sv["height"] <= s["height"] + 1 and sv["width"] <= s["width"] + 1, (sv, s))
    check("volet | large : bouton aligné verticalement sur « Logement »", abs(s["y"] - r["y"]) <= 1, (s, r))
    check("volet | pictogramme « réduire » conservé", "M18 9" in page.locator("#tree-shrink svg path").first.get_attribute("d"))
    check("volet | largeur du volet large inchangée (≈ 288 px)", 285 <= box(page, "#pane-tree")["width"] <= 290)
    check("volet | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_icons(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1100, errors)
    names = ["actions", "open", "add-place", "add-item", "grid", "move-to", "duplicate", "delete"]
    check("pictogrammes | les 8 nouveaux pictogrammes existent", all(js(page, "Rangement.ui.icons.has(%r)" % n) for n in names))
    a = page.locator("#manage-toggle svg")
    check("Actions | nouveau pictogramme : carré arrondi + éclair plein", a.locator("rect").count() == 1 and a.locator("rect").get_attribute("rx") == "3.5" and a.locator("path").get_attribute("fill") == "currentColor", a.inner_html())
    page.locator("#manage-toggle").click()
    page.wait_for_selector(".ctx-menu")
    check("menu Actions (logement) | pictogramme devant chaque commande", all_have_icon(page) and menu_items(page).all_inner_texts() == ["Ajouter une pièce", "Régler la grille…"], menu_items(page).all_inner_texts())
    page.keyboard.press("Escape")
    # menu « Actions » d'une pièce
    sej = js(page, "Rangement.store.locations().filter(function(l){return l.name==='Séjour';})[0].id")
    page.goto(base + "#/l/" + sej)
    page.wait_for_selector(".furn-body[data-fit]")
    page.locator("#manage-toggle").click()
    page.wait_for_selector(".ctx-menu")
    txt = menu_items(page).all_inner_texts()
    check("menu Actions (pièce) | 7 commandes, chacune avec son pictogramme", all_have_icon(page) and len(txt) == 7, txt)
    d = menu_items(page).last
    check("menu Actions | « Supprimer » : corbeille, texte et pictogramme rouges", d.inner_text() == "Supprimer" and js(page, "getComputedStyle(document.querySelector('.ctx-item--danger')).color") == RED and js(page, "getComputedStyle(document.querySelector('.ctx-item--danger svg')).color") == RED)
    check("menu Actions | pictogrammes de 20 px à gauche du libellé", js(page, "(function(){var i=document.querySelector('.ctx-item svg').getBoundingClientRect(); var b=document.querySelector('.ctx-item').getBoundingClientRect(); return i.width===20 && i.left < b.left + 24;})()"))
    page.keyboard.press("Escape")
    # menu d'une case (appui long)
    page.goto(base + "#/")
    page.wait_for_selector(".furn-body[data-fit]")
    longpress(page, page.locator(".furn-cell", has_text="Séjour"))
    page.wait_for_selector(".ctx-menu")
    check("menu d'une case | « Ouvrir » et les 7 autres commandes ont un pictogramme", all_have_icon(page) and menu_items(page).count() == 8 and menu_items(page).first.inner_text() == "Ouvrir")
    check("menu d'une case | « Ouvrir » : pictogramme « open »", menu_items(page).first.locator("svg path").first.get_attribute("d").startswith("M15 3h4"))
    page.locator(".ctx-menu").get_by_role("button", name="Ouvrir", exact=True).click()
    page.wait_for_function("document.querySelector('#pane-detail .detail-title').textContent === 'Séjour'")
    check("menu d'une case | « Ouvrir » fonctionne toujours", js(page, "location.hash") == "#/l/" + sej)
    # menu d'une case libre
    page.goto(base + "#/")
    page.wait_for_selector(".furn-body[data-fit]")
    longpress(page, page.locator(".furn-slot").first)
    page.wait_for_selector(".ctx-menu")
    check("menu d'une case libre | pictogramme devant chaque commande", all_have_icon(page) and menu_items(page).all_inner_texts() == ["Ajouter une pièce ici", "Régler la grille…"], menu_items(page).all_inner_texts())
    page.keyboard.press("Escape")
    # fiche d'un objet
    page.goto(base + "#/o/" + js(page, "Rangement.store.items().filter(function(i){return i.name==='Piles neuves';})[0].id"))
    page.wait_for_selector("#pane-detail .item-detail")
    page.locator("#manage-toggle").click()
    page.wait_for_selector(".ctx-menu")
    check("menu Actions (objet) | 4 commandes avec pictogramme", all_have_icon(page) and menu_items(page).count() == 4)
    page.keyboard.press("Escape")
    check("pictogrammes | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_bottom(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1100, errors)
    F = "Rangement.features.furniture"
    pb = float(css(page, "#pane-detail", "paddingBottom").replace("px", ""))
    check("marge | le volet de détail garde ≥ 40 px sous le contenu (24 + 16)", pb >= 40, pb)
    js(page, "%s.setGrid(%s.ROOT,{cols:7, rows:10})" % (F, F))
    page.wait_for_function("Rangement.store.plan() && Rangement.store.plan().cols === 7")
    page.wait_for_timeout(300)
    b = box(page, ".furn-body")
    check("marge | plan 7 × 10 : au moins 40 px libres sous le plan", b["y"] + b["height"] <= 1100 - 40 + 2, b)
    check("marge | plan 7 × 10 : la page ne défile toujours pas", js(page, "document.getElementById('pane-detail').scrollHeight - document.getElementById('pane-detail').clientHeight") <= 1)
    cs = js(page, "(function(){var c=document.querySelector('.furn-cell').getBoundingClientRect(); return c.width;})()")
    check("marge | cases toujours ≥ 47 px", cs >= 47, cs)
    check("marge | aucune erreur console", not errors, errors)
    ctx.close()


def main():
    server = QuietServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=ROOT))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        scenario_focus(browser, base)
        scenario_groups(browser, base)
        scenario_tree(browser, base)
        scenario_icons(browser, base)
        scenario_bottom(browser, base)
        browser.close()
    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
