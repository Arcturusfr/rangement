# tests/test_jalon14.py — Application « Rangement »
# Version : V023b
# Horodatage : 2026-11-27 01:20 (heure de Paris)
# Résumé : jalon 14 (V023, V023a, V023b) : pieds « Sans / Petits / Grands / Très grands » (grands = pieds de la hauteur du cadre, très grands = 3 × le cadre) ; bande « Dessous » entre les pieds ; ancienne valeur « avec » lue comme « petits » ; meubles non « Haut » entièrement visibles à l'écran.
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon14.py
# Nécessite : pip install playwright  puis  playwright install chromium

import functools
import http.server
import os
import sys
import threading

from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
F = "Rangement.features.furniture"
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
    ctx = browser.new_context(viewport={"width": w, "height": h})
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector(".furn-body[data-fit]")
    return ctx, page


def loc_id(page, name):
    return js(page, "Rangement.store.locations().filter(function(l){return l.name===%r;})[0].id" % name)


def goto_meuble(page, base):
    page.goto(base + "#/l/" + loc_id(page, "Meuble living"))
    page.wait_for_function("document.querySelector('#pane-detail .detail-title') && document.querySelector('#pane-detail .detail-title').textContent === 'Meuble living'")
    page.wait_for_selector(".furn-body:not([data-plan])")
    page.wait_for_timeout(150)


def geo(page, name):
    return js(page, "Rangement.store.getLocation(%r).geometry" % loc_id(page, name))


def sizes(page):
    """[hauteur du cadre du meuble, hauteur de la zone des pieds]"""
    return js(page, "(function(){return [document.querySelector('.furn-body').getBoundingClientRect().height, document.querySelector('.furn-legs').getBoundingClientRect().height];})()")


def wait_legs(page):
    page.wait_for_function("(function(){var l=document.querySelector('.furn-legs'); return !!l && l.style.minHeight !== '';})()")
    page.wait_for_timeout(100)


def open_grid(page):
    page.locator("#manage-toggle").click()
    page.locator(".ctx-menu").get_by_role("button", name="Régler la grille…", exact=True).click()
    return page.locator("dialog.dialog[open]")


def apply_grid(page, **kw):
    d = open_grid(page)
    labels = {"bottom": "Dessous", "feet": "Pieds"}
    for k, v in kw.items():
        d.get_by_label(labels[k]).select_option(str(v))
    d.get_by_role("button", name="Appliquer").click()
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    page.wait_for_timeout(150)


def valid(page):
    return js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok")


