export function initPageTransitions() {
  const page = document.querySelector("[data-page]");
  if (!page) return;

  // allow CSS to apply initial state
  requestAnimationFrame(() => {
    page.classList.add("is-ready");
  });
}
