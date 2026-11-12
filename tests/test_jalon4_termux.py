# tests/test_jalon4_termux.py — Application « Rangement » (Version Termux / Selenium)
# Adapté de V018 pour fonctionner avec Chromium + ChromeDriver sous Android Termux

import functools
import http.server
import os
import sys
import threading

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHOTS = os.environ.get("RANGEMENT_SHOTS")

_INIT = (
    "try{ if(!localStorage.getItem('rangement.data.planview')){localStorage.setItem('rangement.data.planview','list');"
    "localStorage.setItem('rangement.data.view','list');} if(!localStorage.getItem('rangement.data.ui')){"
    "localStorage.setItem('rangement.data.ui','{\"tree\":\"wide\"}');} }catch(e){}"
)

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


def new_driver(width, height):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--window-size={width},{height}")
    options.binary_location = "/data/data/com.termux/files/usr/bin/chromium-browser"
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    service = Service("/data/data/com.termux/files/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": _INIT})
    driver.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": width < 600},
    )
    return driver


def collect_errors(driver, errors):
    try:
        for entry in driver.get_log("browser"):
            if entry.get("level") == "SEVERE":
                errors.append(entry.get("message", ""))
    except Exception:
        pass


def wait_for_selector(driver, css, timeout=5):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))


def wait_for_fn(driver, js_cond, timeout=5):
    WebDriverWait(driver, timeout).until(lambda d: bool(d.execute_script(f"return Boolean({js_cond});")))


def is_visible(driver, css):
    els = driver.find_elements(By.CSS_SELECTOR, css)
    return len(els) > 0 and els[0].is_displayed()


def load_demo(driver):
    btn = driver.find_element(By.XPATH, "//button[contains(., 'Charger les données de démonstration')]")
    btn.click()
    wait_for_selector(driver, "#pane-detail .list")


def search_box(driver):
    return driver.find_element(By.CSS_SELECTOR, "#search-input")


def type_query(driver, text):
    box = search_box(driver)
    box.click()
    box.clear()
    driver.execute_script("arguments[0].value = ''; arguments[0].dispatchEvent(new Event('input', {bubbles:true}));", box)
    if text:
        box.send_keys(text)


def results_text(driver):
    return driver.find_element(By.CSS_SELECTOR, "#pane-detail .search-results").text


def rows(driver, section):
    sections = driver.find_elements(By.CSS_SELECTOR, "#pane-detail .search-results .section")
    for sec in sections:
        h3 = sec.find_elements(By.TAG_NAME, "h3")
        if h3 and section in h3[0].text:
            return sec.find_elements(By.CSS_SELECTOR, ".list-item")
    return []


def js(driver, expr):
    return driver.execute_script(f"return {expr};")


