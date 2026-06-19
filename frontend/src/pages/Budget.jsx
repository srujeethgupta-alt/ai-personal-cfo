import { useState, useEffect, useCallback } from "react";
import API from "../services/api";
import DataTable from "../components/DataTable";
import EmptyState from "../components/EmptyState";
import { SkeletonTable } from "../components/Skeleton";
import { Plus, Search, X, Wallet, TrendingDown, AlertTriangle, CheckCircle2 } from "lucide-react";
import { formatCurrency, formatMonthYear } from "../utils/formatters";
import { prepareFormPayload, getApiErrorMessage } from "../utils/formPayload";

function Budget() {
    const [budgets, setBudgets] = useState([]);
    const [status, setStatus] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [showForm, setShowForm] = useState(false);
    const [editing, setEditing] = useState(null);
    const [month, setMonth] = useState(new Date().getMonth() + 1);
    const [year, setYear] = useState(new Date().getFullYear());
    const [formData, setFormData] = useState({
        category: "", budget_amount: "", month: new Date().getMonth() + 1, year: new Date().getFullYear()
    });

    const loadData = useCallback(async () => {
        setLoading(true);
        try {
            const [list, stat] = await Promise.all([
                API.get(`/api/budgets?month=${month}&year=${year}`),
                API.get(`/api/budgets/status?month=${month}&year=${year}`)
            ]);
            setBudgets(list.data?.data || []);
            setStatus(stat.data?.data || []);
        } catch (e) { console.error(e); }
        finally { setLoading(false); }
    }, [month, year]);

    useEffect(() => { loadData(); }, [loadData]);

    const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

    const handleSubmit = async () => {
        try {
            const payload = prepareFormPayload(formData, {
                numbers: ["budget_amount"],
                integers: ["month", "year"],
            });
            if (editing) await API.put(`/api/budgets/${editing.id}`, payload);
            else await API.post("/api/budgets", payload);
            setShowForm(false); setEditing(null);
            setFormData({ category: "", budget_amount: "", month, year });
            loadData();
        } catch (e) { alert(getApiErrorMessage(e)); }
    };

    const handleDelete = async (row) => {
        if (!confirm("Delete this budget?")) return;
        try { await API.delete(`/api/budgets/${row.id}`); loadData(); }
        catch (e) { alert(e.response?.data?.error || "Failed to delete"); }
    };

    const filtered = budgets.filter(b => b.category?.toLowerCase().includes(search.toLowerCase()));

    const columns = [
        { field: "category", header: "Category", sortable: true },
        { field: "budget_amount", header: "Budgeted", format: "currency", sortable: true },
        { field: "month", header: "Month", sortable: true, render: (v, row) => formatMonthYear(row.month, row.year) }
    ];

    const totalBudgeted = budgets.reduce((s, b) => s + parseFloat(b.budget_amount || 0), 0);
    const totalSpent = status.reduce((s, st) => s + st.spent, 0);
    const overallUtilization = totalBudgeted > 0 ? (totalSpent / totalBudgeted) * 100 : 0;

    return (
        <div>
            <div className="page-header">
                <div><h1>Budget</h1><p>Set budgets and track spending against them</p></div>
                <button className="btn btn-primary" onClick={() => { setEditing(null); setShowForm(true); }}><Plus size={18} /> Set Budget</button>
            </div>

            {/* Month/Year selector */}
            <div style={{ display: "flex", gap: 12, marginBottom: 20, alignItems: "center" }}>
                <select value={month} onChange={(e) => setMonth(Number(e.target.value))} style={{ width: "auto", minWidth: 120 }}>
                    {Array.from({ length: 12 }, (_, i) => (
                        <option key={i + 1} value={i + 1}>{new Date(2000, i, 1).toLocaleString("en-IN", { month: "long" })}</option>
                    ))}
                </select>
                <select value={year} onChange={(e) => setYear(Number(e.target.value))} style={{ width: "auto", minWidth: 100 }}>
                    {[year - 1, year, year + 1].map(y => <option key={y} value={y}>{y}</option>)}
                </select>
            </div>

            {/* Summary */}
            <div className="grid-kpi" style={{ marginBottom: 24 }}>
                <div className="kpi-card"><div className="kpi-label">Total Budgeted</div><div className="kpi-value">{formatCurrency(totalBudgeted)}</div></div>
                <div className="kpi-card"><div className="kpi-label">Total Spent</div><div className="kpi-value" style={{ color: totalSpent > totalBudgeted ? "var(--danger)" : "var(--text-primary)" }}>{formatCurrency(totalSpent)}</div></div>
                <div className="kpi-card">
                    <div className="kpi-label">Utilization</div>
                    <div className="kpi-value" style={{ color: overallUtilization > 100 ? "var(--danger)" : overallUtilization > 80 ? "var(--warning)" : "var(--success)" }}>
                        {overallUtilization.toFixed(1)}%
                    </div>
                </div>
            </div>

            {/* Budget Status */}
            <div className="card" style={{ padding: 24, marginBottom: 24 }}>
                <div className="section-title"><Wallet size={18} /> Budget vs Actual — {formatMonthYear(month, year)}</div>
                {status.length === 0 ? (
                    <EmptyState icon={Wallet} title="No budget data" description="Set budgets for this month to see comparisons" />
                ) : (
                    <div style={{ display: "flex", flexDirection: "column", gap: 16, marginTop: 12 }}>
                        {status.map((st) => (
                            <div key={st.category}>
                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.875rem", fontWeight: 600, marginBottom: 6 }}>
                                    <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                        {st.utilization_pct > 100 ? <AlertTriangle size={14} color="var(--danger)" /> : st.utilization_pct > 80 ? <TrendingDown size={14} color="var(--warning)" /> : <CheckCircle2 size={14} color="var(--success)" />}
                                        {st.category}
                                    </span>
                                    <span style={{ color: "var(--text-muted)" }}>
                                        {formatCurrency(st.spent)} of {formatCurrency(st.budgeted)} ({st.utilization_pct.toFixed(0)}%)
                                    </span>
                                </div>
                                <div className="progress-bar-track" style={{ height: 8 }}>
                                    <div
                                        className="progress-bar-fill"
                                        style={{
                                            width: `${Math.min(100, st.utilization_pct)}%`,
                                            background: st.utilization_pct > 100 ? "var(--danger)" : st.utilization_pct > 80 ? "var(--warning)" : "var(--success)"
                                        }}
                                    />
                                </div>
                                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "var(--text-muted)", marginTop: 4 }}>
                                    <span>Remaining: {formatCurrency(st.remaining)}</span>
                                    <span>{st.utilization_pct > 100 ? "Over budget!" : st.utilization_pct > 80 ? "Getting close" : "On track"}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="search-bar" style={{ marginBottom: 20, maxWidth: 400 }}>
                <Search size={18} style={{ color: "var(--text-muted)", flexShrink: 0 }} />
                <input type="text" placeholder="Search budgets..." value={search} onChange={(e) => setSearch(e.target.value)} />
                {search && <button className="btn btn-ghost btn-sm" onClick={() => setSearch("")}><X size={16} /></button>}
            </div>

            {loading ? <SkeletonTable rows={4} cols={3} /> : (
                <DataTable columns={columns} data={filtered} onDelete={handleDelete} />
            )}

            {filtered.length === 0 && !loading && (
                <EmptyState icon={Wallet} title="No budgets set" description={search ? "Try a different search" : "Set monthly budgets to control spending"} actionText={!search ? "Set Budget" : null} onAction={() => setShowForm(true)} />
            )}

            {showForm && (
                <div className="modal-overlay" onClick={() => setShowForm(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header"><h3>{editing ? "Edit Budget" : "Set Budget"}</h3><button className="btn btn-ghost btn-sm" onClick={() => setShowForm(false)}><X size={18} /></button></div>
                        <div className="modal-body">
                            <div className="form-row" style={{ gridTemplateColumns: "1fr" }}>
                                <div className="form-group"><label className="form-label">Category</label><input type="text" name="category" value={formData.category} onChange={handleChange} placeholder="e.g., Food, Entertainment" /></div>
                                <div className="form-group"><label className="form-label">Budget Amount</label><input type="number" name="budget_amount" value={formData.budget_amount} onChange={handleChange} /></div>
                                <div className="form-group"><label className="form-label">Month</label><input type="number" name="month" min={1} max={12} value={formData.month} onChange={handleChange} /></div>
                                <div className="form-group"><label className="form-label">Year</label><input type="number" name="year" value={formData.year} onChange={handleChange} /></div>
                            </div>
                        </div>
                        <div className="modal-footer"><button className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button><button className="btn btn-primary" onClick={handleSubmit}>{editing ? "Update" : "Set Budget"}</button></div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Budget;
