(function () {
  console.log("loader.js loaded ✅");

  const loader = document.getElementById("app-loader"); // 👈 fijo
  if (!loader) {
    console.warn("AppLoader: #app-loader not found");
    return;
  }

  const labelEl = loader.querySelector(".loader-label");

  function show(label) {
    if (labelEl) labelEl.textContent = label || "Cargando…";
    loader.classList.add("is-open");
    loader.setAttribute("aria-hidden", "false");
  }

  function hide() {
    loader.classList.remove("is-open");
    loader.setAttribute("aria-hidden", "true");
  }

  window.AppLoader = { show, hide };

  // forms submit (captura)
  document.addEventListener(
    "submit",
    function (e) {
      const form = e.target;
      if (form && form.matches("[data-no-loader]")) return;
      show("Procesando…");
    },
    true
  );

  // clicks en links
  document.addEventListener(
    "click",
    function (e) {
      const link = e.target.closest("a");
      if (link) {
        const href = link.getAttribute("href");
        if (!href || href.startsWith("#") || href.startsWith("javascript:")) return;
        if (link.hasAttribute("data-no-loader")) return;
        if (link.target === "_blank") return;
        show("Cargando…");
        return;
      }

      // clicks en submit buttons
      const btn = e.target.closest('button[type="submit"], input[type="submit"]');
      if (btn) show("Procesando…");
    },
    true
  );

  // por si vuelves con bfcache
  window.addEventListener("pageshow", hide);
})();
