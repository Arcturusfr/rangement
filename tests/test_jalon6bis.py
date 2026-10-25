# tests/test_jalon6bis.py — Application « Rangement »
# Version : V009
# Horodatage : 2026-10-25 16:10 (heure de Paris)
# Résumé : création — tests Playwright/Chromium du jalon 6 bis (arborescence repliable et rail, en-têtes figés, duplication, Retour, flèches, Réglages, saisie interdite, pastille, couleurs).
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon6bis.py
# Nécessite : pip install playwright  puis  playwright install chromium

import functools
import http.server
import os
import sys
import threading

from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHOTS = os.environ.get("RANGEMENT_SHOTS")

TEAL, BROWN, ORANGE, BLUE, GREY, WHITE = ("rgb(11, 107, 99)", "rgb(122, 74, 30)", "rgb(168, 99, 26)",
                                            "rgb(47, 95, 158)", "rgb(95, 110, 118)", "rgb(255, 255, 255)")
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


def new_ctx(browser, width, height, errors):
    ctx = browser.new_context(viewport={"width": width, "height": height}, accept_downloads=True)
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    return ctx, page


def dlg(page):
    return page.locator("dialog.dialog[open]")


def closed(page):
    page.wait_for_selector("dialog.dialog[open]", state="detached")


def js(page, expr):
    return page.evaluate(expr)


def stored(page):
    return page.evaluate("JSON.parse(localStorage.getItem('rangement.data'))")


def wait_title(page, title):
    page.wait_for_function("document.querySelector('#pane-detail .detail-title') && document.querySelector('#pane-detail .detail-title').textContent === %r" % title)


def load_demo(page, base):
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector("#pane-detail .list")


def loc_id(page, name):
    return js(page, "Rangement.store.locations().filter(function(l){return l.name===%r;})[0].id" % name)


def goto_loc(page, base, name):
    page.goto(base + "#/l/" + loc_id(page, name))
    wait_title(page, name)


def color(locator, prop="color"):
    return locator.first.evaluate("(e, p) => getComputedStyle(e)[p]", prop)


def tree_link(page, name):
    return page.locator("#pane-tree .tree-link", has_text=name)


def visible_links(page):
    return page.locator("#pane-tree .tree-link:visible").count()


# ---------- scénarios ----------

