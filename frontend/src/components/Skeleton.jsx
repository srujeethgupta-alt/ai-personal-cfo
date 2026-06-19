function Skeleton({ width, height = 20, circle = false, style = {} }) {
  return (
    <div
      className="skeleton"
      style={{
        width: width || '100%',
        height: circle ? width || height : height,
        borderRadius: circle ? '50%' : 8,
        ...style
      }}
    />
  );
}

export function SkeletonKpi() {
  return (
    <div className="kpi-card">
      <Skeleton width={80} height={12} style={{ marginBottom: 12 }} />
      <Skeleton width={120} height={28} style={{ marginBottom: 8 }} />
      <Skeleton width={100} height={14} />
    </div>
  );
}

export function SkeletonTable({ rows = 5, cols = 4 }) {
  return (
    <div className="card">
      <div style={{ padding: 16 }}>
        <Skeleton width={200} height={20} style={{ marginBottom: 16 }} />
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} style={{ display: 'flex', gap: 16, marginBottom: 12 }}>
            {Array.from({ length: cols }).map((_, j) => (
              <Skeleton key={j} height={16} style={{ flex: 1 }} />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export function SkeletonChart() {
  return (
    <div className="card" style={{ padding: 24 }}>
      <Skeleton width={180} height={20} style={{ marginBottom: 20 }} />
      <Skeleton height={250} style={{ borderRadius: 12 }} />
    </div>
  );
}

export default Skeleton;
