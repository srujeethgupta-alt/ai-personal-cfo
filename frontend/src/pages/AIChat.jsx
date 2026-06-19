import { useState, useRef, useEffect } from "react";
import API from "../services/api";
import { Send, User, Bot, Sparkles, Trash2 } from "lucide-react";
import ReactMarkdown from "react-markdown";

function AIChat() {
    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState(() => {
        const saved = localStorage.getItem("ai-cfo-chat");
        return saved ? JSON.parse(saved) : [
            { sender: "ai", text: "Hello! I'm your AI Personal CFO. Ask me anything about your finances — from budgeting tips to investment strategies, I'm here to help." }
        ];
    });
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    useEffect(() => {
        localStorage.setItem("ai-cfo-chat", JSON.stringify(messages));
    }, [messages]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, loading]);

    const askCFO = async () => {
        if (!question.trim()) return;
        const userMsg = { sender: "user", text: question };
        setMessages(prev => [...prev, userMsg]);
        setLoading(true);
        setQuestion("");

        try {
            const response = await API.post("/api/ai/ask-cfo", {
                question: userMsg.text,
                history: messages
            });
            const data = response.data?.data;
            
            // Check if a tool was executed
            if (data?.tool_executed) {
                const toolMsg = { 
                    sender: "ai", 
                    text: `✓ Action completed: ${data.tool_executed}\n\n${data.answer || ""}`,
                    isTool: true 
                };
                setMessages(prev => [...prev, toolMsg]);
            } else {
                const aiMsg = { sender: "ai", text: data?.answer || "No response" };
                setMessages(prev => [...prev, aiMsg]);
            }
        } catch (e) {
            console.error(e);
            setMessages(prev => [...prev, { sender: "ai", text: "I'm having trouble connecting right now. Please try again in a moment." }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            askCFO();
        }
    };

    const clearChat = () => {
        if (!confirm("Clear all conversation history?")) return;
        const welcome = { sender: "ai", text: "Hello! I'm your AI Personal CFO. Ask me anything about your finances." };
        setMessages([welcome]);
        localStorage.setItem("ai-cfo-chat", JSON.stringify([welcome]));
    };

    return (
        <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 48px)" }}>
            <div className="page-header" style={{ marginBottom: 16, flexShrink: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <div style={{ width: 40, height: 40, borderRadius: 12, background: "linear-gradient(135deg, var(--primary-500), var(--accent-400))", display: "flex", alignItems: "center", justifyContent: "center", color: "white" }}>
                        <Sparkles size={20} />
                    </div>
                    <div>
                        <h1 style={{ margin: 0 }}>AI Personal CFO</h1>
                        <p style={{ margin: 0, fontSize: "0.875rem" }}>Your conversational financial copilot</p>
                    </div>
                </div>
                <button className="btn btn-ghost" onClick={clearChat} title="Clear chat">
                    <Trash2 size={16} /> Clear
                </button>
            </div>

            <div className="chat-container">
                <div className="chat-messages">
                    {messages.map((msg, i) => (
                        <div
                            key={i}
                            style={{
                                display: "flex",
                                justifyContent: msg.sender === "user" ? "flex-end" : "flex-start",
                                gap: 10,
                                alignItems: "flex-start"
                            }}
                        >
                            {msg.sender === "ai" && (
                                <div style={{ width: 32, height: 32, borderRadius: 10, background: "linear-gradient(135deg, var(--primary-500), var(--accent-400))", display: "flex", alignItems: "center", justifyContent: "center", color: "white", flexShrink: 0, marginTop: 4 }}>
                                    <Bot size={18} />
                                </div>
                            )}
                            <div className={`chat-message ${msg.sender}`}>
                                {msg.sender === "ai" ? (
                                    <ReactMarkdown
                                        components={{
                                            p: ({ children }) => <p style={{ margin: "0 0 8px 0" }}>{children}</p>,
                                            ul: ({ children }) => <ul style={{ margin: "0 0 8px 0", paddingLeft: 20 }}>{children}</ul>,
                                            li: ({ children }) => <li style={{ marginBottom: 4 }}>{children}</li>,
                                            strong: ({ children }) => <strong style={{ color: "var(--text-primary)" }}>{children}</strong>,
                                        }}
                                    >
                                        {msg.text}
                                    </ReactMarkdown>
                                ) : (
                                    msg.text
                                )}
                            </div>
                            {msg.sender === "user" && (
                                <div style={{ width: 32, height: 32, borderRadius: 10, background: "var(--bg-hover)", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-primary)", flexShrink: 0, marginTop: 4, border: "1px solid var(--border-color)" }}>
                                    <User size={18} />
                                </div>
                            )}
                        </div>
                    ))}
                    {loading && (
                        <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
                            <div style={{ width: 32, height: 32, borderRadius: 10, background: "linear-gradient(135deg, var(--primary-500), var(--accent-400))", display: "flex", alignItems: "center", justifyContent: "center", color: "white", flexShrink: 0 }}>
                                <Bot size={18} />
                            </div>
                            <div className="typing-indicator">
                                <div className="typing-dot" /><div className="typing-dot" /><div className="typing-dot" />
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
                <div className="chat-input-bar">
                    <input
                        ref={inputRef}
                        type="text"
                        placeholder="Ask your AI Personal CFO..."
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        onKeyDown={handleKeyPress}
                        style={{ flex: 1 }}
                        disabled={loading}
                    />
                    <button className="btn btn-primary" onClick={askCFO} disabled={loading || !question.trim()}>
                        <Send size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
}

export default AIChat;
