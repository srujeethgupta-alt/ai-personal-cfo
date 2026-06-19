import { useState, useEffect, useCallback } from "react";
import API from "../services/api";
import DataTable from "../components/DataTable";
import EmptyState from "../components/EmptyState";
import { SkeletonTable } from "../components/Skeleton";
import { Plus, Search, X, Target, Calendar, TrendingUp, Clock } from "lucide-react";
import { formatCurrency, formatDate } from "../utils/formatters";
import { prepareFormPayload, getApiErrorMessage } from "../utils/formPayload";
import ProgressRing from "../components/ProgressRing";

function Goals() {
    const [goals, setGoals] = useState([]);
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [showForm, setShowForm] = useState(false);
    const [editing, setEditing] = useState(null);
    const [formData, setFormData] = useState({
        goal_name: "", target_amount: "", current_amount: "", target_date: "", status: "Active"
    });

    const loadData = useCallback(async () => {
        setLoading(true);
        try {
            const [list, sum] = await Promise.all([
                API.get("/api/goals"),
                API.get("/api/goals/summary")
            ]);
            setGoals(list.data?.data || []);
            setSummary(sum.data?.data || null);
        } catch (e) { console.error(e); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { loadData(); }, [loadData]);

    const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

    const handleSubmit = async () => {
        try {
            const payload = prepareFormPayload(formData, {
                numbers: ["target_amount", "current_amount"],
                dates: ["target_date"],
            });
            if (editing) await API.put(`/api/goals/${editing.id}`, payload);
            else await API.post("/api/goals", payload);
            setShowForm(false); setEditing(null);
            setFormData({ goal_name: "", target_amount: "", current_amount: "", target_date: "", status: "Active" });
            loadData();
        } catch (e) { alert(getApiErrorMessage(e)); }
    };

    const handleEdit = (row) => {
        setEditing(row);
        setFormData({ goal_name: row.goal_name, target_amount: row.target_amount, current_amount: row.current_amount, target_date: row.target_date || "", status: row.status });
        setShowForm(true);
    };

    const handleDelete = async (row) => {
        if (!confirm("Delete this goal?")) return;
        try { await API.delete(`/api/goals/${row.id}`); loadData(); }
        catch (e) { alert(e.response?.data?.error || "Failed to delete"); }
    };

    const filtered = goals.filter(g => g.goal_name?.toLowerCase().includes(search.toLowerCase()));

    const columns = [
        { field: "goal_name", header: "Goal", sortable: true },
        { field: "target_amount", header: "Target", format: "currency", sortable: true },
        { field: "current_amount", header: "Saved", format: "currency", sortable: true },
        { field: "remaining", header: "Remaining", format: "currency", sortable: true },
        { field: "progress", header: "Progress", sortable: true, render: (v) => <span style={{ fontWeight: 600, color: v >= 80 ? "var(--success)" : v >= 40 ? "var(--warning)" : "var(--danger)" }}>{v}%</span> },
        { field: "target_date", header: "Target Date", format: "date", sortable: true },
        { field: "status", header: "Status", sortable: true, render: (v) => <span className={`badge ${v === "Active" ? "badge-info" : "badge-success"}`}>{v}</span> }
    ];

    return (
        <div>
            <div className="page-header">
                <div><h1>Goals</h1><p>Smart goal tracking with projections and AI planning</p></div>
                <button className="btn btn-primary" onClick={() => { setEditing(null); setShowForm(true); }}><Plus size={18} /> Add Goal</button>
            </div>

            {summary && (
                <div className="grid-kpi" style={{ marginBottom: 24 }}>
                    <div className="kpi-card"><div className="kpi-label">Total Target</div><div className="kpi-value">{formatCurrency(summary.total_target)}</div></div>
                    <div className="kpi-card"><div className="kpi-label">Total Saved</div><div className="kpi-value">{formatCurrency(summary.total_saved)}</div></div>
                    <div className="kpi-card"><div className="kpi-label">Overall Progress</div><div className="kpi-value">{summary.progress}%</div></div>
                    <div className="kpi-card"><div className="kpi-label">Active Goals</div><div className="kpi-value">{summary.active_goals}</div></div>
                </div>
            )}

            <div className="search-bar" style={{ marginBottom: 20, maxWidth: 400 }}>
                <Search size={18} style={{ color: "var(--text-muted)", flexShrink: 0 }} />
                <input type="text" placeholder="Search goals..." value={search} onChange={(e) => setSearch(e.target.value)} />
                {search && <button className="btn btn-ghost btn-sm" onClick={() => setSearch("")}><X size={16} /></button>}
            </div>

            {loading ? <SkeletonTable rows={4} cols={6} /> : (
                <DataTable columns={columns} data={filtered} onEdit={handleEdit} onDelete={handleDelete} />
            )}

            {filtered.length === 0 && !loading && (
                <EmptyState icon={Target} title="No goals yet" description={search ? "Try a different search" : "Set financial goals and track your progress"} actionText={!search ? "Add Goal" : null} onAction={() => setShowForm(true)} />
            )}

            {/* Goal Cards */}
            {!loading && goals.length > 0 && (
                <div className="card" style={{ padding: 24, marginTop: 24 }}>
                    <div className="section-title"><Target size={18} /> Goal Visualizer</div>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 20, marginTop: 16 }}>
                        {goals.map((goal) => (
                            <div key={goal.id} className="goal-card">
                                <div className="goal-card-header">
                                    <div>
                                        <div className="goal-card-title">{goal.goal_name}</div>
                                        <div className="goal-card-meta">{goal.target_date ? `Target: ${formatDate(goal.target_date)}` : "No target date"}</div>
                                    </div>
                                    <ProgressRing value={goal.progress} size={64} strokeWidth={5} color={goal.progress >= 80 ? "var(--success)" : goal.progress >= 40 ? "var(--warning)" : "var(--primary-500)"} />
                                </div>
                                <div className="progress-bar-track" style={{ marginTop: 8 }}>
                                    <div className="progress-bar-fill" style={{ width: `${goal.progress}%`, background: goal.progress >= 80 ? "var(--success)" : goal.progress >= 40 ? "var(--warning)" : "var(--primary-500)" }} />
                                </div>
                                <div className="goal-card-stats">
                                    <span>{formatCurrency(goal.current_amount)} of {formatCurrency(goal.target_amount)}</span>
                                    <span style={{ fontWeight: 600, color: "var(--primary-500)" }}>{goal.progress}%</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {showForm && (
                <div className="modal-overlay" onClick={() => setShowForm(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header"><h3>{editing ? "Edit Goal" : "Add Goal"}</h3><button className="btn btn-ghost btn-sm" onClick={() => setShowForm(false)}><X size={18} /></button></div>
                        <div className="modal-body">
                            <div className="form-row" style={{ gridTemplateColumns: "1fr" }}>
                                <div className="form-group"><label className="form-label">Goal Name</label><input type="text" name="goal_name" value={formData.goal_name} onChange={handleChange} placeholder="e.g., Emergency Fund, New Car" /></div>
                                <div className="form-group"><label className="form-label">Target Amount</label><input type="number" name="target_amount" value={formData.target_amount} onChange={handleChange} /></div>
                                <div className="form-group"><label className="form-label">Current Amount</label><input type="number" name="current_amount" value={formData.current_amount} onChange={handleChange} /></div>
                                <div className="form-group"><label className="form-label">Target Date</label><input type="date" name="target_date" value={formData.target_date} onChange={handleChange} /></div>
                            </div>
                        </div>
                        <div className="modal-footer"><button className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button><button className="btn btn-primary" onClick={handleSubmit}>{editing ? "Update" : "Add"}</button></div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Goals;
