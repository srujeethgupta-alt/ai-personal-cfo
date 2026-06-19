import { createContext, useContext, useState, useEffect, useCallback, useRef } from "react";
import API, { bumpAuthEpoch, setUnauthorizedHandler } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(() => {
        const saved = localStorage.getItem("user");
        return saved ? JSON.parse(saved) : null;
    });
    const [loading, setLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(() => !!localStorage.getItem("access_token"));
    const sessionCheckRef = useRef(null);

    const logout = useCallback(() => {
        bumpAuthEpoch();
        sessionCheckRef.current?.abort();
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user");
        setUser(null);
        setIsAuthenticated(false);
    }, []);

    useEffect(() => {
        setUnauthorizedHandler(() => logout());
        return () => setUnauthorizedHandler(null);
    }, [logout]);

    const validateSession = useCallback(async (signal, expectedToken) => {
        const res = await API.get("/api/auth/me", { signal });
        if (localStorage.getItem("access_token") !== expectedToken) {
            return null;
        }
        const u = res.data?.data;
        setUser(u);
        localStorage.setItem("user", JSON.stringify(u));
        setIsAuthenticated(true);
        return u;
    }, []);

    useEffect(() => {
        const token = localStorage.getItem("access_token");
        if (!token) {
            setLoading(false);
            return;
        }

        const controller = new AbortController();
        sessionCheckRef.current = controller;

        validateSession(controller.signal, token)
            .catch((err) => {
                if (err.name === "CanceledError" || err.code === "ERR_CANCELED") return;
                if (controller.signal.aborted) return;
                if (localStorage.getItem("access_token") !== token) return;
                if (err.response?.status === 401) {
                    logout();
                }
            })
            .finally(() => {
                if (!controller.signal.aborted) {
                    setLoading(false);
                }
            });

        return () => controller.abort();
    }, [logout, validateSession]);

    const login = useCallback(async (email, password) => {
        bumpAuthEpoch();
        sessionCheckRef.current?.abort();

        const res = await API.post("/api/auth/login", { email, password });
        const data = res.data?.data;
        if (data?.access_token) {
            localStorage.setItem("access_token", data.access_token);
            localStorage.setItem("refresh_token", data.refresh_token);
            localStorage.setItem("user", JSON.stringify(data.user));
            setUser(data.user);
            setIsAuthenticated(true);
            setLoading(false);
            return { success: true, user: data.user };
        }
        return { success: false, error: res.data?.error || "Login failed" };
    }, []);

    const register = useCallback(async (email, password, name, country, currency) => {
        bumpAuthEpoch();
        sessionCheckRef.current?.abort();

        const res = await API.post("/api/auth/register", { email, password, name, country, currency });
        const data = res.data?.data;
        if (data?.access_token) {
            localStorage.setItem("access_token", data.access_token);
            localStorage.setItem("refresh_token", data.refresh_token);
            localStorage.setItem("user", JSON.stringify(data.user));
            setUser(data.user);
            setIsAuthenticated(true);
            setLoading(false);
            return { success: true, user: data.user };
        }
        return { success: false, error: res.data?.error || "Registration failed" };
    }, []);

    const updateUser = useCallback((updates) => {
        setUser((prev) => {
            const updated = { ...prev, ...updates };
            localStorage.setItem("user", JSON.stringify(updated));
            return updated;
        });
    }, []);

    return (
        <AuthContext.Provider value={{ user, isAuthenticated, loading, login, register, logout, updateUser }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("useAuth must be used within AuthProvider");
    return ctx;
}
