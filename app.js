// Small behaviours shared by every page: which nav link is current, and a quiet fade-in
// for the lower sections. Nothing here is needed to read the site.
(function () {
  "use strict";

  // The nav links are written with aria-current on the right page already; this keeps it
  // right if a page is reached by another address (for example /about/index.html).
  function key(p) { return p.replace(/index\.html$/, "").replace(/\/$/, ""); }
  var here = key(location.pathname);
  document.querySelectorAll(".nav__links a").forEach(function (a) {
    var href = a.getAttribute("href");
    if (href.charAt(0) === "#") return;          // Contact is a jump on the same page, never "current"
    if (key(href) === here) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  });

  // Fade in lower sections once, as they arrive. .pre is added here, never in the HTML,
  // so without this script (or without motion) everything is simply visible.
  var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (calm || !("IntersectionObserver" in window)) return;
  var items = document.querySelectorAll("[data-reveal]");
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.remove("pre"); io.unobserve(e.target); }
    });
  }, { threshold: 0.12 });
  items.forEach(function (el) {
    var r = el.getBoundingClientRect();
    if (r.top < window.innerHeight * 0.9) return; // already on screen: leave it alone
    el.classList.add("pre");
    io.observe(el);
  });
})();
