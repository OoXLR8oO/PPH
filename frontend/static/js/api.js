// api.js
import { goToLogin, refreshSession } from "/static/js/auth.js";


async function makeRequest(url, options) {
  const isFormData = options.body instanceof FormData;

  return fetch(url, {
    ...options,
    credentials: "include",
    headers: {
      ...(options.headers || {}),
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
    },
  });
}


/**
 * Fetch wrapper with automatic one-time refresh on 401.
 */
export async function apiFetch(url, options = {}) {
  let response = await makeRequest(url, options);

  if (response.status !== 401) {
    return response;
  }

  const refreshed = await refreshSession();

  if (!refreshed) {
    goToLogin();
    return response;
  }

  response = await makeRequest(url, options);

  if (response.status === 401) {
    goToLogin();
  }

  return response;
}