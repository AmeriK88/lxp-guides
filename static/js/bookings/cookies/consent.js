/* static/js/bookings/cookies/consent.js */
(() => {
  "use strict";

  // --- Config ---
  const STORAGE_KEY = "lx_cookie_consent_v1";
  const DEFAULTS = {
    decided: false,
    functional: false,
    analytics: false,
    marketing: false,
    timestamp: null,
  };

  // --- DOM helpers ---
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const banner = $("#cookie-banner");
  const modal = $("#cookie-modal");
  if (!banner || !modal) return;

  const overlay = modal.querySelector(".absolute.inset-0"); // backdrop
  const toggles = {
    functional: $('[data-cookie-toggle="functional"]', modal),
    analytics: $('[data-cookie-toggle="analytics"]', modal),
    marketing: $('[data-cookie-toggle="marketing"]', modal),
  };

  // --- State ---
  function readState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return { ...DEFAULTS };
      const parsed = JSON.parse(raw);
      return { ...DEFAULTS, ...parsed };
    } catch (e) {
      return { ...DEFAULTS };
    }
  }

  function writeState(next) {
    const state = {
      ...DEFAULTS,
      ...next,
      decided: true,
      timestamp: new Date().toISOString(),
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    return state;
  }

  function hasDecision(state) {
    return !!state?.decided;
  }

  // --- UI ---
  function show(el) {
    el.classList.remove("hidden");
    el.setAttribute("aria-hidden", "false");
  }

  function hide(el) {
    el.classList.add("hidden");
    el.setAttribute("aria-hidden", "true");
  }

  function syncTogglesFromState(state) {
    if (toggles.functional) toggles.functional.checked = !!state.functional;
    if (toggles.analytics) toggles.analytics.checked = !!state.analytics;
    if (toggles.marketing) toggles.marketing.checked = !!state.marketing;
  }

  function getTogglesValue() {
    return {
      functional: !!toggles.functional?.checked,
      analytics: !!toggles.analytics?.checked,
      marketing: !!toggles.marketing?.checked,
    };
  }

  function openModal() {
    // Siempre sincroniza con el estado actual
    const state = readState();
    syncTogglesFromState(state);
    show(modal);

    // Focus accesible: intenta enfocar el primer toggle
    const firstFocusable =
      toggles.functional ||
      $('[data-cookie-action="save"]', modal) ||
      $('[data-cookie-action="close"]', modal);
    firstFocusable?.focus?.();
  }

  function closeModal() {
    hide(modal);
  }

  function showBannerIfNeeded() {
    const state = readState();
    if (!hasDecision(state)) show(banner);
    else hide(banner);
  }

  // --- Consent actions ---
  function acceptAll() {
    const state = writeState({ functional: true, analytics: true, marketing: true });
    syncTogglesFromState(state);
    hide(banner);
    closeModal();
    // Hook opcional por si luego metes analytics:
    window.dispatchEvent(new CustomEvent("lx:cookies:consent", { detail: state }));
  }

  function rejectAll() {
    // necesarias siempre ON (no guardamos flag, se asume)
    const state = writeState({ functional: false, analytics: false, marketing: false });
    syncTogglesFromState(state);
    hide(banner);
    closeModal();
    window.dispatchEvent(new CustomEvent("lx:cookies:consent", { detail: state }));
  }

  function savePreferences() {
    const prefs = getTogglesValue();
    const state = writeState(prefs);
    hide(banner);
    closeModal();
    window.dispatchEvent(new CustomEvent("lx:cookies:consent", { detail: state }));
  }

  // --- Event bindings ---
  function handleAction(action) {
    switch (action) {
      case "accept":
        acceptAll();
        break;
      case "reject":
        rejectAll();
        break;
      case "manage":
        openModal();
        break;
      case "save":
        savePreferences();
        break;
      case "close":
        closeModal();
        break;
      default:
        break;
    }
  }

  // Clicks en botones con data-cookie-action (banner + modal)
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-cookie-action]");
    if (!btn) return;

    const action = btn.getAttribute("data-cookie-action");
    if (!action) return;

    e.preventDefault();
    handleAction(action);
  });

  // Botón footer: "Preferencias de cookies"
  document.addEventListener("click", (e) => {
    const openBtn = e.target.closest("[data-cookie-open]");
    if (!openBtn) return;
    e.preventDefault();
    openModal();
  });

  // Cerrar modal al click fuera (backdrop)
  if (overlay) {
    overlay.addEventListener("click", () => closeModal());
  }

  // Cerrar con ESC
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    if (!modal.classList.contains("hidden")) closeModal();
  });

  // Al cargar
  showBannerIfNeeded();

  // Si el usuario ya decidió, sincroniza toggles cuando abras modal
  // (ya lo hacemos dentro de openModal)
})();