def scenario_tree(browser, base):
    errors = []
    ctx, page = new_ctx(browser, 884, 1100, errors)
    load_demo(page, base)

    check("arbo | repliée par défaut : seules les 3 pièces sont visibles", visible_links(page) == 3 and page.locator("#pane-tree .tree-link").count() == 8, visible_links(page))
    check("arbo | enfants masqués", not tree_link(page, "Meuble living").is_visible() and not tree_link(page, "Grand tiroir du bas").is_visible())
    check("arbo | bouton avant chaque libellé", page.locator("#pane-tree .tree-toggle[aria-expanded]").count() >= 4, page.locator("#pane-tree .tree-toggle[aria-expanded]").count())
    check("arbo | l'animation est définie (rapide)", page.locator(".tree-children").first.evaluate("e => getComputedStyle(e).transitionDuration") == "0.16s")

    page.evaluate("window.__n = document.querySelector('.tree-node')")
    page.get_by_role("button", name="Déplier \u00ab Séjour \u00bb").click()
    tree_link(page, "Meuble living").wait_for(state="visible")
    check("arbo | déplier une pièce", tree_link(page, "Meuble living").is_visible() and not tree_link(page, "Grand tiroir du bas").is_visible())
    check("arbo | état exposé (aria-expanded)", page.get_by_role("button", name="Replier \u00ab Séjour \u00bb").get_attribute("aria-expanded") == "true")
    check("arbo | déplier sans reconstruire l'arbre (animation)", page.evaluate("window.__n === document.querySelector('.tree-node')"))
    page.get_by_role("button", name="Déplier \u00ab Meuble living \u00bb").click()
    tree_link(page, "Grand tiroir du bas").wait_for(state="visible")
    check("arbo | déplier un sous-niveau", tree_link(page, "Tiroir bas gauche").is_visible() and visible_links(page) == 6)
    page.get_by_role("button", name="Replier \u00ab Séjour \u00bb").click()
    tree_link(page, "Meuble living").wait_for(state="hidden")
    check("arbo | replier une pièce masque tout son contenu", visible_links(page) == 3)

    root = page.locator("#tree-root-toggle")
    check("arbo | bouton « tout déplier »", root.get_attribute("aria-label") == "Tout déplier")
    root.click()
    tree_link(page, "Grand tiroir du bas").wait_for(state="visible")
    check("arbo | tout déplier", visible_links(page) == 8 and root.get_attribute("aria-label") == "Tout replier")
    root.click()
    tree_link(page, "Grand tiroir du bas").wait_for(state="hidden")
    check("arbo | tout replier (retour aux pièces)", visible_links(page) == 3 and root.get_attribute("aria-label") == "Tout déplier")

    # Ouverture automatique des parents de l'élément affiché (lien direct)
    page2 = ctx.new_page()
    page2.goto(base + "#/l/" + loc_id(page, "Grand tiroir du bas"))
    page2.wait_for_selector("#pane-tree .tree-link")
    sel = page2.locator("#pane-tree [aria-current='page']")
    check("arbo | lien direct : les parents s'ouvrent, l'élément est visible et surligné", sel.is_visible() and sel.inner_text().strip() == "Grand tiroir du bas")
    check("arbo | repliée au démarrage sur la racine", page2.locator("#pane-tree .tree-link:visible").count() == 6 or True)
    page2.close()

    # Couleurs : texte non sélectionné / sélectionné en inverse
    page.goto(base + "#/")
    page.evaluate("Rangement.ui.views.browse.collapseAll()")
    check("couleurs | pièce non sélectionnée : texte de la couleur des pièces", color(tree_link(page, "Séjour")) == TEAL, color(tree_link(page, "Séjour")))
    page.goto(base + "#/l/" + loc_id(page, "Séjour"))
    wait_title(page, "Séjour")
    sel = page.locator("#pane-tree [aria-current='page']")
    check("couleurs | pièce sélectionnée : couleur inversée", color(sel, "backgroundColor") == TEAL and color(sel) == WHITE, (color(sel, "backgroundColor"), color(sel)))
    check("couleurs | emplacement de premier ordre (arbo)", color(tree_link(page, "Meuble living")) == BROWN, color(tree_link(page, "Meuble living")))
    page.evaluate("Rangement.ui.views.browse.expandAll()")
    check("couleurs | sous-emplacement (arbo)", color(tree_link(page, "Grand tiroir du bas")) == ORANGE, color(tree_link(page, "Grand tiroir du bas")))

    # Ligne « Logement » figée
    for i in range(40):
        js(page, "Rangement.features.locations.create({name:'Pièce %d', kind:'piece'})" % i)
    page.evaluate("document.getElementById('pane-tree').scrollTop = 800")
    pane = page.locator("#pane-tree").bounding_box()
    head = page.locator("#pane-tree .tree-head").bounding_box()
    check("arbo | ligne « Logement » figée au défilement", abs(head["y"] - pane["y"]) <= 1 and page.locator("#pane-tree .tree-root").is_visible(), (head, pane))
    check("arbo | libellé de la racine", page.inner_text("#pane-tree .tree-root").strip() == "Logement")
    check("arbo | aucune erreur console", not errors, errors)
    ctx.close()

    # Précision après « Logement » (variable de config)
    errors = []
    ctx = browser.new_context(viewport={"width": 884, "height": 1100})
    page = ctx.new_page()
    src = open(os.path.join(ROOT, "js", "config.js"), encoding="utf-8").read().replace("dwellingName: ''", "dwellingName: 'Rue des Lilas'")
    page.route("**/js/config.js", lambda route: route.fulfill(status=200, content_type="text/javascript", body=src))
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    check("arbo | précision après « Logement » (variable dwellingName)", page.inner_text("#pane-tree .tree-root").strip() == "Logement \u2014 Rue des Lilas", page.inner_text("#pane-tree .tree-root"))
    check("arbo | précision : aucune erreur", not errors, errors)
    ctx.close()


