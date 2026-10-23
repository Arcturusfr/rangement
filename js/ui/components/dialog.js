/*
  js/ui/components/dialog.js — Application « Rangement »
  Version : V004
  Horodatage : 2026-10-23 11:34 (heure de Paris)
  Résumé : création — boîtes de dialogue : formulaire, confirmation, message.
*/
(function () {
  'use strict';

  var R = window.Rangement;
  var el = R.ui.dom.el;
  var counter = 0;

  function button(label, variant, attrs) {
    var cls = 'button' + (variant ? ' button--' + variant : '');
    return el('button', Object.assign({ class: cls, type: 'button' }, attrs || {}), [label]);
  }

  // Coque commune : <dialog> modale, retour du focus à la fermeture.
  // wrapperTag/wrapperAttrs(close) : 'form' pour un formulaire, 'div' sinon.
  function shell(title, wrapperTag, wrapperAttrs, bodyNodes, buttons) {
    counter += 1;
    var titleId = 'dlg-title-' + counter;
    var opener = document.activeElement;
    var dlg = el('dialog', { class: 'dialog', 'aria-labelledby': titleId });

    function close() { if (dlg.open) { dlg.close(); } }

    dlg.appendChild(el(wrapperTag, wrapperAttrs(close), [
      el('div', { class: 'dialog-body' }, [el('h2', { class: 'dialog-title', id: titleId }, [title])].concat(bodyNodes)),
      el('div', { class: 'dialog-actions' }, buttons(close))
    ]));

    dlg.addEventListener('close', function () {
      if (dlg.parentNode) { dlg.parentNode.removeChild(dlg); }
      if (opener && opener.focus && document.contains(opener)) { opener.focus(); }
    });

    document.body.appendChild(dlg);
    if (dlg.showModal) { dlg.showModal(); } else { dlg.setAttribute('open', ''); }
    return dlg;
  }

  function errorBox() {
    return el('p', { class: 'form-error', role: 'alert', hidden: true });
  }

  function showError(box, message) {
    box.textContent = message || 'Action impossible.';
    box.hidden = false;
  }

  // cfg : { title, fields, submitLabel, onSubmit(values) → { ok, error? } }
  function form(cfg) {
    counter += 1;
    var prefix = 'f' + counter + '_';
    var fields = cfg.fields.map(function (def, i) { return R.ui.components.form.field(def, prefix + i); });
    var box = errorBox();

    shell(
      cfg.title,
      'form',
      function (close) {
        return {
          class: 'dialog-form',
          novalidate: true,
          onsubmit: function (event) {
            event.preventDefault();
            var res = cfg.onSubmit(R.ui.components.form.read(fields));
            if (res && res.ok) { close(); } else { showError(box, res && res.error); }
          }
        };
      },
      fields.map(function (f) { return f.node; }).concat([box]),
      function (close) {
        return [
          button('Annuler', 'secondary', { onclick: close }),
          button(cfg.submitLabel || 'Enregistrer', '', { type: 'submit' })
        ];
      }
    );
  }

  // cfg : { title, message, confirmLabel, danger?, onConfirm() → { ok, error? } }
  function confirm(cfg) {
    var box = errorBox();
    shell(
      cfg.title,
      'div',
      function () { return { class: 'dialog-form' }; },
      [el('p', null, [cfg.message]), box],
      function (close) {
        return [
          button('Annuler', 'secondary', { onclick: close }),
          button(cfg.confirmLabel || 'Confirmer', cfg.danger ? 'danger' : '', {
            onclick: function () {
              var res = cfg.onConfirm();
              if (res && res.ok) { close(); } else { showError(box, res && res.error); }
            }
          })
        ];
      }
    );
  }

  // cfg : { title, message }
  function alertBox(cfg) {
    shell(
      cfg.title,
      'div',
      function () { return { class: 'dialog-form' }; },
      [el('p', null, [cfg.message])],
      function (close) { return [button('OK', '', { onclick: close })]; }
    );
  }

  R.ns('ui.components').dialog = { form: form, confirm: confirm, alert: alertBox };
})();
