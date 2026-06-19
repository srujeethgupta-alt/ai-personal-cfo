
import { Pie } from "react-chartjs-2";

import {
    Chart as ChartJS,
    ArcElement,
    Tooltip,
    Legend
} from "chart.js";

ChartJS.register(
    ArcElement,
    Tooltip,
    Legend
);

function ExpenseChart({ chartData }) {

    const data = {
        labels: Object.keys(chartData),

        datasets: [
            {
                label: "Expenses",

                data: Object.values(chartData),

                backgroundColor: [
                    "#3B82F6",
                    "#10B981",
                    "#F59E0B",
                    "#EF4444",
                    "#8B5CF6",
                    "#EC4899",
                    "#06B6D4",
                    "#14B8A6"
                ],

                borderColor: "#ffffff",

                borderWidth: 3
            }
        ]
    };

    const options = {
        responsive: true,

        maintainAspectRatio: false,

        plugins: {

            legend: {

                position: "top",

                labels: {

                    color: "#111827",

                    font: {
                        size: 18,
                        weight: "bold"
                    }
                }
            },

            tooltip: {

                titleFont: {
                    size: 18
                },

                bodyFont: {
                    size: 18
                }
            }
        }
    };

    return (
        <div
            style={{
                background: "#ffffff",

                padding: "30px",

                marginTop: "30px",

                borderRadius: "15px",

                boxShadow: "0 4px 12px rgba(0,0,0,0.1)"
            }}
        >
            <h2
                style={{
                    textAlign: "center",

                    color: "#111827",

                    marginBottom: "20px"
                }}
            >
                📊 Expense Distribution
            </h2>

            <div
                style={{
                    width: "600px",

                    height: "600px",

                    margin: "0 auto"
                }}
            >
                <Pie
                    data={data}
                    options={options}
                />
            </div>
        </div>
    );
}

export default ExpenseChart;
