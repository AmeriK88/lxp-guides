export function initPageTransitions() {
  const page = document.querySelector(".page-enter");
  if (!page) return;

  page.classList.add("is-animating");

  requestAnimationFrame(() => {
    page.classList.add("is-ready");
  });

  page.addEventListener("transitionend", () => {
    page.classList.remove("is-animating");
    // Esto es clave: elimina cualquier transform residual
    page.style.transform = "none";
  }, { once: true });
}
