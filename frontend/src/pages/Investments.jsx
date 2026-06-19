import { useState, useEffect, useCallback } from "react";
import API from "../services/api";
import DataTable from "../components/DataTable";
import EmptyState from "../components/EmptyState";
import { SkeletonTable } from "../components/Skeleton";
import { Plus, Search, X, TrendingUp, PieChart, DollarSign } from "lucide-react";
import { formatCurrency, formatPercentage, getChartColors } from "../utils/formatters";
import { prepareFormPayload, getApiErrorMessage } from "../utils/formPayload";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { Pie } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend);
const COLORS = ["#6366f1", "#14b8a6", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4", "#22c55e"];

function Investments() {
    const [investments, setInvestments] = useState([]);
    const [summary, setSummary] = useState(null);
    const [allocation, setAllocation] = useState({});
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [showForm, setShowForm] = useState(false);
    const [editing, setEditing] = useState(null);
    const [formData, setFormData] = useState({
        investment_type: "", investment_name: "", amount_invested: "", current_value: "", start_date: "", maturity_date: "", status: "Active"
    });

    const loadData = useCallback(async () => {
        setLoading(true);
        try {
            const [list, sum, alloc] = await Promise.all([
                API.get("/api/investments"),
                API.get("/api/investments/summary"),
                API.get("/api/investment-allocation")
            ]);
            setInvestments(list.data?.data || []);
            setSummary(sum.data?.data || null);
            setAllocation(alloc.data?.data || {});
        } catch (e) { console.error(e); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { loadData(); }, [loadData]);

    const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

    const handleSubmit = async () => {
        try {
            const payload = prepareFormPayload(formData, {
                numbers: ["amount_invested", "current_value"],
                dates: ["start_date", "maturity_date"],
            });
            if (editing) await API.put(`/api/investments/${editing.id}`, payload);
            else await API.post("/api/investments", payload);
            setShowForm(false); setEditing(null);
            setFormData({ investment_type: "", investment_name: "", amount_invested: "", current_value: "", start_date: "", maturity_date: "", status: "Active" });
            loadData();
        } catch (e) { alert(getApiErrorMessage(e)); }
    };

    const handleEdit = (row) => {
        setEditing(row);
        setFormData({ investment_type: row.investment_type, investment_name: row.investment_name, amount_invested: row.amount_invested, current_value: row.current_value, start_date: row.start_date || "", maturity_date: row.maturity_date || "", status: row.status });
        setShowForm(true);
    };

    const handleDelete = async (row) => {
        if (!confirm("Delete this investment?")) return;
        try { await API.delete(`/api/investments/${row.id}`); loadData(); }
        catch (e) { alert(e.response?.data?.error || "Failed to delete"); }
    };

    const filtered = investments.filter(i =>
        i.investment_name?.toLowerCase().includes(search.toLowerCase()) ||
        i.investment_type?.toLowerCase().includes(search.toLowerCase())
    );

    const pieData = {
        labels: Object.keys(allocation),
        datasets: [{ data: Object.values(allocation), backgroundColor: COLORS, borderWidth: 2, borderColor: "var(--bg-card)" }]
    };

    const chartColors = getChartColors();
    const pieOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: "right",
                labels: { color: chartColors.text, padding: 16, font: { size: 12 } }
            }
        }
    };

    const columns = [
        { field: "investment_name", header: "Name", sortable: true },
        { field: "investment_type", header: "Type", sortable: true },
        { field: "amount_invested", header: "Invested", format: "currency", sortable: true },
        { field: "current_value", header: "Current", format: "currency", sortable: true },
        { field: "profit_loss", header: "P&L", format: "currency", sortable: true, render: (v) => <span style={{ color: v >= 0 ? "var(--success)" : "var(--danger)", fontWeight: 600 }}>{formatCurrency(v)}</span> },
        { field: "roi", header: "ROI", format: "percentage", sortable: true, render: (v) => <span style={{ color: v >= 0 ? "var(--success)" : "var(--danger)", fontWeight: 600 }}>{formatPercentage(v)}</span> },
        { field: "status", header: "Status", sortable: true, render: (v) => <span className={`badge ${v === "Active" ? "badge-success" : "badge-info"}`}>{v}</span> }
    ];

    return (
        <div>
            <div className="page-header">
                <div><h1>Investments</h1><p>Portfolio analytics and performance tracking</p></div>
                <button className="btn btn-primary" onClick={() => { setEditing(null); setShowForm(true); }}><Plus size={18} /> Add Investment</button>
            </div>

            {summary && (
                <div className="grid-kpi" style={{ marginBottom: 24 }}>
                    <div className="kpi-card"><div className="kpi-label">Total Invested</div><div className="kpi-value">{formatCurrency(summary.total_invested)}</div></div>
                    <div className="kpi-card"><div className="kpi-label">Current Value</div><div className="kpi-value">{formatCurrency(summary.current_value)}</div></div>
                    <div className="kpi-card">
                        <div className="kpi-label">Profit / Loss</div>
                        <div className="kpi-value" style={{ color: summary.profit >= 0 ? "var(--success)" : "var(--danger)" }}>{formatCurrency(summary.profit)}</div>
                    </div>
                    <div className="kpi-card">
                        <div className="kpi-label">ROI</div>
                        <div className="kpi-value" style={{ color: summary.roi >= 0 ? "var(--success)" : "var(--danger)" }}>{formatPercentage(summary.roi)}</div>
                    </div>
                </div>
            )}

            <div className="grid-2" style={{ marginBottom: 24 }}>
                <div className="card" style={{ padding: 24 }}>
                    <div className="section-title"><PieChart size={18} /> Allocation</div>
                    <div className="chart-container" style={{ height: 280 }}>
                        <Pie data={pieData} options={pieOptions} />
                    </div>
                </div>
                <div className="card" style={{ padding: 24 }}>
                    <div className="section-title"><DollarSign size={18} /> Allocation Breakdown</div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 8 }}>
                        {Object.entries(allocation).sort((a, b) => b[1] - a[1]).map(([type, val], i) => (
                            <div key={type} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                                <div style={{ width: 12, height: 12, borderRadius: 3, background: COLORS[i % COLORS.length], flexShrink: 0 }} />
                                <div style={{ flex: 1 }}>
                                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.875rem", fontWeight: 600 }}>
                                        <span>{type}</span><span>{formatCurrency(val)}</span>
                                    </div>
                                    <div className="progress-bar-track" style={{ height: 6, marginTop: 4 }}>
                                        <div className="progress-bar-fill" style={{ width: `${summary?.total_invested > 0 ? (val / summary.total_invested) * 100 : 0}%`, background: COLORS[i % COLORS.length] }} />
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="search-bar" style={{ marginBottom: 20, maxWidth: 400 }}>
                <Search size={18} style={{ color: "var(--text-muted)", flexShrink: 0 }} />
                <input type="text" placeholder="Search investments..." value={search} onChange={(e) => setSearch(e.target.value)} />
                {search && <button className="btn btn-ghost btn-sm" onClick={() => setSearch("")}><X size={16} /></button>}
            </div>

            {loading ? <SkeletonTable rows={5} cols={6} /> : (
                <DataTable columns={columns} data={filtered} onEdit={handleEdit} onDelete={handleDelete} />
            )}

            {filtered.length === 0 && !loading && (
                <EmptyState icon={TrendingUp} title="No investments found" description={search ? "Try a different search" : "Start tracking your portfolio"} actionText={!search ? "Add Investment" : null} onAction={() => setShowForm(true)} />
            )}

            {showForm && (
                <div className="modal-overlay" onClick={() => setShowForm(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header"><h3>{editing ? "Edit Investment" : "Add Investment"}</h3><button className="btn btn-ghost btn-sm" onClick={() => setShowForm(false)}><X size={18} /></button></div>
                        <div className="modal-body">
                            <div className="form-row" style={{ gridTemplateColumns: "1fr" }}>
                                <div className="form-group"><label className="form-label">Type</label><input type="text" name="investment_type" value={formData.investment_type} onChange={handleChange} placeholder="e.g., Stocks, Mutual Funds, FD" /></div>
                                <div className="form-group"><label className="form-label">Name</label><input type="text" name="investment_name" value={formData.investment_name} onChange={handleChange} placeholder="Investment name" /></div>
                                <div className="form-group"><label className="form-label">Amount Invested</label><input type="number" name="amount_invested" value={formData.amount_invested} onChange={handleChange} /></div>
                                <div className="form-group"><label className="form-label">Current Value</label><input type="number" name="current_value" value={formData.current_value} onChange={handleChange} /></div>
                                <div className="form-group"><label className="form-label">Start Date</label><input type="date" name="start_date" value={formData.start_date} onChange={handleChange} /></div>
                                <div className="form-group"><label className="form-label">Maturity Date</label><input type="date" name="maturity_date" value={formData.maturity_date} onChange={handleChange} /></div>
                            </div>
                        </div>
                        <div className="modal-footer"><button className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button><button className="btn btn-primary" onClick={handleSubmit}>{editing ? "Update" : "Add"}</button></div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Investments;
