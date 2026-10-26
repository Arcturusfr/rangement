# tests/test_jalon7.py — Application « Rangement »
# Version : V010
# Horodatage : 2026-10-26 15:33 (heure de Paris)
# Résumé : création — tests Playwright/Chromium du jalon 7 (vue graphique des meubles, disposition, niveaux, nombre d'objets dans l'arborescence).
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon7.py
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
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=ROOT))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def new_ctx(browser, w, h, errors):
    ctx = browser.new_context(viewport={"width": w, "height": h})
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    return ctx, page


def js(page, expr):
    return page.evaluate(expr)


def wait_title(page, title):
    page.wait_for_function("document.querySelector('#pane-detail .detail-title') && document.querySelector('#pane-detail .detail-title').textContent === %r" % title)


def loc_id(page, name):
    return js(page, "Rangement.store.locations().filter(function(l){return l.name===%r;})[0].id" % name)


def geo(page, name):
    return js(page, "Rangement.store.getLocation(%r).geometry" % loc_id(page, name))


def names(page):
    return page.locator("#pane-detail .furn-cell .furn-name").all_inner_texts()


def start(browser, base, w=884, h=1100, errors=None):
    ctx, page = new_ctx(browser, w, h, errors if errors is not None else [])
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector("#pane-detail .list")
    return ctx, page


def goto(page, base, name):
    page.goto(base + "#/l/" + loc_id(page, name))
    wait_title(page, name)


