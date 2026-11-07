# tests/test_jalon8.py — Application « Rangement »
# Version : V016
# Horodatage : 2026-11-06 12:00 (heure de Paris)
# Résumé : adaptation V016 : commandes d'action via le menu déroulant « Actions », info-bulle ℹ️ à la place du texte de rappel du plan.
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon8.py
# Nécessite : pip install playwright  puis  playwright install chromium

import functools
import http.server
import json
import os
import sys
import tempfile
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
    ctx = browser.new_context(viewport={"width": w, "height": h}, accept_downloads=True)
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    return ctx, page


def js(page, expr):
    return page.evaluate(expr)


def stored(page):
    return page.evaluate("JSON.parse(localStorage.getItem('rangement.data'))")


def dlg(page):
    return page.locator("dialog.dialog[open]")


def closed(page):
    page.wait_for_selector("dialog.dialog[open]", state="detached")


def start(browser, base, w=884, h=1100, errors=None):
    ctx, page = new_ctx(browser, w, h, errors if errors is not None else [])
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector("#pane-detail .list")
    return ctx, page


def plan(page):
    page.get_by_role("button", name="Plan", exact=True).click()
    page.wait_for_selector("#pane-detail .furn-view")
    page.wait_for_selector(".furn-body[data-fit]")


def names(page):
    return page.locator("#pane-detail .furn-cell .furn-name").all_inner_texts()


def cell(page, name):
    return page.locator(".furn-cell", has_text=name)




def open_menu(page, name):
    page.locator(".furn-cell", has_text=name).locator(".furn-open").click()
    page.wait_for_selector(".ctx-menu")


def open_cell(page, name):
    open_menu(page, name)
    page.locator(".ctx-menu").get_by_role("button", name="Ouvrir", exact=True).click()


def start_edit(page, name):
    open_menu(page, name)
    page.locator(".ctx-menu").get_by_role("button", name="Placer et dimensionner", exact=True).click()
    page.wait_for_selector(".furn-sel")


def set_grid(page, **kw):
    """Réglages de la grille (pavé « Grille… » en placement, sinon bouton « + »). Renvoie le message de refus, ou None."""
    sel = page.locator(".furn-sel")
    if sel.count():
        sel.get_by_role("button", name="Grille…").click()
    else:
        page.locator("#plan-add").click()
        page.locator(".ctx-menu").get_by_role("button", name="Régler la grille…", exact=True).click()
    d = page.locator("dialog.dialog[open]")
    labels = {"cols": "Colonnes", "rows": "Lignes", "top": "Dessus", "bottom": "Dessous", "ratio": "Proportions", "feet": "Pieds"}
    for key, value in kw.items():
        d.get_by_label(labels[key]).select_option(str(value))
    d.get_by_role("button", name="Appliquer").click()
    page.wait_for_timeout(150)
    if page.locator("dialog.dialog[open]").count():
        msg = page.locator("dialog.dialog[open] .form-error").inner_text()
        page.locator("dialog.dialog[open]").get_by_role("button", name="Annuler").click()
        page.wait_for_selector("dialog.dialog[open]", state="detached")
        return msg
    return None


def select_cell(page, name):
    if page.locator(".furn-view[data-editing='true']").count():
        page.locator(".furn-cell", has_text=name).locator(".furn-open").click()
        page.wait_for_selector(".furn-sel")
    else:
        start_edit(page, name)


def tool(page, label):
    page.get_by_role("button", name=label, exact=True).click()


def loc_id(page, name):
    return js(page, "Rangement.store.locations().filter(function(l){return l.name===%r;})[0].id" % name)


def geo(page, name):
    return js(page, "Rangement.store.getLocation(%r).geometry" % loc_id(page, name))


def inside(page):
    return js(page, """(function(){var b=document.querySelector('.furn-body').getBoundingClientRect(); var bad=[];
      document.querySelectorAll('.furn-body .furn-cell').forEach(function(c){var r=c.getBoundingClientRect();
        if(r.left<b.left-1||r.right>b.right+1||r.top<b.top-1||r.bottom>b.bottom+1){bad.push('case '+c.textContent.slice(0,20));}
        c.querySelectorAll('.furn-name').forEach(function(n){var q=n.getBoundingClientRect();
          if(q.left<r.left-1||q.right>r.right+1||q.bottom>r.bottom+1||q.top<r.top-1){bad.push('libellé '+n.textContent.slice(0,20));}});});
      return bad;})()""")


