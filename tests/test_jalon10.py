# tests/test_jalon10.py — Application « Rangement »
# Version : V020
# Horodatage : 2026-11-20 22:57 (heure de Paris)
# Résumé : V020 : adapté au jalon 11 (recherche masquée ouverte au chargement, boutons de l'en-tête, groupes, volet d'arborescence) ; parcours inchangés.
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon10.py
# Nécessite : pip install playwright  puis  playwright install chromium

import functools
import http.server
import os
import sys
import threading

from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHOTS = os.environ.get("RANGEMENT_SHOTS")
F = "Rangement.features.furniture"
results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (("  -> " + str(detail)) if (detail and not cond) else ""))


class QuietServer(http.server.ThreadingHTTPServer):
    """Serveur de test : une connexion coupée par le navigateur en cours d'envoi n'est pas une erreur."""

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
    ctx = browser.new_context(viewport={"width": w, "height": h})     # sans réglage préalable : on teste les valeurs par défaut
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


def wait_title(page, title):
    page.wait_for_function("document.querySelector('#pane-detail .detail-title') && document.querySelector('#pane-detail .detail-title').textContent === %r" % title)


def longpress(page, locator, ms=650):
    b = locator.bounding_box()
    page.mouse.move(b["x"] + b["width"] / 2, b["y"] + b["height"] / 2)
    page.mouse.down()
    page.wait_for_timeout(ms)
    page.mouse.up()


def cell(page, name):
    return page.locator(".furn-cell", has_text=name)


def menu(page):
    return page.locator(".ctx-menu")


def items_of(page):
    return page.locator(".ctx-menu .ctx-item").all_inner_texts()


def box(page, sel):
    return page.locator(sel).bounding_box()


