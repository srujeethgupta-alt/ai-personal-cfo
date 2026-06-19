function GoalCard({ goal, progress }) {

    return (
        <div
            style={{
                background: "white",
                padding: "20px",
                borderRadius: "15px",
                marginTop: "20px",
                boxShadow: "0 2px 10px rgba(0,0,0,0.1)"
            }}
        >
            <h3 style={{
        color: "#111827",
        fontSize: "28px",
        fontWeight: "bold",
        textAlign: "center"
    }}>{goal}</h3>

            <progress
                value={progress}
                max="100"
                style={{
                    width: "100%"
                }}
            />

            <p style={{
        color: "#1F2937",
        fontSize: "20px",
        fontWeight: "600",
        textAlign: "center"
    }}>{progress}% Completed</p>
        </div>
    );
}

export default GoalCard;