/*
  js/ui/components/form.js — Application « Rangement »
  Version : V009
  Horodatage : 2026-10-25 16:10 (heure de Paris)
  Résumé : validation champ par champ (validate, error, check) avec message sous le champ.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;

  // def : { name, label, type?: 'text'|'textarea'|'select', value?, options?: [{value,label}], hint?, maxlength?, inputmode?, validate?(valeur) → message|null }
  // Renvoie { name, input, node, validate, error, setError(msg), check() }.
  function field(def, id) {
    var input;
    if (def.type === 'select') {
      input = el('select', { id: id, name: def.name }, (def.options || []).map(function (o) {
        return el('option', { value: o.value }, [o.label]);
      }));
      input.value = def.value !== undefined ? def.value : '';
    } else if (def.type === 'textarea') {
      input = el('textarea', { id: id, name: def.name, rows: 3 });
      input.value = def.value || '';
    } else {
      input = el('input', {
        id: id,
        name: def.name,
        type: 'text',
        autocomplete: 'off',
        autocapitalize: 'sentences',
        inputmode: def.inputmode || null,
        maxlength: def.maxlength || null
      });
      input.value = def.value || '';
    }
    var errorNode = el('p', { class: 'field-error', id: id + '-err', role: 'alert', hidden: true });
    var node = el('div', { class: 'field' }, [
      el('label', { 'for': id }, [def.label]),
      input,
      def.hint ? el('p', { class: 'field-hint' }, [def.hint]) : null,
      errorNode
    ]);
    var f = { name: def.name, input: input, node: node, validate: def.validate || null, error: null };
    f.setError = function (msg) {
      f.error = msg || null;
      errorNode.textContent = msg || '';
      errorNode.hidden = !msg;
      if (msg) { input.setAttribute('aria-invalid', 'true'); input.setAttribute('aria-describedby', id + '-err'); }
      else { input.removeAttribute('aria-invalid'); input.removeAttribute('aria-describedby'); }
    };
    // Contrôle la valeur saisie : affiche le message d'erreur sous le champ. Renvoie true si la valeur est permise.
    f.check = function () {
      var msg = f.validate ? f.validate(input.value) : null;
      f.setError(msg);
      return !msg;
    };
    return f;
  }

  function read(fields) {
    var values = {};
    fields.forEach(function (f) { values[f.name] = f.input.value; });
    return values;
  }

  R.ns('ui.components').form = { field: field, read: read };
})();
