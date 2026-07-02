export async function apiFetch(url, options = {}) {
  let token = localStorage.getItem("access_token");

  const isFormData = options.body instanceof FormData;

  const makeRequest = (t) =>
    fetch(url, {
      ...options,
      headers: {
        ...(options.headers || {}),
        ...(isFormData ? {} : { "Content-Type": "application/json" }),
        Authorization: t ? `Bearer ${t}` : ""
      }
    });

  let res = await makeRequest(token);

  // If token expired → try refresh once
  if (res.status === 401) {
    const newToken = await refreshAccessToken();

    if (!newToken) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
      return;
    }

    res = await makeRequest(newToken);
  }

  return res;
}