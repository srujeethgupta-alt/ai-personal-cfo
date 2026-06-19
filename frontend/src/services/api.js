import axios from "axios";

let apiBaseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Bumped on login/logout so stale in-flight requests cannot clear a fresh session.
let authEpoch = 0;
let onUnauthorized = null;

export function bumpAuthEpoch() {
    authEpoch += 1;
}

export function setUnauthorizedHandler(handler) {
    onUnauthorized = handler;
}

const API = axios.create({
    baseURL: apiBaseUrl,
    withCredentials: true,
    headers: {
        "Content-Type": "application/json"
    }
});

API.interceptors.request.use((config) => {
    config.authEpoch = authEpoch;
    const token = localStorage.getItem("access_token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

API.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            const url = error.config?.url || "";
            const isSessionCheck = url.includes("/api/auth/me");
            const isAuthRoute = url.includes("/api/auth/login") || url.includes("/api/auth/register");
            const isStale = error.config?.authEpoch !== authEpoch;

            if (!isSessionCheck && !isAuthRoute && !isStale) {
                onUnauthorized?.();
            }
        }
        return Promise.reject(error);
    }
);

export default API;