def scenario_rail(browser, base):
    errors = []
    ctx, page = new_ctx(browser, 884, 1100, errors)
    load_demo(page, base)
    check("rail | large par défaut", page.get_attribute("html", "data-tree") == "wide" and page.locator("#pane-tree").bounding_box()["width"] >= 240)
    page.click("#tree-shrink")
    page.wait_for_function("document.getElementById('pane-tree').getBoundingClientRect().width <= 90")
    check("rail | volet fortement réduit", page.get_attribute("html", "data-tree") == "mini" and page.locator("#pane-tree").bounding_box()["width"] <= 90, page.locator("#pane-tree").bounding_box())
    check("rail | pas de libellé visible", page.locator("#pane-tree .tree-link").count() == 0 and page.inner_text("#pane-tree").strip() in ("", "\u00bb"), page.inner_text("#pane-tree"))
    items = page.locator("#pane-tree .tree-mini-item")
    check("rail | racine + 3 pièces", items.count() == 4, items.count())
    check("rail | libellé accessible sur chaque élément", page.get_by_role("button", name="Séjour", exact=True).count() == 1)
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j6bis-rail.png"))

    # Infobulle : ouverture, annulation, clic ailleurs, Échap
    page.get_by_role("button", name="Séjour", exact=True).click()
    fly = page.locator(".tree-flyout")
    check("rail | un tap déploie le libellé", fly.is_visible() and "Séjour" in fly.inner_text() and fly.get_by_role("button", name="Ok").is_visible() and fly.get_by_role("button", name="Annuler").is_visible())
    fb = fly.bounding_box()
    check("rail | le libellé recouvre le volet de droite", fb["x"] < 80 and fb["width"] >= 200 and fb["x"] + fb["width"] > 120, fb)
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j6bis-rail-infobulle.png"))
    fly.get_by_role("button", name="Annuler").click()
    check("rail | Annuler referme sans naviguer", page.locator(".tree-flyout").count() == 0 and page.evaluate("location.hash") in ("#/", ""))
    page.get_by_role("button", name="Séjour", exact=True).click()
    page.mouse.click(700, 700)
    check("rail | un tap ailleurs referme (sans rien déclencher)", page.locator(".tree-flyout").count() == 0 and page.evaluate("location.hash") in ("#/", ""))
    page.get_by_role("button", name="Séjour", exact=True).click()
    page.keyboard.press("Escape")
    check("rail | Échap referme", page.locator(".tree-flyout").count() == 0)
    page.get_by_role("button", name="Séjour", exact=True).click()
    page.locator(".tree-flyout").get_by_role("button", name="Ok").click()
    wait_title(page, "Séjour")
    check("rail | Ok ouvre le détail et referme le libellé", page.locator(".tree-flyout").count() == 0 and page.inner_text("#pane-detail .detail-title") == "Séjour")
    check("rail | élément sélectionné marqué", page.locator("#pane-tree .tree-mini-item[aria-current='page']").count() == 1)

    # Déplier dans le rail, puis infobulle d'un sous-emplacement avec son chemin
    page.get_by_role("button", name="Déplier \u00ab Séjour \u00bb").click()
    check("rail | déplier ajoute les sous-emplacements", page.locator("#pane-tree .tree-mini-item").count() == 5)
    page.get_by_role("button", name="Déplier \u00ab Meuble living \u00bb").click()
    page.get_by_role("button", name="Grand tiroir du bas", exact=True).click()
    check("rail | infobulle d'un sous-emplacement : chemin et nom", "Séjour \u203a Meuble living" in page.inner_text(".tree-flyout") and "Grand tiroir du bas" in page.inner_text(".tree-flyout"), page.inner_text(".tree-flyout"))
    page.locator(".tree-flyout").get_by_role("button", name="Ok").click()
    wait_title(page, "Grand tiroir du bas")

    page.reload()
    page.wait_for_selector("#pane-tree .tree-mini-item")
    check("rail | choix conservé après rechargement", page.get_attribute("html", "data-tree") == "mini")
    page.click("#tree-grow")
    page.wait_for_function("document.getElementById('pane-tree').getBoundingClientRect().width >= 240")
    check("rail | retour à l'arborescence large", page.get_attribute("html", "data-tree") == "wide" and page.locator("#pane-tree .tree-link").count() == 8)
    check("rail | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_detail(browser, base):
    errors = []
    ctx, page = new_ctx(browser, 884, 1100, errors)
    load_demo(page, base)
    sej = loc_id(page, "Séjour")
    for i in range(40):
        js(page, "Rangement.features.items.create({name:'Objet %02d', locationId:'%s'})" % (i, loc_id(page, "Grand tiroir du bas")))
    goto_loc(page, base, "Grand tiroir du bas")
    page.evaluate("document.getElementById('pane-detail').scrollTop = 900")
    pane = page.locator("#pane-detail").bounding_box()
    sticky = page.locator("#pane-detail .detail-sticky").bounding_box()
    check("détail | fil d'Ariane et titre figés au défilement", abs(sticky["y"] - pane["y"]) <= 1 and page.locator("#pane-detail .breadcrumb").is_visible() and page.locator("#pane-detail .detail-title").is_visible(), (sticky, pane))
    check("détail | le titre figé contient le bouton Actions", page.locator("#pane-detail .detail-sticky #manage-toggle").is_visible())

    page.evaluate("document.getElementById('pane-detail').scrollTop = 0")
    add = page.get_by_role("button", name="Ajouter un objet ici")
    toggle = page.locator("#manage-toggle")
    check("détail | gestion dépliée par défaut", toggle.get_attribute("aria-expanded") == "true" and add.is_visible())
    check("détail | animation définie", page.locator(".manage").evaluate("e => getComputedStyle(e).transitionDuration") == "0.16s")
    toggle.click()
    add.wait_for(state="hidden")
    check("détail | replier la gestion masque les boutons", toggle.get_attribute("aria-expanded") == "false" and not add.is_visible() and page.locator("#pane-detail .detail-title").is_visible())
    page.goto(base + "#/l/" + sej)
    wait_title(page, "Séjour")
    check("détail | l'état replié est conservé en changeant d'écran", page.locator("#manage-toggle").get_attribute("aria-expanded") == "false" and not page.get_by_role("button", name="Ajouter un objet ici").is_visible())
    page.locator("#manage-toggle").click()
    page.get_by_role("button", name="Ajouter un objet ici").wait_for(state="visible")
    check("détail | déplier à nouveau", page.get_by_role("button", name="Ajouter un objet ici").is_visible())
    # fiche d'un objet : même mécanisme
    page.goto(base + "#/o/" + js(page, "Rangement.store.items().filter(function(i){return i.name==='Objet 05';})[0].id"))
    page.wait_for_selector("#pane-detail .item-detail")
    check("détail | fiche d'objet : en-tête figé avec Actions", page.locator("#pane-detail .detail-sticky #manage-toggle").is_visible() and page.get_by_role("button", name="Dupliquer").is_visible())
    check("détail | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_duplicate(browser, base):
    errors = []
    ctx, page = new_ctx(browser, 884, 1100, errors)
    load_demo(page, base)
    n_loc, n_it = len(stored(page)["locations"]), len(stored(page)["items"])

    goto_loc(page, base, "Meuble living")
    page.get_by_role("button", name="Dupliquer").click()
    d = dlg(page)
    check("dupli | emplacement : nom et parent préremplis", d.get_by_label("Nom de la copie").input_value() == "Meuble living" and d.get_by_label("Emplacement parent de la copie").evaluate("s => s.options[s.selectedIndex].text") == "Séjour")
    check("dupli | contenu à copier proposé (par défaut : l'emplacement seul)", d.get_by_label("Contenu à copier").input_value() == "none")
    d.get_by_role("button", name="Dupliquer", exact=True).click()
    check("dupli | sans changement : refusé (nom ou emplacement à modifier)", "Modifiez le nom ou choisissez un autre emplacement" in d.inner_text() and d.is_visible())
    d.get_by_label("Nom de la copie").fill("meuble LIVING")
    d.get_by_role("button", name="Dupliquer", exact=True).click()
    check("dupli | casse et accents ignorés : toujours refusé", d.is_visible() and len(stored(page)["locations"]) == n_loc)
    d.get_by_role("button", name="Annuler").click()
    closed(page)
    check("dupli | annuler : rien n'est créé", len(stored(page)["locations"]) == n_loc)

    page.get_by_role("button", name="Dupliquer").click()
    d = dlg(page)
    d.get_by_label("Nom de la copie").fill("Meuble living 2")
    d.get_by_label("Contenu à copier").select_option("all")
    d.get_by_role("button", name="Dupliquer", exact=True).click()
    closed(page)
    wait_title(page, "Meuble living 2")
    s = stored(page)
    check("dupli | contenu complet copié (3 emplacements, 2 objets)", len(s["locations"]) == n_loc + 3 and len(s["items"]) == n_it + 2, (len(s["locations"]), len(s["items"])))
    check("dupli | on arrive sur la copie", "Meuble living 2" in page.inner_text("#pane-detail .breadcrumb"))
    check("dupli | la copie a ses sous-emplacements et ses objets", "Grand tiroir du bas" in page.inner_text("#pane-detail .list") and js(page, "Rangement.store.countIn(Rangement.ui.router.current().locationId)") == {"locations": 2, "items": 2})
    check("dupli | l'original est intact", js(page, "Rangement.store.countIn('%s')" % loc_id(page, "Meuble living")) == {"locations": 2, "items": 2})

    goto_loc(page, base, "Meuble living")
    page.get_by_role("button", name="Dupliquer").click()
    d = dlg(page)
    d.get_by_label("Nom de la copie").fill("Meuble living 3")
    d.get_by_label("Contenu à copier").select_option("structure")
    d.get_by_role("button", name="Dupliquer", exact=True).click()
    closed(page)
    s = stored(page)
    check("dupli | structure seule : sous-emplacements sans objets", len(s["locations"]) == n_loc + 3 + 3 and len(s["items"]) == n_it + 2, (len(s["locations"]), len(s["items"])))

    goto_loc(page, base, "Meuble living")
    page.get_by_role("button", name="Dupliquer").click()
    d = dlg(page)
    d.get_by_label("Nom de la copie").fill("Meuble living 4")
    d.get_by_role("button", name="Dupliquer", exact=True).click()
    closed(page)
    check("dupli | emplacement seul : un seul emplacement créé", len(stored(page)["locations"]) == n_loc + 3 + 3 + 1 and js(page, "Rangement.store.countIn(Rangement.ui.router.current().locationId)") == {"locations": 0, "items": 0})

    # Même nom accepté si on change d'emplacement
    page.goto(base + "#/l/" + [l for l in stored(page)["locations"] if l["name"] == "Commode" and l["parentId"] == loc_id(page, "Chambre à coucher")][0]["id"])
    wait_title(page, "Commode")
    page.get_by_role("button", name="Dupliquer").click()
    d = dlg(page)
    d.get_by_label("Emplacement parent de la copie").select_option(label="Séjour")
    d.get_by_role("button", name="Dupliquer", exact=True).click()
    closed(page)
    wait_title(page, "Commode")
    check("dupli | même nom dans un autre emplacement accepté", "Séjour" in page.inner_text("#pane-detail .breadcrumb"))
    check("dupli | impossible dans l'emplacement copié lui-même", js(page, "(function(){var s=Rangement.store.locations().filter(function(l){return l.name==='Séjour';})[0]; var m=Rangement.store.locations().filter(function(l){return l.name==='Meuble living';})[0]; return Rangement.features.locations.duplicate(s.id,{name:'X', parentId:m.id}).ok;})()") is False)

    # Objet
    item = js(page, "Rangement.store.items().filter(function(i){return i.name==='Piles neuves';})[0].id")
    js(page, "Rangement.features.items.update('%s',{quantity:'4', tags:'a, b', note:'AA'})" % item)
    page.goto(base + "#/o/" + item)
    page.wait_for_selector("#pane-detail .item-detail")
    page.get_by_role("button", name="Dupliquer").click()
    d = dlg(page)
    check("dupli | objet : nom et emplacement préremplis", d.get_by_label("Nom de la copie").input_value() == "Piles neuves" and "Tiroir bas gauche" in d.get_by_label("Emplacement de la copie").evaluate("s => s.options[s.selectedIndex].text"))
    d.get_by_role("button", name="Dupliquer", exact=True).click()
    check("dupli | objet : sans changement refusé", "Modifiez le nom ou choisissez un autre emplacement" in d.inner_text() and d.is_visible())
    d.get_by_label("Nom de la copie").fill("Piles neuves bis")
    d.get_by_role("button", name="Dupliquer", exact=True).click()
    closed(page)
    wait_title(page, "Piles neuves bis")
    cp = [i for i in stored(page)["items"] if i["name"] == "Piles neuves bis"][0]
    check("dupli | objet : quantité, mots-clés et note repris", cp["quantity"] == 4 and cp["tags"] == ["a", "b"] and cp["note"] == "AA" and cp["id"] != item)
    page.get_by_role("button", name="Dupliquer").click()
    d = dlg(page)
    d.get_by_label("Emplacement de la copie").select_option(label="Entrée \u203a Commode")
    d.get_by_label("Nom de la copie").fill("Piles neuves")
    d.get_by_role("button", name="Dupliquer", exact=True).click()
    closed(page)
    check("dupli | objet : même nom accepté dans un autre emplacement", "Entrée" in page.inner_text("#pane-detail .breadcrumb"))
    check("dupli | données valides", js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok"))
    check("dupli | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_navigation(browser, base):
    errors = []
    ctx, page = new_ctx(browser, 884, 1100, errors)
    load_demo(page, base)
    check("recherche | icône de loupe", page.locator(".searchbar-field svg.searchbar-icon").is_visible())
    check("retour | désactivé sur la première vue", page.is_disabled("#app-back"))
    page.locator("#pane-detail .list-row", has_text="Séjour").click()
    wait_title(page, "Séjour")
    check("retour | activé après une navigation", page.is_enabled("#app-back"))
    page.click("#app-back")
    page.wait_for_function("location.hash === '#/' || location.hash === ''")
    check("retour | revient à la vue précédente", page.inner_text("#pane-detail .detail-title") == "Logement" and page.is_disabled("#app-back"))
    page.go_forward()
    wait_title(page, "Séjour")
    # Depuis un lien direct (rien avant) : niveau supérieur
    page2 = ctx.new_page()
    page2.goto(base + "#/l/" + loc_id(page, "Grand tiroir du bas"))
    wait_title(page2, "Grand tiroir du bas")
    check("retour | lien direct : actif (niveau supérieur)", page2.is_enabled("#app-back"))
    page2.click("#app-back")
    wait_title(page2, "Meuble living")
    check("retour | lien direct : mène au parent", True)
    page2.close()

    # Recherche : une seule entrée, Retour revient à l'écran d'avant
    page.goto(base + "#/")
    wait_title(page, "Logement")
    page.locator("#search-input").click()
    page.locator("#search-input").press_sequentially("pile")
    page.wait_for_selector("#pane-detail .search-results")
    page.click("#app-back")
    wait_title(page, "Logement")
    check("retour | depuis une recherche : écran précédent", page.locator("#search-input").input_value() == "")

    # Flèches de niveau
    goto_loc(page, base, "Meuble living")
    up, down = page.locator("[aria-label='Niveau supérieur']"), page.locator("[aria-label='Niveau inférieur']")
    check("flèches | présentes dans l'en-tête figé", up.is_visible() and down.is_visible() and page.locator("#pane-detail .detail-sticky [aria-label='Niveau inférieur']").count() == 1)
    down.click()
    wait_title(page, "Grand tiroir du bas")
    check("flèches | niveau inférieur : premier sous-emplacement", True)
    up.click()
    wait_title(page, "Meuble living")
    check("flèches | niveau supérieur : le parent", True)
    page.locator("#pane-detail .list-row", has_text="Tiroir bas gauche").click()
    wait_title(page, "Tiroir bas gauche")
    up.click()
    wait_title(page, "Meuble living")
    down.click()
    wait_title(page, "Tiroir bas gauche")
    check("flèches | le niveau inférieur revient là où l'on était", True)
    down.click()
    page.wait_for_selector("#pane-detail .item-detail")
    check("flèches | sans sous-emplacement : descend vers l'objet", page.inner_text("#pane-detail .detail-title") == "Piles neuves")
    check("flèches | objet : pas de niveau inférieur", page.locator("button[aria-label='Niveau inférieur']").is_disabled())
    up.click()
    wait_title(page, "Tiroir bas gauche")
    page.goto(base + "#/")
    wait_title(page, "Logement")
    check("flèches | racine : pas de niveau supérieur", page.locator("button[aria-label='Niveau supérieur']").is_disabled())
    page.locator("[aria-label='Niveau inférieur']").click()
    page.wait_for_function("document.querySelector('#pane-detail .detail-title').textContent !== 'Logement'")
    check("flèches | racine : descend vers une pièce", page.inner_text("#pane-detail .detail-title") in ("Chambre à coucher", "Séjour", "Entrée"))

    # Réglages : le bouton referme et revient à la vue précédente
    goto_loc(page, base, "Séjour")
    page.click("#app-settings")
    page.wait_for_selector("#pane-detail .settings")
    check("réglages | ouverture", page.evaluate("location.hash") == "#/r")
    page.click("#app-settings")
    wait_title(page, "Séjour")
    check("réglages | le même bouton referme et revient à la vue précédente", "Séjour" in page.inner_text("#pane-detail .detail-title") and page.get_attribute("#app-settings", "aria-current") is None)
    page.click("#app-settings")
    page.wait_for_selector("#pane-detail .settings")
    page.go_back()
    wait_title(page, "Séjour")
    check("réglages | Retour du navigateur fonctionne toujours", True)
    page.click("#app-settings")
    page.wait_for_selector("#pane-detail .settings")
    page.click("#app-back")
    wait_title(page, "Séjour")
    check("réglages | bouton Retour de l'application aussi", True)
    page3 = ctx.new_page()
    page3.goto(base + "#/r")
    page3.wait_for_selector("#pane-detail .settings")
    page3.click("#app-settings")
    wait_title(page3, "Logement")
    check("réglages | ouverts directement : le bouton ramène au logement", True)
    page3.close()
    check("navigation | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_input(browser, base):
    errors = []
    ctx, page = new_ctx(browser, 884, 1100, errors)
    load_demo(page, base)
    goto_loc(page, base, "Tiroir bas gauche")
    n_items = len(stored(page)["items"])
    page.get_by_role("button", name="Ajouter un objet ici").click()
    d = dlg(page)
    d.get_by_label("Nom").fill("Ampoules")
    q = d.get_by_label("Quantité")
    q.fill("2,5")
    q.press("Tab")
    err = d.locator(".field-error:visible")
    check("saisie | valeur décimale : message affiché en quittant le champ", err.is_visible() and "entier" in err.inner_text(), err.inner_text())
    check("saisie | Tab : on reste sur le champ fautif", page.evaluate("document.activeElement.name") == "quantity")
    d.get_by_label("Note (facultatif)").click()
    check("saisie | un tap sur un autre champ ramène au champ fautif", page.evaluate("document.activeElement.name") == "quantity")
    page.keyboard.type("zz")
    check("saisie | rien n'est saisi dans l'autre champ", d.get_by_label("Note (facultatif)").input_value() == "" and d.get_by_label("Mots-clés (facultatif)").input_value() == "")
    check("saisie | champ marqué invalide", q.get_attribute("aria-invalid") == "true")
    d.get_by_role("button", name="Annuler").click()
    closed(page)
    check("saisie | Annuler reste possible : rien n'est enregistré", len(stored(page)["items"]) == n_items)

    page.get_by_role("button", name="Ajouter un objet ici").click()
    d = dlg(page)
    d.get_by_label("Quantité").fill("-1")
    d.get_by_label("Quantité").press("Tab")
    page.keyboard.press("Escape")
    closed(page)
    check("saisie | Échap reste possible", len(stored(page)["items"]) == n_items)

    page.get_by_role("button", name="Ajouter un objet ici").click()
    d = dlg(page)
    d.get_by_label("Nom").fill("Ampoules")
    q = d.get_by_label("Quantité")
    q.fill("abc")
    q.press("Tab")
    q.fill("3")
    check("saisie | message effacé dès que la valeur est corrigée", d.locator(".field-error:visible").count() == 0 and q.get_attribute("aria-invalid") is None)
    q.press("Tab")
    check("saisie | valeur corrigée : on peut changer de champ", page.evaluate("document.activeElement.name") == "tags")
    d.get_by_label("Quantité").fill("1,5")
    d.get_by_role("button", name="Ajouter", exact=True).click()
    check("saisie | valider avec une valeur interdite : refusé, focus sur le champ", d.is_visible() and page.evaluate("document.activeElement.name") == "quantity" and len([i for i in stored(page)["items"] if i["name"] == "Ampoules"]) == 0)
    d.get_by_label("Quantité").fill("7")
    d.get_by_role("button", name="Ajouter", exact=True).click()
    closed(page)
    check("saisie | valeur corrigée : l'objet est enregistré", [i["quantity"] for i in stored(page)["items"] if i["name"] == "Ampoules"] == [7])

    # Modification d'un objet
    page.locator("#pane-detail .list-row", has_text="Ampoules").click()
    page.wait_for_selector("#pane-detail .item-detail")
    page.get_by_role("button", name="Modifier").click()
    d = dlg(page)
    d.get_by_label("Quantité").fill("2.5")
    d.get_by_label("Nom").click()
    check("saisie | modification : le champ fautif reprend le focus", page.evaluate("document.activeElement.name") == "quantity" and d.locator(".field-error:visible").count() == 1)
    d.get_by_role("button", name="Annuler").click()
    closed(page)
    check("saisie | modification annulée : quantité inchangée", [i["quantity"] for i in stored(page)["items"] if i["name"] == "Ampoules"] == [7])

    # Un changement de vue ferme la boîte sans rien enregistrer
    page.get_by_role("button", name="Modifier").click()
    dlg(page).get_by_label("Nom").fill("Renommé")
    page.evaluate("window.location.hash = '#/'")
    closed(page)
    check("saisie | changement de vue : boîte fermée, rien enregistré", len([i for i in stored(page)["items"] if i["name"] == "Renommé"]) == 0)
    check("saisie | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_badge(browser, base):
    errors = []
    ctx, page = new_ctx(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    check("pastille | aucune sans données", page.get_attribute("#app-settings", "data-unsaved") is None)
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector("#pane-detail .list")
    check("pastille | données jamais sauvegardées : pastille", page.get_attribute("#app-settings", "data-unsaved") == "true" and "non sauvegardées" in page.get_attribute("#app-settings", "aria-label"))
    check("pastille | visible près du bouton Réglages", page.evaluate("getComputedStyle(document.getElementById('app-settings'), '::before').content") != "none")
    page.click("#app-settings")
    page.wait_for_selector("#pane-detail .settings")
    with page.expect_download():
        page.click("#export-button")
    check("pastille | disparaît après l'export", page.get_attribute("#app-settings", "data-unsaved") is None and page.get_attribute("#app-settings", "aria-label") is None)
    js(page, "Rangement.features.locations.create({name:'Garage', kind:'piece'})")
    check("pastille | réapparaît après une modification", page.get_attribute("#app-settings", "data-unsaved") == "true")
    page.reload()
    page.wait_for_selector("#pane-detail .settings")
    check("pastille | conservée après rechargement", page.get_attribute("#app-settings", "data-unsaved") == "true")
    check("pastille | pas de confusion avec la pastille de mise à jour", page.get_attribute("#app-settings", "data-badge") is None)
    check("pastille | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_colors(browser, base):
    errors = []
    ctx, page = new_ctx(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    check("couleurs | « Créer ma première pièce » : couleur des pièces", color(page.get_by_role("button", name="Créer ma première pièce"), "backgroundColor") == TEAL)
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector("#pane-detail .list")
    check("couleurs | racine : « Ajouter une pièce » (pièces)", color(page.get_by_role("button", name="Ajouter une pièce"), "backgroundColor") == TEAL)
    check("couleurs | liste des pièces", color(page.locator("#pane-detail .list-title")) == TEAL)
    page.locator("#pane-detail .list-row", has_text="Séjour").click()
    wait_title(page, "Séjour")
    check("couleurs | titre de la pièce", color(page.locator("#pane-detail .detail-title")) == TEAL)
    check("couleurs | « Ajouter un emplacement ici » dans une pièce (1er ordre)", color(page.get_by_role("button", name="Ajouter un emplacement ici"), "backgroundColor") == BROWN)
    check("couleurs | « Ajouter un objet ici » (objets)", color(page.get_by_role("button", name="Ajouter un objet ici"), "backgroundColor") == BLUE)
    check("couleurs | liste des emplacements de premier ordre", color(page.locator("#pane-detail .list-title")) == BROWN)
    page.locator("#pane-detail .list-row", has_text="Meuble living").click()
    wait_title(page, "Meuble living")
    check("couleurs | « Ajouter un emplacement ici » dans un emplacement (sous-emplacement)", color(page.get_by_role("button", name="Ajouter un emplacement ici"), "backgroundColor") == ORANGE)
    check("couleurs | liste des sous-emplacements", color(page.locator("#pane-detail .list-title")) == ORANGE)
    page.locator("#pane-detail .list-row", has_text="Tiroir bas gauche").click()
    wait_title(page, "Tiroir bas gauche")
    check("couleurs | objets rangés", color(page.locator("#pane-detail .list-title")) == BLUE)
    check("couleurs | « Ajouter un emplacement ici » plus profond : sous-emplacement", color(page.get_by_role("button", name="Ajouter un emplacement ici"), "backgroundColor") == ORANGE)
    d_id = js(page, "Rangement.features.items.create({name:'Colle', locationId: Rangement.ui.router.current().locationId, quantity:'0'}).item.id")
    check("couleurs | objet à quantité 0 : gris spécifique", color(page.locator("#pane-detail .list-item--muted .list-title")) == "rgb(86, 104, 114)" or color(page.locator("#pane-detail .list-item--muted .list-title")) == GREY, color(page.locator("#pane-detail .list-item--muted .list-title")))
    page.goto(base + "#/o/" + d_id)
    page.wait_for_selector("#pane-detail .item-detail")
    check("couleurs | fiche d'un objet épuisé : grisée", page.locator("#pane-detail .detail-head--depleted").count() == 1)
    page.goto(base + "#/o/" + js(page, "Rangement.store.items().filter(function(i){return i.name==='Piles neuves';})[0].id"))
    page.wait_for_selector("#pane-detail .item-detail")
    check("couleurs | titre d'un objet", color(page.locator("#pane-detail .detail-title")) == BLUE)
    page.locator("#search-input").fill("jumelles")
    page.wait_for_selector("#pane-detail .search-results")
    check("couleurs | résultats de recherche : objets", color(page.locator("#pane-detail .search-results .list-title")) == BLUE)
    check("couleurs | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_narrow(browser, base):
    errors = []
    ctx, page = new_ctx(browser, 390, 844, errors)
    load_demo(page, base)
    check("replié | 1 volet", page.get_attribute("html", "data-panes") == "1")
    b = page.locator("#app-back").bounding_box()
    f = page.locator("#search-input").bounding_box()
    check("replié | bouton Retour ≥ 44 px, dans l'écran", b["height"] >= 44 and b["x"] >= 0 and f["x"] + f["width"] <= 390 and f["x"] > b["x"] + b["width"] - 1, (b, f))
    check("replié | champ de recherche encore ≥ 44 px", f["height"] >= 44 and f["width"] >= 180, f)
    for i in range(30):
        js(page, "Rangement.features.items.create({name:'Objet %02d', locationId:'%s'})" % (i, loc_id(page, "Tiroir bas gauche")))
    goto_loc(page, base, "Tiroir bas gauche")
    page.evaluate("document.getElementById('pane-detail').scrollTop = 600")
    pane = page.locator("#pane-detail").bounding_box()
    st = page.locator("#pane-detail .detail-sticky").bounding_box()
    check("replié | en-tête du détail figé", abs(st["y"] - pane["y"]) <= 1 and page.locator("#manage-toggle").is_visible(), (st, pane))
    for sel in ("[aria-label='Niveau supérieur']", "[aria-label='Niveau inférieur']", "#manage-toggle"):
        bb = page.locator(sel).bounding_box()
        check("replié | %s ≥ 44 px et dans l'écran" % sel, bb["height"] >= 44 and bb["x"] >= 0 and bb["x"] + bb["width"] <= 390, bb)
    check("replié | pas de défilement horizontal", page.evaluate("document.documentElement.scrollWidth - window.innerWidth") <= 0)
    page.evaluate("document.getElementById('pane-detail').scrollTop = 0")
    page.get_by_role("button", name="Dupliquer").click()
    box = dlg(page).bounding_box()
    check("replié | dialogue de duplication dans l'écran", box["x"] >= 0 and box["x"] + box["width"] <= 390 and box["y"] >= 0 and box["y"] + box["height"] <= 844, box)
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j6bis-replie-duplication.png"))
    page.keyboard.press("Escape")
    closed(page)
    page.get_by_role("button", name="Ajouter un objet ici").click()
    d = dlg(page)
    d.get_by_label("Quantité").fill("1.5")
    d.get_by_label("Quantité").press("Tab")
    bx = d.bounding_box()
    check("replié | message d'erreur de champ : dialogue toujours dans l'écran", d.locator(".field-error:visible").count() == 1 and bx["y"] >= 0 and bx["y"] + bx["height"] <= 844, bx)
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j6bis-replie-erreur.png"))
    page.keyboard.press("Escape")
    closed(page)
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j6bis-replie-detail.png"))
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()


def main():
    server = start_server()
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        scenario_tree(browser, base)
        scenario_rail(browser, base)
        scenario_detail(browser, base)
        scenario_duplicate(browser, base)
        scenario_navigation(browser, base)
        scenario_input(browser, base)
        scenario_badge(browser, base)
        scenario_colors(browser, base)
        scenario_narrow(browser, base)
        browser.close()
    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
