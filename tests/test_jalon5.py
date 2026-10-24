# tests/test_jalon5.py — Application « Rangement »
# Version : V007
# Horodatage : 2026-10-24 22:30 (heure de Paris)
# Résumé : création — tests Playwright/Chromium du jalon 5 (sauvegarde : export / import JSON, écran Réglages).
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon5.py
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
    handler = functools.partial(QuietHandler, directory=ROOT)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def new_page(browser, width, height, errors, init_script=None, accept_downloads=True):
    ctx = browser.new_context(viewport={"width": width, "height": height}, accept_downloads=accept_downloads)
    if init_script:
        ctx.add_init_script(init_script)
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    return ctx, page


# ---------- aides ----------

def dlg(page):
    return page.locator("dialog.dialog[open]")


def closed(page):
    page.wait_for_selector("dialog.dialog[open]", state="detached")


def load_demo(page):
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector("#pane-detail .list")


def go_settings(page):
    page.click("#app-settings")
    page.wait_for_selector("#pane-detail .settings")


def stored(page):
    return page.evaluate("JSON.parse(localStorage.getItem('rangement.data'))")


def js(page, expr):
    return page.evaluate(expr)


def tmp_file(content, name="sauvegarde.json"):
    d = tempfile.mkdtemp()
    path = os.path.join(d, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def do_export(page):
    with page.expect_download() as info:
        page.click("#export-button")
    dl = info.value
    path = tempfile.mktemp(suffix=".json")
    dl.save_as(path)
    with open(path, encoding="utf-8") as f:
        return dl.suggested_filename, f.read()


def import_file(page, path):
    page.set_input_files("#import-file", path)


# ---------- scénarios ----------

def scenario_flow(browser, base, label):
    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")

    # Accès aux réglages, même sans données
    check(label + " | lien « Réglages » dans l'en-tête", page.locator("#app-settings").count() == 1 and page.is_visible("#app-settings"))
    check(label + " | écran de démarrage : bouton d'importation", page.get_by_role("link", name="Importer une sauvegarde").count() == 1)
    go_settings(page)
    check(label + " | adresse #/r", page.evaluate("location.hash") == "#/r")
    check(label + " | titre Réglages", page.inner_text("#pane-detail .detail-title") == "Réglages")
    check(label + " | lien d'en-tête marqué actif", page.get_attribute("#app-settings", "aria-current") == "page")
    check(label + " | arborescence : rien de surligné sur les réglages", page.locator("#pane-tree [aria-current='page']").count() == 0)
    check(label + " | sans donnée : export désactivé", page.is_disabled("#export-button"))
    check(label + " | version affichée dans « À propos »", "V" in page.inner_text("#pane-detail .settings") and page.inner_text("#app-version").strip() in page.inner_text("#pane-detail .settings"))

    # Import dans un logement vide
    demo_src = js(page, "JSON.stringify(Rangement.features.demo.build())")
    path = tmp_file(demo_src)
    import_file(page, path)
    d = dlg(page)
    check(label + " | import (vide) : confirmation avec résumé du fichier", "Importer cette sauvegarde" in d.inner_text() and "8 emplacements" in d.inner_text() and "4 objets" in d.inner_text() and "vide" in d.inner_text(), d.inner_text())
    d.get_by_role("button", name="Annuler").click()
    closed(page)
    check(label + " | import annulé : rien n'est importé", js(page, "localStorage.getItem('rangement.data')") is None or len(stored(page)["locations"]) == 0)
    import_file(page, path)
    dlg(page).get_by_role("button", name="Importer", exact=True).click()
    closed(page)
    check(label + " | import (vide) : données chargées", len(stored(page)["locations"]) == 8 and len(stored(page)["items"]) == 4)
    check(label + " | import : message de confirmation", "Importation terminée" in page.inner_text("#pane-detail .settings"))
    check(label + " | import : arborescence mise à jour", page.locator("#pane-tree .tree-link").count() == 8)
    check(label + " | données importées valides", js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok"))

    # Export
    check(label + " | avant export : avertissement « aucune sauvegarde »", "Aucune sauvegarde" in page.inner_text("#pane-detail .settings"))
    name, text = do_export(page)
    check(label + " | export : nom de fichier horodaté", name.startswith("rangement-") and name.endswith(".json") and len(name) == len("rangement-2026-10-24-2230.json"), name)
    data = json.loads(text)
    check(label + " | export : contenu complet", data["schemaVersion"] == 1 and len(data["locations"]) == 8 and len(data["items"]) == 4 and data.get("exportedAt") and data.get("appVersion"), list(data.keys()))
    check(label + " | export : identique aux données enregistrées", data["locations"] == stored(page)["locations"] and data["items"] == stored(page)["items"])
    check(label + " | export : message de confirmation", "Sauvegarde exportée" in page.inner_text("#pane-detail .settings"))
    check(label + " | après export : statut « aucune modification depuis »", "Aucune modification depuis" in page.inner_text("#pane-detail .settings"))

    # Modification : le statut le signale
    page.goto(base + "#/")
    page.wait_for_selector("#pane-detail .list")
    js(page, "Rangement.features.locations.create({name:'Garage', kind:'piece'})")
    go_settings(page)
    check(label + " | après modification : statut « modifications depuis »", "Des modifications ont été faites depuis" in page.inner_text("#pane-detail .settings"))
    page.reload()
    page.wait_for_selector("#pane-detail .settings")
    check(label + " | suivi conservé après rechargement", "Des modifications ont été faites depuis" in page.inner_text("#pane-detail .settings"))

    # Import qui remplace : confirmation, copie de sécurité, annulation
    check(label + " | import dans un logement vide : copie de sécurité vide proposée", page.locator("#undo-button").count() == 1)
    other = json.loads(demo_src)
    other["locations"] = other["locations"][:2]
    keep = {l["id"] for l in other["locations"]}
    other["items"] = [i for i in other["items"] if i["locationId"] in keep]
    other["exportedAt"] = "2026-01-02T10:30:00.000Z"
    path2 = tmp_file(json.dumps(other), "autre.json")
    before = stored(page)
    import_file(page, path2)
    d = dlg(page)
    txt = d.inner_text()
    check(label + " | import (remplacement) : résumé fichier et données actuelles", "autre.json" in txt and "2 emplacements" in txt and "9 emplacements" in txt and "remplacées" in txt and "copie de sécurité" in txt, txt)
    check(label + " | import : date de la sauvegarde mentionnée", "janvier 2026" in txt, txt)
    d.get_by_role("button", name="Remplacer mes données").click()
    closed(page)
    after = stored(page)
    check(label + " | import : données remplacées", len(after["locations"]) == 2, len(after["locations"]))
    check(label + " | import : statut « modifications » (le contenu a changé)", "Des modifications ont été faites depuis" in page.inner_text("#pane-detail .settings"))
    check(label + " | bouton « Annuler la dernière importation » proposé", page.locator("#undo-button").count() == 1)
    check(label + " | copie de sécurité enregistrée", js(page, "JSON.parse(localStorage.getItem('rangement.data.preimport')).data.locations.length") == 9)

    page.click("#undo-button")
    d = dlg(page)
    check(label + " | annulation : confirmation", "Annuler la dernière importation" in d.inner_text() and "9 emplacements" in d.inner_text(), d.inner_text())
    d.get_by_role("button", name="Annuler", exact=True).click()
    closed(page)
    check(label + " | annulation refusée : données inchangées", len(stored(page)["locations"]) == 2)
    page.click("#undo-button")
    dlg(page).get_by_role("button", name="Restaurer").click()
    closed(page)
    restored = stored(page)
    check(label + " | annulation : données d'avant restaurées", restored["locations"] == before["locations"] and restored["items"] == before["items"])
    check(label + " | annulation : bouton retiré", page.locator("#undo-button").count() == 0)
    check(label + " | annulation : copie de sécurité supprimée", js(page, "localStorage.getItem('rangement.data.preimport')") is None)
    check(label + " | annulation : message de confirmation", "Données restaurées" in page.inner_text("#pane-detail .settings"))

    # Le message de confirmation disparaît quand on quitte l'écran
    page.click("#pane-detail .button:has-text('Retour au logement')")
    page.wait_for_selector("#pane-detail .list")
    go_settings(page)
    check(label + " | message de confirmation effacé après navigation", "Données restaurées" not in page.inner_text("#pane-detail .settings"))
    page.click("#pane-detail .button:has-text('Retour au logement')")
    page.wait_for_function("document.getElementById('app-settings').getAttribute('aria-current') === null")
    check(label + " | hors réglages : aria-current retiré", page.get_attribute("#app-settings", "aria-current") is None)

    check(label + " | données valides à la fin", js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok"))
    check(label + " | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_invalid(browser, base):
    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    load_demo(page)
    go_settings(page)
    snapshot = js(page, "localStorage.getItem('rangement.data')")

    def refused(name, content, expected, fname="x.json"):
        import_file(page, tmp_file(content, fname))
        page.wait_for_selector("dialog.dialog[open]")
        d = dlg(page)
        txt = d.inner_text()
        ok = "Importation impossible" in txt and expected in txt
        check("refus | " + name, ok, txt)
        d.get_by_role("button", name="OK").click()
        closed(page)
        check("refus | " + name + " : données intactes", js(page, "localStorage.getItem('rangement.data')") == snapshot)

    refused("fichier vide", "   ", "vide")
    refused("pas du JSON", "{pas du json", "JSON valide")
    refused("tableau JSON", "[1,2,3]", "pas une sauvegarde")
    refused("schéma inconnu", '{"schemaVersion":99,"locations":[],"items":[]}', "format de données différent")
    refused("schéma absent", '{"locations":[],"items":[]}', "version inconnue")
    refused("listes absentes", '{"schemaVersion":1}', "pas une sauvegarde")
    refused("parent introuvable", json.dumps({"schemaVersion": 1, "locations": [{"id": "a", "parentId": "zzz", "name": "A"}], "items": []}), "incohérentes")
    refused("objet sans emplacement", json.dumps({"schemaVersion": 1, "locations": [{"id": "a", "name": "A"}], "items": [{"id": "i", "locationId": "nope", "name": "x", "quantity": 1, "tags": []}]}), "incohérentes")
    refused("quantité invalide", json.dumps({"schemaVersion": 1, "locations": [{"id": "a", "name": "A"}], "items": [{"id": "i", "locationId": "a", "name": "x", "quantity": -3, "tags": []}]}), "incohérentes")
    loop = json.dumps({"schemaVersion": 1, "locations": [{"id": "a", "parentId": "b", "name": "A"}, {"id": "b", "parentId": "a", "name": "B"}], "items": []})
    refused("boucle dans l'arborescence", loop, "incohérentes")

    check("refus | aucune copie de sécurité créée par un refus", js(page, "localStorage.getItem('rangement.data.preimport')") is None)

    # Fichier minimal valide (champs facultatifs absents, champs inconnus ignorés)
    minimal = json.dumps({"schemaVersion": 1, "extra": "x", "locations": [{"id": "a", "name": "Cave", "zzz": 1}], "items": [{"id": "i", "locationId": "a", "name": "Vin", "quantity": 6, "tags": ["rouge"]}]})
    import_file(page, tmp_file(minimal, "mini.json"))
    dlg(page).get_by_role("button", name="Remplacer mes données").click()
    closed(page)
    s = stored(page)
    check("import minimal | accepté et complété", len(s["locations"]) == 1 and s["locations"][0]["kind"] == "autre" and s["locations"][0]["note"] == "" and s["locations"][0]["parentId"] is None and "zzz" not in s["locations"][0], s["locations"])
    check("import minimal | objet conservé avec note vide", s["items"][0]["quantity"] == 6 and s["items"][0]["note"] == "" and s["items"][0]["tags"] == ["rouge"])
    check("import minimal | données valides", js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok"))

    # Fichier avec BOM
    bom = "\ufeff" + json.dumps({"schemaVersion": 1, "locations": [{"id": "a", "name": "BOM"}], "items": []})
    import_file(page, tmp_file(bom, "bom.json"))
    dlg(page).get_by_role("button", name="Remplacer mes données").click()
    closed(page)
    check("import BOM | accepté", stored(page)["locations"][0]["name"] == "BOM")

    # Texte hostile : jamais interprété comme du HTML
    hostile = json.dumps({"schemaVersion": 1, "locations": [{"id": "a", "name": "<img src=x onerror=window.__xss=1>"}], "items": [{"id": "i", "locationId": "a", "name": "<b>gras</b>", "quantity": 1, "tags": []}]})
    import_file(page, tmp_file(hostile, "<img src=x onerror=window.__xss=2>.json"))
    d = dlg(page)
    check("sécurité | nom de fichier affiché comme texte", d.locator("img").count() == 0 and "<img src=x" in d.inner_text())
    d.get_by_role("button", name="Remplacer mes données").click()
    closed(page)
    page.click("#pane-detail .button:has-text('Retour au logement')")
    page.wait_for_selector("#pane-detail .list")
    check("sécurité | données importées affichées comme texte", page.locator("#pane-tree img, #pane-detail img").count() == 0 and "<img src=x" in page.inner_text("#pane-tree"))
    check("sécurité | aucun script exécuté", page.evaluate("window.__xss") is None)
    check("refus | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_roundtrip(browser, base):
    """Exporter puis réimporter sur un autre appareil (contexte vierge) redonne exactement les mêmes données."""
    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    load_demo(page)
    js(page, "Rangement.features.items.create({name:'Zéro', locationId: Rangement.store.locations()[0].id, quantity:'0', tags:'a, b', note:'ligne1\\nligne2'})")
    js(page, "Rangement.features.locations.create({name:'Étagère « test »', kind:'etagere', note:'n', parentId: Rangement.store.locations()[0].id})")
    go_settings(page)
    name, text = do_export(page)
    original = stored(page)
    ctx.close()

    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    go_settings(page)
    import_file(page, tmp_file(text, name))
    dlg(page).get_by_role("button", name="Importer", exact=True).click()
    closed(page)
    again = stored(page)
    check("aller-retour | emplacements identiques", again["locations"] == original["locations"])
    check("aller-retour | objets identiques (quantité 0, mots-clés, note)", again["items"] == original["items"])
    check("aller-retour | recherche opérationnelle après import", js(page, "Rangement.features.search.search('zero').items.length") == 1)
    page.reload()
    page.wait_for_selector("#pane-detail .settings")
    check("aller-retour | persistance après rechargement", stored(page)["items"] == original["items"])
    check("aller-retour | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_no_storage(browser, base):
    errors = []
    script = "Object.defineProperty(window,'localStorage',{get(){throw new DOMException('denied','SecurityError');}});"
    ctx, page = new_page(browser, 884, 1100, errors, script)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    go_settings(page)
    check("sans stockage | réglages accessibles", page.inner_text("#pane-detail .detail-title") == "Réglages")
    check("sans stockage | mention du stockage indisponible", "indisponible" in page.inner_text("#pane-detail .settings"))
    d = '{"schemaVersion":1,"locations":[{"id":"a","name":"Salon"}],"items":[]}'
    import_file(page, tmp_file(d))
    dlg(page).get_by_role("button", name="Importer", exact=True).click()
    closed(page)
    check("sans stockage | import fonctionnel en mémoire", page.locator("#pane-tree .tree-link").count() == 1)
    name, text = do_export(page)
    check("sans stockage | export fonctionnel", len(json.loads(text)["locations"]) == 1)
    check("sans stockage | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_logic(browser, base):
    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    B = "Rangement.features.backup"
    check("logique | nom de fichier", js(page, "%s.fileName(new Date(2026, 9, 4, 8, 5))" % B) == "rangement-2026-10-04-0805.json")
    check("logique | parse : texte non texte refusé", js(page, "%s.parse(null).ok" % B) is False)
    big = "x" * 4600000
    check("logique | parse : fichier trop volumineux refusé", js(page, "%s.parse('%s').ok" % (B, big)) is False)
    check("logique | annuler sans copie refusé", js(page, "%s.undoImport().ok" % B) is False)
    check("logique | pas de copie de sécurité au départ", js(page, "%s.undoInfo()" % B) is None)
    check("logique | statut initial", js(page, "%s.status()" % B) == {"lastExportAt": None, "dirty": False, "counts": {"locations": 0, "items": 0}})
    # Un quota plein empêche d'importer sans copie de sécurité
    load_demo(page)
    js(page, "window.__orig = Storage.prototype.setItem; Storage.prototype.setItem = function(k){ if (typeof k === 'string' && k.indexOf('preimport') !== -1) { throw new DOMException('full','QuotaExceededError'); } return window.__orig.apply(this, arguments); }; null")
    res = js(page, "%s.importData(%s.parse(JSON.stringify({schemaVersion:1,locations:[{id:'z',name:'Z'}],items:[]})).data)" % (B, B))
    check("logique | copie de sécurité impossible : import refusé", res["ok"] is False and "copie de sécurité" in res["error"], res)
    check("logique | import refusé : données intactes", len(stored(page)["locations"]) == 8)
    js(page, "Storage.prototype.setItem = window.__orig; null")
    check("logique | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_narrow(browser, base):
    errors = []
    ctx, page = new_page(browser, 390, 844, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    load_demo(page)
    check("replié | 1 volet", page.get_attribute("html", "data-panes") == "1")
    box = page.locator("#app-settings").bounding_box()
    check("replié | lien « Réglages » ≥ 44 px et dans l'écran", box["height"] >= 44 and box["x"] >= 0 and box["x"] + box["width"] <= 390, box)
    hb = page.locator(".app-header").bounding_box()
    check("replié | en-tête compact (≤ 80 px)", hb["height"] <= 80, hb)
    go_settings(page)
    overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    check("replié | réglages : pas de défilement horizontal", overflow <= 0, overflow)
    buttons = page.locator("#pane-detail .settings .button:not([disabled])")
    check("replié | boutons des réglages ≥ 44 px", all(buttons.nth(i).bounding_box()["height"] >= 44 for i in range(buttons.count())))
    check("replié | arborescence masquée, réglages visibles", page.is_visible("#pane-detail .settings") and not page.is_visible("#pane-tree"))
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j5-replie-reglages.png"), full_page=True)
    page.set_input_files("#import-file", tmp_file(page.evaluate("JSON.stringify(Rangement.features.demo.build())")))
    dd = dlg(page)
    box = dd.bounding_box()
    check("replié | dialogue d'import contenu dans l'écran", box["x"] >= 0 and box["x"] + box["width"] <= 390 and box["y"] >= 0 and box["y"] + box["height"] <= 844, box)
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j5-replie-import.png"))
    page.keyboard.press("Escape")
    closed(page)
    check("replié | Échap : rien n'est changé", len(stored(page)["locations"]) == 8)
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()

    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    load_demo(page)
    go_settings(page)
    check("déplié | arborescence et réglages côte à côte", page.is_visible("#pane-tree") and page.is_visible("#pane-detail .settings"))
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j5-deplie-reglages.png"))
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
        scenario_invalid(browser, base)
        scenario_roundtrip(browser, base)
        scenario_no_storage(browser, base)
        scenario_logic(browser, base)
        scenario_narrow(browser, base)
        browser.close()

    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
