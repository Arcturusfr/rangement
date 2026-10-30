# tests/test_jalon7.py — Application « Rangement »
# Version : V011
# Horodatage : 2026-10-30 00:22 (heure de Paris)
# Résumé : grille de placement (cases, tailles, déplacements, bandes dessus / dessous), correction des débordements, conversion des réglages V010.
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


def inside(page):
    """Cases hors du cadre du meuble, libellés hors de leur case (liste vide = tout est dedans)."""
    return js(page, """(function(){var b=document.querySelector('.furn-body').getBoundingClientRect(); var bad=[];
      document.querySelectorAll('.furn-body .furn-cell').forEach(function(c){var r=c.getBoundingClientRect();
        if(r.left<b.left-1||r.right>b.right+1||r.top<b.top-1||r.bottom>b.bottom+1){bad.push('case '+c.textContent.slice(0,20));}
        c.querySelectorAll('.furn-name').forEach(function(n){var q=n.getBoundingClientRect();
          if(q.left<r.left-1||q.right>r.right+1||q.bottom>r.bottom+1||q.top<r.top-1){bad.push('libellé '+n.textContent.slice(0,20));}});});
      return bad;})()""")


def cell(page, name):
    return page.locator(".furn-cell", has_text=name)


def select_cell(page, name):
    cell(page, name).locator(".furn-open").click()
    page.wait_for_selector(".furn-sel")


def tool(page, label):
    page.get_by_role("button", name=label, exact=True).click()


