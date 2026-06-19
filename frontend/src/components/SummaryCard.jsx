function SummaryCard({ title, value }) {
    return (
        <div
            style={{
                background: "white",
                padding: "20px",
                borderRadius: "15px",
                boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
                minWidth: "220px"
            }}
        >
            <h3 style={{
        color: "#374151"
    }}>{title}</h3>
            <h2 style={{
        color: "#1F2937"
    }}>{value}</h2>
        </div>
    );
}

export default SummaryCard;