def scenario_icons_and_press(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1100, errors)
    names = ["list", "plan", "settings", "edit-text", "edit-plan", "move-cell", "enlarge-cell", "zoom-in", "zoom-out"]
    check("pictogrammes | tous les pictogrammes existent", all(js(page, "Rangement.ui.icons.has(%r)" % n) for n in names))
    info = js(page, "(function(){var s=Rangement.ui.icons.create('plan', 30); return [s.tagName.toLowerCase(), s.getAttribute('aria-hidden'), s.getAttribute('width'), s.getAttribute('stroke'), s.childNodes.length, Rangement.ui.icons.has('inconnu')];})()")
    check("pictogrammes | SVG décoratif, couleur du texte, taille réglable, nom inconnu toléré", info == ["svg", "true", "30", "currentColor", 4, False], info)
    check("pictogrammes | engrenage seul pour « Réglages » (nom accessible conservé)", page.locator("#app-settings svg").count() == 1 and page.get_attribute("#app-settings", "aria-label").startswith("Réglages") and box(page, "#app-settings")["width"] <= 46)
    check("pictogrammes | version affichée", page.inner_text("#app-version").strip() == js(page, "Rangement.config.version"))

    # composant d'appui long, sur un élément d'essai (souris, toucher simulé, clavier)
    js(page, """(function(){
      var b = document.createElement('button'); b.id = 'lp'; b.textContent = 'essai'; b.style.cssText = 'position:fixed;left:300px;top:300px;width:120px;height:60px;z-index:99';
      document.body.appendChild(b); window.__log = [];
      Rangement.ui.components.longpress.attach(b, { onShort: function () { window.__log.push('short'); }, onLong: function () { window.__log.push('long'); } });
    })()""")
    lp = page.locator("#lp")
    lp.click()
    check("appui | un clic simple = appui simple", js(page, "window.__log") == ["short"], js(page, "window.__log"))
    js(page, "window.__log = []")
    longpress(page, lp)
    page.wait_for_timeout(500)
    check("appui | appui long (souris) : une seule fois, le clic qui suit est ignoré", js(page, "window.__log") == ["long"], js(page, "window.__log"))
    js(page, "window.__log = []")
    b = lp.bounding_box()
    page.mouse.move(b["x"] + 10, b["y"] + 10)
    page.mouse.down()
    page.mouse.move(b["x"] + 60, b["y"] + 10, steps=4)
    page.wait_for_timeout(650)
    page.mouse.up()
    page.wait_for_timeout(500)
    check("appui | un doigt qui bouge (défilement) n'ouvre rien", "long" not in js(page, "window.__log"), js(page, "window.__log"))
    js(page, "window.__log = []")
    page.mouse.move(b["x"] + 30, b["y"] + 30)
    page.mouse.down()
    page.wait_for_timeout(150)
    page.mouse.up()
    check("appui | un appui trop court n'est pas un appui long", js(page, "window.__log") == ["short"], js(page, "window.__log"))
    js(page, "window.__log = []")
    lp.click(button="right")
    check("appui | clic droit = appui long (menu natif supprimé)", js(page, "window.__log") == ["long"], js(page, "window.__log"))
    page.wait_for_timeout(500)
    js(page, "window.__log = []")
    lp.focus()
    page.keyboard.press("Enter")
    check("appui | la touche Entrée = appui simple, même juste après un appui long", js(page, "window.__log") == ["short"], js(page, "window.__log"))
    # toucher simulé : événements de pointeur « touch »
    js(page, "window.__log = []")
    page.wait_for_timeout(500)
    js(page, """(function(){
      var b = document.getElementById('lp'); var r = b.getBoundingClientRect(); var o = { bubbles: true, cancelable: true, pointerType: 'touch', isPrimary: true, clientX: r.left + 20, clientY: r.top + 20, button: 0 };
      b.dispatchEvent(new PointerEvent('pointerdown', o));
      window.__touch = function () { b.dispatchEvent(new PointerEvent('pointerup', o)); b.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, detail: 1 })); };
    })()""")
    page.wait_for_timeout(650)
    js(page, "window.__touch()")
    check("appui | toucher maintenu : appui long, puis le clic de relâchement est ignoré", js(page, "window.__log") == ["long"], js(page, "window.__log"))
    check("appui | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_navigation(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1100, errors)
    cell(page, "Séjour").locator(".furn-open").click()
    wait_title(page, "Séjour")
    check("navigation | un appui simple sur une pièce l'ouvre", js(page, "location.hash") == "#/l/" + loc_id(page, "Séjour") and menu(page).count() == 0)
    cell(page, "Meuble living").click()
    wait_title(page, "Meuble living")
    check("navigation | un appui simple sur un meuble l'ouvre aussi", True)
    page.goto(base + "#/")
    page.wait_for_selector(".furn-body[data-fit]")
    longpress(page, cell(page, "Entrée"))
    page.wait_for_selector(".ctx-menu")
    check("navigation | un appui long ouvre le menu sans ouvrir la pièce", js(page, "location.hash") in ("#/", "") and items_of(page)[0] == "Ouvrir")
    check("navigation | le menu : « Ouvrir » est écrit comme les autres commandes", menu(page).locator(".ctx-primary").count() == 0 and items_of(page) == ["Ouvrir", "Placer et dimensionner", "Ajouter un objet ici", "Ajouter un emplacement ici", "Modifier", "Déplacer", "Dupliquer", "Supprimer"], items_of(page))
    check("navigation | pictogrammes devant « Modifier » et « Placer et dimensionner »", menu(page).get_by_role("button", name="Modifier", exact=True).locator("svg").count() == 1 and menu(page).get_by_role("button", name="Placer et dimensionner", exact=True).locator("svg").count() == 1)
    page.keyboard.press("Escape")

    # mode « Modifier le plan »
    page.locator("#plan-edit").click()
    page.wait_for_selector(".furn-view[data-editing='true']")
    check("modifier | le bouton est enfoncé, le plan est entouré, les cases libres sont marquées", page.locator("#plan-edit").get_attribute("aria-pressed") == "true" and page.locator(".furn-slot").count() == 1)
    check("modifier | sans sélection : « Grille… » et « Terminer » proposés, pas de pavé", page.locator(".furn-bar").get_by_role("button", name="Grille…").count() == 1 and page.locator(".furn-bar #plan-done").count() == 1 and page.locator(".furn-sel").count() == 0)
    cell(page, "Entrée").locator(".furn-open").click()
    page.wait_for_selector(".furn-sel")
    check("modifier | un appui simple sélectionne (n'ouvre pas)", "Entrée" in page.inner_text(".furn-sel-text") and js(page, "location.hash") in ("#/", ""))
    check("modifier | pictogrammes au centre des pavés de flèches", page.locator(".furn-pad-mid svg").count() == 2)
    longpress(page, cell(page, "Séjour"))
    page.wait_for_selector(".ctx-menu")
    check("modifier | un appui long ouvre quand même le menu", items_of(page)[0] == "Ouvrir")
    page.keyboard.press("Escape")
    page.locator("#plan-edit").click()
    page.wait_for_selector(".furn-view[data-editing='false']")
    check("modifier | le bouton termine la modification (plus de pavé)", page.locator(".furn-sel").count() == 0 and page.locator("#plan-edit").get_attribute("aria-pressed") == "false")
    # menu « Placer et dimensionner » : entre dans le mode avec la case sélectionnée
    longpress(page, cell(page, "Séjour"))
    page.locator(".ctx-menu").get_by_role("button", name="Placer et dimensionner", exact=True).click()
    page.wait_for_selector(".furn-sel")
    check("modifier | « Placer et dimensionner » active le mode et sélectionne la case", page.locator("#plan-edit").get_attribute("aria-pressed") == "true" and "Séjour" in page.inner_text(".furn-sel-text"))
    page.locator(".furn-sel").get_by_role("button", name="Terminer").click()
    page.wait_for_selector(".furn-view[data-editing='false']")
    check("modifier | « Terminer » du pavé relâche aussi le bouton de l'en-tête", page.locator("#plan-edit").get_attribute("aria-pressed") == "false")
    # un changement d'écran referme la modification ; la liste n'a pas ce bouton
    page.locator("#plan-edit").click()
    page.wait_for_selector(".furn-view[data-editing='true']")
    page.goto(base + "#/l/" + loc_id(page, "Séjour"))
    wait_title(page, "Séjour")
    check("modifier | un changement d'écran termine la modification", page.locator("#plan-edit").get_attribute("aria-pressed") == "false" and page.locator(".furn-view[data-editing='true']").count() == 0)
    page.locator("#plan-edit").click()
    page.wait_for_selector(".furn-view[data-editing='true']")
    page.locator("#view-toggle").click()
    page.wait_for_selector("#pane-detail .list")
    check("modifier | en liste : pas de bouton « Modifier », et la modification est terminée", page.locator("#plan-edit").count() == 0 and page.locator("#plan-zoom").count() == 0)
    page.locator("#view-toggle").click()
    page.wait_for_selector(".furn-body[data-fit]")
    check("modifier | de retour sur le plan, hors modification", page.locator("#plan-edit").get_attribute("aria-pressed") == "false")

    # menu « Actions » : « Régler la grille… » à la racine
    page.goto(base + "#/")
    page.wait_for_selector(".furn-body[data-fit]")
    page.locator("#manage-toggle").click()
    page.wait_for_selector(".ctx-menu")
    check("actions | logement en vue graphique : Ajouter une pièce, Régler la grille…", items_of(page) == ["Ajouter une pièce", "Régler la grille…"], items_of(page))
    page.keyboard.press("Escape")
    page.get_by_role("button", name="Liste", exact=True).click()
    page.wait_for_selector("#pane-detail .list")
    page.locator("#manage-toggle").click()
    check("actions | en liste : pas de « Régler la grille… »", items_of(page) == ["Ajouter une pièce"], items_of(page))
    page.keyboard.press("Escape")
    check("navigation | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_layout(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1100, errors)
    top = box(page, ".app-top")
    check("bandeaux | écran déplié : en-tête et recherche sur une seule ligne (≤ 72 px)", top["height"] <= 72, top)
    ys = [box(page, s)["y"] + box(page, s)["height"] / 2 for s in (".app-name", "#search-toggle", "#app-settings", "#app-version")]
    check("bandeaux | nom, loupe, Réglages et version alignés", max(ys) - min(ys) <= 8, ys)
    check("bandeaux | le bouton Retour est à gauche du nom", box(page, "#app-back")["x"] < box(page, ".app-name")["x"])
    check("bandeaux | champ de recherche masqué par défaut", not page.is_visible("#search-input"))
    page.locator("#search-toggle").click()
    page.wait_for_selector("#search-input", state="visible")
    check("bandeaux | la loupe affiche le champ, sur la même ligne, avec une largeur confortable", box(page, "#search-input")["width"] >= 250 and box(page, ".app-top")["height"] <= 72, (box(page, "#search-input"), box(page, ".app-top")))
    page.locator("#search-toggle").click()
    st = box(page, ".detail-sticky")
    check("bandeaux | en-tête du détail resserré (≤ 112 px)", st["height"] <= 112, st)
    check("bandeaux | pas de zone flottante ni de bouton « + »", page.locator(".float-zone, .float-btn, #plan-add, .furn-add").count() == 0)
    bt = [box(page, s) for s in ("#view-toggle", "#plan-zoom", "#plan-edit")]
    tools = box(page, ".detail-bar-tools-row")
    check("boutons | trois boutons ronds de 44 px alignés à droite sous les flèches et « Actions »", all(b["width"] >= 43 and b["height"] >= 43 for b in bt) and bt[0]["y"] >= tools["y"] + tools["height"] - 1 and abs(bt[2]["x"] + bt[2]["width"] - (tools["x"] + tools["width"])) <= 6, (bt, tools))
    check("boutons | rien ne recouvre le plan", bt[0]["y"] + bt[0]["height"] <= box(page, ".furn-body")["y"] + 1, (bt[0], box(page, ".furn-body")))
    # plan 7 × 10 : cases d'au moins 48 px et plan entier dans l'écran
    js(page, "%s.setGrid(%s.ROOT,{cols:7, rows:10})" % (F, F))
    page.wait_for_function("Rangement.store.plan() && Rangement.store.plan().cols === 7")
    page.wait_for_timeout(300)
    cs = js(page, "(function(){var c=document.querySelector('.furn-cell').getBoundingClientRect(); return [c.width, c.height];})()")
    bb = box(page, ".furn-body")
    check("plan | 7 × 10 : cases ≥ 48 px, plan entier dans l'écran sans défiler", cs[0] >= 47 and bb["y"] + bb["height"] <= 1100 and js(page, "document.getElementById('pane-detail').scrollHeight - document.getElementById('pane-detail').clientHeight") <= 1, (cs, bb))
    # volet central agrandi (arborescence masquée) : le plan reste entier
    page.locator("#tree-toggle").click()
    page.wait_for_function("document.documentElement.dataset.tree === 'hidden'")
    page.wait_for_timeout(300)
    bb = box(page, ".furn-body")
    check("plan | arborescence masquée : le plan tient toujours dans l'écran", bb["y"] + bb["height"] <= 1100 and bb["x"] >= 0, bb)
    check("bandeaux | aucune erreur console", not errors, errors)
    ctx.close()

    errors = []
    ctx, page = start(browser, base, 390, 844, errors)
    page.locator("#search-toggle").click()
    page.wait_for_selector("#search-input", state="visible")
    hb, sb = box(page, ".app-header"), box(page, ".searchbar")
    page.locator("#search-toggle").click()
    check("replié | en-tête et recherche (ouverte par la loupe) restent deux bandeaux superposés", sb["y"] >= hb["y"] + hb["height"] - 1 and hb["height"] <= 80, (hb, sb))
    bt = [box(page, s) for s in ("#view-toggle", "#plan-zoom", "#plan-edit")]
    check("replié | trois boutons sur une même ligne, alignés à droite", max(b["y"] for b in bt) - min(b["y"] for b in bt) <= 1 and bt[2]["x"] + bt[2]["width"] >= 390 - 24, bt)
    check("replié | rien ne recouvre le plan", bt[0]["y"] + bt[0]["height"] <= box(page, ".furn-body")["y"] + 1)
    check("replié | pas de défilement horizontal", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    check("replié | en-tête du détail ≤ 140 px", box(page, ".detail-sticky")["height"] <= 140, box(page, ".detail-sticky"))
    # nom d'emplacement long : l'en-tête ne déborde pas
    longpress(page, cell(page, "Séjour"))
    page.wait_for_selector(".ctx-menu")
    mb = box(page, ".ctx-menu")
    check("replié | menu d'une case dans l'écran", mb["x"] >= 0 and mb["x"] + mb["width"] <= 391 and mb["y"] >= 0 and mb["y"] + mb["height"] <= 845, mb)
    page.keyboard.press("Escape")
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_startup(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1100, errors)
    check("démarrage | rail par défaut", page.get_attribute("html", "data-tree") == "mini")
    page.locator("#tree-toggle").click()
    page.wait_for_function("document.documentElement.dataset.tree === 'hidden'")
    check("démarrage | l'état choisi n'est pas mémorisé", js(page, "localStorage.getItem('rangement.data.ui')") is None)
    page.reload()
    page.wait_for_selector(".furn-body[data-fit]")
    check("démarrage | après rechargement : rail", page.get_attribute("html", "data-tree") == "mini" and page.locator("#pane-tree .tree-mini-item").count() == 4)
    js(page, "localStorage.setItem('rangement.data.ui', JSON.stringify({tree:'hidden'}))")
    page.reload()
    page.wait_for_selector(".furn-body[data-fit]")
    check("démarrage | un ancien réglage mémorisé est ignoré", page.get_attribute("html", "data-tree") == "mini")
    check("démarrage | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_slots(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1100, errors)
    sej = loc_id(page, "Séjour")
    page.goto(base + "#/l/" + sej)
    wait_title(page, "Séjour")
    page.wait_for_selector(".furn-body[data-fit]")
    check("cases libres | une pièce à un seul meuble (2 colonnes) : une case libre visible hors modification", page.locator(".furn-slot").count() == 1, page.locator(".furn-slot").count())
    # pièce vide : la grille est dessinée avec une case libre, et le texte d'aide
    js(page, "Rangement.features.locations.create({name:'Cave', kind:'piece'})")
    page.goto(base + "#/l/" + loc_id(page, "Cave"))
    wait_title(page, "Cave")
    page.wait_for_selector(".furn-body[data-fit]")
    check("cases libres | pièce vide : deux cases libres et un texte d'aide", page.locator(".furn-slot").count() == 2 and "appui long" in page.inner_text(".furn-empty-hint"), page.locator(".furn-slot").count())
    longpress(page, page.locator(".furn-slot").first)
    page.wait_for_selector(".ctx-menu")
    page.locator(".ctx-menu").get_by_role("button", name="Ajouter un emplacement ici", exact=True).click()
    d = page.locator("dialog.dialog[open]")
    d.get_by_label("Nom").fill("Étagère")
    d.get_by_label("Nom").press("Enter")
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    page.wait_for_selector(".furn-cell:has-text('Étagère')")
    g = js(page, "Rangement.store.locations().filter(function(l){return l.name==='Étagère';})[0].geometry")
    check("cases libres | emplacement créé sur la case, taille 1 × 1", g["col"] == 0 and g["row"] == 0 and g["w"] == 1 and g["h"] == 1 and "appui long" not in (page.inner_text("#pane-detail") if page.locator(".furn-empty-hint").count() else ""), g)
    check("cases libres | données valides", js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok"))
    # création refusée (nom en double) : la boîte reste ouverte, rien n'est créé de plus
    n = len(js(page, "Rangement.store.locations()"))
    longpress(page, page.locator(".furn-slot").first)
    page.wait_for_selector(".ctx-menu")
    page.locator(".ctx-menu").get_by_role("button", name="Ajouter un emplacement ici", exact=True).click()
    d = page.locator("dialog.dialog[open]")
    d.get_by_label("Nom").fill("étagere")
    d.get_by_role("button", name="Ajouter", exact=True).click()
    check("cases libres | nom en double : refusé, boîte conservée", d.is_visible() and "existe déjà" in d.inner_text() and len(js(page, "Rangement.store.locations()")) == n)
    d.get_by_role("button", name="Annuler").click()
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    check("cases libres | aucune erreur console", not errors, errors)
    ctx.close()


def main():
    server = QuietServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=ROOT))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        scenario_icons_and_press(browser, base)
        scenario_navigation(browser, base)
        scenario_layout(browser, base)
        scenario_startup(browser, base)
        scenario_slots(browser, base)
        browser.close()
    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
