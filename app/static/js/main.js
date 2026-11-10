/* SkyBook front-end behaviour: seat map, hold countdown, filters, payment sim. */
(function () {
  "use strict";

  const money = (value) =>
    "₹" + Number(value).toLocaleString("en-IN", { maximumFractionDigits: 0 });

  /* ----------------------------- seat map ------------------------------ */
  const seatMap = document.querySelector("[data-seat-map]");
  if (seatMap) {
    const maxSeats = parseInt(seatMap.dataset.maxSeats || "1", 10);
    const form = document.getElementById("seatForm");
    const holder = document.getElementById("seatIds");
    const counter = document.getElementById("selectedCount");
    const totalEl = document.getElementById("seatTotal");
    const fareEl = document.getElementById("baseFare");
    const submitBtn = document.getElementById("continueBtn");
    const warning = document.getElementById("seatWarning");
    const maxPrice = parseFloat(seatMap.dataset.maxPrice || "0");
    const selected = new Map();

    function sync() {
      holder.innerHTML = "";
      let total = 0;
      selected.forEach((info, id) => {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "seat_ids";
        input.value = id;
        holder.appendChild(input);
        total += info.price;
      });
      if (counter) counter.textContent = selected.size;
      if (totalEl) totalEl.textContent = money(total);
      if (fareEl) fareEl.textContent = money(maxPrice + total);
      if (submitBtn) submitBtn.disabled = selected.size === 0;
      if (warning) {
        warning.style.display = selected.size === maxSeats ? "none" : "block";
      }
      const badge = document.getElementById("seatProgress");
      if (badge) badge.textContent = selected.size + " / " + maxSeats;
    }

    seatMap.addEventListener("click", (event) => {
      const seat = event.target.closest(
        ".seat.available, .seat[data-seat-status='AVAILABLE'], .seat[data-status='AVAILABLE']"
      );
      if (!seat || seat.disabled || seat.classList.contains("booked") || seat.classList.contains("held")) return;
      const id = seat.dataset.seatId;
      if (selected.has(id)) {
        selected.delete(id);
        seat.classList.remove("selected");
      } else {
        if (selected.size >= maxSeats) {
          if (warning) {
            warning.textContent =
              "You can select up to " + maxSeats + " seat" + (maxSeats > 1 ? "s" : "") + " for this booking.";
            warning.style.display = "block";
          }
          return;
        }
        selected.set(id, {
          price: parseFloat(seat.dataset.price || "0"),
          number: seat.dataset.seatNumber,
        });
        seat.classList.add("selected");
      }
      if (warning) warning.textContent = "";
      sync();
    });

    if (form) {
      form.addEventListener("submit", (event) => {
        if (selected.size === 0) {
          event.preventDefault();
          if (warning) {
            warning.textContent = "Select at least one seat to continue.";
            warning.style.display = "block";
          }
        }
      });
    }
    sync();
  }

  /* ---------------------------- countdowns ----------------------------- */
  document.querySelectorAll("[data-countdown]").forEach((el) => {
    let remaining = parseInt(el.dataset.countdown, 10);
    if (isNaN(remaining) || remaining < 0) remaining = 0;
    const target = el.querySelector("strong") || el;

    const render = () => {
      const minutes = Math.floor(remaining / 60);
      const seconds = remaining % 60;
      target.textContent =
        String(minutes).padStart(2, "0") + ":" + String(seconds).padStart(2, "0");
      if (remaining <= 300) el.classList.add("urgent");
    };
    render();
    if (remaining <= 0) return;
    const timer = setInterval(() => {
      remaining -= 1;
      if (remaining <= 0) {
        clearInterval(timer);
        render();
        const key = "skybook-reload-" + (el.dataset.countdownKey || "hold");
        if (!sessionStorage.getItem(key)) {
          sessionStorage.setItem(key, "1");
          window.location.reload();
        }
        return;
      }
      render();
    }, 1000);
  });

  /* -------------------------- filters auto-submit ---------------------- */
  document.querySelectorAll("[data-auto-submit] select, [data-auto-submit] input[type='checkbox']").forEach((input) => {
    input.addEventListener("change", () => {
      if (input.type === "checkbox" && input.form && input.form.querySelectorAll("input[type='checkbox']:checked").length === 0 && !input.dataset.alone) {
        return;
      }
      if (input.form) input.form.submit();
    });
  });

  /* --------------------------- payment outcome -------------------------- */
  const outcomeInputs = document.querySelectorAll("input[name='outcome']");
  const outcomePreview = document.getElementById("outcomePreview");
  outcomeInputs.forEach((input) => {
    input.addEventListener("change", () => {
      if (!outcomePreview) return;
      const fail = input.value === "failure" && input.checked;
      outcomePreview.className = fail
        ? "mock-switch mt-3 border-danger-subtle"
        : "mock-switch mt-3";
      outcomePreview.innerHTML = fail
        ? "<strong>Bank declined (simulated)</strong><br><span class='text-muted-2' style='font-size:.8rem'>The hold stays active so you can retry before it expires.</span>"
        : "<strong>Payment will succeed (simulated)</strong><br><span class='text-muted-2' style='font-size:.8rem'>The booking is confirmed and your e-ticket is generated instantly.</span>";
    });
  });

  /* ---------------------- confirmation before cancel -------------------- */
  const cancelForm = document.querySelector("[data-cancel-form]");
  if (cancelForm) {
    const confirmBox = cancelForm.querySelector("input[name='confirm']");
    const submit = cancelForm.querySelector("button[type='submit']");
    const syncCancel = () => {
      if (submit) submit.disabled = !(confirmBox && confirmBox.checked);
    };
    if (confirmBox) confirmBox.addEventListener("change", syncCancel);
    syncCancel();
  }

  /* ---------------------- payment method highlight ---------------------- */
  document.querySelectorAll(".pay-option input[type='radio']").forEach((input) => {
    const paint = () => {
      document.querySelectorAll(".pay-option").forEach((option) => {
        const radio = option.querySelector("input[type='radio']");
        option.style.borderColor = radio && radio.checked ? "var(--sky)" : "";
        option.style.background = radio && radio.checked ? "var(--sky-50)" : "";
      });
    };
    input.addEventListener("change", paint);
    paint();
  });

  /* -------------------------- dark mode toggle -------------------------- */
  const themeToggle = document.getElementById("themeToggle");
  if (themeToggle) {
    const getStoredTheme = () => {
      try {
        return localStorage.getItem("skybook_theme");
      } catch (e) {
        return null;
      }
    };

    const setStoredTheme = (theme) => {
      try {
        localStorage.setItem("skybook_theme", theme);
      } catch (e) {}
    };

    const applyTheme = (theme) => {
      document.documentElement.setAttribute("data-theme", theme);
      themeToggle.setAttribute("aria-label", "Switch to " + (theme === "dark" ? "light" : "dark") + " mode");
      themeToggle.setAttribute("title", "Switch to " + (theme === "dark" ? "light" : "dark") + " mode");
    };

    themeToggle.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "light";
      const next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      setStoredTheme(next);
    });

    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
      if (!getStoredTheme()) {
        applyTheme(e.matches ? "dark" : "light");
      }
    });
  }

  /* --------------------------- swap locations --------------------------- */
  const swap = document.getElementById("swapLocations");
  if (swap) {
    swap.addEventListener("click", () => {
      const from = document.getElementById("source");
      const to = document.getElementById("destination");
      if (!from || !to) return;
      const value = from.value;
      from.value = to.value;
      to.value = value;
    });
  }

  /* ----------------------------- date guard ---------------------------- */
  document.querySelectorAll("input[type='date']:not([name*='birth']):not([name*='dob'])").forEach((input) => {
    if (!input.min) {
      input.min = new Date().toISOString().split("T")[0];
    }
  });
})();
