// auth.js
let currentUser = null;
let fetchPromise = null;


export async function getCurrentUser() {
  if (currentUser) return currentUser;
  if (fetchPromise) return fetchPromise;

  fetchPromise = (async () => {
    try {
      const response = await fetch("/me", {
        credentials: "include",
      });

      if (response.ok) {
        currentUser = await response.json();
        return currentUser;
      }

      return null;
    } catch (err) {
      console.error(err);
      return null;
    } finally {
      fetchPromise = null;
    }
  })();

  return fetchPromise;
}


export function logout() {
  currentUser = null;
  window.location.href = "/";
}


export function clearUserCache() {
  currentUser = null;
}


export function isAuthPage() {
  return window.location.pathname === "/login";
}


export async function redirectToLoginIfNeeded() {
  if (isAuthPage()) return;

  let res = await fetch("/me", {
    credentials: "include",
  });

  if (res.ok) return;

  if (res.status === 401) {
    const refreshed = await refreshAccessToken();

    if (!refreshed) {
      window.location.href = "/login";
      return;
    }

    res = await fetch("/me", {
      credentials: "include",
    });

    if (!res.ok) {
      window.location.href = "/login";
    }
  }
}


export function setupLogout() {
  const btn = document.getElementById("logoutBtn");

  if (!btn) return;

  btn.addEventListener("click", async () => {
    try {
      await fetch("/logout", {
        method: "POST",
        credentials: "include",
      });
    } 
    finally {
      currentUser = null;
      window.location.href = "/login";
    }
  });
}


async function refreshAccessToken() {
  const res = await fetch("/refresh", {
    method: "POST",
    credentials: "include"
  });

  if (!res.ok) return null;
  return res.ok;
}