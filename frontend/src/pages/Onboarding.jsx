import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import API from "../services/api";
import { ArrowRight, CheckCircle2, Briefcase, Globe, DollarSign, Target, Shield } from "lucide-react";

function Onboarding() {
    const [step, setStep] = useState(1);
    const [data, setData] = useState({
        occupation: "",
        salary: "",
        currency: "INR",
        country: "",
        risk_profile: "moderate",
        goals: []
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const { user, updateUser } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => setData({ ...data, [e.target.name]: e.target.value });

    const handleGoalToggle = (goal) => {
        const current = data.goals;
        if (current.includes(goal)) {
            setData({ ...data, goals: current.filter((g) => g !== goal) });
        } else {
            setData({ ...data, goals: [...current, goal] });
        }
    };

    const handleSubmit = async () => {
        setLoading(true);
        setError("");
        try {
            await API.post("/api/auth/onboarding", {
                occupation: data.occupation,
                salary: parseFloat(data.salary) || 0,
                currency: data.currency,
                country: data.country,
                risk_profile: data.risk_profile,
                goals: data.goals
            });
            updateUser({ onboarding_complete: true, occupation: data.occupation, salary: data.salary, currency: data.currency, country: data.country, risk_profile: data.risk_profile });
            navigate("/");
        } catch (e) {
            setError(e.response?.data?.error || "Failed to complete onboarding");
        } finally {
            setLoading(false);
        }
    };

    const goalOptions = [
        "Emergency Fund",
        "Buy a House",
        "Buy a Car",
        "Retirement",
        "Child Education",
        "Start a Business",
        "Travel",
        "Debt Freedom"
    ];

    return (
        <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: 24, background: "var(--bg-body)" }}>
            <div className="card-glass" style={{ width: "100%", maxWidth: 560, padding: 40 }}>
                <div style={{ textAlign: "center", marginBottom: 32 }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8, marginBottom: 16 }}>
                        {[1, 2, 3].map((s) => (
                            <div key={s} style={{
                                width: 32, height: 32, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center",
                                background: step >= s ? "linear-gradient(135deg, var(--primary-500), var(--accent-400))" : "var(--bg-hover)",
                                color: step >= s ? "white" : "var(--text-muted)", fontWeight: 700, fontSize: "0.875rem"
                            }}>
                                {step > s ? <CheckCircle2 size={16} /> : s}
                            </div>
                        ))}
                    </div>
                    <h1 style={{ fontSize: "1.375rem", fontWeight: 700, color: "var(--text-primary)" }}>
                        {step === 1 ? "Tell us about yourself" : step === 2 ? "Your financial profile" : "Your goals"}
                    </h1>
                    <p style={{ color: "var(--text-muted)", fontSize: "0.875rem", marginTop: 4 }}>
                        {step === 1 ? "Help us personalize your experience" : step === 2 ? "This helps us give better advice" : "What are you working towards?"}
                    </p>
                </div>

                {error && (
                    <div className="insight-card critical" style={{ marginBottom: 20, padding: 12 }}>
                        {error}
                    </div>
                )}

                {step === 1 && (
                    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                        <div className="form-group">
                            <label className="form-label">Occupation</label>
                            <div className="search-bar" style={{ padding: 0, borderRadius: "var(--radius-md)" }}>
                                <Briefcase size={18} style={{ color: "var(--text-muted)", marginLeft: 14, flexShrink: 0 }} />
                                <input type="text" name="occupation" value={data.occupation} onChange={handleChange} placeholder="e.g., Software Engineer, Doctor" style={{ border: "none", boxShadow: "none" }} />
                            </div>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Country</label>
                            <div className="search-bar" style={{ padding: 0, borderRadius: "var(--radius-md)" }}>
                                <Globe size={18} style={{ color: "var(--text-muted)", marginLeft: 14, flexShrink: 0 }} />
                                <select name="country" value={data.country} onChange={handleChange} style={{ border: "none", boxShadow: "none", background: "var(--bg-input)", color: "var(--text-primary)" }}>
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
                            <label className="form-label">Monthly Income</label>
                            <div className="search-bar" style={{ padding: 0, borderRadius: "var(--radius-md)" }}>
                                <DollarSign size={18} style={{ color: "var(--text-muted)", marginLeft: 14, flexShrink: 0 }} />
                                <input type="number" name="salary" value={data.salary} onChange={handleChange} placeholder="Your monthly salary" style={{ border: "none", boxShadow: "none" }} />
                            </div>
                        </div>
                        <button className="btn btn-primary btn-lg" onClick={() => setStep(2)}>
                            Continue <ArrowRight size={18} />
                        </button>
                    </div>
                )}

                {step === 2 && (
                    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                        <div className="form-group">
                            <label className="form-label">Risk Profile</label>
                            <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                                {["conservative", "moderate", "aggressive"].map((profile) => (
                                    <button
                                        key={profile}
                                        type="button"
                                        className={`btn ${data.risk_profile === profile ? "btn-primary" : "btn-secondary"}`}
                                        onClick={() => setData({ ...data, risk_profile: profile })}
                                        style={{ flex: 1, minWidth: 100, textTransform: "capitalize" }}
                                    >
                                        <Shield size={16} /> {profile}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Currency</label>
                            <select name="currency" value={data.currency} onChange={handleChange} style={{ border: "none", boxShadow: "none", background: "var(--bg-input)", color: "var(--text-primary)" }}>
                                <option value="INR">INR ₹</option>
                                <option value="USD">USD $</option>
                                <option value="EUR">EUR €</option>
                                <option value="GBP">GBP £</option>
                                <option value="JPY">JPY ¥</option>
                            </select>
                        </div>
                        <div style={{ display: "flex", gap: 12 }}>
                            <button className="btn btn-secondary" onClick={() => setStep(1)}>Back</button>
                            <button className="btn btn-primary btn-lg" onClick={() => setStep(3)} style={{ flex: 1 }}>
                                Continue <ArrowRight size={18} />
                            </button>
                        </div>
                    </div>
                )}

                {step === 3 && (
                    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                        <div className="form-group">
                            <label className="form-label">Select Your Goals</label>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                                {goalOptions.map((goal) => (
                                    <button
                                        key={goal}
                                        type="button"
                                        className={`btn ${data.goals.includes(goal) ? "btn-primary" : "btn-secondary"}`}
                                        onClick={() => handleGoalToggle(goal)}
                                        style={{ justifyContent: "flex-start", textAlign: "left" }}
                                    >
                                        <Target size={16} /> {goal}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div style={{ display: "flex", gap: 12 }}>
                            <button className="btn btn-secondary" onClick={() => setStep(2)}>Back</button>
                            <button className="btn btn-primary btn-lg" onClick={handleSubmit} disabled={loading} style={{ flex: 1 }}>
                                {loading ? "Saving..." : "Complete Setup"} <ArrowRight size={18} />
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Onboarding;
