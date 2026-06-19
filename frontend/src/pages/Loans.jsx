import { useState, useEffect, useCallback } from "react";
import API from "../services/api";
import DataTable from "../components/DataTable";
import EmptyState from "../components/EmptyState";
import { SkeletonTable } from "../components/Skeleton";
import { Plus, Search, X, CreditCard, ShieldAlert, Calendar, Clock } from "lucide-react";
import { formatCurrency, formatDate } from "../utils/formatters";
import { prepareFormPayload, getApiErrorMessage } from "../utils/formPayload";
import ProgressRing from "../components/ProgressRing";

function Loans() {
    const [loans, setLoans] = useState([]);
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [showForm, setShowForm] = useState(false);
    const [editing, setEditing] = useState(null);
    const [formData, setFormData] = useState({
        loan_name: "", principal_amount: "", remaining_amount: "", interest_rate: "", emi: "", start_date: "", end_date: "", status: "Active"
    });

    const loadData = useCallback(async () => {
        setLoading(true);
        try {
            const [list, sum] = await Promise.all([
                API.get("/api/loans"),
                API.get("/api/loan-summary")
            ]);
            setLoans(list.data?.data || []);
            setSummary(sum.data?.data || null);
        } catch (e) { console.error(e); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { loadData(); }, [loadData]);

    const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

    const handleSubmit = async () => {
        try {
            const payload = prepareFormPayload(formData, {
                numbers: ["principal_amount", "remaining_amount", "interest_rate", "emi"],
                dates: ["start_date", "end_date"],
            });
            if (editing) await API.put(`/api/loans/${editing.id}`, payload);
            else await API.post("/api/loans", payload);
            setShowForm(false); setEditing(null);
            setFormData({ loan_name: "", principal_amount: "", remaining_amount: "", interest_rate: "", emi: "", start_date: "", end_date: "", status: "Active" });
            loadData();
        } catch (e) { alert(getApiErrorMessage(e)); }
    };

    const handleEdit = (row) => {
        setEditing(row);
        setFormData({ loan_name: row.loan_name, principal_amount: row.principal_amount, remaining_amount: row.remaining_amount, interest_rate: row.interest_rate, emi: row.emi, start_date: row.start_date || "", end_date: row.end_date || "", status: row.status });
        setShowForm(true);
    };

    const handleDelete = async (row) => {
        if (!confirm("Delete this loan?")) return;
        try { await API.delete(`/api/loans/${row.id}`); loadData(); }
        catch (e) { alert(e.response?.data?.error || "Failed to delete"); }
    };

    const filtered = loans.filter(l => l.loan_name?.toLowerCase().includes(search.toLowerCase()));

    const columns = [
        { field: "loan_name", header: "Loan", sortable: true },
        { field: "principal_amount", header: "Principal", format: "currency", sortable: true },
        { field: "remaining_amount", header: "Remaining", format: "currency", sortable: true },
        { field: "interest_rate", header: "Rate", sortable: true, render: (v) => `${v}%` },
        { field: "emi", header: "EMI", format: "currency", sortable: true },
        { field: "months_remaining", header: "Months Left", sortable: true },
        { field: "status", header: "Status", sortable: true, render: (v) => <span className={`badge ${v === "Active" ? "badge-warning" : "badge-success"}`}>{v}</span> }
    ];

    const debtHealthColor = summary?.debt_burden_ratio > 40 ? "#ef4444" : summary?.debt_burden_ratio > 25 ? "#f59e0b" : "#10b981";

    return (
        <div>
            <div className="page-header">
                <div><h1>Loans</h1><p>Debt health, EMI analysis, and payoff projections</p></div>
                <button className="btn btn-primary" onClick={() => { setEditing(null); setShowForm(true); }}><Plus size={18} /> Add Loan</button>
            </div>

            {summary && (
                <div className="grid-kpi" style={{ marginBottom: 24 }}>
                    <div className="kpi-card"><div className="kpi-label">Total Debt</div><div className="kpi-value">{formatCurrency(summary.total_loan)}</div></div>
                    <div className="kpi-card"><div className="kpi-label">Total EMI</div><div className="kpi-value">{formatCurrency(summary.total_emi)}/mo</div></div>
                    <div className="kpi-card">
                        <div className="kpi-label">Debt Burden</div>
                        <div className="kpi-value" style={{ color: debtHealthColor }}>{summary.debt_burden_ratio}%</div>
                    </div>
                    <div className="kpi-card"><div className="kpi-label">Payoff Projection</div><div className="kpi-value">{summary.payoff_projection_months} months</div></div>
                </div>
            )}

            <div className="grid-2" style={{ marginBottom: 24 }}>
                <div className="card-glass" style={{ padding: 24, display: "flex", alignItems: "center", gap: 32 }}>
                    <ProgressRing
                        value={summary ? Math.max(0, 100 - summary.debt_burden_ratio) : 0}
                        size={130}
                        strokeWidth={10}
                        color={debtHealthColor}
                    />
                    <div>
                        <div className="kpi-label" style={{ marginBottom: 4 }}>Debt Health Score</div>
                        <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--text-primary)" }}>
                            {summary ? Math.max(0, 100 - summary.debt_burden_ratio).toFixed(0) : 0}/100
                        </div>
                        <p style={{ fontSize: "0.875rem", color: "var(--text-muted)", marginTop: 4 }}>
                            {summary?.debt_burden_ratio > 40 ? "High debt burden — consider consolidation" : summary?.debt_burden_ratio > 25 ? "Moderate burden — monitor closely" : "Healthy debt profile"}
                        </p>
                    </div>
                </div>
                <div className="card" style={{ padding: 24 }}>
                    <div className="section-title"><ShieldAlert size={18} /> Payoff Analysis</div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 16, marginTop: 8 }}>
                        {loans.slice(0, 3).map((loan) => {
                            const paidPct = loan.principal_amount > 0 ? ((loan.principal_amount - loan.remaining_amount) / loan.principal_amount) * 100 : 0;
                            return (
                                <div key={loan.id}>
                                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.875rem", fontWeight: 600, marginBottom: 6 }}>
                                        <span>{loan.loan_name}</span>
                                        <span style={{ color: "var(--text-muted)" }}>{loan.months_remaining} months left</span>
                                    </div>
                                    <div className="progress-bar-track">
                                        <div className="progress-bar-fill" style={{ width: `${paidPct}%` }} />
                                    </div>
                                    <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: 4 }}>
                                        {formatCurrency(loan.principal_amount - loan.remaining_amount)} paid of {formatCurrency(loan.principal_amount)} @ {loan.interest_rate}%
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>

            <div className="search-bar" style={{ marginBottom: 20, maxWidth: 400 }}>
                <Search size={18} style={{ color: "var(--text-muted)", flexShrink: 0 }} />
                <input type="text" placeholder="Search loans..." value={search} onChange={(e) => setSearch(e.target.value)} />
                {search && <button className="btn btn-ghost btn-sm" onClick={() => setSearch("")}><X size={16} /></button>}
            </div>

            {loading ? <SkeletonTable rows={4} cols={6} /> : (
                <DataTable columns={columns} data={filtered} onEdit={handleEdit} onDelete={handleDelete} />
            )}

            {filtered.length === 0 && !loading && (
                <EmptyState icon={CreditCard} title="No loans found" description={search ? "Try a different search" : "Track your loans and EMIs"} actionText={!search ? "Add Loan" : null} onAction={() => setShowForm(true)} />
            )}

            {showForm && (
                <div className="modal-overlay" onClick={() => setShowForm(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header"><h3>{editing ? "Edit Loan" : "Add Loan"}</h3><button className="btn btn-ghost btn-sm" onClick={() => setShowForm(false)}><X size={18} /></button></div>
                        <div className="modal-body">
                            <div className="form-row" style={{ gridTemplateColumns: "1fr" }}>
                                <div className="form-group"><label className="form-label">Loan Name</label><input type="text" name="loan_name" value={formData.loan_name} onChange={handleChange} placeholder="e.g., Home Loan, Car Loan" /></div>
                                <div className="form-group"><label className="form-label">Principal Amount</label><input type="number" name="principal_amount" value={formData.principal_amount} onChange={handleChange} /></div>
                                <div className="form-group"><label className="form-label">Remaining Amount</label><input type="number" name="remaining_amount" value={formData.remaining_amount} onChange={handleChange} /></div>
                                <div className="form-group"><label className="form-label">Interest Rate (%)</label><input type="number" step="0.01" name="interest_rate" value={formData.interest_rate} onChange={handleChange} /></div>
                                <div className="form-group"><label className="form-label">Monthly EMI</label><input type="number" name="emi" value={formData.emi} onChange={handleChange} /></div>
                                <div className="form-group"><label className="form-label">Start Date</label><input type="date" name="start_date" value={formData.start_date} onChange={handleChange} /></div>
                                <div className="form-group"><label className="form-label">End Date</label><input type="date" name="end_date" value={formData.end_date} onChange={handleChange} /></div>
                            </div>
                        </div>
                        <div className="modal-footer"><button className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button><button className="btn btn-primary" onClick={handleSubmit}>{editing ? "Update" : "Add"}</button></div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Loans;
