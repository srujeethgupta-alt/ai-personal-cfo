// Utility for formatting numbers, dates, and currencies

const CURRENCY_MAP = {
  INR: { symbol: '₹', locale: 'en-IN' },
  USD: { symbol: '$', locale: 'en-US' },
  EUR: { symbol: '€', locale: 'en-DE' },
  GBP: { symbol: '£', locale: 'en-GB' },
  JPY: { symbol: '¥', locale: 'ja-JP' }
};

export function formatCurrency(amount, currency = 'INR') {
  if (amount === null || amount === undefined || isNaN(amount)) return '₹0';
  const config = CURRENCY_MAP[currency] || CURRENCY_MAP.INR;
  try {
    return new Intl.NumberFormat(config.locale, {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(amount);
  } catch {
    return `${config.symbol}${Number(amount).toLocaleString()}`;
  }
}

export function formatNumber(num, decimals = 0) {
  if (num === null || num === undefined || isNaN(num)) return '0';
  return new Intl.NumberFormat('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(num);
}

export function formatPercentage(value, decimals = 2) {
  if (value === null || value === undefined || isNaN(value)) return '0%';
  return `${Number(value).toFixed(decimals)}%`;
}

export function formatDate(dateStr) {
  if (!dateStr) return '-';
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;
    return new Intl.DateTimeFormat('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    }).format(date);
  } catch {
    return dateStr;
  }
}

export function formatShortDate(dateStr) {
  if (!dateStr) return '-';
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;
    return new Intl.DateTimeFormat('en-IN', {
      day: 'numeric',
      month: 'short'
    }).format(date);
  } catch {
    return dateStr;
  }
}

export function formatMonthYear(month, year) {
  try {
    return new Intl.DateTimeFormat('en-IN', { month: 'long', year: 'numeric' }).format(
      new Date(year, month - 1, 1)
    );
  } catch {
    return `${month}/${year}`;
  }
}

export function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

export function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}

export function getChartColors() {
  try {
    const style = getComputedStyle(document.documentElement);
    return {
      text: style.getPropertyValue('--text-secondary').trim() || '#64748b',
      grid: style.getPropertyValue('--border-light').trim() || '#e2e8f0',
      primary: style.getPropertyValue('--primary-500').trim() || '#6366f1'
    };
  } catch {
    return { text: '#64748b', grid: '#e2e8f0', primary: '#6366f1' };
  }
}
