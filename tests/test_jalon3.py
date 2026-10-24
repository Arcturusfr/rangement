# tests/test_jalon3.py — Application « Rangement »
# Version : V006
# Horodatage : 2026-10-24 13:10 (heure de Paris)
# Résumé : règles V006 — noms d'objets uniques par emplacement, quantité entière, objets à quantité nulle grisés.
#
# Lancement (depuis la racine du projet) :  python3 tests/test_jalon3.py
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


def closed(page):
    page.wait_for_selector("dialog.dialog[open]", state="detached")


def wait_title(page, title):
    page.wait_for_function("document.querySelector('#pane-detail .detail-title') && document.querySelector('#pane-detail .detail-title').textContent === %r" % title)


def open_row(page, name):
    page.locator("#pane-detail .list-row", has_text=name).first.click()
    wait_title(page, name)


def stored(page):
    return page.evaluate("JSON.parse(localStorage.getItem('rangement.data'))")


def js(page, expr):
    return page.evaluate(expr)


def load_demo(page):
    page.get_by_role("button", name="Charger les données de démonstration").click()
    page.wait_for_selector("#pane-detail .list")


def goto_tiroir(page):
    open_row(page, "Séjour")
    open_row(page, "Meuble living")
    open_row(page, "Tiroir bas gauche")


def add_item(page, name, quantity=None, tags=None, note=None):
    page.get_by_role("button", name="Ajouter un objet ici").click()
    d = dlg(page)
    d.get_by_label("Nom").fill(name)
    if quantity is not None:
        d.get_by_label("Quantité").fill(quantity)
    if tags is not None:
        d.get_by_label("Mots-clés").fill(tags)
    if note is not None:
        d.get_by_label("Note (facultatif)").fill(note)
    d.get_by_role("button", name="Ajouter", exact=True).click()


def item_by_name(page, name):
    return [i for i in stored(page)["items"] if i["name"] == name]


# ---------- scénarios ----------

