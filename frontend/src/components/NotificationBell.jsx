import { useState, useEffect, useCallback } from "react";
import { Bell, X, CheckCheck } from "lucide-react";
import API from "../services/api";

function NotificationBell() {
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [open, setOpen] = useState(false);
    const [loading, setLoading] = useState(false);

    const load = useCallback(async () => {
        try {
            const res = await API.get("/api/notifications?limit=20");
            const data = res.data?.data;
            if (data) {
                setNotifications(data.notifications || []);
                setUnreadCount(data.unread_count || 0);
            }
        } catch (e) {
            console.error(e);
        }
    }, []);

    useEffect(() => {
        if (!localStorage.getItem("access_token")) return;

        const controller = new AbortController();

        const load = async () => {
            try {
                const res = await API.get("/api/notifications?limit=20", { signal: controller.signal });
                const data = res.data?.data;
                if (data) {
                    setNotifications(data.notifications || []);
                    setUnreadCount(data.unread_count || 0);
                }
            } catch (e) {
                if (e.name === "CanceledError" || e.code === "ERR_CANCELED") return;
                console.error(e);
            }
        };

        load();
        const interval = setInterval(load, 30000);
        return () => {
            controller.abort();
            clearInterval(interval);
        };
    }, []);

    const markAllRead = async () => {
        try {
            await API.post("/api/notifications/mark-read");
            load();
        } catch (e) {
            console.error(e);
        }
    };

    const markRead = async (id) => {
        try {
            await API.post(`/api/notifications/${id}/read`);
            load();
        } catch (e) {
            console.error(e);
        }
    };

    const deleteNotification = async (id) => {
        try {
            await API.delete(`/api/notifications/${id}`);
            load();
        } catch (e) {
            console.error(e);
        }
    };

    const severityColors = {
        info: "var(--info)",
        warning: "var(--warning)",
        critical: "var(--danger)",
        success: "var(--success)"
    };

    return (
        <div style={{ position: "relative" }}>
            <button className="btn btn-ghost" onClick={() => setOpen(!open)} style={{ position: "relative" }}>
                <Bell size={20} />
                {unreadCount > 0 && (
                    <span style={{
                        position: "absolute", top: -2, right: -2, width: 18, height: 18, borderRadius: "50%",
                        background: "var(--danger)", color: "white", fontSize: "0.625rem", fontWeight: 700,
                        display: "flex", alignItems: "center", justifyContent: "center"
                    }}>
                        {unreadCount > 9 ? "9+" : unreadCount}
                    </span>
                )}
            </button>

            {open && (
                <>
                    <div style={{ position: "fixed", inset: 0, zIndex: 149 }} onClick={() => setOpen(false)} />
                    <div className="card" style={{
                        position: "absolute", top: 44, right: 0, width: 360, maxHeight: 480, overflow: "hidden",
                        zIndex: 150, boxShadow: "var(--shadow-xl)"
                    }}>
                        <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--border-light)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                            <span style={{ fontWeight: 700, fontSize: "0.9375rem", color: "var(--text-primary)" }}>Notifications</span>
                            {unreadCount > 0 && (
                                <button className="btn btn-ghost btn-sm" onClick={markAllRead}>
                                    <CheckCheck size={14} /> Mark all read
                                </button>
                            )}
                        </div>
                        <div style={{ overflowY: "auto", maxHeight: 400 }}>
                            {notifications.length === 0 ? (
                                <div style={{ padding: 32, textAlign: "center", color: "var(--text-muted)", fontSize: "0.875rem" }}>
                                    No notifications yet
                                </div>
                            ) : (
                                notifications.map((n) => (
                                    <div
                                        key={n.id}
                                        style={{
                                            padding: "14px 20px", borderBottom: "1px solid var(--border-light)",
                                            background: n.is_read ? "transparent" : "var(--bg-hover)",
                                            cursor: "pointer", transition: "background 0.15s"
                                        }}
                                        onClick={() => !n.is_read && markRead(n.id)}
                                    >
                                        <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
                                            <div style={{
                                                width: 8, height: 8, borderRadius: "50%", marginTop: 6, flexShrink: 0,
                                                background: severityColors[n.severity] || "var(--info)"
                                            }} />
                                            <div style={{ flex: 1, minWidth: 0 }}>
                                                <div style={{ fontWeight: 600, fontSize: "0.8125rem", color: "var(--text-primary)", marginBottom: 2 }}>
                                                    {n.title}
                                                </div>
                                                <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                                                    {n.message}
                                                </div>
                                                <div style={{ fontSize: "0.6875rem", color: "var(--text-muted)", marginTop: 4 }}>
                                                    {new Date(n.created_at).toLocaleDateString()}
                                                </div>
                                            </div>
                                            <button className="btn btn-ghost btn-sm" onClick={(e) => { e.stopPropagation(); deleteNotification(n.id); }} style={{ color: "var(--text-muted)", padding: 4 }}>
                                                <X size={14} />
                                            </button>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}

export default NotificationBell;