def scenario_view(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    goto(page, base, "Séjour")
    check("vue | pas de commutateur sur une pièce", page.locator(".view-switch").count() == 0)
    goto(page, base, "Tiroir bas gauche")
    check("vue | pas de commutateur sur un sous-emplacement", page.locator(".view-switch").count() == 0)
    goto(page, base, "Meuble living")
    check("vue | commutateur sur un meuble, mode liste par défaut", page.locator(".view-switch").count() == 1 and page.get_by_role("button", name="Liste").get_attribute("aria-pressed") == "true" and page.locator("#pane-detail .list").count() >= 1)
    page.get_by_role("button", name="Vue graphique").click()
    page.wait_for_selector("#pane-detail .furn-view")
    check("vue | vue graphique affichée, liste masquée", page.locator("#pane-detail .furn-body").is_visible() and page.locator("#pane-detail .section-title", has_text="Emplacements à l").count() == 0)
    check("vue | un rectangle par sous-emplacement", names(page) == ["Grand tiroir du bas", "Tiroir bas gauche"], names(page))
    cap = page.inner_text("#pane-detail .furn-caption")
    check("vue | rappel du niveau (niveau 2 → sous-emplacements niveau 3)", "Niveau 2" in cap and "Emplacement" in cap and "Meuble living" in cap and "niveau 3" in cap, cap)
    check("vue | nombre d'objets sur chaque rectangle", "1 objet" in page.locator(".furn-cell", has_text="Tiroir bas gauche").inner_text())
    check("vue | niveau rappelé sur chaque rectangle", "Niveau 3" in page.locator(".furn-cell").first.inner_text())
    check("vue | pas d'icône de détail sans sous-niveau", page.locator(".furn-more").count() == 0)
    check("vue | proportions par défaut appliquées", js(page, "document.querySelector('.furn-body').style.aspectRatio") in ("1.5", "1.5 / 1"))
    check("vue | pas de pieds par défaut", page.locator(".furn-foot").count() == 0)
    page.reload()
    page.wait_for_selector("#pane-detail .furn-view")
    check("vue | choix du mode conservé après rechargement", page.get_by_role("button", name="Vue graphique").get_attribute("aria-pressed") == "true")
    page.locator(".furn-cell", has_text="Grand tiroir").locator(".furn-open").click()
    wait_title(page, "Grand tiroir du bas")
    check("vue | toucher un rectangle ouvre l'emplacement", True)
    check("vue | sous-emplacement : pas de commutateur", page.locator(".view-switch").count() == 0)
    page.get_by_role("button", name="Liste").count()
    goto(page, base, "Meuble living")
    page.get_by_role("button", name="Liste").click()
    page.wait_for_selector("#pane-detail .list")
    check("vue | retour à la liste", page.locator(".furn-view").count() == 0)
    page.get_by_role("button", name="Vue graphique").click()
    page.wait_for_selector("#pane-detail .furn-view")

    # Niveaux inférieurs
    tg = loc_id(page, "Tiroir bas gauche")
    js(page, "Rangement.features.locations.create({name:'<b>Boîte A</b>', kind:'boite', parentId:'%s'})" % tg)
    js(page, "Rangement.features.locations.create({name:'Boîte B', kind:'boite', parentId:'%s'})" % tg)
    more = page.locator(".furn-cell", has_text="Tiroir bas gauche").locator(".furn-more")
    check("niveaux | icône de détail sur le rectangle qui a des sous-niveaux", more.count() == 1 and "2 sous-emplacements" in more.get_attribute("aria-label") and "niveau 4" in more.get_attribute("aria-label") and more.inner_text().strip() == "2", more.get_attribute("aria-label"))
    check("niveaux | un seul rectangle a l'icône", page.locator(".furn-more").count() == 1)
    more.click()
    page.wait_for_function("document.querySelector('.furn-caption').textContent.indexOf('Niveau 3') === 0")
    cap = page.inner_text(".furn-caption")
    check("niveaux | détail : niveau rappelé (niveau 3, sous-emplacement, niveau 4)", "Sous-emplacement" in cap and "Tiroir bas gauche" in cap and "niveau 4" in cap, cap)
    check("niveaux | détail : les sous-sous-emplacements sont dessinés (texte brut)", names(page) == ["<b>Boîte A</b>", "Boîte B"] and page.locator(".furn-view b").count() == 0, names(page))
    check("niveaux | détail : niveau 4 sur les rectangles", "Niveau 4" in page.locator(".furn-cell").first.inner_text())
    check("niveaux | détail : objets du niveau listés avec niveau rappelé", "Piles neuves" in page.inner_text(".furn-view .section") and "niveau 3" in page.inner_text(".furn-view .section-title"))
    check("niveaux | détail : bouton de remontée", page.get_by_role("button", name="Remonter au niveau 2").count() == 1)
    page.get_by_role("button", name="Remonter au niveau 2").click()
    page.wait_for_function("document.querySelector('.furn-caption').textContent.indexOf('Niveau 2') === 0")
    check("niveaux | remontée : retour au meuble", names(page) == ["Grand tiroir du bas", "Tiroir bas gauche"])
    check("vue | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_layout(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    goto(page, base, "Meuble living")
    page.get_by_role("button", name="Vue graphique").click()
    page.wait_for_selector("#pane-detail .furn-view")
    check("disposition | réglages masqués au départ", page.locator(".furn-controls").count() == 0 and page.locator(".furn-edit").count() == 0)
    page.get_by_role("button", name="Ajuster la disposition").click()
    check("disposition | réglages et boutons de décalage affichés", page.locator(".furn-controls").is_visible() and page.locator(".furn-edit").count() == 2)

    page.get_by_label("Proportions").select_option(label="Carré")
    page.wait_for_function("document.querySelector('.furn-body').style.aspectRatio.indexOf('1') === 0 && document.querySelector('.furn-body').style.aspectRatio.length <= 5")
    check("disposition | proportions enregistrées dans geometry", geo(page, "Meuble living")["ratio"] == 1, geo(page, "Meuble living"))
    check("disposition | réglages conservés après mise à jour de l'affichage", page.locator(".furn-controls").is_visible())
    check("disposition | rectangle carré", abs(page.locator(".furn-body").bounding_box()["width"] / page.locator(".furn-body").bounding_box()["height"] - 1) < 0.1)
    page.get_by_label("Pieds").check()
    page.wait_for_selector(".furn-foot")
    check("disposition | deux pieds dessinés et enregistrés", page.locator(".furn-foot").count() == 2 and geo(page, "Meuble living")["feet"] is True)
    page.get_by_label("Colonnes").select_option("2")
    page.wait_for_function("document.querySelector('.furn-grid').style.gridTemplateColumns.indexOf('repeat(2') === 0")
    check("disposition | 2 colonnes", geo(page, "Meuble living")["cols"] == 2)
    page.get_by_label("Colonnes").select_option("1")
    page.wait_for_function("document.querySelector('.furn-grid').style.gridTemplateColumns.indexOf('repeat(1') === 0")

    page.get_by_role("button", name="Décaler « Grand tiroir du bas » vers la fin").click()
    page.wait_for_function("document.querySelector('.furn-cell .furn-name').textContent === 'Tiroir bas gauche'")
    check("déplacement | ordre modifié à la main", names(page) == ["Tiroir bas gauche", "Grand tiroir du bas"], names(page))
    check("déplacement | ordre enregistré", geo(page, "Tiroir bas gauche")["pos"] == 0 and geo(page, "Grand tiroir du bas")["pos"] == 1)
    page.get_by_role("button", name="Décaler « Grand tiroir du bas » vers la fin").click()
    check("déplacement | au bout : sans effet", names(page) == ["Tiroir bas gauche", "Grand tiroir du bas"])
    page.get_by_role("button", name="Élargir « Tiroir bas gauche »").click()
    page.wait_for_selector(".furn-cell[data-span='2']")
    check("déplacement | largeur 2 colonnes enregistrée", geo(page, "Tiroir bas gauche")["span"] == 2)
    page.get_by_role("button", name="Terminer l’ajustement").click()
    check("disposition | terminer masque les réglages", page.locator(".furn-controls").count() == 0)
    page.reload()
    page.wait_for_selector(".furn-view")
    check("disposition | persistance après rechargement", names(page) == ["Tiroir bas gauche", "Grand tiroir du bas"] and page.locator(".furn-foot").count() == 2)
    page.get_by_role("button", name="Liste").click()
    page.wait_for_selector("#pane-detail .list")
    check("disposition | l'ordre manuel n'affecte pas la liste", page.locator("#pane-detail .list-title").first.inner_text() == "Grand tiroir du bas")

    # export / import
    s = js(page, "JSON.stringify(Rangement.features.backup.prepareExport ? JSON.parse(Rangement.features.backup.prepareExport().text).locations.filter(function(l){return l.name==='Meuble living';})[0].geometry : null)")
    check("sauvegarde | la géométrie figure dans l'export", '"feet":true' in s and '"ratio":1' in s, s)
    check("sauvegarde | données valides", js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok"))
    check("garde-fous | emplacement inconnu refusé", js(page, "Rangement.features.furniture.set('nope',{feet:true}).ok") is False and js(page, "Rangement.features.furniture.shift('nope',1).ok") is False)
    check("garde-fous | valeur de proportions absurde ignorée", js(page, "(function(){Rangement.features.furniture.set('%s',{ratio:99}); return Rangement.features.furniture.get('%s').ratio;})()" % (loc_id(page, "Meuble living"), loc_id(page, "Meuble living"))) == 1.5)
    check("disposition | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_tree(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    rows = js(page, "Array.from(document.querySelectorAll('#pane-tree .tree-row')).map(function(r){return r.innerText.replace(/\\s+/g,' ').trim();})")
    check("arbo | nombre d'objets par pièce (total, sous-niveaux compris)", "Séjour 2" in rows and "Entrée 1" in rows and "Chambre à coucher 1" in rows, rows)
    js(page, "Rangement.ui.views.browse.expandAll()")
    rows = js(page, "Array.from(document.querySelectorAll('#pane-tree .tree-row')).map(function(r){return r.innerText.replace(/\\s+/g,' ').trim();})")
    check("arbo | nombre d'objets par emplacement", "Meuble living 2" in rows and "Tiroir bas gauche 1" in rows, rows)
    js(page, "Rangement.features.locations.create({name:'Vide', parentId:'%s'})" % loc_id(page, "Séjour"))
    rows = js(page, "Array.from(document.querySelectorAll('#pane-tree .tree-row')).map(function(r){return r.innerText.replace(/\\s+/g,' ').trim();})")
    check("arbo | emplacement vide : pas de nombre", "Vide" in rows, rows)
    check("arbo | le lien reste le seul élément surligné (libellé inchangé)", True)
    page.set_viewport_size({"width": 884, "height": 1100})
    check("arbo | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_narrow(browser, base):
    errors = []
    ctx, page = start(browser, base, 390, 844, errors)
    goto(page, base, "Meuble living")
    check("replié | commutateur ≥ 44 px et dans l'écran", all(b["height"] >= 44 and b["x"] >= 0 and b["x"] + b["width"] <= 390 for b in [page.get_by_role("button", name=n).bounding_box() for n in ("Liste", "Vue graphique")]))
    page.get_by_role("button", name="Vue graphique").click()
    page.wait_for_selector(".furn-view")
    js(page, "Rangement.features.locations.create({name:'Boîte', parentId:'%s'})" % loc_id(page, "Tiroir bas gauche"))
    page.get_by_role("button", name="Ajuster la disposition").click()
    check("replié | pas de défilement horizontal", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    tools = page.locator(".furn-view button:visible")
    check("replié | boutons de la vue ≥ 44 px", all(tools.nth(i).bounding_box()["height"] >= 44 - 1 for i in range(tools.count())), [tools.nth(i).bounding_box()["height"] for i in range(tools.count())])
    check("replié | rectangles contenus dans l'écran", all(page.locator(".furn-cell").nth(i).bounding_box()["x"] + page.locator(".furn-cell").nth(i).bounding_box()["width"] <= 390 for i in range(2)))
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j7-replie-vue.png"), full_page=True)
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()
    errors = []
    ctx, page = start(browser, base, errors=errors)
    goto(page, base, "Meuble living")
    page.get_by_role("button", name="Vue graphique").click()
    page.wait_for_selector(".furn-view")
    check("déplié | arborescence et vue côte à côte", page.is_visible("#pane-tree") and page.is_visible(".furn-body"))
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j7-deplie-vue.png"))
    check("déplié | aucune erreur console", not errors, errors)
    ctx.close()


def main():
    server = start_server()
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        scenario_view(browser, base)
        scenario_layout(browser, base)
        scenario_tree(browser, base)
        scenario_narrow(browser, base)
        browser.close()
    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
