function setStaggerDelays() {
  document.querySelectorAll("[data-stagger]").forEach((parent) => {
    const items = parent.querySelectorAll("[data-animate]");
    items.forEach((el, idx) => {
      el.style.setProperty("--delay", `${idx * 70}ms`);
    });
  });
}

export function initScrollReveal() {
  setStaggerDelays();

  const els = document.querySelectorAll("[data-animate]");
  if (!els.length) return;

  const observer = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-in");
        // reveal once (more “pro”)
        obs.unobserve(entry.target);
      });
    },
    {
      root: null,
      threshold: 0.12,
      rootMargin: "0px 0px -10% 0px", // reveal a bit before fully visible
    }
  );

  els.forEach((el) => observer.observe(el));
}
