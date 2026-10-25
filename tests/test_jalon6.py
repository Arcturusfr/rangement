# tests/test_jalon6.py — Application « Rangement »
# Version : V009
# Horodatage : 2026-10-25 16:10 (heure de Paris)
# Résumé : adaptation V009 : go_settings n'appuie plus si les Réglages sont déjà ouverts.
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon6.py
# Nécessite : pip install playwright  puis  playwright install chromium

import functools
import http.server
import json
import os
import re
import shutil
import sys
import tempfile
import threading

from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHOTS = os.environ.get("RANGEMENT_SHOTS")
VERSION = re.search(r"version: '([^']+)'", open(os.path.join(ROOT, "js", "config.js"), encoding="utf-8").read()).group(1)

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + (("  -> " + str(detail)) if (detail and not cond) else ""))


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def start_server(root):
    handler = functools.partial(QuietHandler, directory=root)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def new_page(browser, width, height, errors):
    ctx = browser.new_context(viewport={"width": width, "height": height})
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    return ctx, page


def dlg(page):
    return page.locator("dialog.dialog[open]")


def closed(page):
    page.wait_for_selector("dialog.dialog[open]", state="detached")


def go_settings(page):
    if page.evaluate("location.hash") != "#/r":     # depuis V009, un second appui sur « Réglages » les referme
        page.click("#app-settings")
    page.wait_for_selector("#pane-detail .settings")


def wait_controlled(page):
    page.wait_for_function("navigator.serviceWorker.controller !== null", timeout=15000)
    page.wait_for_function("Rangement.pwa.status().cacheName !== null", timeout=15000)


def sw_files():
    src = open(os.path.join(ROOT, "sw.js"), encoding="utf-8").read()
    block = re.search(r"var FILES = \[(.*?)\];", src, re.S).group(1)
    return re.findall(r"'([^']+)'", block), src


# ---------- scénarios ----------