def scenario_flow(browser, base, label):
    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    load_demo(page)

    # À la racine : on ne range pas d'objet directement dans le logement
    check(label + " | racine : pas de bouton « Ajouter un objet »", page.get_by_role("button", name="Ajouter un objet ici").count() == 0)

    goto_tiroir(page)
    check(label + " | bouton « Ajouter un objet ici » présent", page.get_by_role("button", name="Ajouter un objet ici").count() == 1)

    # Formulaire : valeurs par défaut, validations
    page.get_by_role("button", name="Ajouter un objet ici").click()
    d = dlg(page)
    check(label + " | quantité à 1 par défaut", d.get_by_label("Quantité").input_value() == "1")
    check(label + " | indication des virgules pour les mots-clés", "virgules" in d.inner_text())
    d.get_by_role("button", name="Ajouter", exact=True).click()
    check(label + " | nom vide refusé", "obligatoire" in d.inner_text() and d.is_visible())
    d.get_by_label("Nom").fill("Ampoules")
    d.get_by_label("Quantité").fill("abc")
    d.get_by_role("button", name="Ajouter", exact=True).click()
    check(label + " | quantité invalide refusée", "quantité" in d.inner_text().lower() and d.is_visible())
    d.get_by_label("Quantité").fill("-2")
    d.get_by_role("button", name="Ajouter", exact=True).click()
    check(label + " | quantité négative refusée", d.is_visible() and len(item_by_name(page, "Ampoules")) == 0)
    d.get_by_label("Quantité").fill("2,5")
    d.get_by_role("button", name="Ajouter", exact=True).click()
    check(label + " | quantité décimale refusée", "entier" in d.inner_text() and d.is_visible() and len(item_by_name(page, "Ampoules")) == 0, d.inner_text())
    d.get_by_label("Quantité").fill("3")
    d.get_by_label("Mots-clés").fill("  électricité , maison,Electricite, ")
    d.get_by_label("Note (facultatif)").fill("culot E27")
    d.get_by_label("Nom").press("Enter")
    closed(page)

    it = item_by_name(page, "Ampoules")
    check(label + " | objet créé", len(it) == 1)
    it = it[0] if it else {}
    check(label + " | quantité entière lue", it.get("quantity") == 3, it.get("quantity"))
    check(label + " | mots-clés séparés par des virgules, rognés, sans doublon", it.get("tags") == ["électricité", "maison"], it.get("tags"))
    check(label + " | rattaché au bon emplacement", bool(it) and js(page, "Rangement.store.getLocation('%s').name" % it["locationId"]) == "Tiroir bas gauche")
    row = page.locator("#pane-detail .list-item", has_text="Ampoules")
    check(label + " | ligne : quantité et mots-clés affichés", "\u00d7 3" in row.inner_text() and "électricité" in row.inner_text() and "maison" in row.inner_text(), row.inner_text())
    check(label + " | ligne : note affichée", "culot E27" in row.inner_text())

    # Quantité 1 : pas de pastille « × »
    row = page.locator("#pane-detail .list-item", has_text="Piles neuves")
    check(label + " | quantité 1 : pas de pastille « × »", "\u00d7" not in row.inner_text(), row.inner_text())
    check(label + " | quantité par défaut enregistrée = 1", item_by_name(page, "Piles neuves")[0]["quantity"] == 1)

    # Nom identique dans le même emplacement : refusé (casse et accents ignorés)
    page.get_by_role("button", name="Ajouter un objet ici").click()
    d = dlg(page)
    d.get_by_label("Nom").fill("piles NEUVES")
    d.get_by_role("button", name="Ajouter", exact=True).click()
    check(label + " | nom d'objet identique refusé dans un même emplacement", "existe déjà" in d.inner_text() and "quantité" in d.inner_text().lower() and d.is_visible(), d.inner_text())
    d.get_by_role("button", name="Annuler").click()
    closed(page)
    check(label + " | aucun doublon créé", len(item_by_name(page, "Piles neuves")) == 1 and len(item_by_name(page, "piles NEUVES")) == 0)

    # Annulation / Échap
    page.get_by_role("button", name="Ajouter un objet ici").click()
    dlg(page).get_by_label("Nom").fill("Fantôme")
    page.keyboard.press("Escape")
    closed(page)
    check(label + " | Échap : rien n'est créé", len(item_by_name(page, "Fantôme")) == 0)

    # Fiche d'un objet
    page.locator("#pane-detail .list-row", has_text="Ampoules").click()
    wait_title(page, "Ampoules")
    check(label + " | fiche : quantité", "Quantité : 3" in page.inner_text("#pane-detail .detail-meta"))
    crumb = page.inner_text("#pane-detail .breadcrumb").replace("\n", " ")
    check(label + " | fiche : fil d'Ariane complet", all(s in crumb for s in ["Logement", "Séjour", "Meuble living", "Tiroir bas gauche", "Ampoules"]), crumb)
    check(label + " | fiche : l'objet est l'élément courant du fil d'Ariane",
          page.locator("#pane-detail .breadcrumb [aria-current='page']").inner_text() == "Ampoules")
    check(label + " | fiche : mots-clés et note", "électricité" in page.inner_text("#pane-detail") and "culot E27" in page.inner_text("#pane-detail"))
    check(label + " | fiche : 3 actions", page.locator("#pane-detail .toolbar .button").count() == 3)
    check(label + " | fiche : emplacement surligné dans l'arborescence",
          page.locator("#pane-tree [aria-current='page']").inner_text().strip() == "Tiroir bas gauche")
    check(label + " | fiche : lien vers l'emplacement", "Séjour \u203a Meuble living \u203a Tiroir bas gauche" in page.inner_text("#pane-detail .item-where"))

    page.reload()
    page.wait_for_selector("#pane-detail .item-detail")
    check(label + " | fiche : lien direct conservé après rechargement", page.inner_text("#pane-detail .detail-title") == "Ampoules")
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, label + "-j3-fiche.png"))

    # Modification
    page.get_by_role("button", name="Modifier").click()
    d = dlg(page)
    check(label + " | modifier : champs préremplis",
          d.get_by_label("Nom").input_value() == "Ampoules" and d.get_by_label("Quantité").input_value() == "3"
          and d.get_by_label("Mots-clés").input_value() == "électricité, maison" and d.get_by_label("Note (facultatif)").input_value() == "culot E27",
          [d.get_by_label("Nom").input_value(), d.get_by_label("Quantité").input_value(), d.get_by_label("Mots-clés").input_value()])
    d.get_by_label("Nom").fill("Ampoules LED")
    d.get_by_label("Quantité").fill("6")
    d.get_by_label("Mots-clés").fill("éclairage")
    d.get_by_label("Note (facultatif)").fill("")
    d.get_by_role("button", name="Enregistrer").click()
    wait_title(page, "Ampoules LED")
    txt = page.inner_text("#pane-detail")
    check(label + " | modification affichée", "Quantité : 6" in txt and "éclairage" in txt and "maison" not in txt and "culot" not in txt, txt)
    check(label + " | nom vide refusé à la modification", js(page, "Rangement.features.items.update('%s',{name:'  '})" % item_by_name(page, "Ampoules LED")[0]["id"])["ok"] is False)

    # Déplacement
    page.get_by_role("button", name="Déplacer").click()
    d = dlg(page)
    options = d.get_by_label("Nouvel emplacement").locator("option").all_inner_texts()
    check(label + " | déplacer : propose tous les emplacements avec leur chemin",
          "Entrée \u203a Commode" in options and "Séjour \u203a Meuble living" in options and len(options) == 8, options)
    check(label + " | déplacer : emplacement actuel présélectionné", d.get_by_label("Nouvel emplacement").evaluate("s => s.options[s.selectedIndex].text") == "Séjour \u203a Meuble living \u203a Tiroir bas gauche")
    d.get_by_label("Nouvel emplacement").select_option(label="Entrée \u203a Commode")
    d.get_by_role("button", name="Déplacer", exact=True).click()
    closed(page)
    crumb = page.inner_text("#pane-detail .breadcrumb").replace("\n", " ")
    check(label + " | déplacé : fil d'Ariane à jour", "Entrée" in crumb and "Commode" in crumb and "Séjour" not in crumb, crumb)
    check(label + " | déplacé : arborescence surlignée à jour", page.locator("#pane-tree [aria-current='page']").inner_text().strip() == "Commode")
    page.locator("#pane-detail .item-where").click()
    wait_title(page, "Commode")
    check(label + " | emplacement d'arrivée liste l'objet", "Ampoules LED" in page.inner_text("#pane-detail .list"))

    # La suppression de l'ancien emplacement vidé reste possible, celle du nouveau est refusée
    page.get_by_role("button", name="Supprimer").click()
    d = dlg(page)
    check(label + " | emplacement contenant un objet : suppression refusée", "Suppression impossible" in d.inner_text() and "2 objets" in d.inner_text(), d.inner_text())
    d.get_by_role("button", name="OK").click()
    closed(page)

    # Suppression d'un objet
    n_before = len(stored(page)["items"])
    page.locator("#pane-detail .list-row", has_text="Ampoules LED").click()
    wait_title(page, "Ampoules LED")
    page.get_by_role("button", name="Supprimer").click()
    d = dlg(page)
    check(label + " | confirmation de suppression d'un objet", "Supprimer cet objet" in d.inner_text())
    d.get_by_role("button", name="Annuler").click()
    closed(page)
    check(label + " | annuler conserve l'objet", len(stored(page)["items"]) == n_before)
    page.get_by_role("button", name="Supprimer").click()
    dlg(page).get_by_role("button", name="Supprimer", exact=True).click()
    wait_title(page, "Commode")
    check(label + " | suppression effectuée, retour à l'emplacement", len(stored(page)["items"]) == n_before - 1 and "Ampoules LED" not in page.inner_text("#pane-detail"))

    # Objet inconnu
    page.goto(base + "#/o/inconnu")
    page.wait_for_selector("#pane-detail .empty")
    check(label + " | objet inconnu géré", "Objet introuvable" in page.inner_text("#pane-detail"))
    check(label + " | objet inconnu : racine surlignée", page.locator("#pane-tree [aria-current='page']").inner_text().strip() == "Logement")

    check(label + " | données enregistrées valides", js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok"))
    check(label + " | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_guards(browser, base):
    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    load_demo(page)

    I = "Rangement.features.items"
    loc_id = js(page, "Rangement.store.locations().filter(function(l){return l.name==='Meuble living';})[0].id")
    item_id = js(page, "Rangement.store.items()[0].id")

    check("métier | créer sans nom refusé", js(page, "%s.create({name:' ', locationId:'%s'})" % (I, loc_id))["ok"] is False)
    check("métier | créer dans un emplacement inconnu refusé", js(page, "%s.create({name:'X', locationId:'nope'})" % I)["ok"] is False)
    check("métier | créer sans emplacement refusé", js(page, "%s.create({name:'X'})" % I)["ok"] is False)
    check("métier | quantité négative refusée", js(page, "%s.create({name:'X', locationId:'%s', quantity:-1})" % (I, loc_id))["ok"] is False)
    check("métier | quantité décimale refusée (texte et nombre)", js(page, "[%s.create({name:'D1', locationId:'%s', quantity:'2,5'}).ok, %s.create({name:'D2', locationId:'%s', quantity:2.5}).ok, %s.create({name:'D3', locationId:'%s', quantity:'3.5'}).ok]" % (I, loc_id, I, loc_id, I, loc_id)) == [False, False, False])
    check("métier | quantité texte refusée", js(page, "%s.create({name:'X', locationId:'%s', quantity:'12abc'})" % (I, loc_id))["ok"] is False)
    check("métier | quantité 0 acceptée", js(page, "%s.create({name:'Zéro', locationId:'%s', quantity:'0'})" % (I, loc_id))["ok"] is True)
    check("métier | quantité 0 conservée", js(page, "Rangement.store.items().filter(function(i){return i.name==='Zéro';})[0].quantity") == 0)
    check("métier | quantité 1 par défaut", js(page, "%s.create({name:'Défaut', locationId:'%s'}).item.quantity" % (I, loc_id)) == 1)
    check("métier | mots-clés en tableau acceptés", js(page, "%s.create({name:'Tab', locationId:'%s', tags:['a','A',' b ']}).item.tags" % (I, loc_id)) == ["a", "b"])
    check("métier | analyse de la quantité (point et virgule)",
          js(page, "[%s.parseQuantity('3').value, %s.parseQuantity(' 12 ').value, %s.parseQuantity('').value, %s.parseQuantity('3,5').ok, %s.parseQuantity('3.5').ok]" % (I, I, I, I, I)) == [3, 12, 1, False, False])
    check("métier | modification partielle : le reste est inchangé", js(page, """(function(){
      var it = Rangement.store.getItem('%s'); var q = it.quantity, t = it.tags.join('|');
      var r = %s.update('%s', {note:'nouvelle note'});
      var a = Rangement.store.getItem('%s');
      return r.ok && a.quantity === q && a.tags.join('|') === t && a.note === 'nouvelle note';})()""" % (item_id, I, item_id, item_id)))
    tiroir_id = js(page, "Rangement.store.locations().filter(function(l){return l.name==='Tiroir bas gauche';})[0].id")
    res = js(page, "%s.create({name:'piles neuves', locationId:'%s'})" % (I, tiroir_id))
    check("métier | créer un nom identique refusé (casse ignorée)", res["ok"] is False and "existe déjà" in res["error"], res)
    res = js(page, "%s.create({name:'Piles neuves', locationId:'%s'})" % (I, loc_id))
    check("métier | même nom dans un autre emplacement autorisé", res["ok"] is True, res)
    twin = res["item"]["id"]
    res = js(page, "%s.move('%s','%s')" % (I, twin, tiroir_id))
    check("métier | déplacer vers un emplacement contenant ce nom refusé", res["ok"] is False and "destination" in res["error"], res)
    defaut = js(page, "Rangement.store.items().filter(function(i){return i.name==='Défaut';})[0].id")
    check("métier | renommer vers un nom existant refusé (accents ignorés)", js(page, "%s.update('%s',{name:'zero'})" % (I, defaut))["ok"] is False)
    check("métier | renommer en changeant seulement la casse autorisé", js(page, "%s.update('%s',{name:'défaut'})" % (I, defaut))["ok"] is True)
    check("métier | modifier un objet inconnu refusé", js(page, "%s.update('nope',{name:'x'})" % I)["ok"] is False)
    check("métier | déplacer vers un emplacement inconnu refusé", js(page, "%s.move('%s','nope')" % (I, item_id))["ok"] is False)
    check("métier | déplacer un objet inconnu refusé", js(page, "%s.move('nope','%s')" % (I, loc_id))["ok"] is False)
    check("métier | déplacer au même endroit = sans effet", js(page, "%s.move('%s', Rangement.store.getItem('%s').locationId)" % (I, item_id, item_id)).get("unchanged") is True)
    check("métier | supprimer un objet inconnu refusé", js(page, "%s.remove('nope')" % I)["ok"] is False)
    check("métier | l'horodatage de modification est mis à jour", js(page, "Rangement.store.getItem('%s').updatedAt >= Rangement.store.getItem('%s').createdAt" % (item_id, item_id)))
    check("métier | données valides après les essais", js(page, "Rangement.models.validateData(JSON.parse(localStorage.getItem('rangement.data'))).ok"))

    # Quantité nulle : cadre grisé dans la liste et sur la fiche
    page.goto(base + "#/l/" + loc_id)
    page.wait_for_selector("#pane-detail .list")
    muted = page.locator("#pane-detail .list-item--muted")
    check("quantité nulle | un seul cadre grisé dans la liste", muted.count() == 1 and "Zéro" in muted.inner_text(), muted.count())
    check("quantité nulle | pastille « × 0 »", "\u00d7 0" in muted.inner_text())
    bg_muted = muted.evaluate("e => getComputedStyle(e).backgroundColor")
    bg_normal = page.locator("#pane-detail .list-item:not(.list-item--muted)").first.evaluate("e => getComputedStyle(e).backgroundColor")
    check("quantité nulle | fond différent des autres objets", bg_muted != bg_normal, [bg_muted, bg_normal])
    col_muted = muted.locator(".list-title").evaluate("e => getComputedStyle(e).color")
    col_normal = page.locator("#pane-detail .list-item:not(.list-item--muted) .list-title").first.evaluate("e => getComputedStyle(e).color")
    check("quantité nulle | texte grisé", col_muted != col_normal, [col_muted, col_normal])
    muted.locator(".list-row").click()
    page.wait_for_selector("#pane-detail .item-detail")
    check("quantité nulle | fiche : cadre grisé et mention épuisé", page.locator("#pane-detail .detail-head--depleted").count() == 1 and "épuisé" in page.inner_text("#pane-detail .detail-meta"))

    # Texte hostile : jamais interprété comme du HTML
    res = js(page, "%s.create({name:'<img src=x onerror=window.__xss=1>', locationId:'%s', tags:'<b>gras</b>', note:'<script>window.__xss=2</script>'})" % (I, loc_id))
    page.goto(base + "#/l/" + loc_id)
    page.wait_for_selector("#pane-detail .list")
    check("sécurité | objet hostile affiché comme texte dans la liste", "<img src=x" in page.inner_text("#pane-detail") and page.locator("#pane-detail img, #pane-detail b").count() == 0)
    page.goto(base + "#/o/" + res["item"]["id"])
    page.wait_for_selector("#pane-detail .item-detail")
    check("sécurité | fiche : texte brut", "<img src=x" in page.inner_text("#pane-detail") and "<script>" in page.inner_text("#pane-detail") and page.locator("#pane-detail img, #pane-detail b").count() == 0)
    page.get_by_role("button", name="Modifier").click()
    check("sécurité | dialogue : titre en texte", "<img src=x" in dlg(page).inner_text() and dlg(page).locator("img").count() == 0)
    page.keyboard.press("Escape")
    closed(page)
    check("sécurité | aucun script exécuté", page.evaluate("window.__xss") is None)
    check("garde-fous | aucune erreur console", not errors, errors)
    ctx.close()


def scenario_narrow(browser, base):
    errors = []
    ctx, page = new_page(browser, 390, 844, errors)
    page.goto(base)
    page.wait_for_selector("#pane-detail .empty")
    load_demo(page)
    check("replié | 1 volet", page.get_attribute("html", "data-panes") == "1")
    goto_tiroir(page)

    page.get_by_role("button", name="Ajouter un objet ici").click()
    d = dlg(page)
    box = d.bounding_box()
    check("replié | dialogue d'objet contenu dans l'écran", box["x"] >= 0 and box["x"] + box["width"] <= 390 and box["y"] >= 0 and box["y"] + box["height"] <= 844, box)
    inputs = [d.get_by_label(n).bounding_box() for n in ("Nom", "Quantité", "Mots-clés")]
    check("replié | champs ≥ 44 px", all(b["height"] >= 44 for b in inputs), inputs)
    check("replié | clavier numérique pour la quantité", d.get_by_label("Quantité").get_attribute("inputmode") == "numeric")
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j3-replie-dialogue.png"))
    d.get_by_label("Nom").fill("Un objet au nom vraiment très très long pour vérifier le retour à la ligne sans débordement")
    d.get_by_label("Quantité").fill("12")
    d.get_by_label("Mots-clés").fill("alpha, beta, gamma")
    d.get_by_role("button", name="Ajouter", exact=True).click()
    closed(page)
    page.locator("#pane-detail .list-row", has_text="Un objet au nom").click()
    page.wait_for_selector("#pane-detail .item-detail")
    overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    check("replié | fiche : pas de défilement horizontal", overflow <= 0, overflow)
    tools = page.locator("#pane-detail .toolbar .button")
    check("replié | fiche : 3 actions ≥ 44 px", tools.count() == 3 and all(tools.nth(i).bounding_box()["height"] >= 44 for i in range(3)))
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j3-replie-fiche.png"))
    page.locator("#pane-detail .breadcrumb a", has_text="Tiroir bas gauche").click()
    wait_title(page, "Tiroir bas gauche")
    overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    check("replié | liste d'objets : pas de défilement horizontal", overflow <= 0, overflow)
    tools = page.locator("#pane-detail .toolbar .button")
    check("replié | barre d'actions : boutons ≥ 44 px", all(tools.nth(i).bounding_box()["height"] >= 44 for i in range(tools.count())))
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j3-replie-liste.png"))
    check("replié | aucune erreur console", not errors, errors)
    ctx.close()

    errors = []
    ctx, page = new_page(browser, 884, 1100, errors)
    page.goto(base)
    load_demo(page)
    page.locator("#pane-tree .tree-link", has_text="Grand tiroir du bas").click()
    wait_title(page, "Grand tiroir du bas")
    page.locator("#pane-detail .list-row", has_text="Jumelles Nikon").click()
    page.wait_for_selector("#pane-detail .item-detail")
    check("déplié | fiche d'objet à côté de l'arborescence", page.is_visible("#pane-tree") and page.is_visible("#pane-detail .item-detail"))
    if SHOTS:
        page.screenshot(path=os.path.join(SHOTS, "j3-deplie-fiche.png"))
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
        scenario_guards(browser, base)
        scenario_narrow(browser, base)
        browser.close()

    failed = [r for r in results if not r[1]]
    print("\n%d tests, %d échec(s)" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
