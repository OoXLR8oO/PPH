// auth.js
let currentUser = null;
let userFetchPromise = null;


/**
 * Fetches the current user from the backend.
 * Returns the user object or null if unauthenticated.
 */
async function fetchCurrentUser() {
  const response = await fetch("/me", {
    credentials: "include",
  });

  if (!response.ok) {
    return null;
  }

  return await response.json();
}


/**
 * Attempts to refresh the access token.
 * Returns true if successful.
 */
export async function refreshSession() {
  const response = await fetch("/refresh", {
    method: "POST",
    credentials: "include",
  });

  return response.ok;
}


/**
 * Ensures the browser has a valid authenticated session.
 *
 * Returns true if authenticated.
 * Returns false if the user must log in again.
 */
export async function ensureAuthenticated() {
  if (isAuthPage()) {
    return true;
  }

  let response = await fetch("/me", {
    credentials: "include",
  });

  if (response.ok) {
    return true;
  }

  if (response.status !== 401) {
    return false;
  }

  const refreshed = await refreshSession();

  if (!refreshed) {
    return false;
  }

  response = await fetch("/me", {
    credentials: "include",
  });

  return response.ok;
}


/**
 * Returns the currently authenticated user.
 * Uses an in-memory cache to avoid unnecessary requests.
 */
export async function getCurrentUser() {
  if (currentUser) {
    return currentUser;
  }

  if (userFetchPromise) {
    return userFetchPromise;
  }

  userFetchPromise = (async () => {
    const authenticated = await ensureAuthenticated();

    if (!authenticated) {
      return null;
    }

    currentUser = await fetchCurrentUser();
    return currentUser;
  })();

  try {
    return await userFetchPromise;
  } finally {
    userFetchPromise = null;
  }
}


/**
 * Clears the cached user.
 */
export function clearUserCache() {
  currentUser = null;
}


/**
 * Returns true if the current page is the login page.
 */
export function isAuthPage() {
  return window.location.pathname === "/login";
}


/**
 * Redirects the browser to the login page.
 */
export function goToLogin() {
  clearUserCache();
  window.location.href = "/login";
}


/**
 * Logs the current user out.
 */
export async function logout() {
  try {
    await fetch("/logout", {
      method: "POST",
      credentials: "include",
    });
  } finally {
    goToLogin();
  }
}


/**
 * Wires the logout button.
 */
export function setupLogout() {
  const button = document.getElementById("logoutBtn");

  if (!button) {
    return;
  }

  button.addEventListener("click", logout);
}