/*
  js/ui/components/form.js — Application « Rangement »
  Version : V005
  Horodatage : 2026-10-23 23:50 (heure de Paris)
  Résumé : champ texte : attribut inputmode facultatif (clavier numérique pour la quantité).
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;

  // def : { name, label, type?: 'text'|'textarea'|'select', value?, options?: [{value,label}], hint?, maxlength?, inputmode? }
  // Renvoie { name, input, node }.
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
    var node = el('div', { class: 'field' }, [
      el('label', { 'for': id }, [def.label]),
      input,
      def.hint ? el('p', { class: 'field-hint' }, [def.hint]) : null
    ]);
    return { name: def.name, input: input, node: node };
  }

  function read(fields) {
    var values = {};
    fields.forEach(function (f) { values[f.name] = f.input.value; });
    return values;
  }

  R.ns('ui.components').form = { field: field, read: read };
})();