def scenario_static():
    files, src = sw_files()
    check("statique | version du service worker = version de l'application", re.search(r"var VERSION = '([^']+)'", src).group(1) == VERSION, VERSION)
    missing = [f for f in files if f != "./" and not os.path.isfile(os.path.join(ROOT, f))]
    check("statique | tous les fichiers pré-cachés existent", not missing, missing)
    check("statique | pas de doublon dans la liste de pré-cache", len(files) == len(set(files)))
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    used = re.findall(r'(?:src|href)="((?:js|css|icons)/[^"]+|manifest\.webmanifest)"', html)
    check("statique | tout ce que charge index.html est pré-caché", all(u in files for u in used), [u for u in used if u not in files])
    jsfiles = []
    for d, _, fs in os.walk(os.path.join(ROOT, "js")):
        for f in fs:
            jsfiles.append(os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/"))
    check("statique | chaque fichier js/ est pré-caché", all(j in files for j in jsfiles), [j for j in jsfiles if j not in files])
    inst = src[src.index("addEventListener('install'"):src.index("// Activation")]
    check("statique | pas de skipWaiting automatique à l'installation", "skipWaiting" not in inst)
    m = json.load(open(os.path.join(ROOT, "manifest.webmanifest"), encoding="utf-8"))
    check("manifeste | nom, affichage, couleurs", m["name"] == "Rangement" and m["display"] == "standalone" and m["theme_color"] == "#16222A" and m["lang"] == "fr")
    check("manifeste | start_url et scope relatifs (GitHub Pages)", not m["start_url"].startswith("/") and not m["scope"].startswith("/"), (m["start_url"], m["scope"]))
    sizes = {(i["sizes"], i["purpose"]): i["src"] for i in m["icons"]}
    check("manifeste | 4 icônes (192/512, any et maskable)", set(sizes) == {("192x192", "any"), ("512x512", "any"), ("192x192", "maskable"), ("512x512", "maskable")}, list(sizes))
    from struct import unpack
    ok = True
    for i in m["icons"]:
        with open(os.path.join(ROOT, i["src"]), "rb") as f:
            head = f.read(24)
        w, h = unpack(">II", head[16:24])
        ok = ok and head[:8] == b"\x89PNG\r\n\x1a\n" and "%dx%d" % (w, h) == i["sizes"]
    check("manifeste | les icônes existent avec la bonne taille", ok)
    check("index.html | manifeste et icône Apple liés", 'rel="manifest"' in html and 'rel="apple-touch-icon"' in html and "js/pwa.js" in html)


def scenario_online(browser, base, label):
    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector("#pane-detail .list")
    wait_controlled(page)
    files, _ = sw_files()

    keys = page.evaluate("caches.keys()")
    check(label + " | un seul cache : rangement-" + VERSION, keys == ["rangement-" + VERSION], keys)
    n = page.evaluate("caches.open('rangement-%s').then(c => c.keys()).then(k => k.length)" % VERSION)
    check(label + " | tous les fichiers sont dans le cache", n == len(files), (n, len(files)))
    check(label + " | lien manifeste présent", page.evaluate("document.querySelector('link[rel=manifest]').href").endswith("manifest.webmanifest"))
    check(label + " | pas de pastille de mise à jour au premier chargement", page.get_attribute("#app-settings", "data-badge") is None)

    go_settings(page)
    txt = page.inner_text("#pane-detail .settings")
    check(label + " | réglages : section hors ligne avec cache actif", "Application hors ligne" in txt and "rangement-" + VERSION in txt, txt)
    check(label + " | réglages : boutons de recherche de mise à jour et de vidage", page.locator("#check-update-button").count() == 1 and page.locator("#clear-cache-button").count() == 1)
    check(label + " | réglages : pas de bouton « Mettre à jour » sans nouvelle version", page.locator("#update-button").count() == 0)
    check(label + " | réglages : pas d'installation proposée sans invitation du navigateur", page.locator("#install-button").count() == 0)
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, label + "-j6-reglages.png"), full_page=True)

    # Recherche de mise à jour : aucune
    page.click("#check-update-button")
    page.wait_for_function("document.querySelector('#pane-detail .settings').innerText.indexOf('dernière version') !== -1", timeout=10000)
    check(label + " | aucune mise à jour : message « dernière version »", True)

    # Invitation à installer (événement simulé)
    page.evaluate("""(function(){var e=new Event('beforeinstallprompt',{cancelable:true}); e.prompt=function(){window.__prompted=1;}; e.userChoice=Promise.resolve({outcome:'accepted'}); window.dispatchEvent(e);})()""")
    page.wait_for_selector("#install-button")
    page.click("#install-button")
    page.wait_for_function("window.__prompted === 1")
    check(label + " | installation : l'invite du navigateur est déclenchée puis le bouton disparaît", page.locator("#install-button").count() == 0)

    # Hors ligne : rechargement et usage
    ctx.set_offline(True)
    page.goto(base + "#/")
    page.wait_for_selector("#pane-tree .tree-link")
    check(label + " | hors ligne : l'application se charge", page.inner_text("#app-version").strip() == VERSION)
    check(label + " | hors ligne : les données sont là", page.locator("#pane-tree .tree-link").count() == 8)
    page.fill("#search-input", "piles")
    page.wait_for_selector("#pane-detail .search-results")
    check(label + " | hors ligne : la recherche fonctionne", "Piles neuves" in page.inner_text("#pane-detail .search-results"))
    page.goto(base + "#/o/inconnu")
    page.wait_for_selector("#pane-detail .empty")
    page.goto(base.replace("index.html", "") + "#/")           # adresse de dossier (start_url)
    page.wait_for_selector("#pane-tree .tree-link")
    check(label + " | hors ligne : l'adresse du dossier ouvre l'application", page.locator("#pane-tree .tree-link").count() == 8)
    go_settings(page)
    page.click("#check-update-button")
    page.wait_for_function("document.querySelector('#pane-detail .settings').innerText.indexOf('hors connexion') !== -1 || document.querySelector('#pane-detail .settings').innerText.indexOf('dernière version') !== -1", timeout=10000)
    check(label + " | hors ligne : la recherche de mise à jour ne plante pas", True)
    ctx.set_offline(False)
    check(label + " | aucune erreur console (hors erreurs réseau volontaires)", not [e for e in errors if "net::ERR" not in e and "Failed to load resource" not in e], errors)
    ctx.close()


