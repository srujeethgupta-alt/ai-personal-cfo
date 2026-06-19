import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { formatCurrency, formatNumber } from '../utils/formatters';

function KpiCard({ title, value, prefix, suffix, change, changeType, icon: Icon, color, delay = 0 }) {
  const isCurrency = prefix === 'currency';
  const displayValue = isCurrency ? formatCurrency(value) : (suffix === '%' ? formatNumber(value, 2) + '%' : formatNumber(value));

  let changeIcon = <Minus size={14} />;
  let changeClass = '';
  if (change > 0) {
    changeIcon = <TrendingUp size={14} />;
    changeClass = 'positive';
  } else if (change < 0) {
    changeIcon = <TrendingDown size={14} />;
    changeClass = 'negative';
  }

  const accentColor = color || 'linear-gradient(135deg, var(--primary-500), var(--accent-400))';

  return (
    <div className="kpi-card animate-fade-in-up" style={{ animationDelay: `${delay}ms` }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
        <div className="kpi-label">{title}</div>
        {Icon && (
          <div style={{
            width: 36, height: 36, borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: accentColor, color: 'white'
          }}>
            <Icon size={18} />
          </div>
        )}
      </div>
      <div className="kpi-value">{displayValue}</div>
      {change !== undefined && (
        <div className={`kpi-change ${changeClass}`}>
          {changeIcon}
          <span>{Math.abs(change).toFixed(1)}% vs last month</span>
        </div>
      )}
    </div>
  );
}

export default KpiCard;