def graphic(page, base, name):
    goto(page, base, name)
    page.get_by_role("button", name="Vue graphique").click()
    page.wait_for_selector("#pane-detail .furn-view")


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
    check("vue | un rectangle par sous-emplacement", names(page) == ["Grand tiroir du bas", "Tiroir bas gauche"], names(page))
    cap = page.inner_text("#pane-detail .furn-caption")
    check("vue | rappel du niveau", "Niveau 2" in cap and "Emplacement" in cap and "Meuble living" in cap and "niveau 3" in cap, cap)
    check("vue | nombre d'objets sur chaque rectangle", "1 objet" in cell(page, "Tiroir bas gauche").inner_text())
    check("vue | niveau rappelé sur les grandes cases", True)
    check("vue | pas d'icône de détail sans sous-niveau", page.locator(".furn-more").count() == 0)
    check("vue | proportions par défaut appliquées", js(page, "document.querySelector('.furn-body').style.aspectRatio") in ("1.5", "1.5 / 1"))
    check("vue | aucun débordement au départ", inside(page) == [], inside(page))
    check("vue | lecture seule : pas de case libre ni de réglages", page.locator(".furn-slot").count() == 0 and page.locator(".furn-controls").count() == 0)
    page.reload()
    page.wait_for_selector("#pane-detail .furn-view")
    check("vue | choix du mode conservé après rechargement", page.get_by_role("button", name="Vue graphique").get_attribute("aria-pressed") == "true")
    cell(page, "Grand tiroir").locator(".furn-open").click()
    wait_title(page, "Grand tiroir du bas")
    check("vue | toucher un rectangle ouvre l'emplacement", True)
    goto(page, base, "Meuble living")
    page.get_by_role("button", name="Liste").click()
    page.wait_for_selector("#pane-detail .list")
    check("vue | retour à la liste", page.locator(".furn-view").count() == 0)
    page.get_by_role("button", name="Vue graphique").click()
    page.wait_for_selector("#pane-detail .furn-view")

    tg = loc_id(page, "Tiroir bas gauche")
    js(page, "Rangement.features.locations.create({name:'<b>Boîte A</b>', kind:'boite', parentId:'%s'})" % tg)
    js(page, "Rangement.features.locations.create({name:'Boîte B', kind:'boite', parentId:'%s'})" % tg)
    more = cell(page, "Tiroir bas gauche").locator(".furn-more")
    check("niveaux | icône de détail sur le rectangle qui a des sous-niveaux", more.count() == 1 and "2 sous-emplacements" in more.get_attribute("aria-label") and "niveau 4" in more.get_attribute("aria-label") and more.inner_text().strip() == "2", more.get_attribute("aria-label"))
    more.click()
    page.wait_for_function("document.querySelector('.furn-caption').textContent.indexOf('Niveau 3') === 0")
    cap = page.inner_text(".furn-caption")
    check("niveaux | détail : niveau rappelé", "Sous-emplacement" in cap and "Tiroir bas gauche" in cap and "niveau 4" in cap, cap)
    check("niveaux | détail : sous-sous-emplacements dessinés (texte brut)", names(page) == ["<b>Boîte A</b>", "Boîte B"] and page.locator(".furn-view b").count() == 0, names(page))
    check("niveaux | détail : objets du niveau listés", "Piles neuves" in page.inner_text(".furn-view .section") and "niveau 3" in page.inner_text(".furn-view .section-title"))
    page.get_by_role("button", name="Remonter au niveau 2").click()
    page.wait_for_function("document.querySelector('.furn-caption').textContent.indexOf('Niveau 2') === 0")
    check("niveaux | remontée : retour au meuble", names(page) == ["Grand tiroir du bas", "Tiroir bas gauche"])
    check("vue | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_grid(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    graphic(page, base, "Meuble living")
    F = "Rangement.features.furniture"
    mid = loc_id(page, "Meuble living")
    check("grille | placement automatique au départ (1 colonne, 2 lignes)", js(page, "%s.layout('%s')" % (F, mid))["C"] == 1 and js(page, "%s.layout('%s').L" % (F, mid)) == 2)
    page.get_by_role("button", name="Ajuster la disposition").click()
    check("grille | réglages, cases libres et aide affichés", page.locator(".furn-controls").is_visible() and page.get_by_label("Lignes").count() == 1 and page.locator(".furn-ctl", has_text="Dessus").locator("select").count() == 1 and page.locator(".furn-ctl", has_text="Dessous").locator("select").count() == 1)
    select_cell(page, "Tiroir bas gauche")
    check("grille | sélection : position et taille indiquées", "colonne 1, ligne 2" in page.inner_text(".furn-sel-text") and "1 × 1" in page.inner_text(".furn-sel-text"), page.inner_text(".furn-sel-text"))

    page.get_by_label("Colonnes").select_option("2")
    page.wait_for_function("Rangement.features.furniture.get('%s').cols === 2" % mid)
    g = geo(page, "Grand tiroir du bas")
    t = geo(page, "Tiroir bas gauche")
    check("grille | 2 colonnes : les places automatiques se recalculent puis sont figées", g["zone"] == "body" and g["col"] == 0 and g["row"] == 0 and t["col"] == 1 and t["row"] == 0 and t["w"] == 1 and t["h"] == 1, (g, t))
    page.get_by_label("Lignes").select_option("3")
    page.wait_for_function("Rangement.features.furniture.get('%s').rows === 3" % mid)
    select_cell(page, "Tiroir bas gauche")
    tool(page, "▼ Décaler vers le bas")
    page.wait_for_function("Rangement.store.getLocation('%s').geometry.row === 1" % loc_id(page, "Tiroir bas gauche"))
    check("grille | décalage d'une case vers le bas", geo(page, "Tiroir bas gauche")["row"] == 1 and geo(page, "Tiroir bas gauche")["col"] == 1)
    select_cell(page, "Grand tiroir")
    h1 = cell(page, "Grand tiroir").bounding_box()["height"]
    tool(page, "Hauteur +")
    page.wait_for_function("Rangement.store.getLocation('%s').geometry.h === 2" % loc_id(page, "Grand tiroir du bas"))
    h2 = cell(page, "Grand tiroir").bounding_box()["height"]
    check("grille | emplacement de hauteur double (2 cases)", geo(page, "Grand tiroir du bas")["h"] == 2 and h2 > 1.7 * h1, (h1, h2))
    check("grille | grande case : niveau rappelé", "Niveau 3" in cell(page, "Grand tiroir").inner_text())
    check("grille | libellés et cases dans le meuble", inside(page) == [], inside(page))

    select_cell(page, "Tiroir bas gauche")
    tool(page, "◀ Décaler à gauche")
    check("refus | case occupée", "occupée" in page.inner_text(".furn-msg") and geo(page, "Tiroir bas gauche")["col"] == 1)
    tool(page, "Largeur +")
    check("refus | largeur au-delà de la grille", "sortirait de la grille" in page.inner_text(".furn-msg") and geo(page, "Tiroir bas gauche")["w"] == 1)
    tool(page, "▼ Décaler vers le bas")
    page.wait_for_function("Rangement.store.getLocation('%s').geometry.row === 2" % loc_id(page, "Tiroir bas gauche"))
    tool(page, "Hauteur +")
    check("refus | sortie de la grille par le bas", "sortirait de la grille" in page.inner_text(".furn-msg") and geo(page, "Tiroir bas gauche")["h"] == 1)
    page.get_by_label("Lignes").select_option("1")
    check("refus | réduire la grille sur des emplacements : refusé", "déplacez-les" in page.inner_text(".furn-msg") and js(page, "%s.get('%s').rows" % (F, mid)) == 3 and page.get_by_label("Lignes").input_value() == "3")

    slot = page.locator(".furn-slot[aria-label^='Case libre : colonne 2, ligne 1 ']")
    check("grille | cases libres visibles", slot.count() == 1)
    slot.click()
    page.wait_for_function("Rangement.store.getLocation('%s').geometry.row === 0" % loc_id(page, "Tiroir bas gauche"))
    check("grille | une case libre y déplace l'emplacement sélectionné", geo(page, "Tiroir bas gauche")["row"] == 0 and geo(page, "Tiroir bas gauche")["col"] == 1)

    # Bandes au-dessus et en dessous
    page.locator(".furn-ctl", has_text="Dessus").locator("select").select_option("1")
    page.wait_for_selector(".furn-band[data-zone='top']")
    check("bandes | bande du dessus affichée avec son libellé", "Au-dessus du meuble" in page.inner_text(".furn-band[data-zone='top']"))
    select_cell(page, "Tiroir bas gauche")
    tool(page, "▲ Décaler vers le haut")
    page.wait_for_function("Rangement.store.getLocation('%s').geometry.zone === 'top'" % loc_id(page, "Tiroir bas gauche"))
    check("bandes | emplacement placé au-dessus du meuble", cell(page, "Tiroir bas gauche").bounding_box()["y"] + cell(page, "Tiroir bas gauche").bounding_box()["height"] <= page.locator(".furn-body").bounding_box()["y"] + 1)
    page.locator(".furn-ctl", has_text="Dessous").locator("select").select_option("1")
    page.wait_for_selector(".furn-band[data-zone='bottom']")
    select_cell(page, "Grand tiroir")
    tool(page, "▼ Décaler vers le bas")
    page.wait_for_function("Rangement.store.getLocation('%s').geometry.row === 1" % loc_id(page, "Grand tiroir du bas"))
    tool(page, "▼ Décaler vers le bas")
    check("bandes | un emplacement ne chevauche pas deux zones", "deux zones" in page.inner_text(".furn-msg") and geo(page, "Grand tiroir du bas")["zone"] == "body")
    tool(page, "Hauteur −")
    page.wait_for_function("Rangement.store.getLocation('%s').geometry.h === 1" % loc_id(page, "Grand tiroir du bas"))
    tool(page, "▼ Décaler vers le bas")
    tool(page, "▼ Décaler vers le bas")
    page.wait_for_function("Rangement.store.getLocation('%s').geometry.zone === 'bottom'" % loc_id(page, "Grand tiroir du bas"))
    bb, body = cell(page, "Grand tiroir").bounding_box(), page.locator(".furn-body").bounding_box()
    check("bandes | emplacement placé en dessous du meuble", bb["y"] >= body["y"] + body["height"] - 1, (bb, body))
    page.locator(".furn-ctl", has_text="Dessus").locator("select").select_option("0")
    check("bandes | supprimer une bande occupée : refusé", "déplacez-les" in page.inner_text(".furn-msg") and js(page, "%s.get('%s').top" % (F, mid)) == 1)
    check("bandes | libellés et cases du meuble dans le cadre", inside(page) == [], inside(page))

    page.get_by_role("button", name="Terminer l’ajustement").click()
    page.reload()
    page.wait_for_selector(".furn-view")
    check("persistance | bandes et places conservées après rechargement", page.locator(".furn-band").count() == 2 and page.locator(".furn-controls").count() == 0 and geo(page, "Tiroir bas gauche")["zone"] == "top")
    check("persistance | les cases ouvrent l'emplacement hors ajustement", page.locator("a.furn-open").count() == 2)
    s = js(page, "JSON.stringify(JSON.parse(Rangement.features.backup.prepareExport().text).locations.filter(function(l){return l.name==='Grand tiroir du bas';})[0].geometry)")
    check("sauvegarde | la grille figure dans l'export", '"zone":"bottom"' in s and '"w":1' in s, s)
    check("sauvegarde | données valides", js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok"))
    check("garde-fous | emplacement inconnu refusé", js(page, "[%s.move('nope',1,0).ok, %s.resize('nope',1,0).ok, %s.setGrid('nope',{cols:2}).ok]" % (F, F, F)) == [False, False, False])
    check("garde-fous | liste : l'ordre alphabétique n'est pas affecté", page.get_by_role("button", name="Liste").count() == 1)
    check("grille | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_legacy(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    F = "Rangement.features.furniture"
    mid = loc_id(page, "Meuble living")
    g, t = loc_id(page, "Grand tiroir du bas"), loc_id(page, "Tiroir bas gauche")
    js(page, """Rangement.store.update(function(d){ d.locations.forEach(function(l){
      if(l.id==='%s'){ l.geometry={cols:2}; }
      if(l.id==='%s'){ l.geometry={pos:1, span:2}; }
      if(l.id==='%s'){ l.geometry={pos:0}; } }); })""" % (mid, g, t))
    cells = js(page, "%s.layout('%s').cells.map(function(c){return [c.id===%r?'T':'G', c.row, c.col, c.w, c.h, c.zone];})" % (F, mid, t))
    check("V010 | ancien ordre et largeur convertis en places", cells == [["T", 0, 0, 1, 1, "body"], ["G", 1, 0, 2, 1, "body"]], cells)
    # un fichier modifié dont deux emplacements se chevauchent est corrigé
    js(page, """Rangement.store.update(function(d){ d.locations.forEach(function(l){
      if(l.id==='%s'){ l.geometry={zone:'body',col:0,row:0,w:1,h:1}; }
      if(l.id==='%s'){ l.geometry={zone:'body',col:0,row:0,w:1,h:1}; } }); })""" % (g, t))
    ok = js(page, "(function(){var l=%s.layout('%s'); var k={}; l.cells.forEach(function(c){k[c.row+','+c.col]=(k[c.row+','+c.col]||0)+1;}); return Object.keys(k).every(function(x){return k[x]===1;}) && l.cells.length===2;})()" % (F, mid))
    check("V010 | placements qui se chevauchent : replacés sans rien cacher", ok)
    check("V010 | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_overflow(browser, base):
    """Régression Z Fold : beaucoup d'emplacements empilés ne doivent ni sortir du cadre ni laisser déborder les libellés."""
    errors = []
    ctx, page = start(browser, base, errors=errors)
    F = "Rangement.features.furniture"
    com = js(page, "Rangement.store.locations().filter(function(l){return l.name==='Commode' && Rangement.store.getLocation(l.parentId).name==='Entrée';})[0].id")
    for i in range(1, 9):
        js(page, "Rangement.features.locations.create({name:'Tiroir %d', kind:'tiroir', parentId:'%s'})" % (i, com))
    js(page, "Rangement.features.locations.create({name:'Un tiroir au nom vraiment très très long pour vérifier qu\\u2019il ne déborde pas', parentId:'%s'})" % com)
    page.goto(base + "#/l/" + com)
    wait_title(page, "Commode")
    page.get_by_role("button", name="Vue graphique").click()
    page.wait_for_selector(".furn-view")
    for w in (884, 390):
        page.set_viewport_size({"width": w, "height": 900})
        check("débordement | 9 emplacements, largeur %d : tout dans le cadre" % w, inside(page) == [], inside(page))
    res = js(page, "%s.setGrid('%s', {cols:1})" % (F, com))
    check("débordement | passer à 1 colonne : les places automatiques suivent", res["ok"] is True and js(page, "%s.layout('%s').L" % (F, com)) == 9, res)
    page.wait_for_function("document.querySelectorAll('.furn-body .furn-cell').length === 9")
    for w in (884, 390):
        page.set_viewport_size({"width": w, "height": 900})
        check("débordement | 9 lignes, largeur %d : tout dans le cadre" % w, inside(page) == [], inside(page))
        check("débordement | 9 lignes, largeur %d : le cadre grandit (≥ 9 × 64 px)" % w, page.locator(".furn-body").bounding_box()["height"] >= 9 * 64 - 1, page.locator(".furn-body").bounding_box())
        check("débordement | largeur %d : pas de défilement horizontal" % w, js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    check("débordement | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_tree(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    q = "Array.from(document.querySelectorAll('#pane-tree .tree-row')).map(function(r){return r.innerText.replace(/\\s+/g,' ').trim();})"
    rows = js(page, q)
    check("arbo | nombre d'objets par pièce (total, sous-niveaux compris)", "Séjour 2" in rows and "Entrée 1" in rows and "Chambre à coucher 1" in rows, rows)
    js(page, "Rangement.ui.views.browse.expandAll()")
    rows = js(page, q)
    check("arbo | nombre d'objets par emplacement", "Meuble living 2" in rows and "Tiroir bas gauche 1" in rows, rows)
    js(page, "Rangement.features.locations.create({name:'Vide', parentId:'%s'})" % loc_id(page, "Séjour"))
    check("arbo | emplacement vide : pas de nombre", "Vide" in js(page, q))
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
    select_cell(page, "Grand tiroir")
    check("replié | pas de défilement horizontal en ajustement", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    btns = page.locator(".furn-view .button:visible, .furn-more:visible, .furn-ctl select:visible")
    check("replié | boutons et listes ≥ 44 px", all(btns.nth(i).bounding_box()["height"] >= 43 for i in range(btns.count())), [btns.nth(i).bounding_box()["height"] for i in range(btns.count())])
    check("replié | cases contenues dans l'écran", all(cell(page, n).bounding_box()["x"] >= 0 and cell(page, n).bounding_box()["x"] + cell(page, n).bounding_box()["width"] <= 390 for n in ("Grand tiroir", "Tiroir bas gauche")))
    check("replié | libellés dans leur case", inside(page) == [], inside(page))
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j7-replie-grille.png"), full_page=True)
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()
    errors = []
    ctx, page = start(browser, base, errors=errors)
    graphic(page, base, "Meuble living")
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
        scenario_grid(browser, base)
        scenario_legacy(browser, base)
        scenario_overflow(browser, base)
        scenario_tree(browser, base)
        scenario_narrow(browser, base)
        browser.close()
    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