def scenario_flow(base, label):
    errors = []
    driver = new_driver(884, 1100)
    try:
        driver.get(base)
        wait_for_selector(driver, "#pane-detail .empty")

        boxes = driver.find_elements(By.CSS_SELECTOR, "#search-input")
        check(label + " | champ de recherche présent dès le départ", len(boxes) == 1 and is_visible(driver, "#search-input"))

        has_label = js(driver, "document.querySelectorAll('[aria-label*=\"Rechercher\"], label[for=\"search-input\"]').length >= 1")
        check(label + " | champ de recherche : étiquette accessible", has_label)

        load_demo(driver)

        type_query(driver, "piles")
        wait_for_fn(driver, "document.querySelector('#pane-detail .detail-title')?.textContent === 'Recherche'")
        h = js(driver, "location.hash")
        check(label + " | la saisie ouvre la recherche (#/s/piles)", h == "#/s/piles", h)

        r = rows(driver, "Objets")
        first_txt = r[0].text if r else ""
        check(label + " | « piles » : 1 objet trouvé", len(r) == 1 and "Piles neuves" in first_txt, results_text(driver))
        check(label + " | résultat : chemin complet affiché", "Séjour \u203a Meuble living \u203a Tiroir bas gauche" in first_txt, first_txt)

        meta_txt = driver.find_element(By.CSS_SELECTOR, "#pane-detail .detail-meta").text
        check(label + " | nombre de résultats annoncé", "1 résultat" in meta_txt, meta_txt)

        current_tree = driver.find_elements(By.CSS_SELECTOR, "#pane-tree [aria-current='page']")
        check(label + " | arborescence : rien de surligné pendant la recherche", len(current_tree) == 0)

        type_query(driver, "ELECTRICITE")
        check(label + " | mot-clé trouvé sans accents ni casse", "Piles neuves" in results_text(driver), results_text(driver))

        type_query(driver, "nature")
        check(label + " | mot-clé « nature » → Jumelles Nikon", len(rows(driver, "Objets")) == 1 and "Jumelles Nikon" in results_text(driver))

        type_query(driver, "jumelles optique")
        check(label + " | plusieurs mots : tous requis (trouvé)", len(rows(driver, "Objets")) == 1)

        type_query(driver, "jumelles piles")
        check(label + " | plusieurs mots : tous requis (non trouvé)", "Aucun résultat" in results_text(driver), results_text(driver))

        type_query(driver, "jumlles")
        check(label + " | pas de tolérance aux fautes de frappe", "Aucun résultat" in results_text(driver))

        type_query(driver, "NiKoN")
        check(label + " | casse ignorée dans le nom", "Jumelles Nikon" in results_text(driver))

        type_query(driver, "   ")
        list_count = len(driver.find_elements(By.CSS_SELECTOR, "#pane-detail .list"))
        check(label + " | requête vide : message d'aide", "Saisissez" in results_text(driver) and list_count == 0)

        type_query(driver, "séjour")
        check(label + " | « séjour » : objets rangés dans le séjour", len(rows(driver, "Objets")) == 2, results_text(driver))

        locs = rows(driver, "Emplacements")
        check(label + " | « séjour » : emplacements trouvés (la pièce et son contenu)", len(locs) == 4, results_text(driver))
        first_loc_title = locs[0].find_element(By.CSS_SELECTOR, ".list-title").text if locs else ""
        check(label + " | emplacement : nom propre en premier", "Séjour" in first_loc_title)

        type_query(driver, "tiroir bas")
        txt = results_text(driver)
        meta_txt = driver.find_element(By.CSS_SELECTOR, "#pane-detail .detail-meta").text
        check(
            label + " | « tiroir bas » : les 2 tiroirs et leurs 2 objets",
            len(rows(driver, "Emplacements")) == 2 and len(rows(driver, "Objets")) == 2 and "4 résultats" in meta_txt,
            txt,
        )
        type_query(driver, "jumelles")
        row_jumelles = driver.find_element(By.XPATH, "//*[@id='pane-detail']//*[contains(@class,'search-results')]//*[contains(@class,'list-row') and contains(., 'Jumelles Nikon')]")
        row_jumelles.click()
        wait_for_selector(driver, "#pane-detail .item-detail")
        check(label + " | un objet trouvé ouvre sa fiche", driver.find_element(By.CSS_SELECTOR, "#pane-detail .detail-title").text == "Jumelles Nikon")
        check(label + " | champ vidé hors recherche", search_box(driver).get_attribute("value") == "")

        driver.back()
        wait_for_selector(driver, "#pane-detail .search-results")
        val_after_back = search_box(driver).get_attribute("value")
        check(label + " | Retour : résultats et champ restaurés", val_after_back == "jumelles" and "Jumelles Nikon" in results_text(driver), val_after_back)

        type_query(driver, "meuble living")
        emp_rows = rows(driver, "Emplacements")
        emp_rows[0].find_element(By.CSS_SELECTOR, ".list-row").click()
        wait_for_fn(driver, "document.querySelector('#pane-detail .detail-title')?.textContent === 'Meuble living'")
        current_txt = driver.find_element(By.CSS_SELECTOR, "#pane-tree [aria-current='page']").text.strip()
        check(label + " | un emplacement trouvé ouvre l'emplacement", current_txt == "Meuble living")

        driver.get(base + "#/")
        wait_for_selector(driver, "#pane-detail .list")
        type_query(driver, "pile")
        wait_for_selector(driver, "#pane-detail .search-results")
        driver.back()
        wait_for_fn(driver, "location.hash === '#/' || location.hash === ''")
        sr_count = len(driver.find_elements(By.CSS_SELECTOR, "#pane-detail .search-results"))
        check(label + " | Retour après une saisie : revient à l'écran précédent", sr_count == 0 and search_box(driver).get_attribute("value") == "")

        driver.get(base + "#/s/piles")
        driver.refresh()
        wait_for_selector(driver, "#pane-detail .search-results")
        check(label + " | lien direct : champ prérempli et résultats", search_box(driver).get_attribute("value") == "piles" and "Piles neuves" in results_text(driver))

        search_box(driver).click()
        search_box(driver).send_keys(Keys.ENTER)
        check(label + " | Entrée : le champ perd le focus, résultats conservés", js(driver, "document.activeElement.id") != "search-input" and "Piles neuves" in results_text(driver))

        type_query(driver, "")
        check(label + " | champ effacé : message d'aide", "Saisissez" in results_text(driver))

        type_query(driver, "<b>x</b>")
        b_tags = driver.find_elements(By.CSS_SELECTOR, "#pane-detail .search-results b")
        check(label + " | requête hostile affichée comme texte", len(b_tags) == 0 and "<b>x</b>" in results_text(driver), results_text(driver))

        driver.get(base + "#/s/%E0%A4%A")
        wait_for_selector(driver, "#pane-detail .search-results")
        check(label + " | adresse mal encodée tolérée", True)

        collect_errors(driver, errors)
        check(label + " | aucune erreur console", not errors, errors)
    finally:
        driver.quit()