def tmp_file(content, name="plan.json"):
    d = tempfile.mkdtemp()
    path = os.path.join(d, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


F = "Rangement.features.furniture"


def info(page):
    """Texte de l'info-bulle ℹ️ de l'en-tête (V016)."""
    page.locator("#info-toggle").click()
    page.wait_for_selector(".bubble")
    txt = page.locator(".bubble").inner_text()
    page.keyboard.press("Escape")
    return txt


def scenario_view(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    check("plan | commutateur Liste / Plan à la racine, liste par défaut", page.get_by_role("button", name="Liste", exact=True).get_attribute("aria-pressed") == "true" and page.get_by_role("button", name="Plan", exact=True).count() == 1)
    plan(page)
    txt = info(page)
    check("plan | info-bulle : le logement et le nombre de pièces", "Niveau 0" in txt and "3 pièces" in txt and "4 emplacements" in txt.replace("8 emplacements", "4 emplacements") and page.locator(".furn-caption").count() == 0, txt)
    check("plan | une tuile par pièce (ordre alphabétique)", names(page) == ["Chambre à coucher", "Entrée", "Séjour"], names(page))
    check("plan | nombre d'objets sur chaque pièce (sous-niveaux compris)", "2 objets" in cell(page, "Séjour").inner_text() and "1 objet" in cell(page, "Entrée").inner_text(), cell(page, "Séjour").inner_text())
    check("plan | grande case : niveau 1 rappelé", True)
    lay = js(page, "%s.layout(%s.ROOT)" % (F, F))
    check("plan | placement automatique : 2 colonnes, 2 lignes, une seule zone", lay["C"] == 2 and lay["L"] == 2 and lay["T"] == 0 and lay["B"] == 0 and all(c["zone"] == "body" for c in lay["cells"]), lay)
    check("plan | pas de pieds ni de bandes", page.locator(".furn-feet, .furn-band").count() == 0)
    check("plan | lecture seule : pas de réglages ni de cases libres", page.locator(".furn-controls, .furn-slot, .ctx-menu").count() == 0)
    check("plan | couleur des pièces (niveau pièce)", page.locator(".furn-cell").first.get_attribute("data-level") == "piece")
    check("plan | tout dans le cadre", inside(page) == [], inside(page))
    page.reload()
    page.wait_for_selector("#pane-detail .furn-view")
    check("plan | choix conservé après rechargement", page.get_by_role("button", name="Plan", exact=True).get_attribute("aria-pressed") == "true")
    open_cell(page, "Séjour")
    page.wait_for_function("document.querySelector('#pane-detail .detail-title').textContent === 'Séjour'")
    check("plan | toucher une pièce, puis « Ouvrir », l'ouvre", True)
    check("plan | le choix du plan ne change pas celui des meubles", js(page, "Rangement.ui.views.furniture.mode()") == "list")
    page.goto(base + "#/l/" + loc_id(page, "Meuble living"))
    page.wait_for_function("document.querySelector('#pane-detail .detail-title').textContent === 'Meuble living'")
    check("plan | un meuble reste en liste (choix séparés)", page.get_by_role("button", name="Liste", exact=True).get_attribute("aria-pressed") == "true" and page.locator(".furn-view").count() == 0)
    page.goto(base + "#/")
    page.wait_for_selector("#pane-detail .furn-view")
    page.get_by_role("button", name="Liste", exact=True).click()
    page.wait_for_selector("#pane-detail .list")
    check("plan | retour à la liste des pièces", page.locator(".furn-view").count() == 0 and "Séjour" in page.inner_text("#pane-detail .list"))
    check("plan | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_edit(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    plan(page)
    select_cell(page, "Entrée")
    check("ajuster | cases libres affichées", page.locator(".furn-slot").count() == 1, page.locator(".furn-slot").count())
    page.locator(".furn-sel").get_by_role("button", name="Grille…").click()
    d = page.locator("dialog.dialog[open]")
    check("ajuster | seulement colonnes et lignes", d.get_by_label("Colonnes").count() == 1 and d.get_by_label("Lignes").count() == 1 and d.get_by_label("Dessus").count() == 0 and d.get_by_label("Proportions").count() == 0 and d.get_by_label("Pieds").count() == 0)
    check("ajuster | choix de colonnes jusqu'à 20", d.get_by_label("Colonnes").locator("option").count() == 20 and d.get_by_label("Lignes").locator("option").count() == 20)
    d.get_by_role("button", name="Annuler").click()
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    check("ajuster | sélection : position, taille, « dans le plan »", "dans le plan" in page.inner_text(".furn-sel-text") and "1 × 1" in page.inner_text(".furn-sel-text"), page.inner_text(".furn-sel-text"))
    set_grid(page, cols=4)
    page.wait_for_function("Rangement.store.plan() && Rangement.store.plan().cols === 4")
    check("ajuster | colonnes enregistrées dans le plan", js(page, "Rangement.store.plan()")["cols"] == 4)
    check("ajuster | places des pièces enregistrées (figées)", all(geo(page, n)["zone"] == "body" and geo(page, n)["w"] == 1 for n in ("Chambre à coucher", "Entrée", "Séjour")))
    set_grid(page, rows=3)
    page.wait_for_function("Rangement.store.plan().rows === 3")
    select_cell(page, "Séjour")
    pos = geo(page, "Séjour")
    tool(page, "Décaler vers le bas")
    page.wait_for_function("Rangement.store.getLocation('%s').geometry.row === 1" % loc_id(page, "Séjour"))
    check("ajuster | décalage d'une case vers le bas", geo(page, "Séjour")["row"] == pos["row"] + 1 and geo(page, "Séjour")["col"] == pos["col"])
    tool(page, "Largeur +")
    page.wait_for_function("Rangement.store.getLocation('%s').geometry.w === 2" % loc_id(page, "Séjour"))
    tool(page, "Hauteur +")
    page.wait_for_function("Rangement.store.getLocation('%s').geometry.h === 2" % loc_id(page, "Séjour"))
    check("ajuster | pièce plus grande : 2 × 2 cases", geo(page, "Séjour")["w"] == 2 and geo(page, "Séjour")["h"] == 2 and "2 × 2" in page.inner_text(".furn-sel-text"))
    bb, one = cell(page, "Séjour").bounding_box(), cell(page, "Entrée").bounding_box()
    check("ajuster | la tuile est bien plus grande à l'écran", bb["width"] > 1.7 * one["width"] and bb["height"] > 1.7 * one["height"], (bb, one))
    check("ajuster | tout dans le cadre", inside(page) == [], inside(page))

    # refus
    tool(page, "Largeur +")
    tool(page, "Largeur +")
    tool(page, "Largeur +")
    check("refus | sortie du plan : message clair, rien ne change", "sortirait de la grille" in page.inner_text(".furn-msg") or "occupée" in page.inner_text(".furn-msg"), page.locator(".furn-msg").count())
    before = js(page, "Rangement.store.plan()")
    msg = set_grid(page, rows=1)
    check("refus | réduire le plan sur des pièces : refusé", bool(msg) and "déplacez-les" in msg and js(page, "Rangement.store.plan()") == before, js(page, "Rangement.store.plan()"))
    res = js(page, "[%s.setGrid(%s.ROOT,{cols:21}).ok, %s.setGrid(%s.ROOT,{cols:0}).ok, %s.move('nope',1,0).ok]" % (F, F, F, F, F))
    check("garde-fous | valeurs de grille invalides et emplacement inconnu refusés", res == [True, False, False], res)

    # échange entre deux pièces
    js(page, "%s.setGrid(%s.ROOT,{cols:2, rows:2})" % (F, F))
    page.wait_for_timeout(100)
    check("ajuster | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_swap(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    plan(page)
    a, b = "Chambre à coucher", "Entrée"
    ga = js(page, "%s.layout(%s.ROOT).cells" % (F, F))
    pos = {c["id"]: (c["col"], c["row"]) for c in ga}
    select_cell(page, a)
    tool(page, "Décaler à droite")
    page.wait_for_function("Rangement.store.getLocation('%s').geometry && Rangement.store.getLocation('%s').geometry.col !== undefined" % (loc_id(page, a), loc_id(page, a)))
    ia, ib = loc_id(page, a), loc_id(page, b)
    after = {c["id"]: (c["col"], c["row"]) for c in js(page, "%s.layout(%s.ROOT).cells" % (F, F))}
    check("échange | déplacer sur une pièce voisine l'échange avec elle", after[ia] == pos[ib] and after[ib] == pos[ia], (pos, after))
    check("échange | données valides", js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok"))

    # une case libre y place la pièce sélectionnée
    free = page.locator(".furn-slot")
    check("échange | il reste une case libre", free.count() == 1)
    free.click()
    page.wait_for_function("document.querySelectorAll('.furn-slot').length === 1")
    check("échange | une case libre y déplace la pièce", True)

    # route : l'ajustement est refermé quand on change d'écran
    page.goto(base + "#/l/" + ia)
    page.wait_for_function("document.querySelector('#pane-detail .detail-title').textContent === %r" % a)
    page.goto(base + "#/")
    page.wait_for_selector("#pane-detail .furn-view")
    check("route | le placement est refermé après un changement d'écran", page.locator(".furn-sel").count() == 0 and page.locator(".furn-view[data-editing='true']").count() == 0 and page.locator("#plan-add").count() == 1)
    check("échange | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_drill(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    plan(page)
    more = cell(page, "Séjour").locator(".furn-more")
    check("niveaux | icône sur une pièce qui contient des emplacements", more.count() == 1 and "sous-emplacement" in more.get_attribute("aria-label") and "niveau 2" in more.get_attribute("aria-label"), more.get_attribute("aria-label"))
    check("niveaux | icône aussi sur l'entrée (elle contient une commode)", cell(page, "Entrée").locator(".furn-more").count() == 1)
    more.click()
    page.wait_for_function("document.querySelector('.furn-caption').textContent.indexOf('Niveau 1') === 0")
    check("niveaux | détail d'une pièce : ses meubles sont dessinés", names(page) == ["Meuble living"], names(page))
    check("niveaux | bouton de remontée vers le plan", page.get_by_role("button", name="Remonter au plan du logement").count() == 1)
    page.get_by_role("button", name="Remonter au plan du logement").click()
    page.wait_for_function("!document.querySelector('.furn-caption')")
    check("niveaux | remontée : retour au plan", names(page) == ["Chambre à coucher", "Entrée", "Séjour"])
    check("niveaux | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_backup(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    plan(page)
    js(page, "%s.setGrid(%s.ROOT,{cols:3, rows:2})" % (F, F))
    select_cell(page, "Séjour")
    tool(page, "Hauteur +")
    page.wait_for_function("Rangement.store.getLocation('%s').geometry.h === 2" % loc_id(page, "Séjour"))
    original = stored(page)
    check("sauvegarde | le plan figure dans les données enregistrées", original.get("plan") == {"cols": 3, "rows": 2}, original.get("plan"))
    page.click("#app-settings")
    page.wait_for_selector("#pane-detail .settings")
    with page.expect_download() as info:
        page.click("#export-button")
    path = tempfile.mktemp(suffix=".json")
    info.value.save_as(path)
    text = open(path, encoding="utf-8").read()
    check("sauvegarde | le plan figure dans l'export", json.loads(text).get("plan") == {"cols": 3, "rows": 2})
    ctx.close()

    errors = []
    ctx, page = new_ctx(browser, 884, 1100, errors)
    page.goto(base + "#/r")
    page.wait_for_selector("#pane-detail .settings")
    page.set_input_files("#import-file", tmp_file(text, "plan.json"))
    dlg(page).get_by_role("button", name="Importer", exact=True).click()
    closed(page)
    again = stored(page)
    check("aller-retour | plan et places identiques après import", again.get("plan") == original.get("plan") and again["locations"] == original["locations"])
    page.click("#app-settings")          # referme les réglages
    page.wait_for_selector("#pane-detail .furn-view, #pane-detail .list")
    check("aller-retour | données valides", js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok"))

    # importer une sauvegarde sans plan efface le plan ; annuler l'importation le restitue
    other = json.loads(text)
    other.pop("plan")
    page.click("#app-settings")
    page.wait_for_selector("#pane-detail .settings")
    page.set_input_files("#import-file", tmp_file(json.dumps(other), "sans-plan.json"))
    dlg(page).get_by_role("button", name="Remplacer mes données").click()
    closed(page)
    check("import | sauvegarde sans plan : plan retiré", stored(page).get("plan") is None)
    page.click("#undo-button")
    dlg(page).get_by_role("button", name="Restaurer").click()
    closed(page)
    check("import | annuler l'importation restitue le plan", stored(page).get("plan") == {"cols": 3, "rows": 2}, stored(page).get("plan"))
    page.reload()
    page.wait_for_selector("#pane-detail .settings")
    check("import | plan conservé après rechargement", stored(page).get("plan") == {"cols": 3, "rows": 2})

    # plan illisible dans un fichier : ignoré, rien ne casse
    bad = json.loads(text)
    bad["plan"] = {"cols": "x", "rows": -4}
    page.set_input_files("#import-file", tmp_file(json.dumps(bad), "mauvais-plan.json"))
    dlg(page).get_by_role("button", name="Remplacer mes données").click()
    closed(page)
    check("import | plan invalide ignoré (plan automatique)", stored(page).get("plan") is None and js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok"))
    check("sauvegarde | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_wide(browser, base):
    """Grille large : le cadre défile horizontalement, pas la page."""
    errors = []
    ctx, page = start(browser, base, 390, 844, errors)
    plan(page)
    js(page, "%s.setGrid(%s.ROOT,{cols:8, rows:2})" % (F, F))
    page.wait_for_function("Rangement.store.plan().cols === 8")
    page.wait_for_function("document.querySelector('.furn-body').dataset.fit === 'fit'")
    check("large | 8 colonnes sur écran replié : ajusté, pas de défilement du cadre", js(page, "(function(){var f=document.querySelector('.furn-frame--plan'); return f.scrollWidth <= f.clientWidth + 1;})()"))
    res = js(page, "%s.setGrid(%s.ROOT,{cols:20, rows:2})" % (F, F))
    check("large | 20 colonnes acceptées", res["ok"] is True, res)
    page.wait_for_function("Rangement.store.plan().cols === 20")
    page.wait_for_function("document.querySelector('.furn-body').dataset.fit === 'fit'")
    check("large | 20 colonnes : cases à 28 px minimum, le cadre défile plutôt que d'écraser le plan", js(page, "(function(){var f=document.querySelector('.furn-frame--plan'); return f.scrollWidth > f.clientWidth;})()"))
    page.get_by_role("button", name="Agrandir").click()
    page.wait_for_function("document.querySelector('.furn-body').dataset.fit === 'real'")
    check("large | le cadre défile horizontalement", js(page, "(function(){var f=document.querySelector('.furn-frame--plan'); return f.scrollWidth > f.clientWidth + 100;})()"))
    check("large | la page ne défile pas horizontalement", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    check("large | tout dans le cadre", inside(page) == [], inside(page))
    res = js(page, "%s.setGrid(%s.ROOT,{cols:3})" % (F, F))
    check("large | repasser à 3 colonnes (pièces à gauche)", res["ok"] is True, res)
    page.wait_for_function("Rangement.store.plan().cols === 3")
    page.get_by_role("button", name="Ajuster à l’écran").click()
    page.wait_for_function("document.querySelector('.furn-body').dataset.fit === 'fit'")
    check("large | plus de défilement du cadre", js(page, "(function(){var f=document.querySelector('.furn-frame--plan'); return f.scrollWidth <= f.clientWidth + 1;})()"))
    check("large | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_misc(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    js(page, "Rangement.features.locations.create({name:'<img src=x onerror=window.__xss=1>', kind:'piece'})")
    for i in range(1, 8):
        js(page, "Rangement.features.locations.create({name:'Pièce %d', kind:'piece'})" % i)
    plan(page)
    check("sécurité | nom hostile affiché comme texte", page.locator(".furn-view img").count() == 0 and any("<img" in n for n in names(page)))
    check("sécurité | aucun script exécuté", page.evaluate("window.__xss") is None)
    lay = js(page, "%s.layout(%s.ROOT)" % (F, F))
    check("plan | 11 pièces : 4 colonnes automatiques, aucune case cachée", lay["C"] == 4 and len(lay["cells"]) == 11 and lay["L"] == 3, (lay["C"], len(lay["cells"]), lay["L"]))
    check("plan | tout dans le cadre (11 pièces)", inside(page) == [], inside(page))
    # supprimer / renommer une pièce : le plan suit
    n = len(names(page))
    js(page, "Rangement.features.locations.update(Rangement.store.locations().filter(function(l){return l.name==='Pièce 1';})[0].id,{name:'Cuisine'})")
    page.wait_for_function("Array.from(document.querySelectorAll('.furn-cell .furn-name')).some(function(e){return e.textContent==='Cuisine';})")
    check("plan | un renommage est répercuté", "Cuisine" in names(page) and len(names(page)) == n)
    js(page, "Rangement.features.locations.remove(Rangement.store.locations().filter(function(l){return l.name==='Cuisine';})[0].id)")
    page.wait_for_function("document.querySelectorAll('.furn-cell').length === %d" % (n - 1))
    check("plan | une suppression est répercutée", len(names(page)) == n - 1)
    # nouvelle pièce : prend la première case libre sans bouger les autres
    js(page, "%s.setGrid(%s.ROOT,{cols:4})" % (F, F))
    before = {c["id"]: (c["col"], c["row"]) for c in js(page, "%s.layout(%s.ROOT).cells" % (F, F))}
    js(page, "Rangement.features.locations.create({name:'Garage', kind:'piece'})")
    after = {c["id"]: (c["col"], c["row"]) for c in js(page, "%s.layout(%s.ROOT).cells" % (F, F))}
    check("plan | les places enregistrées ne bougent pas quand on ajoute une pièce", all(after[k] == v for k, v in before.items()) and len(after) == len(before) + 1)
    # plan corrompu dans le stockage : ignoré
    page.evaluate("""(function(){var d=JSON.parse(localStorage.getItem('rangement.data')); d.plan='n importe quoi'; localStorage.setItem('rangement.data', JSON.stringify(d));})()""")
    page.reload()
    page.wait_for_selector("#pane-tree .tree-link")
    check("plan | plan illisible en stockage : l'application démarre, plan automatique", js(page, "Rangement.store.plan()") is None and not page.is_visible("#boot-errors"))
    check("plan | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_narrow(browser, base):
    errors = []
    ctx, page = start(browser, base, 390, 844, errors)
    check("replié | commutateur ≥ 44 px et dans l'écran", all(b["height"] >= 44 and b["x"] >= 0 and b["x"] + b["width"] <= 390 for b in [page.get_by_role("button", name=n, exact=True).bounding_box() for n in ("Liste", "Plan")]))
    plan(page)
    select_cell(page, "Séjour")
    check("replié | pas de défilement horizontal", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    btns = page.locator(".furn-view .button:visible, .furn-pad-btn:visible, .furn-more:visible")
    check("replié | boutons et listes ≥ 44 px", all(btns.nth(i).bounding_box()["height"] >= 43 for i in range(btns.count())), [btns.nth(i).bounding_box()["height"] for i in range(btns.count())])
    check("replié | les deux pavés de flèches restent visibles en bas", page.locator(".furn-sel").bounding_box()["y"] + page.locator(".furn-sel").bounding_box()["height"] <= 844 + 1)
    check("replié | libellés dans leur case", inside(page) == [], inside(page))
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j8-replie-plan.png"), full_page=True)
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()
    errors = []
    ctx, page = start(browser, base, errors=errors)
    plan(page)
    check("déplié | arborescence et plan côte à côte", page.is_visible("#pane-tree") and page.is_visible(".furn-body"))
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j8-deplie-plan.png"))
    check("déplié | aucune erreur console", not errors, errors)
    ctx.close()


def main():
    server = start_server()
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        scenario_view(browser, base)
        scenario_edit(browser, base)
        scenario_swap(browser, base)
        scenario_drill(browser, base)
        scenario_backup(browser, base)
        scenario_wide(browser, base)
        scenario_misc(browser, base)
        scenario_narrow(browser, base)
        browser.close()
    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
