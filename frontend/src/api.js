const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function api(path, options = {}) {
  const token = localStorage.getItem("voice_token");
  const headers = new Headers(options.headers || {});
  if (!(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let res;
  try {
    res = await fetch(`${API}${path}`, { ...options, headers });
  } catch {
    throw new Error("Cannot connect to the backend. Make sure FastAPI is running on http://localhost:8000.");
  }

  const text = await res.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; } catch { data = { detail: text }; }

  if (res.status === 401 && !path.startsWith("/api/auth/")) {
    localStorage.removeItem("voice_token");
    localStorage.removeItem("voice_user");
    if (window.location.pathname !== "/login") {
      window.location.replace("/login?session=expired");
    }
    throw new Error("Your login session expired. Please log in again.");
  }

  if (!res.ok) throw new Error(data.detail || data.message || "Request failed");
  return data;
}

export { API };
