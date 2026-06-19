function AIInsights({ insights }) {

    return (
        <div
            style={{
                background: "#ffffff",
                padding: "25px",
                marginTop: "30px",
                borderRadius: "15px",
                boxShadow: "0 4px 12px rgba(0,0,0,0.1)"
            }}
        >
            <h2
                style={{
                    color: "#111827"
                }}
            >
                🤖 AI Financial Insights
            </h2>

            {
                insights.map((item, index) => (
                    <p
                        key={index}
                        style={{
                            fontSize: "18px",
                            color: "#374151"
                        }}
                    >
                        {item}
                    </p>
                ))
            }
        </div>
    );
}

export default AIInsights;