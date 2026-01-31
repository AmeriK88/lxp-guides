export function initPageTransitions() {
  const page = document.querySelector(".page-enter");
  if (!page) return;

  // Marca que la página está animándose
  page.classList.add("is-animating");

  // Forzamos un frame para que el browser registre el estado inicial
  requestAnimationFrame(() => {
    page.classList.add("is-ready");
  });

  // Cuando termina la transición de entrada
  page.addEventListener(
    "transitionend",
    (e) => {
      // Solo nos interesa la transición del contenedor, no hijos
      if (e.target !== page) return;

      page.classList.remove("is-animating");
      // ❌ NO tocar transform aquí
      // El hover y las cards necesitan el control total del transform
    },
    { once: true }
  );
}
