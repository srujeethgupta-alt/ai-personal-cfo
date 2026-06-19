import { useState, useEffect, useCallback } from "react";
import API from "../services/api";
import DataTable from "../components/DataTable";
import EmptyState from "../components/EmptyState";
import { SkeletonTable } from "../components/Skeleton";
import { Plus, Search, Filter, X, PieChart, TrendingDown, Receipt } from "lucide-react";
import { formatCurrency, formatDate, getChartColors } from "../utils/formatters";
import { prepareFormPayload, getApiErrorMessage } from "../utils/formPayload";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { Pie } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend);
const COLORS = ["#6366f1", "#14b8a6", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4", "#22c55e"];

function Expenses() {
    const [expenses, setExpenses] = useState([]);
    const [summary, setSummary] = useState(null);
    const [chartData, setChartData] = useState({});
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [showForm, setShowForm] = useState(false);
    const [editing, setEditing] = useState(null);
    const [formData, setFormData] = useState({
        category: "", amount: "", expense_date: "", notes: ""
    });

    const loadData = useCallback(async (signal) => {
        if (!localStorage.getItem("access_token")) return;
        setLoading(true);
        try {
            const [list, sum, chart] = await Promise.all([
                API.get("/api/expenses", { signal }),
                API.get("/api/expenses/summary", { signal }),
                API.get("/api/expense-chart", { signal })
            ]);
            setExpenses(list.data?.data || []);
            setSummary(sum.data?.data || null);
            setChartData(chart.data?.data || {});
        } catch (e) {
            if (e.name === "CanceledError" || e.code === "ERR_CANCELED") return;
            console.error(e);
        } finally {
            if (!signal?.aborted) {
                setLoading(false);
            }
        }
    }, []);

    useEffect(() => {
        const controller = new AbortController();
        loadData(controller.signal);
        return () => controller.abort();
    }, [loadData]);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async () => {
        try {
            const payload = prepareFormPayload(formData, {
                numbers: ["amount"],
            });
            if (editing) {
                await API.put(`/api/expenses/${editing.id}`, payload);
            } else {
                await API.post("/api/expenses", payload);
            }
            setShowForm(false);
            setEditing(null);
            setFormData({ category: "", amount: "", expense_date: "", notes: "" });
            loadData();
        } catch (e) {
            alert(getApiErrorMessage(e, "Failed to save expense"));
        }
    };

    const handleEdit = (row) => {
        setEditing(row);
        setFormData({
            category: row.category,
            amount: row.amount,
            expense_date: row.expense_date,
            notes: row.notes || ""
        });
        setShowForm(true);
    };

    const handleDelete = async (row) => {
        if (!confirm("Are you sure you want to delete this expense?")) return;
        try {
            await API.delete(`/api/expenses/${row.id}`);
            loadData();
        } catch (e) {
            alert(e.response?.data?.error || "Failed to delete");
        }
    };

    const filtered = expenses.filter(e =>
        e.category?.toLowerCase().includes(search.toLowerCase()) ||
        e.notes?.toLowerCase().includes(search.toLowerCase())
    );

    const pieData = {
        labels: Object.keys(chartData),
        datasets: [{
            data: Object.values(chartData),
            backgroundColor: COLORS,
            borderWidth: 2,
            borderColor: "var(--bg-card)"
        }]
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
        { field: "category", header: "Category", sortable: true },
        { field: "amount", header: "Amount", format: "currency", sortable: true },
        { field: "expense_date", header: "Date", format: "date", sortable: true },
        { field: "notes", header: "Notes", sortable: false }
    ];

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1>Expenses</h1>
                    <p>Track, analyze, and optimize your spending</p>
                </div>
                <button className="btn btn-primary" onClick={() => { setEditing(null); setShowForm(true); }}>
                    <Plus size={18} /> Add Expense
                </button>
            </div>

            {/* Summary Cards */}
            {summary && (
                <div className="grid-kpi" style={{ marginBottom: 24 }}>
                    <div className="kpi-card">
                        <div className="kpi-label">Total Expenses</div>
                        <div className="kpi-value">{formatCurrency(summary.total_expenses)}</div>
                    </div>
                    <div className="kpi-card">
                        <div className="kpi-label">Categories</div>
                        <div className="kpi-value">{Object.keys(summary.category_breakdown || {}).length}</div>
                    </div>
                    <div className="kpi-card">
                        <div className="kpi-label">Top Category</div>
                        <div className="kpi-value" style={{ fontSize: "1.25rem" }}>
                            {Object.entries(summary.category_breakdown || {}).sort((a, b) => b[1] - a[1])[0]?.[0] || "N/A"}
                        </div>
                    </div>
                </div>
            )}

            {/* Search + Chart */}
            <div className="grid-2" style={{ marginBottom: 24 }}>
                <div className="card" style={{ padding: 24 }}>
                    <div className="section-title"><PieChart size={18} /> Spending by Category</div>
                    <div className="chart-container" style={{ height: 280 }}>
                        <Pie data={pieData} options={pieOptions} />
                    </div>
                </div>
                <div className="card" style={{ padding: 24 }}>
                    <div className="section-title"><TrendingDown size={18} /> Category Breakdown</div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 8 }}>
                        {Object.entries(summary?.category_breakdown || {}).sort((a, b) => b[1] - a[1]).map(([cat, amt], i) => (
                            <div key={cat} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                                <div style={{ width: 12, height: 12, borderRadius: 3, background: COLORS[i % COLORS.length], flexShrink: 0 }} />
                                <div style={{ flex: 1 }}>
                                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.875rem", fontWeight: 600 }}>
                                        <span>{cat}</span>
                                        <span>{formatCurrency(amt)}</span>
                                    </div>
                                    <div className="progress-bar-track" style={{ height: 6, marginTop: 4 }}>
                                        <div className="progress-bar-fill" style={{ width: `${summary.total_expenses > 0 ? (amt / summary.total_expenses) * 100 : 0}%`, background: COLORS[i % COLORS.length] }} />
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Search */}
            <div className="search-bar" style={{ marginBottom: 20, maxWidth: 400 }}>
                <Search size={18} style={{ color: "var(--text-muted)", flexShrink: 0 }} />
                <input
                    type="text"
                    placeholder="Search expenses..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
                {search && <button className="btn btn-ghost btn-sm" onClick={() => setSearch("")}><X size={16} /></button>}
            </div>

            {/* Table */}
            {loading ? <SkeletonTable rows={5} cols={4} /> : (
                <DataTable
                    columns={columns}
                    data={filtered}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                />
            )}

            {filtered.length === 0 && !loading && (
                <EmptyState
                    icon={Receipt}
                    title="No expenses found"
                    description={search ? "Try a different search term" : "Start by adding your first expense"}
                    actionText={!search ? "Add Expense" : null}
                    onAction={() => setShowForm(true)}
                />
            )}

            {/* Modal Form */}
            {showForm && (
                <div className="modal-overlay" onClick={() => setShowForm(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>{editing ? "Edit Expense" : "Add Expense"}</h3>
                            <button className="btn btn-ghost btn-sm" onClick={() => setShowForm(false)}><X size={18} /></button>
                        </div>
                        <div className="modal-body">
                            <div className="form-row" style={{ gridTemplateColumns: "1fr" }}>
                                <div className="form-group">
                                    <label className="form-label">Category</label>
                                    <input type="text" name="category" value={formData.category} onChange={handleChange} placeholder="e.g., Food, Rent, Transport" />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Amount</label>
                                    <input type="number" name="amount" value={formData.amount} onChange={handleChange} placeholder="Enter amount" />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Date</label>
                                    <input type="date" name="expense_date" value={formData.expense_date} onChange={handleChange} />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Notes</label>
                                    <input type="text" name="notes" value={formData.notes} onChange={handleChange} placeholder="Optional notes" />
                                </div>
                            </div>
                        </div>
                        <div className="modal-footer">
                            <button className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
                            <button className="btn btn-primary" onClick={handleSubmit}>{editing ? "Update" : "Add Expense"}</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Expenses;
