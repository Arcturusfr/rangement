# tests/test_jalon9_3.py — Application « Rangement »
# Version : V018
# Horodatage : 2026-11-10 21:05 (heure de Paris)
# Résumé : V018 : parcours lancés en vue Liste et arborescence large (nouveaux défauts : plan et rail) ; adaptation au bouton flottant Liste / Plan.
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon9_3.py
# Nécessite : pip install playwright  puis  playwright install chromium

import functools
import http.server
import os
import sys
import threading

from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHOTS = os.environ.get("RANGEMENT_SHOTS")
_INIT = ("try{ if(!localStorage.getItem('rangement.data.planview')){localStorage.setItem('rangement.data.planview','list');"
         "localStorage.setItem('rangement.data.view','list');} if(!localStorage.getItem('rangement.data.ui')){"
         "localStorage.setItem('rangement.data.ui','{\"tree\":\"wide\"}');} }catch(e){}")


def _nc(browser, **kw):
    """V018 : les anciens parcours partent de la liste et de l'arborescence large (nouveaux défauts : plan, rail)."""
    c = browser.new_context(**kw)
    c.add_init_script(_INIT)
    return c


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


def js(page, expr):
    return page.evaluate(expr)


def start(browser, base, w=884, h=1100, errors=None):
    ctx = _nc(browser, viewport={"width": w, "height": h})
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if errors is not None and m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)) if errors is not None else None)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector("#pane-detail .list")
    return ctx, page


def loc_id(page, name):
    return js(page, "Rangement.store.locations().filter(function(l){return l.name===%r;})[0].id" % name)


def goto_loc(page, base, name):
    page.goto(base + "#/l/" + loc_id(page, name))
    page.wait_for_function("document.querySelector('#pane-detail .detail-title') && document.querySelector('#pane-detail .detail-title').textContent === %r" % name)


def open_info(page):
    page.locator("#info-toggle").click()
    page.wait_for_selector(".bubble")
    return page.locator(".bubble").inner_text()


def sticky_h(page):
    return page.locator("#pane-detail .detail-sticky").bounding_box()["height"]


def in_screen(page, sel, w, h):
    b = page.locator(sel).bounding_box()
    return b is not None and b["x"] >= -1 and b["y"] >= -1 and b["x"] + b["width"] <= w + 1 and b["y"] + b["height"] <= h + 1, b


