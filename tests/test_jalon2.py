# tests/test_jalon2.py — Application « Rangement »
# Version : V009
# Horodatage : 2026-10-25 16:10 (heure de Paris)
# Résumé : adaptation V009 : arborescence repliée par défaut (expand_tree), 6 actions (Dupliquer).
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon2.py
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
    handler = functools.partial(QuietHandler, directory=ROOT)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def new_page(browser, width, height, errors):
    ctx = browser.new_context(viewport={"width": width, "height": height})
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    return ctx, page


# ---------- aides ----------

def dlg(page):
    return page.locator("dialog.dialog[open]")


def wait_title(page, title):
    page.wait_for_function("document.querySelector('#pane-detail .detail-title') && document.querySelector('#pane-detail .detail-title').textContent === %r" % title)


def open_row(page, name):
    page.locator("#pane-detail .list-row", has_text=name).first.click()
    wait_title(page, name)


def add_child(page, name, kind=None, note=None):
    page.get_by_role("button", name="Ajouter un emplacement ici").click()
    d = dlg(page)
    d.get_by_label("Nom").fill(name)
    if kind:
        d.get_by_label("Type").select_option(kind)
    if note:
        d.get_by_label("Note (facultatif)").fill(note)
    d.get_by_role("button", name="Ajouter", exact=True).click()


def stored(page):
    return page.evaluate("JSON.parse(localStorage.getItem('rangement.data'))")


def js(page, expr):
    return page.evaluate(expr)


def expand_tree(page):
    js(page, "Rangement.ui.views.browse.expandAll()")


# ---------- scénarios ----------

