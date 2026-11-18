// Fills the few values that may change (contact details, an announcement) from content.json.
// The same values are already written in the HTML, so the pages are complete without this
// script, and a missing key leaves the HTML as it is.
(function () {
  "use strict";

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function apply(c) {
    var contact = c && c.contact;
    if (contact && contact.email) {
      document.querySelectorAll("[data-email]").forEach(function (a) {
        a.textContent = contact.email;
        a.setAttribute("href", "mailto:" + contact.email);
      });
    }
    if (contact && Array.isArray(contact.mailing) && contact.mailing.length) {
      document.querySelectorAll("[data-mailing]").forEach(function (el) {
        el.innerHTML = contact.mailing.map(esc).join("<br>");
      });
    }
    var note = c && c.announcement;
    if (note && note.show && note.text) {
      document.querySelectorAll("[data-announcement]").forEach(function (el) {
        el.textContent = note.text;
        el.hidden = false;
      });
    }
  }

  fetch("/content.json", { cache: "no-store" })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(apply)
    .catch(function () { /* file:// or offline: the HTML defaults stay */ });
})();
