/* ANTONO - shared behaviour: theme, nav, reveal, counters, card glow, search. */
(function () {
  "use strict";

  var root = document.documentElement;
  var STORAGE_KEY = "antono-theme";

  /* ---- Theme ---- */
  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", theme === "light" ? "#eef6f8" : "#0b1116");
    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      btn.setAttribute("aria-label", theme === "light" ? "Aktifkan tema gelap" : "Aktifkan tema terang");
    });
  }

  var stored = null;
  try { stored = localStorage.getItem(STORAGE_KEY); } catch (e) { stored = null; }
  applyTheme(stored || "dark");

  document.addEventListener("click", function (event) {
    var toggle = event.target.closest("[data-theme-toggle]");
    if (!toggle) return;
    var next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
    applyTheme(next);
    try { localStorage.setItem(STORAGE_KEY, next); } catch (e) {}
  });

  /* ---- Mobile nav ---- */
  var navToggle = document.querySelector("[data-nav-toggle]");
  var nav = document.getElementById("primary-nav");
  if (navToggle && nav) {
    navToggle.addEventListener("click", function () {
      var open = nav.getAttribute("data-open") === "true";
      nav.setAttribute("data-open", String(!open));
      navToggle.setAttribute("aria-expanded", String(!open));
    });
  }

  /* ---- Scroll reveal ---- */
  var revealables = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window) {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    revealables.forEach(function (el) { revealObserver.observe(el); });
  } else {
    revealables.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---- Animated counters ---- */
  function animateCounter(el) {
    var target = parseFloat(el.getAttribute("data-count-to") || "0");
    var duration = 1100;
    var start = performance.now();
    function frame(now) {
      var progress = Math.min((now - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(target * eased).toLocaleString("id-ID");
      if (progress < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  var counters = document.querySelectorAll("[data-count-to]");
  if (counters.length && "IntersectionObserver" in window) {
    var counterObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        animateCounter(entry.target);
        counterObserver.unobserve(entry.target);
      });
    }, { threshold: 0.5 });
    counters.forEach(function (el) { counterObserver.observe(el); });
  } else {
    counters.forEach(function (el) { el.textContent = el.getAttribute("data-count-to"); });
  }

  /* ---- Pointer glow on cards ---- */
  document.querySelectorAll(".card").forEach(function (card) {
    card.addEventListener("pointermove", function (event) {
      var rect = card.getBoundingClientRect();
      card.style.setProperty("--mx", ((event.clientX - rect.left) / rect.width) * 100 + "%");
      card.style.setProperty("--my", ((event.clientY - rect.top) / rect.height) * 100 + "%");
    });
  });

  /* ---- Client-side filter (projects, updates) ---- */
  document.querySelectorAll("[data-filter-root]").forEach(function (rootEl) {
    var items = Array.prototype.slice.call(rootEl.querySelectorAll("[data-tags]"));
    var chips = Array.prototype.slice.call(rootEl.querySelectorAll("[data-filter]"));
    var input = rootEl.querySelector("[data-search]");
    var emptyState = rootEl.querySelector("[data-empty]");
    var countEl = rootEl.querySelector("[data-result-count]");
    var active = "all";

    function apply() {
      var query = (input && input.value ? input.value : "").trim().toLowerCase();
      var visible = 0;
      items.forEach(function (item) {
        var tags = (item.getAttribute("data-tags") || "").toLowerCase();
        var text = item.textContent.toLowerCase();
        var matchesTag = active === "all" || tags.indexOf(active) !== -1;
        var matchesQuery = !query || text.indexOf(query) !== -1;
        var show = matchesTag && matchesQuery;
        item.hidden = !show;
        if (show) visible += 1;
      });
      if (emptyState) emptyState.hidden = visible !== 0;
      if (countEl) countEl.textContent = String(visible);
    }

    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        active = chip.getAttribute("data-filter");
        chips.forEach(function (other) {
          other.setAttribute("aria-pressed", String(other === chip));
        });
        apply();
      });
    });

    if (input) input.addEventListener("input", apply);
    apply();
  });

  /* ---- Command-palette search ---- */
  var dialog = document.querySelector("[data-search-dialog]");
  if (dialog) {
    var searchInput = dialog.querySelector("[data-search-input]");
    var resultsEl = dialog.querySelector("[data-search-results]");
    var index = [];

    try { index = JSON.parse(dialog.getAttribute("data-index") || "[]"); } catch (e) { index = []; }

    function renderResults(query) {
      if (!resultsEl) return;
      var q = (query || "").trim().toLowerCase();
      var matches = index.filter(function (entry) {
        if (!q) return true;
        return (entry.title + " " + (entry.kind || "")).toLowerCase().indexOf(q) !== -1;
      }).slice(0, 8);

      if (!matches.length) {
        resultsEl.innerHTML = '<p class="empty">Tidak ada hasil untuk pencarian ini.</p>';
        return;
      }
      resultsEl.innerHTML = matches.map(function (entry) {
        return '<a class="result" href="' + entry.href + '">' +
          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h10"/></svg>' +
          '<span>' + entry.title + '</span><small>' + (entry.kind || "") + '</small></a>';
      }).join("");
    }

    function openDialog() {
      dialog.setAttribute("data-open", "true");
      if (searchInput) {
        searchInput.value = "";
        renderResults("");
        searchInput.focus();
      } else {
        renderResults("");
      }
    }

    function closeDialog() { dialog.setAttribute("data-open", "false"); }

    document.querySelectorAll("[data-search-open]").forEach(function (btn) {
      btn.addEventListener("click", openDialog);
    });

    dialog.addEventListener("click", function (event) {
      if (event.target === dialog) closeDialog();
    });

    if (searchInput) {
      searchInput.addEventListener("input", function () { renderResults(searchInput.value); });
    }

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeDialog();
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        openDialog();
      }
    });
  }

  /* ---- Contact form (static demo) ---- */
  var form = document.querySelector("[data-contact-form]");
  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var note = form.querySelector("[data-form-status]");
      if (note) {
        note.textContent = "Terima kasih! Pesan Anda tercatat. Ini situs statis - hubungkan ke backend atau layanan form untuk pengiriman nyata.";
        note.classList.remove("muted");
      }
      form.reset();
    });
  }
})();
