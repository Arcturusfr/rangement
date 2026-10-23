# tests/test_jalon1.py — Application « Rangement »
# Version : V004
# Horodatage : 2026-10-23 11:35 (heure de Paris)
# Résumé : la version attendue est lue dans js/config.js (plus de valeur codée en dur).
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon1.py
# Nécessite : pip install playwright  puis  playwright install chromium

import functools
import http.server
import os
import sys
import threading

from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHOTS = os.environ.get("RANGEMENT_SHOTS")  # dossier optionnel pour des captures
import re
VERSION = re.search(r"version: '([^']+)'", open(os.path.join(ROOT, "js", "config.js"), encoding="utf-8").read()).group(1)

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


def watch(page, errors):
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))


def new_page(browser, width, height, errors, init_script=None):
    ctx = browser.new_context(viewport={"width": width, "height": height})
    if init_script:
        ctx.add_init_script(init_script)
    page = ctx.new_page()
    watch(page, errors)
    return ctx, page


def scenario_main(browser, base, label):
    """Parcours principal ; `base` est une URL http:// ou file://."""
    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail")

    check(label + " | version dans le titre", VERSION in page.title(), page.title())
    check(label + " | version dans l'en-tête", page.inner_text("#app-version").strip() == VERSION)
    check(label + " | état vide + bouton démo", page.locator("button:has-text('Charger les données de démonstration')").count() == 1)

    page.click("button:has-text('Charger les données de démonstration')")
    check(label + " | 8 emplacements dans l'arborescence", page.locator("#pane-tree .tree-link").count() == 8,
          page.locator("#pane-tree .tree-link").count())

    page.reload()
    page.wait_for_selector("#pane-tree .tree-link")
    check(label + " | persistance après rechargement", page.locator("#pane-tree .tree-link").count() == 8)

    # Parcours Séjour › Meuble living › Grand tiroir du bas
    page.click("#pane-tree .tree-link:has-text('Séjour')")
    page.wait_for_function("document.querySelector('#pane-detail .detail-title').textContent === 'Séjour'")
    check(label + " | titre Séjour", page.inner_text("#pane-detail .detail-title") == "Séjour")
    page.click("#pane-detail .list-row:has-text('Meuble living')")
    page.wait_for_function("document.querySelector('#pane-detail .detail-title').textContent === 'Meuble living'")
    page.click("#pane-detail .list-row:has-text('Grand tiroir du bas')")
    page.wait_for_function("document.querySelector('#pane-detail .detail-title').textContent === 'Grand tiroir du bas'")
    crumb = page.inner_text("#pane-detail .breadcrumb").replace("\n", " ")
    check(label + " | fil d'Ariane complet", all(s in crumb for s in ["Logement", "Séjour", "Meuble living", "Grand tiroir du bas"]), crumb)
    check(label + " | objet Jumelles Nikon affiché", "Jumelles Nikon" in page.inner_text("#pane-detail"))
    check(label + " | lien actif surligné dans l'arborescence",
          page.locator("#pane-tree [aria-current='page']").inner_text().strip() == "Grand tiroir du bas")

    # Lien direct vers un emplacement inconnu
    page.goto(base + "#/l/inconnu")
    page.wait_for_selector("#pane-detail .empty")
    check(label + " | emplacement inconnu géré", "introuvable" in page.inner_text("#pane-detail"))

    # Mise en page
    page.goto(base + "#/")
    page.wait_for_selector("#pane-tree .tree-link")
    check(label + " | déplié : 2 volets", page.get_attribute("html", "data-panes") == "2")
    check(label + " | déplié : arborescence visible", page.is_visible("#pane-tree"))
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, label + "-deplie.png"))

    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_function("document.documentElement.dataset.panes === '1'")
    check(label + " | replié : 1 volet", page.get_attribute("html", "data-panes") == "1")
    check(label + " | replié : arborescence masquée", not page.is_visible("#pane-tree"))
    check(label + " | replié : volet de détail visible", page.is_visible("#pane-detail"))
    overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    check(label + " | replié : pas de défilement horizontal", overflow <= 0, overflow)
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, label + "-replie.png"))

    check(label + " | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_corrupt(browser, base):
    errors = []
    ctx, page = new_page(browser, 884, 1100, errors, "if(!localStorage.getItem('rangement.data')) localStorage.setItem('rangement.data','{pas du json');")
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    check("corrompu | message d'état visible", page.is_visible("#status") and "illisibles" in page.inner_text("#status"))
    check("corrompu | copie de sauvegarde conservée",
          page.evaluate("localStorage.getItem('rangement.data.corrupt')") == "{pas du json")
    check("corrompu | l'appli démarre à vide", page.locator("button:has-text('Charger les données')").count() == 1)
    check("corrompu | aucune erreur console", not errors, errors)
    ctx.close()

    errors = []
    bad = '{"schemaVersion":99,"locations":[],"items":[]}'
    ctx, page = new_page(browser, 884, 1100, errors, "if(!localStorage.getItem('rangement.data')) localStorage.setItem('rangement.data', '%s');" % bad)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    check("incohérent | message d'état visible", page.is_visible("#status") and "incohérentes" in page.inner_text("#status"))
    ctx.close()


def scenario_no_storage(browser, base):
    errors = []
    script = "Object.defineProperty(window,'localStorage',{get(){throw new DOMException('denied','SecurityError');}});"
    ctx, page = new_page(browser, 884, 1100, errors, script)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    check("sans stockage | avertissement visible", page.is_visible("#status") and "indisponible" in page.inner_text("#status"))
    page.click("button:has-text('Charger les données')")
    check("sans stockage | l'appli fonctionne en mémoire", page.locator("#pane-tree .tree-link").count() == 8)
    check("sans stockage | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_models(browser, base):
    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail")

    def v(expr):
        return page.evaluate(expr)

    ok_demo = v("Rangement.models.validateData(Rangement.features.demo.build()).ok")
    check("modèle | données de démo valides", ok_demo)
    check("modèle | boucle détectée", v("""(function(){
      var d = Rangement.models.emptyData();
      var a = Rangement.models.newLocation({name:'A'}); var b = Rangement.models.newLocation({name:'B', parentId:a.id});
      a.parentId = b.id; d.locations.push(a,b); return Rangement.models.validateData(d).ok;})()""") is False)
    check("modèle | parent manquant détecté", v("""(function(){
      var d = Rangement.models.emptyData();
      d.locations.push(Rangement.models.newLocation({name:'A', parentId:'nope'})); return Rangement.models.validateData(d).ok;})()""") is False)
    check("modèle | identifiant en double détecté", v("""(function(){
      var d = Rangement.models.emptyData(); var a = Rangement.models.newLocation({name:'A'});
      d.locations.push(a, JSON.parse(JSON.stringify(a))); return Rangement.models.validateData(d).ok;})()""") is False)
    check("modèle | objet sans emplacement détecté", v("""(function(){
      var d = Rangement.models.emptyData();
      d.items.push(Rangement.models.newItem({name:'x', locationId:'nope'})); return Rangement.models.validateData(d).ok;})()""") is False)
    check("modèle | quantité par défaut = 1", v("Rangement.models.newItem({name:'x', locationId:'l'}).quantity") == 1)
    check("modèle | quantité 0 conservée", v("Rangement.models.newItem({name:'x', locationId:'l', quantity:0}).quantity") == 0)
    check("modèle | identifiants uniques", v("(function(){var s={};for(var i=0;i<500;i++){s[Rangement.ids.generate('x')]=1;}return Object.keys(s).length;})()") == 500)

    # Mise à jour atomique : une modification incohérente est refusée et n'altère rien
    page.click("button:has-text('Charger les données')")
    before = v("Rangement.store.locations().length")
    res = v("Rangement.store.update(function(d){ d.locations[0].parentId = 'nope'; })")
    check("store | mise à jour incohérente refusée", res["ok"] is False)
    check("store | état inchangé après refus", v("Rangement.store.locations().length") == before
          and v("Rangement.store.locations()[0].parentId") is None)
    counts = v("Rangement.store.countIn(Rangement.store.locations().filter(function(l){return l.name==='Séjour';})[0].id)")
    check("store | comptage récursif (Séjour = 3 emplacements, 2 objets)", counts == {"locations": 3, "items": 2}, counts)

    # Injection HTML : le texte doit rester du texte
    page.evaluate("Rangement.store.update(function(d){ d.locations[0].name = '<img src=x onerror=window.__xss=1>'; })")
    check("sécurité | pas d'élément injecté dans l'arborescence", page.locator("#pane-tree img").count() == 0)
    check("sécurité | aucun script exécuté", page.evaluate("window.__xss") is None)
    check("sécurité | texte affiché tel quel", "<img src=x" in page.inner_text("#pane-tree"))
    check("modèles | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_diagnostic(browser, base):
    """Un fichier absent ou une erreur JS doivent être signalés à l'écran, pas silencieux."""
    ctx = browser.new_context(viewport={"width": 884, "height": 1100})
    page = ctx.new_page()
    page.route("**/js/core/store.js", lambda route: route.fulfill(status=404, content_type="text/html", body="Not found"))
    page.goto(base)
    page.wait_for_selector("#boot-errors:not([hidden])")
    txt = page.inner_text("#boot-errors")
    check("diagnostic | fichier absent signalé à l'écran", "js/core/store.js" in txt, txt)
    check("diagnostic | l'en-tête reste affiché", page.inner_text("#app-version").strip() == VERSION)
    ctx.close()

    ctx = browser.new_context(viewport={"width": 884, "height": 1100})
    page = ctx.new_page()
    page.route("**/js/ui/views/location.js", lambda route: route.fulfill(status=200, content_type="text/javascript", body="throw new Error('panne simulée');"))
    page.goto(base)
    page.wait_for_selector("#boot-errors:not([hidden])")
    txt = page.inner_text("#boot-errors")
    check("diagnostic | erreur JS affichée", "panne simulée" in txt, txt)
    check("diagnostic | module défaillant désigné", "js/ui/views/location.js" in txt, txt)
    ctx.close()

    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    check("diagnostic | aucun message en fonctionnement normal", not page.is_visible("#boot-errors"))
    ctx.close()


def main():
    server = start_server()
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    file_url = "file://" + os.path.join(ROOT, "index.html")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        scenario_main(browser, base, "http")
        scenario_main(browser, file_url, "file")
        scenario_corrupt(browser, base)
        scenario_no_storage(browser, base)
        scenario_models(browser, base)
        scenario_diagnostic(browser, base)
        browser.close()

    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