def scenario_update(browser):
    """Nouvelle version déployée : proposée, activée seulement sur accord, ancien cache supprimé."""
    tmp = tempfile.mkdtemp()
    site = os.path.join(tmp, "site")
    shutil.copytree(ROOT, site, ignore=shutil.ignore_patterns("tests", "__pycache__", ".git"))
    server = start_server(site)
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector("#pane-detail .list")
    wait_controlled(page)
    go_settings(page)

    sw = os.path.join(site, "sw.js")
    text = open(sw, encoding="utf-8").read()
    open(sw, "w", encoding="utf-8").write(text.replace("var VERSION = '%s'" % VERSION, "var VERSION = 'V999'"))

    page.click("#check-update-button")
    page.wait_for_selector("#update-button", timeout=15000)
    check("mise à jour | proposée : bouton « Mettre à jour » et encadré", "nouvelle version" in page.inner_text("#pane-detail .settings"))
    check("mise à jour | pastille sur le lien Réglages", page.get_attribute("#app-settings", "data-badge") == "update" and "mise à jour" in page.get_attribute("#app-settings", "aria-label"))
    keys = sorted(page.evaluate("caches.keys()"))
    check("mise à jour | l'ancien cache reste utilisable en attendant l'accord", keys == ["rangement-V999", "rangement-" + VERSION] or keys == sorted(["rangement-V999", "rangement-" + VERSION]), keys)
    check("mise à jour | pas d'activation automatique (la page n'a pas rechargé)", page.evaluate("Rangement.pwa.status().cacheName") == "rangement-" + VERSION)
    page.evaluate("window.__same = 1")
    page.reload()
    page.wait_for_selector("#pane-detail .settings, #pane-detail .list")
    check("mise à jour | un simple rechargement garde l'ancienne version", page.evaluate("Rangement.pwa.status().cacheName") in (None, "rangement-" + VERSION))

    go_settings(page)
    if page.locator("#update-button").count() == 0:
        page.click("#check-update-button")
        page.wait_for_selector("#update-button", timeout=15000)
    page.click("#update-button")
    page.wait_for_function("Rangement.pwa.status().cacheName === 'rangement-V999'", timeout=20000)
    check("mise à jour | acceptée : nouvelle version active", True)
    keys = page.evaluate("caches.keys()")
    check("mise à jour | ancien cache supprimé", keys == ["rangement-V999"], keys)
    page.wait_for_selector("#pane-tree .tree-link")
    check("mise à jour | les données sont conservées", page.locator("#pane-tree .tree-link").count() == 8)
    check("mise à jour | plus de pastille", page.get_attribute("#app-settings", "data-badge") is None)
    check("mise à jour | aucune erreur console", not errors, errors)

    # Vider le cache
    go_settings(page)
    page.click("#clear-cache-button")
    d = dlg(page)
    check("cache | confirmation : données non touchées", "Vider le cache" in d.inner_text() and "ne sont pas touchées" in d.inner_text(), d.inner_text())
    d.get_by_role("button", name="Annuler").click()
    closed(page)
    check("cache | annuler conserve le cache", page.evaluate("caches.keys()") == ["rangement-V999"])
    page.click("#clear-cache-button")
    with page.expect_navigation():
        dlg(page).get_by_role("button", name="Vider le cache").click()
    page.wait_for_selector("#pane-tree .tree-link")
    check("cache | données conservées après vidage", page.locator("#pane-tree .tree-link").count() == 8)
    wait_controlled(page)
    keys = page.evaluate("caches.keys()")
    check("cache | le cache est recréé proprement (version du serveur)", keys == ["rangement-V999"], keys)
    ctx.close()
    server.shutdown()
    shutil.rmtree(tmp, ignore_errors=True)


def scenario_file(browser, base):
    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    go_settings(page)
    txt = page.inner_text("#pane-detail .settings")
    check("file:// | réglages : mode hors ligne indisponible expliqué", "hors ligne" in txt and "https://" in txt, txt)
    check("file:// | pas de boutons de cache", page.locator("#clear-cache-button").count() == 0)
    check("file:// | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_sw_blocked(browser, base):
    """Service worker refusé par le navigateur : l'application reste utilisable."""
    errors = []
    ctx = browser.new_context(viewport={"width": 884, "height": 1100})
    ctx.add_init_script("navigator.serviceWorker.register = function(){ return Promise.reject(new Error('refusé')); };")
    page = ctx.new_page()
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    go_settings(page)
    check("sw refusé | message explicite dans les réglages", "n\u2019a pas pu être activé" in page.inner_text("#pane-detail .settings") or "n'a pas pu être activé" in page.inner_text("#pane-detail .settings"), page.inner_text("#pane-detail .settings"))
    check("sw refusé | l'application reste utilisable", page.is_visible("#pane-tree") or page.is_visible("#pane-detail"))
    check("sw refusé | aucune exception non gérée", not errors, errors)
    ctx.close()


def scenario_narrow(browser, base):
    errors = []
    ctx, page = new_page(browser, 390, 844, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector("#pane-detail .list")
    wait_controlled(page)
    go_settings(page)
    check("replié | 1 volet", page.get_attribute("html", "data-panes") == "1")
    overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    check("replié | réglages : pas de défilement horizontal", overflow <= 0, overflow)
    btns = page.locator("#pane-detail .settings .button:not([disabled])")
    check("replié | boutons des réglages ≥ 44 px", all(btns.nth(i).bounding_box()["height"] >= 44 for i in range(btns.count())))
    page.click("#clear-cache-button")
    box = dlg(page).bounding_box()
    check("replié | dialogue contenu dans l'écran", box["x"] >= 0 and box["x"] + box["width"] <= 390 and box["y"] >= 0 and box["y"] + box["height"] <= 844, box)
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j6-replie-cache.png"))
    page.keyboard.press("Escape")
    closed(page)
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j6-replie-reglages.png"), full_page=True)
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()


def main():
    scenario_static()
    server = start_server(ROOT)
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    file_url = "file://" + os.path.join(ROOT, "index.html")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        scenario_online(browser, base, "http")
        scenario_update(browser)
        scenario_file(browser, file_url)
        scenario_sw_blocked(browser, base)
        scenario_narrow(browser, base)
        browser.close()
    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
