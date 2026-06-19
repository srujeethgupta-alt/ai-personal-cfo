import { Pencil, Trash2, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { formatCurrency, formatDate, formatNumber } from '../utils/formatters';

function DataTable({
  columns,
  data,
  keyField = 'id',
  onEdit,
  onDelete,
  sortConfig,
  onSort,
  loading = false
}) {
  const handleSort = (field) => {
    if (!onSort) return;
    if (sortConfig?.field === field) {
      onSort({ field, direction: sortConfig.direction === 'asc' ? 'desc' : 'asc' });
    } else {
      onSort({ field, direction: 'asc' });
    }
  };

  const renderCell = (row, col) => {
    const value = row[col.field];
    if (col.format === 'currency') return formatCurrency(value);
    if (col.format === 'number') return formatNumber(value, col.decimals || 0);
    if (col.format === 'date') return formatDate(value);
    if (col.format === 'percentage') return formatNumber(value, 2) + '%';
    if (col.render) return col.render(value, row);
    return value ?? '-';
  };

  const renderSortIcon = (field) => {
    if (!onSort) return null;
    if (sortConfig?.field !== field) return <ArrowUpDown size={14} style={{ opacity: 0.3, marginLeft: 4 }} />;
    return sortConfig.direction === 'asc'
      ? <ArrowUp size={14} style={{ marginLeft: 4, color: 'var(--primary-500)' }} />
      : <ArrowDown size={14} style={{ marginLeft: 4, color: 'var(--primary-500)' }} />;
  };

  if (loading) {
    return (
      <div className="card">
        <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>Loading...</div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="card">
        <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
          No data available
        </div>
      </div>
    );
  }

  return (
    <div className="card" style={{ overflowX: 'auto' }}>
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th
                key={col.field}
                onClick={() => col.sortable && handleSort(col.field)}
                style={{ cursor: col.sortable ? 'pointer' : 'default', userSelect: 'none' }}
              >
                <span style={{ display: 'flex', alignItems: 'center' }}>
                  {col.header}
                  {col.sortable && renderSortIcon(col.field)}
                </span>
              </th>
            ))}
            {(onEdit || onDelete) && <th style={{ width: 100 }}>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row[keyField] ?? Math.random()}>
              {columns.map((col) => (
                <td key={col.field} data-label={col.header}>
                  {renderCell(row, col)}
                </td>
              ))}
              {(onEdit || onDelete) && (
                <td data-label="Actions">
                  <div style={{ display: 'flex', gap: 8 }}>
                    {onEdit && (
                      <button className="btn btn-ghost btn-sm" onClick={() => onEdit(row)} title="Edit">
                        <Pencil size={16} />
                      </button>
                    )}
                    {onDelete && (
                      <button className="btn btn-ghost btn-sm" onClick={() => onDelete(row)} title="Delete" style={{ color: 'var(--danger)' }}>
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DataTable;
