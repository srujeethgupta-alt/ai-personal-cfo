import { Inbox, Plus, Search } from 'lucide-react';

function EmptyState({ icon: Icon, title, description, actionText, onAction, variant = 'default' }) {
  const iconMap = {
    default: Icon || Inbox,
    search: Search,
    add: Plus
  };
  const SelectedIcon = iconMap[variant] || iconMap.default;

  return (
    <div className="empty-state">
      <div className="empty-state-icon">
        <SelectedIcon size={28} strokeWidth={1.5} />
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
      {actionText && onAction && (
        <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={onAction}>
          <Plus size={16} />
          {actionText}
        </button>
      )}
    </div>
  );
}

export default EmptyState;
