// document.addEventListener("DOMContentLoaded", () => {
//   const themeToggle = document.getElementById("themeToggle");

//   // ---------------- THEME ----------------
//   const savedTheme = localStorage.getItem("theme") || "light";
//   applyTheme(savedTheme);
//   themeToggle.checked = savedTheme === "dark";

//   themeToggle.addEventListener("change", () => {
//     const theme = themeToggle.checked ? "dark" : "light";
//     applyTheme(theme);
//     syncTheme(theme);
//   });

document.addEventListener("DOMContentLoaded", async () => {

  // ---------------- THEME ----------------
  const themeToggle = document.getElementById("themeToggle");
  const languageSelect = document.getElementById("languageSelect");

  if (!themeToggle) return;

  // Load preferences from backend (per-user)
  try {
    const res = await fetch("/api/settings/preferences", { credentials: "include" });
    if (res.ok) {
      const prefs = await res.json();
      const theme = prefs.theme || "light";
      const language = prefs.language || "en";

      document.documentElement.classList.toggle("dark", theme === "dark");
      themeToggle.checked = theme === "dark";
      localStorage.setItem("theme", theme);
      localStorage.setItem("language", language);

      if (languageSelect) {
        languageSelect.value = language;
      }
    }
  } catch (err) {
    console.error("Failed to load preferences:", err);
  }

  // Toggle theme
  themeToggle.addEventListener("change", () => {
    const theme = themeToggle.checked ? "dark" : "light";

    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem("theme", theme);
    syncTheme(theme);
  });

  // ---------------- LANGUAGE ----------------
  languageSelect?.addEventListener("change", function () {
    const lang = this.value;
    localStorage.setItem("language", lang);

    fetch("/api/settings/language", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ language: lang })
    });
  });

  // ---------------- EXPORT CSV ----------------
  document.getElementById("exportBtn")?.addEventListener("click", () => {
    window.location.href = "/api/settings/export_csv";
  });

  // ---------------- DELETE ALL ----------------
  document.getElementById("deleteAllBtn")?.addEventListener("click", async () => {
    const confirmText = prompt("Type DELETE to confirm:");
    if (confirmText !== "DELETE") return;

    const res = await fetch("/api/settings/delete_all", {
      method: "DELETE",
      credentials: "include"
    });

    const data = await res.json();
    alert(data.message);
  });

  // ---------------- LOGOUT ----------------
  document.getElementById("logoutBtn")?.addEventListener("click", async () => {
    await fetch("/logout", {
      method: "POST",
      credentials: "include"
    });
    window.location.href = "/";
  });

});

// ---------- HELPERS ----------
function applyTheme(theme) {
  document.documentElement.classList.toggle("dark", theme === "dark");
  localStorage.setItem("theme", theme);
}

function syncTheme(theme) {
  fetch("/api/settings/theme", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ theme })
  });
}

