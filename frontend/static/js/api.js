function apiFetch(url, options = {}) {
  const token = localStorage.getItem("access_token");

  const isFormData = options.body instanceof FormData;

  return fetch(url, {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      "Authorization": token ? `Bearer ${token}` : ""
    }
  });
}