def scenario_flow(browser, base, label):
    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")

    # Écran de démarrage
    check(label + " | écran de démarrage : créer une pièce", page.get_by_role("button", name="Créer ma première pièce").count() == 1)
    check(label + " | écran de démarrage : démo toujours proposée", page.get_by_role("button", name="Charger les données de démonstration").count() == 1)

    # Création d'une pièce : validation, puis succès
    page.get_by_role("button", name="Créer ma première pièce").click()
    d = dlg(page)
    check(label + " | dialogue ouvert avec le type Pièce par défaut", d.get_by_label("Type").input_value() == "piece")
    d.get_by_role("button", name="Ajouter", exact=True).click()
    check(label + " | nom vide refusé", "obligatoire" in d.inner_text() and d.is_visible())
    d.get_by_label("Nom").fill("  Cuisine  ")
    d.get_by_label("Nom").press("Enter")
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    check(label + " | pièce créée (touche Entrée)", "Cuisine" in page.inner_text("#pane-detail .list"))
    check(label + " | nom rogné", stored(page)["locations"][0]["name"] == "Cuisine")

    page.reload()
    page.wait_for_selector("#pane-detail .list")
    check(label + " | pièce conservée après rechargement", "Cuisine" in page.inner_text("#pane-detail .list"))

    # Sous-emplacements
    open_row(page, "Cuisine")
    add_child(page, "Placard sous évier", kind="meuble", note="porte de gauche")
    page.wait_for_selector("#pane-detail .list-row:has-text('Placard sous évier')")
    row = page.locator("#pane-detail .list-item", has_text="Placard sous évier")
    check(label + " | sous-emplacement créé avec type et note", "Meuble" in row.inner_text() and "porte de gauche" in row.inner_text())
    expand_tree(page)
    check(label + " | arborescence mise à jour", "Placard sous évier" in page.inner_text("#pane-tree"))

    # Doublon (sans tenir compte casse / accents)
    page.get_by_role("button", name="Ajouter un emplacement ici").click()
    d = dlg(page)
    d.get_by_label("Nom").fill("placard SOUS evier")
    d.get_by_role("button", name="Ajouter", exact=True).click()
    check(label + " | doublon refusé (casse et accents ignorés)", "existe déjà" in d.inner_text())
    d.get_by_role("button", name="Annuler").click()
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    check(label + " | annulation : rien n'est créé", len(stored(page)["locations"]) == 2)

    # Échap ferme sans rien changer
    page.get_by_role("button", name="Ajouter un emplacement ici").click()
    dlg(page).get_by_label("Nom").fill("Ne pas créer")
    page.keyboard.press("Escape")
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    check(label + " | Échap : rien n'est créé", len(stored(page)["locations"]) == 2)

    # Modification
    open_row(page, "Placard sous évier")
    page.get_by_role("button", name="Modifier").click()
    d = dlg(page)
    check(label + " | modifier : champs préremplis", d.get_by_label("Nom").input_value() == "Placard sous évier" and d.get_by_label("Type").input_value() == "meuble")
    d.get_by_label("Nom").fill("Placard évier")
    d.get_by_label("Type").select_option("autre")
    d.get_by_role("button", name="Enregistrer").click()
    wait_title(page, "Placard évier")
    check(label + " | modification affichée (titre, type)", "Autre" in page.inner_text("#pane-detail .detail-meta"))
    check(label + " | fil d'Ariane mis à jour", "Placard évier" in page.inner_text("#pane-detail .breadcrumb"))

    # Sous-sous-emplacement et déplacement
    add_child(page, "Étagère haute", kind="etagere")
    page.wait_for_selector("#pane-detail .list-row:has-text('Étagère haute')")
    page.get_by_role("button", name="Ajouter un emplacement ici").click()  # vérifie que la barre reste utilisable
    page.keyboard.press("Escape")
    page.wait_for_selector("dialog.dialog[open]", state="detached")

    page.goto(base + "#/")
    page.wait_for_selector("#pane-detail .list")
    page.get_by_role("button", name="Ajouter une pièce").click()
    dlg(page).get_by_label("Nom").fill("Garage")
    dlg(page).get_by_role("button", name="Ajouter", exact=True).click()
    page.wait_for_selector("#pane-detail .list-row:has-text('Garage')")

    open_row(page, "Cuisine")
    open_row(page, "Placard évier")
    page.get_by_role("button", name="Déplacer").click()
    d = dlg(page)
    options = d.get_by_label("Nouvel emplacement parent").locator("option").all_inner_texts()
    check(label + " | déplacer : propose la racine et les autres emplacements", "Logement (racine)" in options and "Garage" in options and "Cuisine" in options, options)
    check(label + " | déplacer : exclut l'emplacement et son contenu",
          not any("Placard évier" in o for o in options), options)
    d.get_by_label("Nouvel emplacement parent").select_option(label="Garage")
    d.get_by_role("button", name="Déplacer", exact=True).click()
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    crumb = page.inner_text("#pane-detail .breadcrumb").replace("\n", " ")
    check(label + " | déplacé : fil d'Ariane à jour", "Garage" in crumb and "Cuisine" not in crumb, crumb)
    check(label + " | déplacé : le contenu suit", "Étagère haute" in page.inner_text("#pane-detail .list"))

    # Suppression refusée (non vide)
    n_before = len(stored(page)["locations"])
    page.get_by_role("button", name="Supprimer").click()
    d = dlg(page)
    check(label + " | suppression d'un emplacement non vide refusée", "Suppression impossible" in d.inner_text() and "1 emplacement" in d.inner_text(), d.inner_text())
    d.get_by_role("button", name="OK").click()
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    check(label + " | rien n'a été supprimé", len(stored(page)["locations"]) == n_before)

    # Suppression d'un emplacement vide + retour au parent
    open_row(page, "Étagère haute")
    page.get_by_role("button", name="Supprimer").click()
    d = dlg(page)
    check(label + " | confirmation demandée pour un emplacement vide", "est vide" in d.inner_text())
    d.get_by_role("button", name="Annuler").click()
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    check(label + " | annuler la suppression conserve l'emplacement", len(stored(page)["locations"]) == n_before)
    page.get_by_role("button", name="Supprimer").click()
    dlg(page).get_by_role("button", name="Supprimer", exact=True).click()
    wait_title(page, "Placard évier")
    check(label + " | suppression effectuée, retour au parent", len(stored(page)["locations"]) == n_before - 1)

    # Cohérence des données enregistrées
    check(label + " | données enregistrées valides", js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok"))
    check(label + " | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_guards(browser, base):
    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector("#pane-detail .list")

    # Un emplacement contenant un objet ne peut pas être supprimé
    open_row(page, "Séjour")
    open_row(page, "Meuble living")
    open_row(page, "Tiroir bas gauche")
    page.get_by_role("button", name="Supprimer").click()
    d = dlg(page)
    check("garde-fous | suppression refusée s'il contient un objet", "1 objet" in d.inner_text(), d.inner_text())
    d.get_by_role("button", name="OK").click()
    page.wait_for_selector("dialog.dialog[open]", state="detached")
    check("garde-fous | l'objet est toujours là", "Piles neuves" in page.inner_text("#pane-detail"))

    # Fonctions de la couche métier
    ids = js(page, "(function(){var m={};Rangement.store.locations().forEach(function(l){m[l.name+'|'+(l.parentId?'c':'r')]=l.id;});return m;})()")
    sejour = ids["Séjour|r"]
    living = ids["Meuble living|c"]
    L = "Rangement.features.locations"
    check("métier | déplacer dans son propre contenu refusé",
          js(page, "%s.move('%s','%s')" % (L, sejour, living))["ok"] is False)
    check("métier | déplacer dans lui-même refusé", js(page, "%s.move('%s','%s')" % (L, sejour, sejour))["ok"] is False)
    check("métier | déplacer au même endroit = sans effet", js(page, "%s.move('%s',null)" % (L, sejour)).get("unchanged") is True)
    check("métier | renommer avec un nom vide refusé", js(page, "%s.update('%s',{name:'   '})" % (L, sejour))["ok"] is False)
    check("métier | supprimer un identifiant inconnu refusé", js(page, "%s.remove('nope')" % L)["ok"] is False)
    check("métier | créer sous un parent inconnu refusé", js(page, "%s.create({name:'X', parentId:'nope'})" % L)["ok"] is False)
    commodes = js(page, "Rangement.store.locations().filter(function(l){return l.name==='Commode';}).map(function(l){return {id:l.id,parent:l.parentId};})")
    other_parent = commodes[0]["parent"]
    res = js(page, "%s.move('%s','%s')" % (L, commodes[1]["id"], other_parent))
    check("métier | nom en double à la destination refusé", res["ok"] is False and "existe déjà" in res["error"], res)
    check("métier | données valides après les essais", js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok"))

    # Texte hostile : jamais interprété comme du HTML
    js(page, "%s.create({name:'<img src=x onerror=window.__xss=1>', parentId:null})" % L)
    check("sécurité | nom hostile affiché comme texte", "<img src=x" in page.inner_text("#pane-tree") and page.locator("#pane-tree img, #pane-detail img").count() == 0)
    page.goto(base + "#/")
    page.wait_for_selector("#pane-detail .list")
    page.locator("#pane-detail .list-row", has_text="<img").first.click()
    page.get_by_role("button", name="Modifier").click()
    check("sécurité | dialogue : titre affiché comme texte", "<img src=x" in dlg(page).inner_text() and dlg(page).locator("img").count() == 0)
    check("sécurité | aucun script exécuté", page.evaluate("window.__xss") is None)
    page.keyboard.press("Escape")
    check("garde-fous | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_narrow(browser, base):
    errors = []
    ctx, page = new_page(browser, 390, 844, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    check("replié | 1 volet", page.get_attribute("html", "data-panes") == "1")
    page.get_by_role("button", name="Créer ma première pièce").click()
    d = dlg(page)
    box = d.bounding_box()
    check("replié | dialogue contenu dans l'écran", box["x"] >= 0 and box["x"] + box["width"] <= 390, box)
    boxes = [d.get_by_role("button", name=n).bounding_box() for n in ("Annuler", "Ajouter")]
    check("replié | boutons du dialogue assez grands (≥ 44 px)", all(b["height"] >= 44 for b in boxes), boxes)
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j2-replie-dialogue.png"))
    d.get_by_label("Nom").fill("Séjour")
    d.get_by_role("button", name="Ajouter", exact=True).click()
    page.wait_for_selector("#pane-detail .list-row:has-text('Séjour')")
    page.locator("#pane-detail .list-row", has_text="Séjour").click()
    wait_title(page, "Séjour")
    overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    check("replié | pas de défilement horizontal avec la barre d'actions", overflow <= 0, overflow)
    tools = page.locator("#pane-detail .toolbar .button")
    check("replié | 6 actions visibles pour un emplacement", tools.count() == 6)
    check("replié | boutons d'action ≥ 44 px", all(tools.nth(i).bounding_box()["height"] >= 44 for i in range(tools.count())))
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j2-replie-fiche.png"))
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()

    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector("#pane-tree .tree-link")
    expand_tree(page)
    page.locator("#pane-tree .tree-link", has_text="Meuble living").click()
    wait_title(page, "Meuble living")
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j2-deplie-fiche.png"))
    page.get_by_role("button", name="Déplacer").click()
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j2-deplie-deplacer.png"))
    page.keyboard.press("Escape")
    ctx.close()


def main():
    server = start_server()
    base = "http://127.0.0.1:%d/index.html" % server.server_address[1]
    file_url = "file://" + os.path.join(ROOT, "index.html")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        scenario_flow(browser, base, "http")
        scenario_flow(browser, file_url, "file")
        scenario_guards(browser, base)
        scenario_narrow(browser, base)
        browser.close()

    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
