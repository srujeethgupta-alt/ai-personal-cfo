import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Mail, Lock, User, Globe, DollarSign, Eye, EyeOff, ArrowLeft, Sparkles } from "lucide-react";

function Register() {
    const [form, setForm] = useState({ name: "", email: "", password: "", country: "", currency: "INR" });
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        const result = await register(form.email, form.password, form.name, form.country, form.currency);
        if (result.success) {
            navigate("/onboarding");
        } else {
            setError(result.error || "Registration failed");
        }
        setLoading(false);
    };

    return (
        <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: 24, background: "var(--bg-body)" }}>
            <div className="card-glass" style={{ width: "100%", maxWidth: 480, padding: 40 }}>
                <div style={{ textAlign: "center", marginBottom: 32 }}>
                    <div style={{ width: 56, height: 56, borderRadius: 16, background: "linear-gradient(135deg, var(--primary-500), var(--accent-400))", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px", color: "white" }}>
                        <Sparkles size={28} />
                    </div>
                    <h1 style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: 4 }}>Create Account</h1>
                    <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>Start your journey with AI Personal CFO</p>
                </div>

                {error && (
                    <div className="insight-card critical" style={{ marginBottom: 20, padding: 12 }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                    <div className="form-group">
                        <label className="form-label">Full Name</label>
                        <div className="search-bar" style={{ padding: 0, borderRadius: "var(--radius-md)" }}>
                            <User size={18} style={{ color: "var(--text-muted)", marginLeft: 14, flexShrink: 0 }} />
                            <input type="text" name="name" value={form.name} onChange={handleChange} placeholder="Your name" required style={{ border: "none", boxShadow: "none" }} />
                        </div>
                    </div>
                    <div className="form-group">
                        <label className="form-label">Email</label>
                        <div className="search-bar" style={{ padding: 0, borderRadius: "var(--radius-md)" }}>
                            <Mail size={18} style={{ color: "var(--text-muted)", marginLeft: 14, flexShrink: 0 }} />
                            <input type="email" name="email" value={form.email} onChange={handleChange} placeholder="you@example.com" required style={{ border: "none", boxShadow: "none" }} />
                        </div>
                    </div>
                    <div className="form-group">
                        <label className="form-label">Password</label>
                        <div className="search-bar" style={{ padding: 0, borderRadius: "var(--radius-md)" }}>
                            <Lock size={18} style={{ color: "var(--text-muted)", marginLeft: 14, flexShrink: 0 }} />
                            <input type={showPassword ? "text" : "password"} name="password" value={form.password} onChange={handleChange} placeholder="Min 6 characters" required minLength={6} style={{ border: "none", boxShadow: "none" }} />
                            <button type="button" className="btn btn-ghost btn-sm" onClick={() => setShowPassword(!showPassword)} style={{ marginRight: 8 }}>
                                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                            </button>
                        </div>
                    </div>
                    <div className="form-row" style={{ gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                        <div className="form-group">
                            <label className="form-label">Country</label>
                            <div className="search-bar" style={{ padding: 0, borderRadius: "var(--radius-md)" }}>
                                <Globe size={18} style={{ color: "var(--text-muted)", marginLeft: 14, flexShrink: 0 }} />
                                <select name="country" value={form.country} onChange={handleChange} style={{ border: "none", boxShadow: "none", background: "var(--bg-input)", color: "var(--text-primary)" }}>
                                    <option value="">Select country</option>
                                    <option value="India">India</option>
                                    <option value="United States">United States</option>
                                    <option value="United Kingdom">United Kingdom</option>
                                    <option value="Canada">Canada</option>
                                    <option value="Australia">Australia</option>
                                    <option value="Germany">Germany</option>
                                    <option value="France">France</option>
                                    <option value="Japan">Japan</option>
                                    <option value="Singapore">Singapore</option>
                                    <option value="United Arab Emirates">United Arab Emirates</option>
                                </select>
                            </div>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Currency</label>
                            <div className="search-bar" style={{ padding: 0, borderRadius: "var(--radius-md)" }}>
                                <DollarSign size={18} style={{ color: "var(--text-muted)", marginLeft: 14, flexShrink: 0 }} />
                                <select name="currency" value={form.currency} onChange={handleChange} style={{ border: "none", boxShadow: "none", background: "var(--bg-input)", color: "var(--text-primary)" }}>
                                    <option value="INR">INR ₹</option>
                                    <option value="USD">USD $</option>
                                    <option value="EUR">EUR €</option>
                                    <option value="GBP">GBP £</option>
                                    <option value="JPY">JPY ¥</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <button type="submit" className="btn btn-primary btn-lg" disabled={loading} style={{ marginTop: 8 }}>
                        <Sparkles size={18} /> {loading ? "Creating account..." : "Create Account"}
                    </button>
                </form>

                <div style={{ textAlign: "center", marginTop: 24, fontSize: "0.875rem", color: "var(--text-muted)" }}>
                    Already have an account? <Link to="/login" style={{ color: "var(--primary-500)", fontWeight: 600 }}>Sign in</Link>
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

export default Register;
