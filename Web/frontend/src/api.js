const BASE = "http://localhost:8000";

async function req(path, options = {}, token = null) {
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

export const api = {
  signup: (name, email, password) =>
    req("/auth/signup", { method: "POST", body: JSON.stringify({ name, email, password }) }),
  login: (email, password) =>
    req("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  analyze: (text, token) =>
    req("/analyze", { method: "POST", body: JSON.stringify({ text }) }, token),
  getHistory: (token) => req("/history", {}, token),
  deleteHistory: (id, token) => req(`/history/${id}`, { method: "DELETE" }, token),
};
