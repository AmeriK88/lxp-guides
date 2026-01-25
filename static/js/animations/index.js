import { initPageTransitions } from "./page_transitions.js";
import { initScrollReveal } from "./scroll_reveal.js";

document.addEventListener("DOMContentLoaded", () => {
  initPageTransitions();
  initScrollReveal();
});
