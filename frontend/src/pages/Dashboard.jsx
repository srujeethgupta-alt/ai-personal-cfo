import { useEffect, useState } from "react";
import API from "../services/api";
import KpiCard from "../components/KpiCard";
import ProgressRing from "../components/ProgressRing";
import EmptyState from "../components/EmptyState";
import { SkeletonKpi, SkeletonChart } from "../components/Skeleton";
import {
    Wallet, TrendingUp, CreditCard, Target, PiggyBank,
    HeartPulse, BarChart3, Lightbulb, ArrowRight, Activity
} from "lucide-react";
import { formatCurrency, formatPercentage, getChartColors } from "../utils/formatters";
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement } from "chart.js";
import { Pie, Bar, Line } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement);

const COLORS = ["#6366f1", "#14b8a6", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4", "#22c55e"];

function Dashboard() {
    const [data, setData] = useState(null);
    const [chartData, setChartData] = useState({});
    const [insights, setInsights] = useState({ insights: [], severity: "good" });
    const [trends, setTrends] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const controller = new AbortController();

        const load = async () => {
            if (!localStorage.getItem("access_token")) return;
            try {
                const [dash, chart, ai, trend] = await Promise.all([
                    API.get("/api/dashboard", { signal: controller.signal }),
                    API.get("/api/expense-chart", { signal: controller.signal }),
                    API.get("/api/ai-insights", { signal: controller.signal }),
                    API.get("/api/expense-trends", { signal: controller.signal })
                ]);
                setData(dash.data?.data || dash.data);
                setChartData(chart.data?.data || chart.data);
                setInsights(ai.data?.data || ai.data);
                setTrends(trend.data?.data || trend.data);
            } catch (e) {
                if (e.name === "CanceledError" || e.code === "ERR_CANCELED") return;
                console.error(e);
            } finally {
                if (!controller.signal.aborted) {
                    setLoading(false);
                }
            }
        };
        load();

        return () => controller.abort();
    }, []);

    if (loading) {
        return (
            <div>
                <div className="page-header">
                    <h1>Executive Dashboard</h1>
                </div>
                <div className="grid-kpi">
                    <SkeletonKpi /><SkeletonKpi /><SkeletonKpi /><SkeletonKpi /><SkeletonKpi /><SkeletonKpi />
                </div>
                <div className="grid-2">
                    <SkeletonChart /><SkeletonChart />
                </div>
            </div>
        );
    }

    if (!data) {
        return (
            <EmptyState
                icon={Activity}
                title="Dashboard Unavailable"
                description="Unable to load dashboard data. Please check your connection and try again."
            />
        );
    }

    const pieData = {
        labels: Object.keys(chartData),
        datasets: [{
            data: Object.values(chartData),
            backgroundColor: COLORS,
            borderWidth: 2,
            borderColor: "var(--bg-card)"
        }]
    };

    const trendLabels = Object.keys(trends);
    const trendValues = Object.values(trends);
    const barData = {
        labels: trendLabels,
        datasets: [{
            label: "Monthly Expenses",
            data: trendValues,
            backgroundColor: "#6366f1",
            borderRadius: 6,
            barThickness: 24
        }]
    };

    const chartColors = getChartColors();
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
            y: { beginAtZero: true, grid: { color: chartColors.grid }, ticks: { color: chartColors.text } },
            x: { grid: { display: false }, ticks: { color: chartColors.text } }
        }
    };

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

    const insightColors = { good: "#10b981", warning: "#f59e0b", critical: "#ef4444" };

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1>Executive Dashboard</h1>
                    <p>Your financial command center at a glance</p>
                </div>
            </div>

            {/* KPI Grid */}
            <div className="grid-kpi">
                <KpiCard title="Net Worth" value={data.net_worth} prefix="currency" icon={Wallet} delay={0} />
                <KpiCard title="Monthly Income" value={data.salary} prefix="currency" icon={BarChart3} delay={50} />
                <KpiCard title="Total Expenses" value={data.expenses} prefix="currency" icon={Activity} delay={100} />
                <KpiCard title="Investments" value={data.investments} prefix="currency" icon={TrendingUp} delay={150} />
                <KpiCard title="Loan Burden" value={data.loans} prefix="currency" icon={CreditCard} delay={200} />
                <KpiCard title="Savings Rate" value={data.savings_rate} suffix="%" icon={PiggyBank} delay={250} />
            </div>

            {/* Health Score + Insights */}
            <div className="grid-2">
                <div className="card-glass" style={{ padding: 24, display: "flex", alignItems: "center", gap: 32 }}>
                    <ProgressRing
                        value={data.health_score}
                        size={140}
                        strokeWidth={10}
                        color={data.health_score >= 50 ? "#10b981" : data.health_score >= 25 ? "#f59e0b" : "#ef4444"}
                    />
                    <div>
                        <div className="kpi-label" style={{ marginBottom: 4 }}>Financial Health Score</div>
                        <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--text-primary)" }}>
                            {formatPercentage(data.health_score)}
                        </div>
                        <p style={{ fontSize: "0.875rem", color: "var(--text-muted)", marginTop: 4 }}>
                            {data.health_score >= 50 ? "Excellent financial health" : data.health_score >= 25 ? "Room for improvement" : "Needs attention"}
                        </p>
                    </div>
                </div>

                <div className="card-glass" style={{ padding: 24 }}>
                    <div className="section-title" style={{ marginBottom: 12 }}>
                        <Lightbulb size={18} />
                        AI Insights
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                        {insights.insights?.map((item, i) => (
                            <div key={i} className={`insight-card ${insights.severity}`} style={{ padding: 12 }}>
                                <span style={{ fontSize: "0.875rem" }}>{item}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Charts */}
            <div className="grid-2">
                <div className="card" style={{ padding: 24 }}>
                    <div className="section-title">Expense Distribution</div>
                    <div className="chart-container" style={{ height: 280 }}>
                        <Pie data={pieData} options={pieOptions} />
                    </div>
                </div>
                <div className="card" style={{ padding: 24 }}>
                    <div className="section-title">Monthly Expense Trends</div>
                    <div className="chart-container" style={{ height: 280 }}>
                        <Bar data={barData} options={chartOptions} />
                    </div>
                </div>
            </div>

            {/* Goals */}
            {data.goal_progress?.length > 0 && (
                <div className="card" style={{ padding: 24, marginBottom: 24 }}>
                    <div className="section-title">
                        <Target size={18} />
                        Goal Progress
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 20 }}>
                        {data.goal_progress.map((goal, i) => (
                            <div key={i} className="goal-card">
                                <div className="goal-card-header">
                                    <div>
                                        <div className="goal-card-title">{goal.goal}</div>
                                        <div className="goal-card-meta">
                                            {goal.months_to_goal !== null ? `~${goal.months_to_goal} months to go` : "Calculating..."}
                                        </div>
                                    </div>
                                    <ProgressRing value={goal.progress} size={56} strokeWidth={5} />
                                </div>
                                <div className="progress-bar-track">
                                    <div
                                        className={`progress-bar-fill ${goal.progress >= 80 ? 'success' : goal.progress >= 40 ? 'warning' : 'danger'}`}
                                        style={{ width: `${goal.progress}%` }}
                                    />
                                </div>
                                <div className="goal-card-stats">
                                    <span>{formatCurrency(goal.current)} of {formatCurrency(goal.target)}</span>
                                    <span style={{ fontWeight: 600, color: "var(--primary-500)" }}>{formatPercentage(goal.progress)}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default Dashboard;
