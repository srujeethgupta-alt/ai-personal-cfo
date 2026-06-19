function GlassCard({ children, className = '', style = {}, hover = true }) {
  return (
    <div
      className={`card-glass ${className}`}
      style={{
        padding: 24,
        ...style
      }}
    >
      {children}
    </div>
  );
}

export default GlassCard;
