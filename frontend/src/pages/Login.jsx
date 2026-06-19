import { useState, useEffect } from "react";
import { Link, useNavigate, Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Mail, Lock, LogIn, Eye, EyeOff, ArrowLeft } from "lucide-react";

function CurrencyCycler({ interval = 1000 }) {
    const symbols = ['₹', '$', '€', '£', '¥'];
    const [symbol, setSymbol] = useState(symbols[0]);

    useEffect(() => {
        let i = 0;
        const iv = setInterval(() => {
            setSymbol(symbols[i % symbols.length]);
            i += 1;
        }, interval);

        return () => clearInterval(iv);
    }, [interval]);

    return (
        <div style={{ width: 56, height: 56, borderRadius: 16, background: "linear-gradient(135deg, var(--primary-500), var(--accent-400))", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px", color: "white", fontSize: 20, fontWeight: 700 }}>
            {symbol}
        </div>
    );
}

function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const { login, isAuthenticated, loading: authLoading } = useAuth();
    const navigate = useNavigate();

    if (!authLoading && isAuthenticated) {
        return <Navigate to="/app" replace />;
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        const result = await login(email, password);
        if (result.success) {
            if (result.user?.onboarding_complete) {
                navigate("/app");
            } else {
                navigate("/onboarding");
            }
        } else {
            setError(result.error || "Login failed");
        }
        setLoading(false);
    };

    return (
        <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: 24, background: "var(--bg-body)" }}>
            <div className="card-glass" style={{ width: "100%", maxWidth: 440, padding: 40 }}>
                <div style={{ textAlign: "center", marginBottom: 32 }}>
                    <CurrencyCycler interval={1000} />
                    <h1 style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: 4 }}>Welcome Back</h1>
                    <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>Sign in to your AI Personal CFO</p>
                </div>

                {error && (
                    <div className="insight-card critical" style={{ marginBottom: 20, padding: 12 }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                    <div className="form-group">
                        <label className="form-label">Email</label>
                        <div className="search-bar" style={{ padding: 0, borderRadius: "var(--radius-md)" }}>
                            <Mail size={18} style={{ color: "var(--text-muted)", marginLeft: 14, flexShrink: 0 }} />
                            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required style={{ border: "none", boxShadow: "none" }} />
                        </div>
                    </div>
                    <div className="form-group">
                        <label className="form-label">Password</label>
                        <div className="search-bar" style={{ padding: 0, borderRadius: "var(--radius-md)" }}>
                            <Lock size={18} style={{ color: "var(--text-muted)", marginLeft: 14, flexShrink: 0 }} />
                            <input type={showPassword ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter your password" required style={{ border: "none", boxShadow: "none" }} />
                            <button type="button" className="btn btn-ghost btn-sm" onClick={() => setShowPassword(!showPassword)} style={{ marginRight: 8 }}>
                                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                            </button>
                        </div>
                    </div>
                    <button type="submit" className="btn btn-primary btn-lg" disabled={loading} style={{ marginTop: 8 }}>
                        <LogIn size={18} /> {loading ? "Signing in..." : "Sign In"}
                    </button>
                </form>

                <div style={{ textAlign: "center", marginTop: 24, fontSize: "0.875rem", color: "var(--text-muted)" }}>
                    Don't have an account? <Link to="/register" style={{ color: "var(--primary-500)", fontWeight: 600 }}>Create one</Link>
                </div>
                <div style={{ textAlign: "center", marginTop: 12, fontSize: "0.875rem" }}>
                    <Link to="/" style={{ color: "var(--text-muted)", display: "inline-flex", alignItems: "center", gap: 6 }}>
                        <ArrowLeft size={16} /> Back to home
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default Login;
