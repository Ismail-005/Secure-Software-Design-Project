(function () {
  const root = document.documentElement;

  function getPreferredTheme() {
    const storedTheme = localStorage.getItem("theme");
    if (storedTheme === "dark" || storedTheme === "light") {
      return storedTheme;
    }

    const prefersDark = window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches;
    return prefersDark ? "dark" : "light";
  }

  function applyTheme(theme) {
    if (theme === "dark") {
      root.dataset.theme = "dark";
      localStorage.setItem("theme", "dark");
    } else {
      delete root.dataset.theme;
      localStorage.setItem("theme", "light");
    }
  }

  function syncToggleLabels() {
    const theme = root.dataset.theme === "dark" ? "dark" : "light";
    const nextLabel = theme === "dark" ? "Switch To Light" : "Switch To Dark";
    document.querySelectorAll("[data-theme-toggle]").forEach((toggle) => {
      toggle.textContent = nextLabel;
      toggle.setAttribute("aria-label", nextLabel);
    });
  }

  applyTheme(getPreferredTheme());

  document.addEventListener("DOMContentLoaded", function () {
    syncToggleLabels();

    document.querySelectorAll("[data-theme-toggle]").forEach((toggle) => {
      toggle.addEventListener("click", function () {
        const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
        applyTheme(nextTheme);
        syncToggleLabels();
      });
    });
  });
})();
