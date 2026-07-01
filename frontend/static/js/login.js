import { getToken } from "/static/js/auth.js";

if (getToken()) {
  window.location.href = "/";
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const error = document.getElementById("error");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    const res = await fetch("/api/login", {
      method: "POST",
      body: formData
    });

    const data = await res.json();

    if (!res.ok) {
      error.innerText = data.detail;
      return;
    }

    localStorage.setItem("access_token", data.access_token);

    window.location.href = "/";
  });
});