def scenario_model(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1000, errors)
    mid = loc_id(page, "Meuble living")
    check("modèle | sans réglage : pas de pieds", js(page, "%s.get('%s').feet" % (F, mid)) is False)
    js(page, "Rangement.store.update(function(d){ d.locations.forEach(function(l){ if (l.id==='%s') { l.geometry = { feet: true }; } }); })" % mid)
    check("migration | l'ancienne valeur « avec » (true) est lue comme « petits »", js(page, "%s.get('%s').feet" % (F, mid)) == "petits")
    goto_meuble(page, base)
    check("migration | dessinés comme des petits pieds", page.locator(".furn-feet").count() == 1 and page.locator(".furn-legs").count() == 0)
    res = js(page, "%s.set('%s', {ratio: 1.5})" % (F, mid))
    check("migration | un enregistrement sans toucher aux pieds les conserve", res["ok"] is True and js(page, "%s.get('%s').feet" % (F, mid)) == "petits")
    check("modèle | set : 'grands' enregistré", js(page, "[%s.set('%s', {feet:'grands'}).ok, %s.get('%s').feet, Rangement.store.getLocation('%s').geometry.feet]" % (F, mid, F, mid, mid)) == [True, "grands", "grands"])
    check("modèle | set : valeur inconnue = sans pieds", js(page, "[%s.set('%s', {feet:'enormes'}).ok, %s.get('%s').feet, Rangement.store.getLocation('%s').geometry.feet]" % (F, mid, F, mid, mid)) == [True, False, False])
    sej = loc_id(page, "Séjour")
    js(page, "%s.setGrid('%s', {cols:2})" % (F, sej))
    js(page, "Rangement.store.update(function(d){ d.locations.forEach(function(l){ if (l.id==='%s') { l.geometry.feet = 'grands'; } }); })" % sej)
    check("modèle | une pièce (plan) n'a jamais de pieds", js(page, "%s.get('%s').feet" % (F, sej)) is False)
    check("modèle | données valides", valid(page))
    check("modèle | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_dialog(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1000, errors)
    goto_meuble(page, base)
    d = open_grid(page)
    opts = d.get_by_label("Pieds").locator("option").all_inner_texts()
    check("boîte | Pieds : Sans, Petits, Grands, Très grands", opts == ["Sans", "Petits", "Grands", "Très grands"], opts)
    check("boîte | valeur de départ : Sans", d.get_by_label("Pieds").input_value() == "0")
    check("boîte | indication sur les grands pieds", "hauteur totale" in d.inner_text(), d.inner_text())
    d.get_by_role("button", name="Annuler").click()
    page.wait_for_selector("dialog.dialog[open]", state="detached")

    apply_grid(page, feet=1)
    check("petits | enregistrés ('petits') et dessinés", geo(page, "Meuble living")["feet"] == "petits" and page.locator(".furn-feet").count() == 1 and page.locator(".furn-legs").count() == 0)
    d = open_grid(page)
    check("petits | la boîte rouverte propose Petits", d.get_by_label("Pieds").input_value() == "1")
    d.get_by_role("button", name="Annuler").click()
    page.wait_for_selector("dialog.dialog[open]", state="detached")

    apply_grid(page, feet=2)
    wait_legs(page)
    check("grands | enregistrés ('grands')", geo(page, "Meuble living")["feet"] == "grands")
    check("grands | deux grands pieds dans une zone dédiée, plus de petits pieds", page.locator(".furn-legs .furn-foot--tall").count() == 2 and page.locator(".furn-feet").count() == 0)
    b, l = sizes(page)
    check("grands | sans bande : la zone des pieds fait la hauteur du cadre (moitié de la hauteur totale)", abs(l - b) <= 2, (b, l))
    f0, f1 = page.locator(".furn-foot--tall").nth(0).bounding_box(), page.locator(".furn-foot--tall").nth(1).bounding_box()
    body = page.locator(".furn-body").bounding_box()
    check("grands | pieds aussi hauts que le cadre, collés sous le cadre, aux deux extrémités", abs(f0["height"] - b) <= 2 and abs(f1["height"] - b) <= 2 and f0["y"] >= body["y"] + body["height"] - 1 and f0["x"] < f1["x"], (f0, f1, body))
    check("grands | pieds dans le cadre de la page", f0["x"] >= 0 and f1["x"] + f1["width"] <= body["x"] + body["width"] + 1)
    check("grands | les cases du meuble restent dans le cadre", js(page, """(function(){var b=document.querySelector('.furn-body').getBoundingClientRect(); return Array.prototype.every.call(document.querySelectorAll('.furn-body .furn-cell'), function(c){var r=c.getBoundingClientRect(); return r.left>=b.left-1&&r.right<=b.right+1&&r.top>=b.top-1&&r.bottom<=b.bottom+1;});})()"""))

    page.reload()
    page.wait_for_selector(".furn-legs")
    wait_legs(page)
    check("grands | conservés après rechargement", page.locator(".furn-legs").count() == 1)
    export = js(page, "JSON.parse(Rangement.features.backup.prepareExport().text).locations.filter(function(l){return l.name==='Meuble living';})[0].geometry.feet")
    check("grands | présents dans l'export", export == "grands", export)

    apply_grid(page, feet=0)
    check("sans | retour sans pieds", page.locator(".furn-legs, .furn-feet").count() == 0 and geo(page, "Meuble living")["feet"] is False)
    check("boîte | données valides", valid(page))
    check("boîte | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_band(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1000, errors)
    goto_meuble(page, base)
    mid = loc_id(page, "Meuble living")
    apply_grid(page, bottom=1, feet=2)
    wait_legs(page)
    band = page.locator(".furn-legs .furn-legs-mid .furn-band[data-zone='bottom']")
    check("bande | « Dessous » placée dans la zone des pieds, entre eux", band.count() == 1 and "En dessous du meuble" in band.inner_text())
    bb = band.bounding_box()
    f0, f1 = page.locator(".furn-foot--tall").nth(0).bounding_box(), page.locator(".furn-foot--tall").nth(1).bounding_box()
    check("bande | entre le pied gauche et le pied droit", bb["x"] >= f0["x"] + f0["width"] - 1 and bb["x"] + bb["width"] <= f1["x"] + 1, (f0, bb, f1))
    body = page.locator(".furn-body").bounding_box()
    check("bande | sous le cadre du meuble", bb["y"] >= body["y"] + body["height"] - 1)
    b, l = sizes(page)
    check("bande | la zone des pieds fait au moins la hauteur du cadre", l >= b - 2, (b, l))
    lb = page.locator(".furn-legs").bounding_box()
    check("bande | la bande tient dans la zone des pieds", bb["y"] + bb["height"] <= lb["y"] + lb["height"] + 1, (bb, lb))

    # un emplacement placé dans la bande « Dessous » s'y dessine
    tg = loc_id(page, "Tiroir bas gauche")
    res = js(page, "%s.move('%s', 0, 1)" % (F, tg))
    check("bande | un emplacement peut être placé dans la bande", res["ok"] is True and geo(page, "Tiroir bas gauche")["zone"] == "bottom", res)
    page.wait_for_selector(".furn-legs .furn-cell")
    check("bande | l'emplacement est dessiné entre les pieds", page.locator(".furn-legs .furn-cell .furn-name").all_inner_texts() == ["Tiroir bas gauche"])
    page.wait_for_timeout(100)
    cb, lb = page.locator(".furn-legs .furn-cell").bounding_box(), page.locator(".furn-legs").bounding_box()
    check("bande | la case reste dans la zone des pieds", cb["y"] >= lb["y"] - 1 and cb["y"] + cb["height"] <= lb["y"] + lb["height"] + 1, (cb, lb))
    # appui long dans la bande : menu de case
    b0 = page.locator(".furn-legs .furn-cell").bounding_box()
    page.mouse.move(b0["x"] + b0["width"] / 2, b0["y"] + b0["height"] / 2)
    page.mouse.down()
    page.wait_for_timeout(650)
    page.mouse.up()
    page.wait_for_selector(".ctx-menu")
    check("bande | un appui long sur la case ouvre son menu", page.locator(".ctx-menu .ctx-item").first.inner_text() == "Ouvrir")
    page.keyboard.press("Escape")

    # petits pieds : la bande reste sous les pieds, hors de la zone des grands pieds
    apply_grid(page, feet=1)
    check("petits | la bande reste sous les petits pieds (hors zone des grands pieds)", page.locator(".furn-feet").count() == 1 and page.locator(".furn-legs").count() == 0 and page.locator(".furn-band[data-zone='bottom']").count() == 1)
    check("bande | données valides", valid(page))
    check("bande | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_resize(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1000, errors)
    goto_meuble(page, base)
    js(page, "%s.set('%s', {feet:'grands'})" % (F, loc_id(page, "Meuble living")))
    wait_legs(page)
    b1, l1 = sizes(page)
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_function("document.documentElement.dataset.panes === '1'")
    page.wait_for_timeout(400)
    b2, l2 = sizes(page)
    check("redimensionnement | écran replié : les pieds suivent la nouvelle hauteur du cadre", b2 != b1 and abs(l2 - b2) <= 2, (b1, l1, b2, l2))
    check("redimensionnement | pas de défilement horizontal", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    f = page.locator(".furn-foot--tall").nth(1).bounding_box()
    check("redimensionnement | pied droit dans l'écran", f["x"] + f["width"] <= 391, f)
    page.set_viewport_size({"width": 884, "height": 1000})
    page.wait_for_function("document.documentElement.dataset.panes === '2'")
    page.wait_for_timeout(400)
    b3, l3 = sizes(page)
    check("redimensionnement | retour à l'écran déplié", abs(l3 - b3) <= 2 and abs(b3 - b1) <= 2, (b1, b3, l3))
    # niveau plus bas dessiné comme un meuble : mêmes pieds
    tg = loc_id(page, "Tiroir bas gauche")
    js(page, "Rangement.features.locations.create({name:'Boîte', kind:'boite', parentId:'%s'})" % tg)
    js(page, "%s.set('%s', {feet:'grands'})" % (F, tg))
    page.goto(base + "#/l/" + tg)
    page.wait_for_function("document.querySelector('#pane-detail .detail-title').textContent === 'Tiroir bas gauche'")
    page.wait_for_selector(".furn-legs")
    wait_legs(page)
    b4, l4 = sizes(page)
    check("niveaux | un niveau plus bas dessiné peut aussi avoir de grands pieds", abs(l4 - b4) <= 2, (b4, l4))
    check("redimensionnement | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_tres_grands(browser, base):
    errors = []
    ctx, page = start(browser, base, 884, 1000, errors)
    goto_meuble(page, base)
    mid = loc_id(page, "Meuble living")
    check("très grands | valeur enregistrée lue telle quelle", js(page, "[%s.set('%s', {feet:'tres-grands'}).ok, %s.get('%s').feet]" % (F, mid, F, mid)) == [True, "tres-grands"])
    page.reload()
    page.wait_for_selector(".furn-legs")
    wait_legs(page)
    check("très grands | pieds dessinés dans la zone dédiée", page.locator(".furn-legs[data-feet='tres-grands'] .furn-foot--tall").count() == 2 and page.locator(".furn-feet").count() == 0)
    js(page, "%s.set('%s', {feet:false})" % (F, mid))
    page.wait_for_selector(".furn-body:not([data-plan])")
    apply_grid(page, bottom=1, feet=3)
    wait_legs(page)
    check("très grands | choix « Très grands » enregistré", geo(page, "Meuble living")["feet"] == "tres-grands")
    d = open_grid(page)
    check("très grands | la boîte rouverte propose Très grands", d.get_by_label("Pieds").input_value() == "3")
    d.get_by_role("button", name="Annuler").click()
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    b, l = sizes(page)
    check("très grands | pieds = 75 % de la hauteur totale (3 × le cadre)", abs(l - 3 * b) <= 3 and abs(l / (l + b) - 0.75) <= 0.01, (b, l))
    f0, f1 = page.locator(".furn-foot--tall").nth(0).bounding_box(), page.locator(".furn-foot--tall").nth(1).bounding_box()
    check("très grands | chaque pied fait 3 × le cadre", abs(f0["height"] - 3 * b) <= 3 and abs(f1["height"] - 3 * b) <= 3, (f0, f1, b))
    bb = page.locator(".furn-legs .furn-band[data-zone='bottom']").bounding_box()
    check("très grands | la bande « Dessous » est entre les pieds", bb["x"] >= f0["x"] + f0["width"] - 1 and bb["x"] + bb["width"] <= f1["x"] + 1)

    # ajout d'un emplacement dans la bande (case libre, appui long)
    slot = page.locator(".furn-legs .furn-slot").first
    sb = slot.bounding_box()
    page.mouse.move(sb["x"] + sb["width"] / 2, sb["y"] + sb["height"] / 2)
    page.mouse.down()
    page.wait_for_timeout(650)
    page.mouse.up()
    page.wait_for_selector(".ctx-menu")
    check("très grands | appui long sur une case libre entre les pieds : menu de création", "Ajouter un emplacement ici" in page.locator(".ctx-menu").inner_text() and "Ajouter un objet ici" in page.locator(".ctx-menu").inner_text())
    page.locator(".ctx-menu").get_by_role("button", name="Ajouter un emplacement ici", exact=True).click()
    dd = page.locator("dialog.dialog[open]")
    dd.get_by_label("Nom").fill("Dessous de table")
    dd.get_by_role("button", name="Ajouter", exact=True).click()
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    page.wait_for_selector(".furn-legs .furn-cell:has-text('Dessous de table')")
    g = geo(page, "Dessous de table")
    check("très grands | l'emplacement créé est placé dans la bande « Dessous », entre les pieds", g["zone"] == "bottom" and page.locator(".furn-legs .furn-cell .furn-name").all_inner_texts().count("Dessous de table") == 1, g)
    # bande pleine : « Ajouter un emplacement ici » du menu « Actions » reste possible ; une ligne de plus rend une case libre
    page.locator("#manage-toggle").click()
    check("très grands | « Ajouter un emplacement ici » reste proposé dans « Actions »", page.locator(".ctx-menu").get_by_role("button", name="Ajouter un emplacement ici", exact=True).count() == 1)
    page.keyboard.press("Escape")
    js(page, "%s.setGrid('%s', {bottom:2})" % (F, mid))
    page.wait_for_selector(".furn-legs .furn-slot")
    wait_legs(page)
    page.wait_for_timeout(150)
    # appui long dans le vide entre les pieds : la case libre la plus proche est choisie
    page.evaluate("document.getElementById('pane-detail').scrollTop = 100000")
    page.wait_for_timeout(150)
    lb = page.locator(".furn-legs").bounding_box()
    page.mouse.move(lb["x"] + lb["width"] / 2, min(lb["y"] + lb["height"] - 20, 960))
    page.mouse.down()
    page.wait_for_timeout(650)
    page.mouse.up()
    page.wait_for_selector(".ctx-menu")
    check("très grands | appui long dans le vide entre les pieds : menu de la case libre la plus proche", "Case libre" in page.locator(".ctx-menu").inner_text())
    page.keyboard.press("Escape")
    # objets : toujours possible via le menu « Actions » et via le menu d'une case
    page.locator("#manage-toggle").click()
    check("très grands | « Ajouter un objet ici » reste proposé dans « Actions »", page.locator(".ctx-menu").get_by_role("button", name="Ajouter un objet ici", exact=True).count() == 1)
    page.locator(".ctx-menu").get_by_role("button", name="Ajouter un objet ici", exact=True).click()
    dd = page.locator("dialog.dialog[open]")
    dd.get_by_label("Nom").fill("Nappe")
    dd.get_by_role("button", name="Ajouter", exact=True).click()
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    check("très grands | un objet peut être ajouté", len(js(page, "Rangement.store.itemsIn('%s').filter(function(i){return i.name==='Nappe';})" % mid)) == 1)
    # meuble sans aucun sous-emplacement (table) : cases libres présentes, création possible
    js(page, "Rangement.features.locations.create({name:'Table', kind:'meuble', parentId:'%s'})" % loc_id(page, "Séjour"))
    page.goto(base + "#/l/" + loc_id(page, "Table"))
    page.wait_for_function("document.querySelector('#pane-detail .detail-title').textContent === 'Table'")
    page.wait_for_selector(".furn-body:not([data-plan])")
    js(page, "%s.set('%s', {feet:'tres-grands'})" % (F, loc_id(page, "Table")))
    page.wait_for_selector(".furn-legs")
    wait_legs(page)
    check("très grands | table sans emplacement : cases libres dans le plateau", page.locator(".furn-body .furn-slot").count() >= 1)
    b, l = sizes(page)
    check("très grands | table : pieds à 75 %", abs(l - 3 * b) <= 3, (b, l))
    # écran replié
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_function("document.documentElement.dataset.panes === '1'")
    page.wait_for_timeout(400)
    b, l = sizes(page)
    check("très grands | écran replié : pieds toujours à 3 × le cadre", abs(l - 3 * b) <= 3, (b, l))
    check("très grands | écran replié : pas de défilement horizontal", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    check("très grands | données valides", valid(page))
    check("très grands | aucune erreur console", not errors, errors)
    ctx.close()


def fits(page):
    """Le cadre du meuble (bandes et pieds compris) tient dans le volet de détail, défilement en haut."""
    page.evaluate("document.getElementById('pane-detail').scrollTop = 0")
    page.wait_for_timeout(120)
    fr, pane = page.locator(".furn-frame").bounding_box(), page.locator("#pane-detail").bounding_box()
    return fr["y"] + fr["height"] <= pane["y"] + pane["height"] + 1, (fr, pane)


def settle_fit(page):
    page.wait_for_function("document.querySelector('.furn-body') && document.querySelector('.furn-body').getAttribute('data-furn-fit') === '1'")
    page.wait_for_timeout(200)


def scenario_fit_screen(browser, base):
    errors = []
    for (w, h) in ((884, 1000), (390, 844)):
        ctx, page = start(browser, base, w, h, errors)
        goto_meuble(page, base)
        mid = loc_id(page, "Meuble living")
        js(page, "%s.setGrid('%s', {bottom:1})" % (F, mid))
        for feet in ("tres-grands", "grands", "petits", False):
            js(page, "%s.set('%s', {feet:%s})" % (F, mid, "false" if feet is False else repr(feet)))
            page.wait_for_selector(".furn-body:not([data-plan])")
            settle_fit(page)
            ok, d = fits(page)
            check("écran | %dx%d, pieds %s : le meuble tient entièrement à l'écran" % (w, h, feet or "sans"), ok, d)
            if feet in ("tres-grands", "grands"):
                b, l = sizes(page)
                fct = 3 if feet == "tres-grands" else 1
                check("écran | %dx%d, pieds %s : proportions des pieds conservées (× %d)" % (w, h, feet, fct), abs(l - fct * b) <= 3, (b, l))
        # proportions « Carré » et « Très large », avec bande du dessus
        js(page, "%s.setGrid('%s', {top:1})" % (F, mid))
        for ratio in (1, 2.2):
            js(page, "%s.set('%s', {ratio:%s, feet:'petits'})" % (F, mid, ratio))
            settle_fit(page)
            ok, d = fits(page)
            check("écran | %dx%d, proportions %s + bande du dessus : tient à l'écran" % (w, h, ratio), ok, d)
        # « Haut » : inchangé (hauteur = largeur / 0,7), pas d'ajustement
        js(page, "%s.set('%s', {ratio:0.7})" % (F, mid))
        page.wait_for_selector(".furn-body:not([data-plan])")
        page.wait_for_timeout(300)
        bb = page.locator(".furn-body").bounding_box()
        check("écran | %dx%d, proportions « Haut » : pas d'ajustement, hauteur = largeur / 0,7" % (w, h), js(page, "document.querySelector('.furn-body').hasAttribute('data-furn-fit')") is False and abs(bb["height"] - bb["width"] / 0.7) <= 3, bb)
        # table sans emplacement, très grands pieds : plateau plat, tient à l'écran, création possible
        js(page, "Rangement.features.locations.create({name:'Table', kind:'meuble', parentId:'%s'})" % loc_id(page, "Séjour"))
        page.goto(base + "#/l/" + loc_id(page, "Table"))
        page.wait_for_function("document.querySelector('#pane-detail .detail-title').textContent === 'Table'")
        page.wait_for_selector(".furn-body:not([data-plan])")
        js(page, "%s.set('%s', {feet:'tres-grands'})" % (F, loc_id(page, "Table")))
        page.wait_for_selector(".furn-legs")
        settle_fit(page)
        ok, d = fits(page)
        check("écran | %dx%d, table à très grands pieds : tient à l'écran" % (w, h), ok, d)
        check("écran | %dx%d, table : cases libres dans le plateau" % (w, h), page.locator(".furn-body .furn-slot").count() >= 1)
        page.locator("#manage-toggle").click()
        check("écran | %dx%d, table : « Ajouter un emplacement / un objet ici » proposés" % (w, h), page.locator(".ctx-menu").get_by_role("button", name="Ajouter un emplacement ici", exact=True).count() == 1 and page.locator(".ctx-menu").get_by_role("button", name="Ajouter un objet ici", exact=True).count() == 1)
        page.keyboard.press("Escape")
        check("écran | %dx%d, pas de défilement horizontal" % (w, h), js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
        ctx.close()
    check("écran | aucune erreur console", not errors, errors)


def main():
    server = QuietServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=ROOT))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        scenario_model(browser, base)
        scenario_dialog(browser, base)
        scenario_band(browser, base)
        scenario_resize(browser, base)
        scenario_tres_grands(browser, base)
        scenario_fit_screen(browser, base)
        browser.close()
    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
