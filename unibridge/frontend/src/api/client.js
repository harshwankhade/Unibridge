import axios from "axios";

const client = axios.create({
  baseURL: "http://localhost:8000",
});

// Attach JWT from localStorage to every request
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 401 → session expired: clear storage, alert, redirect to login
// 403 → authenticated but forbidden: let the calling component handle it
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.alert("Your session has expired. Please log in again.");
      window.location.href = "/login";
    }
    // 403 and all other errors propagate as-is
    return Promise.reject(error);
  }
);

export default client;
