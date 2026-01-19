(function () {
  const input = document.querySelector(".js-booking-date");
  const cfg = document.getElementById("booking-calendar-config");
  if (!input || !cfg) return;

  const urlBase = cfg.dataset.disabledDatesUrl;
  if (!urlBase) return;

  if (!window.flatpickr) return;

  let disabledSet = new Set();

  function getPeople() {
    const a = parseInt(document.querySelector('[name="adults"]')?.value || "1", 10);
    const c = parseInt(document.querySelector('[name="children"]')?.value || "0", 10);
    const i = parseInt(document.querySelector('[name="infants"]')?.value || "0", 10);
    const total = a + c + i;
    return total > 0 ? total : 1;
  }

  async function loadDisabledDates(year, month) {
    const start = new Date(year, month, 1);
    const end = new Date(year, month + 1, 0);

    const startISO = start.toISOString().slice(0, 10);
    const endISO = end.toISOString().slice(0, 10);

    const url = `${urlBase}?start=${startISO}&end=${endISO}&people=${getPeople()}`;
    const res = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
    const data = await res.json();

    disabledSet = new Set(data.disabled || []);
  }

  const fp = window.flatpickr(input, {
    dateFormat: "Y-m-d",
    minDate: "today",
    disable: [
      (date) => disabledSet.has(date.toISOString().slice(0, 10))
    ],
    onReady: async (selectedDates, dateStr, instance) => {
      await loadDisabledDates(instance.currentYear, instance.currentMonth);
      instance.redraw();
    },
    onMonthChange: async (selectedDates, dateStr, instance) => {
      await loadDisabledDates(instance.currentYear, instance.currentMonth);
      instance.redraw();
    },
  });

  ["adults", "children", "infants"].forEach((name) => {
    const el = document.querySelector(`[name="${name}"]`);
    if (!el) return;
    el.addEventListener("change", async () => {
      await loadDisabledDates(fp.currentYear, fp.currentMonth);
      fp.redraw();
    });
  });
})();
