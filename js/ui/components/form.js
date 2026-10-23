/*
  js/ui/components/form.js — Application « Rangement »
  Version : V004
  Horodatage : 2026-10-23 11:34 (heure de Paris)
  Résumé : création — champs de formulaire (texte, zone de texte, liste) et lecture des valeurs.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;

  // def : { name, label, type?: 'text'|'textarea'|'select', value?, options?: [{value,label}], hint?, maxlength? }
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