def scenario_logic(base):
    errors = []
    driver = new_driver(884, 1100)
    try:
        driver.get(base)
        wait_for_selector(driver, "#pane-detail .empty")
        load_demo(driver)
        S = "Rangement.features.search"

        check("logique | requête vide : aucun résultat", js(driver, f"(function(){{var r={S}.search('  ');return r.items.length+r.locations.length;}})()") == 0)
        check("logique | mots normalisés", js(driver, f"{S}.terms('  ÉLECTRICITÉ   Piles ')") == ["electricite", "piles"])

        loc = js(driver, "Rangement.store.locations().filter(function(l){return l.name==='Grand tiroir du bas';})[0].id")
        F = "Rangement.features.items"
        driver.execute_script(f"{F}.create({{name:'Alpha', locationId:'{loc}', tags:'zeta'}})")
        driver.execute_script(f"{F}.create({{name:'Zeta', locationId:'{loc}'}})")
        driver.execute_script(f"{F}.create({{name:'Beta', locationId:'{loc}', note:'voir zeta'}})")
        order = js(driver, f"{S}.search('zeta').items.map(function(h){{return h.item.name;}})")
        check("logique | classement : nom, puis mot-clé, puis note", order == ["Zeta", "Alpha", "Beta"], order)

        driver.execute_script(f"{F}.create({{name:'Colle', locationId:'{loc}', quantity:'0'}})")
        driver.get(base + "#/s/colle")
        wait_for_selector(driver, "#pane-detail .search-results")
        muted = driver.find_elements(By.CSS_SELECTOR, "#pane-detail .list-item--muted")
        check("logique | objet épuisé grisé dans les résultats", len(muted) == 1)

        driver.execute_script(f"{F}.create({{name:'<img src=x onerror=window.__xss=1>', locationId:'{loc}', tags:'<b>gras</b>'}})")
        type_query(driver, "img")
        bad_tags = driver.find_elements(By.CSS_SELECTOR, "#pane-detail .search-results img, #pane-detail .search-results b")
        check("sécurité | objet hostile trouvé et affiché comme texte", "<img src=x" in results_text(driver) and len(bad_tags) == 0)
        check("sécurité | aucun script exécuté", js(driver, "window.__xss") is None)

        driver.get(base + "#/s/zeta")
        wait_for_selector(driver, "#pane-detail .search-results")
        n = len(rows(driver, "Objets"))
        driver.execute_script("Rangement.features.items.remove(Rangement.features.search.search('zeta').items[0].item.id)")
        wait_for_fn(driver, f"document.querySelectorAll('#pane-detail .search-results .section')[0].querySelectorAll('.list-item').length === {n - 1}")
        check("logique | suppression : résultats mis à jour", len(rows(driver, "Objets")) == n - 1, len(rows(driver, "Objets")))

        collect_errors(driver, errors)
        check("logique | aucune erreur console", not errors, errors)
    finally:
        driver.quit()


def scenario_narrow(base):
    errors = []
    driver = new_driver(390, 844)
    try:
        driver.get(base)
        wait_for_selector(driver, "#pane-detail .empty")
        load_demo(driver)

        panes = driver.find_element(By.TAG_NAME, "html").get_attribute("data-panes")
        check("replié | 1 volet", panes == "1")

        box = js(driver, "document.querySelector('#search-input').getBoundingClientRect().toJSON()")
        check("replié | champ de recherche ≥ 44 px et dans l'écran", box["height"] >= 44 and box["x"] >= 0 and box["x"] + box["width"] <= 390, box)

        type_query(driver, "tiroir")
        wait_for_selector(driver, "#pane-detail .search-results")
        overflow = js(driver, "document.documentElement.scrollWidth - window.innerWidth")
        check("replié | résultats : pas de défilement horizontal", overflow <= 0, overflow)
        check("replié | résultats visibles", is_visible(driver, "#pane-detail .search-results") and not is_visible(driver, "#pane-tree"))

        if SHOTS:
            driver.save_screenshot(os.path.join(SHOTS, "j4-replie-recherche.png"))

        collect_errors(driver, errors)
        check("replié | aucune erreur console", not errors, errors)
    finally:
        driver.quit()

    errors = []
    driver = new_driver(884, 1100)
    try:
        driver.get(base)
        load_demo(driver)
        type_query(driver, "séjour")
        wait_for_selector(driver, "#pane-detail .search-results")
        check("déplié | arborescence et résultats côte à côte", is_visible(driver, "#pane-tree") and is_visible(driver, "#pane-detail .search-results"))

        if SHOTS:
            driver.save_screenshot(os.path.join(SHOTS, "j4-deplie-recherche.png"))

        collect_errors(driver, errors)
        check("déplié | aucune erreur console", not errors, errors)
    finally:
        driver.quit()


def main():
    server = start_server()
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    file_url = "file://" + os.path.join(ROOT, "index.html")

    scenario_flow(base, "http")
    scenario_flow(file_url, "file")
    scenario_logic(base)
    scenario_narrow(base)

    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
