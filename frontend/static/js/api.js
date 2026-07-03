// api.js
export async function apiFetch(url, options = {}) {
  const isFormData = options.body instanceof FormData;

  const makeRequest = () =>
    fetch(url, {
      ...options,
      credentials: "include",
      headers: {
        ...(options.headers || {}),
        ...(isFormData ? {} : { "Content-Type": "application/json" }),
      },
    });

  let res = await makeRequest();

  if (res.status === 401) {
    const refreshed = await refreshAccessToken();

    if (!refreshed) {
      window.location.href = "/login";
      return;
    }

    res = await makeRequest();
  }

  return res;
}