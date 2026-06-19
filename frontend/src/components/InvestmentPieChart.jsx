import {
    Chart as ChartJS,
    ArcElement,
    Tooltip,
    Legend
} from "chart.js";

import { Pie } from "react-chartjs-2";

ChartJS.register(
    ArcElement,
    Tooltip,
    Legend
);

function InvestmentPieChart({ investments }) {

    const groupedData = {};

    investments.forEach((inv) => {

        const type = inv.investment_type;

        if (!groupedData[type]) {
            groupedData[type] = 0;
        }

        groupedData[type] += Number(
            inv.amount_invested
        );
    });

    const COLORS = [
        "#10b981", // Green
        "#f59e0b", // Orange
        "#ef4444", // Red
        "#8b5cf6", // Purple
        "#06b6d4", // Cyan
        "#ec4899", // Pink
        "#3b82f6", // Indigo
        "#22c55e", // Emerald
        "#eab308"  // Amber
    ];

    const data = {
        labels: Object.keys(groupedData),
        datasets: [
            {
                label: "Investments",
                data: Object.values(groupedData),
                backgroundColor: COLORS,
                borderColor: "#ffffff",
                borderWidth: 2
            }
        ]
    };

    return (
        <div
            style={{
                background: "white",
                padding: "20px",
                borderRadius: "12px",
                marginBottom: "30px",
                boxShadow:
                    "0 2px 8px rgba(0,0,0,0.1)"
            }}
        >
            <h2
                style={{
                    color: "#111827",
                    marginBottom: "20px"
                }}
            >
                📊 Investment Distribution
            </h2>

            <div
                style={{
                    width: "400px",
                    height: "550px",
                    margin: "auto"
                }}
            >
                <Pie data={data} />
            </div>
        </div>
    );
}

export default InvestmentPieChart;