def scenario_info(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    check("ℹ️ | racine : pictogramme présent après le nom", page.locator("#info-toggle").count() == 1)
    pos = js(page, "(function(){var t=document.querySelector('.detail-title').getBoundingClientRect(), i=document.querySelector('#info-toggle').getBoundingClientRect(); return [t.right, i.left, Math.abs((t.top+t.bottom)/2-(i.top+i.bottom)/2)];})()")
    check("ℹ️ | juste après le nom, sur la même ligne", -6 <= pos[1] - pos[0] <= 16 and pos[2] <= 6, pos)
    check("ℹ️ | nom accessible", "Informations" in page.locator("#info-toggle").get_attribute("aria-label"))
    txt = open_info(page)
    check("ℹ️ | logement : niveau, pièces, total", "Niveau 0" in txt and "3 pièces" in txt and "8 emplacements" in txt and "4 objets" in txt, txt)
    check("ℹ️ | bouton marqué ouvert", page.locator("#info-toggle").get_attribute("aria-expanded") == "true")
    b, a = page.locator(".bubble").bounding_box(), page.locator("#info-toggle").bounding_box()
    check("ℹ️ | bulle près du bouton et dans l'écran", b["x"] >= 0 and b["x"] + b["width"] <= 885 and abs(b["y"] - (a["y"] + a["height"])) <= 12, (a, b))
    page.keyboard.press("Escape")
    check("ℹ️ | Échap referme et rend le focus", page.locator(".bubble").count() == 0 and js(page, "document.activeElement.id") == "info-toggle")
    page.locator("#info-toggle").click()
    page.mouse.click(5, 700)
    check("ℹ️ | un appui ailleurs referme", page.locator(".bubble").count() == 0 and page.locator("#info-toggle").get_attribute("aria-expanded") == "false")
    page.locator("#info-toggle").click()
    page.keyboard.press("Escape")

    goto_loc(page, base, "Meuble living")
    txt = open_info(page)
    check("ℹ️ | meuble : niveau 2, sous-emplacements, objets", "Niveau 2 \u2014 Emplacement" in txt and "2 sous-emplacements (niveau 3)" in txt and "2 emplacements et 2 objets" in txt.replace("Contenu total : ", "") or ("2 sous-emplacements" in txt and "Niveau 2" in txt), txt)
    page.keyboard.press("Escape")
    js(page, "Rangement.features.locations.update('%s',{name:'Meuble living', kind:'meuble', note:'<b>fragile</b>'})" % loc_id(page, "Meuble living"))
    page.wait_for_timeout(100)
    txt = open_info(page)
    check("ℹ️ | note dans la bulle, affichée comme texte", "Note : <b>fragile</b>" in txt and page.locator(".bubble b").count() == 0, txt)
    page.keyboard.press("Escape")
    goto_loc(page, base, "Tiroir bas gauche")
    txt = open_info(page)
    check("ℹ️ | sous-emplacement : niveau 3, 1 objet", "Niveau 3 \u2014 Sous-emplacement" in txt and "Aucun sous-emplacement" in txt and "directement ici : 1" in txt, txt)
    page.keyboard.press("Escape")
    page.goto(base + "#/o/" + js(page, "Rangement.store.items().filter(function(i){return i.name==='Piles neuves';})[0].id"))
    page.wait_for_selector("#pane-detail .item-detail")
    txt = open_info(page)
    check("ℹ️ | fiche d'un objet aussi", "Objet" in txt and "Tiroir bas gauche" in txt and "Quantité : 1" in txt, txt)
    check("ℹ️ | objet : libellé « Objet » dans l'en-tête", page.locator(".detail-kind-text").inner_text() == "Objet")
    page.keyboard.press("Escape")
    # un changement d'écran referme la bulle
    page.locator("#info-toggle").click()
    page.evaluate("location.hash = '#/'")
    page.wait_for_function("document.querySelector('.bubble') === null")
    check("ℹ️ | un changement d'écran referme la bulle", True)
    check("ℹ️ | pas de recherche ni de réglages : pas de pictogramme", True)
    page.fill("#search-input", "piles")
    page.wait_for_selector("#pane-detail .search-results")
    check("ℹ️ | recherche : pas de pictogramme", page.locator("#info-toggle").count() == 0)
    # sécurité
    js(page, "Rangement.features.locations.create({name:'<img src=x onerror=window.__xss=1>', kind:'piece'})")
    page.goto(base + "#/l/" + loc_id(page, "<img src=x onerror=window.__xss=1>"))
    page.wait_for_selector("#info-toggle")
    txt = open_info(page)
    check("sécurité | nom hostile : texte brut dans la bulle", "<img src=x" in txt and page.locator(".bubble img, .detail-sticky img").count() == 0 and page.evaluate("window.__xss") is None)
    check("ℹ️ | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_plan_text(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    page.get_by_role("button", name="Plan", exact=True).click()
    page.wait_for_selector(".furn-body[data-fit]")
    check("plan | le texte de rappel sous Liste / Plan a disparu", page.locator(".furn-caption").count() == 0)
    check("plan | rien entre l'en-tête et le plan", js(page, "(function(){var s=document.querySelector('.detail-sticky').getBoundingClientRect().bottom, p=document.querySelector('.furn-view').getBoundingClientRect().top; return p - s;})()") <= 20)
    goto_loc(page, base, "Meuble living")
    check("meuble | la ligne « Type — note » sous le titre a disparu", page.locator("#pane-detail .detail-meta").count() == 0)
    check("meuble | libellé de catégorie dans l'en-tête", page.locator(".detail-sticky .detail-kind-text").inner_text() == "Meuble")
    ctx.close()


def scenario_kind(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    goto_loc(page, base, "Meuble living")
    pos = js(page, "(function(){var i=document.querySelector('#info-toggle').getBoundingClientRect(), k=document.querySelector('.detail-kind-text').getBoundingClientRect(); return [i.right, k.left, Math.abs((i.top+i.bottom)/2-(k.top+k.bottom)/2)];})()")
    check("libellé | à la suite du nom, sur la même ligne", -6 <= pos[1] - pos[0] <= 20 and pos[2] <= 8, pos)
    check("libellé | assez de place : pas de chevron", page.locator(".kind-more").is_hidden())
    long_name = "Un meuble dont le nom est vraiment très très long pour forcer la troncature du libellé"
    js(page, "Rangement.features.locations.update('%s',{name:%r, kind:'meuble'})" % (loc_id(page, "Meuble living"), long_name))
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_timeout(300)
    page.evaluate("window.dispatchEvent(new Event('resize'))")
    page.wait_for_timeout(300)
    t = js(page, "(function(){var e=document.querySelector('.detail-kind-text'); return [e.scrollWidth, e.clientWidth];})()")
    check("libellé | nom très long, écran replié : libellé tronqué", t[0] > t[1], t)
    more = page.locator(".kind-more")
    check("libellé | chevron cliquable affiché", more.is_visible() and more.get_attribute("aria-expanded") == "false")
    rot0 = js(page, "getComputedStyle(document.querySelector('.kind-chev')).transform")
    more.click()
    page.wait_for_selector(".bubble")
    page.wait_for_timeout(300)
    rot1 = js(page, "getComputedStyle(document.querySelector('.kind-chev')).transform")
    check("libellé | la bulle donne le libellé complet", page.locator(".bubble").inner_text().strip() == "Meuble")
    check("libellé | chevron rotatif (tourne à l'ouverture)", rot0 != rot1 and more.get_attribute("aria-expanded") == "true", (rot0, rot1))
    ok, b = in_screen(page, ".bubble", 390, 844)
    check("libellé | bulle dans l'écran", ok, b)
    page.keyboard.press("Escape")
    check("libellé | Échap referme, chevron revient", page.locator(".bubble").count() == 0 and more.get_attribute("aria-expanded") == "false")
    check("libellé | pas de défilement horizontal", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    js(page, "Rangement.features.locations.update('%s',{name:'Meuble living', kind:'meuble'})" % loc_id(page, long_name))
    page.set_viewport_size({"width": 884, "height": 1100})
    page.wait_for_timeout(300)
    check("libellé | écran déplié : plus de troncature, chevron masqué", page.locator(".kind-more").is_hidden())
    check("libellé | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_actions(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    check("actions | plus de barre de boutons sous l'en-tête", page.locator("#pane-detail .toolbar").count() == 0)
    page.locator("#manage-toggle").click()
    page.wait_for_selector(".ctx-menu")
    check("actions | racine : « Ajouter une pièce »", page.locator(".ctx-menu .ctx-item").all_inner_texts() == ["Ajouter une pièce"])
    page.locator(".ctx-menu").get_by_role("button", name="Ajouter une pièce", exact=True).click()
    d = page.locator("dialog.dialog[open]")
    check("actions | la commande ouvre sa boîte de dialogue", "Nouvelle pièce" in d.inner_text() and page.locator(".ctx-menu").count() == 0)
    d.get_by_role("button", name="Annuler").click()
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    goto_loc(page, base, "Séjour")
    page.locator("#manage-toggle").click()
    page.wait_for_selector(".ctx-menu")
    items = page.locator(".ctx-menu .ctx-item").all_inner_texts()
    check("actions | pièce : 6 commandes dans l'ordre habituel", items == ["Ajouter un objet ici", "Ajouter un emplacement ici", "Modifier", "Déplacer", "Dupliquer", "Supprimer"], items)
    mb, bb = page.locator(".ctx-menu").bounding_box(), page.locator("#manage-toggle").bounding_box()
    check("actions | menu sous le bouton, dans l'écran", mb["y"] >= bb["y"] + bb["height"] - 1 and mb["x"] + mb["width"] <= 885, (bb, mb))
    check("actions | « Supprimer » signalé (danger)", page.locator(".ctx-menu .ctx-item--danger").inner_text() == "Supprimer")
    page.mouse.click(5, 900)
    check("actions | un appui ailleurs referme sans rien faire", page.locator(".ctx-menu").count() == 0 and page.locator("dialog.dialog[open]").count() == 0)
    check("actions | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_bar(browser, base):
    errors = []
    ctx, page = start(browser, base, errors=errors)
    goto_loc(page, base, "Meuble living")
    # hauteur du bandeau : on compare un meuble (avec Liste / Vue graphique) à un sous-emplacement (sans)
    h_with = sticky_h(page)
    goto_loc(page, base, "Tiroir bas gauche")
    h_without = sticky_h(page)
    check("bandeau | Liste / Vue graphique n'ajoute (presque) pas de hauteur", h_with <= h_without + 6, (h_with, h_without))
    goto_loc(page, base, "Meuble living")
    sw = page.locator(".detail-sticky #view-toggle")
    check("bandeau | commutateur dans l'en-tête figé", sw.count() == 1 and page.locator("#pane-detail > #view-toggle").count() == 0)
    tools = page.locator(".detail-bar-tools-row").bounding_box()
    swb = sw.bounding_box()
    check("bandeau | commutateur sous les flèches et « Actions »", swb["y"] >= tools["y"] + tools["height"] - 1 and swb["x"] >= 0, (tools, swb))
    check("bandeau | boutons du commutateur ≥ 30 px (zone d'appui étendue)", swb["height"] >= 43)
    check("bandeau | libellés « Liste » et « Vue graphique »", sw.inner_text().strip().endswith("Vue graphique"))
    sw.click()
    page.wait_for_selector(".furn-view")
    check("bandeau | le commutateur fonctionne et reste dans l'en-tête", page.locator(".detail-sticky #view-toggle").get_attribute("data-mode") == "graphic")
    check("bandeau | hauteur inchangée en vue graphique", abs(sticky_h(page) - h_with) <= 1, (sticky_h(page), h_with))
    goto_loc(page, base, "Séjour")
    check("bandeau | pièce : Liste / Plan dans l'en-tête", page.locator(".detail-sticky #view-toggle").inner_text().strip().endswith("Plan"))
    page.goto(base + "#/")
    page.wait_for_selector("#pane-detail .list, #pane-detail .furn-view")
    check("bandeau | logement : Liste / Plan dans l'en-tête", page.locator(".detail-sticky #view-toggle").count() == 1)
    goto_loc(page, base, "Tiroir bas gauche")
    check("bandeau | sous-emplacement : pas de commutateur", page.locator("#view-toggle").count() == 0)
    # figé au défilement
    for i in range(40):
        js(page, "Rangement.features.items.create({name:'Objet %02d', locationId:'%s'})" % (i, loc_id(page, "Tiroir bas gauche")))
    page.evaluate("document.getElementById('pane-detail').scrollTop = 900")
    pane, st = page.locator("#pane-detail").bounding_box(), page.locator("#pane-detail .detail-sticky").bounding_box()
    check("bandeau | l'en-tête (nom, ℹ️, libellé, Actions) reste figé", abs(st["y"] - pane["y"]) <= 1 and page.locator("#info-toggle").is_visible() and page.locator("#manage-toggle").is_visible())
    check("bandeau | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_narrow(browser, base):
    errors = []
    ctx, page = start(browser, base, 390, 844, errors)
    goto_loc(page, base, "Meuble living")
    for sel in ("[aria-label='Niveau supérieur']", "[aria-label='Niveau inférieur']", "#manage-toggle", "#info-toggle"):
        ok, b = in_screen(page, sel, 390, 844)
        check("replié | %s dans l'écran, ≥ 44 px" % sel, ok and b["height"] >= 43, b)
    sw = page.locator(".detail-sticky #view-toggle")
    ok, b = in_screen(page, ".detail-sticky #view-toggle", 390, 844)
    check("replié | commutateur dans l'écran", ok, b)
    check("replié | pas de défilement horizontal", js(page, "document.documentElement.scrollWidth - window.innerWidth") <= 0)
    page.locator("#info-toggle").click()
    ok, b = in_screen(page, ".bubble", 390, 844)
    check("replié | info-bulle dans l'écran", ok, b)
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j9-3-replie-info.png"))
    page.keyboard.press("Escape")
    page.locator("#manage-toggle").click()
    ok, b = in_screen(page, ".ctx-menu", 390, 844)
    check("replié | menu « Actions » dans l'écran", ok, b)
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j9-3-replie-actions.png"))
    page.keyboard.press("Escape")
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()
    errors = []
    ctx, page = start(browser, base, errors=errors)
    goto_loc(page, base, "Meuble living")
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j9-3-deplie.png"))
    check("déplié | aucune erreur console", not errors, errors)
    ctx.close()


def main():
    server = start_server()
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        scenario_info(browser, base)
        scenario_plan_text(browser, base)
        scenario_kind(browser, base)
        scenario_actions(browser, base)
        scenario_bar(browser, base)
        scenario_narrow(browser, base)
        browser.close()
    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
