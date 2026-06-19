import { Link } from "react-router-dom";
import {
    ArrowRight, Sparkles, Shield, TrendingUp, Target,
    MessageSquare, BarChart3, Zap, CheckCircle2, ChevronDown
} from "lucide-react";

function Landing() {
    const scrollTo = (id) => {
        document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
    };

    return (
        <div style={{ overflow: "hidden" }}>
            {/* Hero Section */}
            <section style={{ position: "relative", minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: "80px 24px", overflow: "hidden" }}>
                <div style={{
                    position: "absolute", inset: 0,
                    background: "radial-gradient(ellipse at 30% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%), radial-gradient(ellipse at 70% 80%, rgba(20, 184, 166, 0.12) 0%, transparent 50%)",
                    pointerEvents: "none"
                }} />
                <div style={{ maxWidth: 1200, width: "100%", position: "relative", zIndex: 1, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 60, alignItems: "center" }}>
                    <div>
                        <div className="badge badge-info" style={{ marginBottom: 24, display: "inline-flex" }}>
                            <Sparkles size={14} /> AI-Powered Financial Intelligence
                        </div>
                        <h1 style={{
                            fontSize: "clamp(2.5rem, 5vw, 4rem)", fontWeight: 800, lineHeight: 1.1, letterSpacing: "-0.03em",
                            background: "linear-gradient(135deg, var(--text-primary), var(--primary-500), var(--accent-400))",
                            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text"
                        }}>
                            Your Personal AI CFO
                        </h1>
                        <p style={{ fontSize: "1.125rem", color: "var(--text-secondary)", marginTop: 20, lineHeight: 1.7, maxWidth: 480 }}>
                            Track expenses, optimize investments, manage loans, and achieve goals — all guided by an AI that understands your finances like a chief financial officer.
                        </p>
                        <div style={{ display: "flex", gap: 16, marginTop: 32, flexWrap: "wrap" }}>
                            <Link to="/register" className="btn btn-primary btn-lg" style={{ boxShadow: "var(--shadow-glow)" }}>
                                Get Started Free <ArrowRight size={18} />
                            </Link>
                            <button className="btn btn-secondary btn-lg" onClick={() => scrollTo("features")}>
                                Explore Features
                            </button>
                        </div>
                        <div style={{ display: "flex", gap: 24, marginTop: 40, fontSize: "0.875rem", color: "var(--text-muted)" }}>
                            <span style={{ display: "flex", alignItems: "center", gap: 6 }}><CheckCircle2 size={16} color="var(--success)" /> No credit card</span>
                            <span style={{ display: "flex", alignItems: "center", gap: 6 }}><CheckCircle2 size={16} color="var(--success)" /> Free forever</span>
                            <span style={{ display: "flex", alignItems: "center", gap: 6 }}><CheckCircle2 size={16} color="var(--success)" /> Bank-level security</span>
                        </div>
                    </div>
                    <div style={{ perspective: 1000 }}>
                        <div style={{
                            transform: "rotateY(-8deg) rotateX(4deg)", transformStyle: "preserve-3d",
                            borderRadius: "var(--radius-xl)", overflow: "hidden",
                            boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px var(--border-glass)"
                        }}>
                            <div style={{
                                background: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: "var(--radius-xl)", padding: 24,
                                display: "flex", flexDirection: "column", gap: 16
                            }}>
                                <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
                                    <div style={{ width: 40, height: 40, borderRadius: 12, background: "linear-gradient(135deg, var(--primary-500), var(--accent-400))", display: "flex", alignItems: "center", justifyContent: "center", color: "white" }}>
                                        <Sparkles size={20} />
                                    </div>
                                    <div>
                                        <div style={{ fontWeight: 700, fontSize: "0.875rem", color: "var(--text-primary)" }}>AI Personal CFO</div>
                                        <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Executive Dashboard</div>
                                    </div>
                                </div>
                                <div className="grid-kpi" style={{ gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                                    {[
                                        { label: "Net Worth", value: "₹24.5L" },
                                        { label: "Investments", value: "₹18.2L" },
                                        { label: "Savings Rate", value: "42%" },
                                        { label: "Health Score", value: "87/100" }
                                    ].map((kpi) => (
                                        <div key={kpi.label} className="kpi-card" style={{ padding: 14 }}>
                                            <div className="kpi-label" style={{ fontSize: "0.6875rem" }}>{kpi.label}</div>
                                            <div className="kpi-value" style={{ fontSize: "1.25rem" }}>{kpi.value}</div>
                                        </div>
                                    ))}
                                </div>
                                <div className="card" style={{ padding: 16, background: "var(--bg-hover)" }}>
                                    <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: 8 }}>AI Insight</div>
                                    <div style={{ fontSize: "0.875rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                                        Your savings rate is excellent. Consider increasing your SIP by ₹5,000 to reach your retirement goal 2 years earlier.
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <button onClick={() => scrollTo("features")} style={{ position: "absolute", bottom: 32, left: "50%", transform: "translateX(-50%)", color: "var(--text-muted)", animation: "bounce 2s infinite" }}>
                    <ChevronDown size={24} />
                </button>
                <style>{`
                    @keyframes bounce {
                        0%, 20%, 50%, 80%, 100% { transform: translateX(-50%) translateY(0); }
                        40% { transform: translateX(-50%) translateY(-10px); }
                        60% { transform: translateX(-50%) translateY(-5px); }
                    }
                `}</style>
            </section>

            {/* Features */}
            <section id="features" style={{ padding: "100px 24px", background: "var(--bg-surface)" }}>
                <div style={{ maxWidth: 1200, margin: "0 auto" }}>
                    <div style={{ textAlign: "center", marginBottom: 64 }}>
                        <div className="badge badge-info" style={{ marginBottom: 16, display: "inline-flex" }}>
                            <Zap size={14} /> Powerful Features
                        </div>
                        <h2 style={{ fontSize: "2.25rem", fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.02em" }}>Everything you need to master your money</h2>
                        <p style={{ color: "var(--text-muted)", marginTop: 12, fontSize: "1.0625rem" }}>A complete financial operating system powered by artificial intelligence</p>
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 24 }}>
                        {[
                            { icon: BarChart3, title: "Expense Tracking", desc: "Categorize, analyze, and optimize every rupee you spend with smart insights." },
                            { icon: TrendingUp, title: "Investment Analytics", desc: "Track portfolio performance, allocation, and ROI with real-time charts." },
                            { icon: Shield, title: "Debt Management", desc: "Monitor loans, EMIs, and payoff projections with a debt health score." },
                            { icon: Target, title: "Goal Planning", desc: "Set financial goals and get AI-powered projections on when you'll achieve them." },
                            { icon: MessageSquare, title: "AI CFO Chat", desc: "Ask questions, get advice, and even let the AI perform actions for you." },
                            { icon: Sparkles, title: "Smart Budgets", desc: "Set monthly budgets and get real-time alerts when you're close to limits." }
                        ].map((feature, i) => (
                            <div key={i} className="card" style={{ padding: 28, transition: "transform 0.3s ease", cursor: "default" }}>
                                <div style={{
                                    width: 48, height: 48, borderRadius: 12,
                                    background: "linear-gradient(135deg, var(--primary-500), var(--accent-400))",
                                    display: "flex", alignItems: "center", justifyContent: "center",
                                    color: "white", marginBottom: 20
                                }}>
                                    <feature.icon size={24} />
                                </div>
                                <h3 style={{ fontSize: "1.125rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: 8 }}>{feature.title}</h3>
                                <p style={{ fontSize: "0.9375rem", color: "var(--text-secondary)", lineHeight: 1.6 }}>{feature.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section style={{ padding: "100px 24px", textAlign: "center" }}>
                <div style={{ maxWidth: 640, margin: "0 auto" }}>
                    <h2 style={{ fontSize: "2.5rem", fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.02em", marginBottom: 16 }}>
                        Ready to meet your AI CFO?
                    </h2>
                    <p style={{ fontSize: "1.125rem", color: "var(--text-secondary)", marginBottom: 32 }}>
                        Join thousands of users who have transformed their financial lives with AI-powered insights and automation.
                    </p>
                    <Link to="/register" className="btn btn-primary btn-lg" style={{ boxShadow: "var(--shadow-glow)" }}>
                        Get Started For Free <ArrowRight size={18} />
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer style={{ padding: "40px 24px", borderTop: "1px solid var(--border-color)", textAlign: "center" }}>
                <p style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>
                    AI Personal CFO — Intelligent financial management for everyone.
                </p>
            </footer>
        </div>
    );
}

export default Landing;
