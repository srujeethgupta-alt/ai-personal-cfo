import { useState, useEffect } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Receipt, TrendingUp, CreditCard,
  Target, MessageSquare, Wallet, Menu, ChevronLeft, ChevronRight, Moon, Sun, LogOut, User
} from 'lucide-react';
import { useTheme } from '../hooks/useTheme';
import { useAuth } from '../contexts/AuthContext';

const NAV_ITEMS = [
  { path: '/app', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/app/expenses', label: 'Expenses', icon: Receipt },
  { path: '/app/investments', label: 'Investments', icon: TrendingUp },
  { path: '/app/loans', label: 'Loans', icon: CreditCard },
  { path: '/app/goals', label: 'Goals', icon: Target },
  { path: '/app/budget', label: 'Budget', icon: Wallet },
  { path: '/app/chat', label: 'AI CFO', icon: MessageSquare },
];

function Sidebar({ collapsed, onToggle }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { isDark, toggleTheme } = useTheme();
  const { user, logout } = useAuth();

  useEffect(() => { setMobileOpen(false); }, [location.pathname]);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <>
      <button className="mobile-hamburger-btn" onClick={() => setMobileOpen(true)} aria-label="Open menu">
        <Menu size={20} />
      </button>

      <style>{`
        .mobile-hamburger-btn {
          position: fixed; top: 16px; left: 16px; z-index: 98; padding: 10px;
          border-radius: 10px; background: var(--bg-card); border: 1px solid var(--border-color);
          box-shadow: var(--shadow-md); color: var(--text-primary); display: none; cursor: pointer;
        }
        @media (max-width: 768px) {
          .mobile-hamburger-btn { display: flex !important; }
        }
      `}</style>

      <div className={`sidebar-overlay ${mobileOpen ? 'open' : ''}`} onClick={() => setMobileOpen(false)} />

      <aside className={`sidebar ${mobileOpen ? 'open' : ''}`} style={{ width: collapsed ? 'var(--sidebar-collapsed)' : 'var(--sidebar-width)' }}>
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
          </div>
          {!collapsed && <span>AI CFO</span>}
        </div>

        {user && !collapsed && (
          <div style={{ padding: '0 20px 12px', borderBottom: '1px solid rgba(255,255,255,0.08)', marginBottom: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'linear-gradient(135deg, var(--primary-500), var(--accent-400))', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 700, fontSize: '0.75rem' }}>
                {user.name?.charAt(0)?.toUpperCase() || 'U'}
              </div>
              <div style={{ overflow: 'hidden' }}>
                <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-sidebar-active)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{user.name}</div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--text-sidebar)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{user.email}</div>
              </div>
            </div>
          </div>
        )}

        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path || (item.path !== '/app' && location.pathname.startsWith(item.path));
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`sidebar-nav-item ${isActive ? 'active' : ''}`}
                title={collapsed ? item.label : ''}
                onClick={() => setMobileOpen(false)}
              >
                <Icon size={20} strokeWidth={isActive ? 2.5 : 2} />
                {!collapsed && <span>{item.label}</span>}
              </NavLink>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <button className="sidebar-nav-item" onClick={toggleTheme} style={{ width: '100%' }}>
            {isDark ? <Moon size={20} /> : <Sun size={20} />}
            {!collapsed && <span>{isDark ? 'Dark Mode' : 'Light Mode'}</span>}
          </button>
          <button className="sidebar-nav-item" onClick={handleLogout} style={{ width: '100%', color: 'var(--danger)' }}>
            <LogOut size={20} />
            {!collapsed && <span>Logout</span>}
          </button>
        </div>

        <button className="sidebar-toggle" onClick={onToggle} aria-label={collapsed ? 'Expand' : 'Collapse'}>
          {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
      </aside>
    </>
  );
}

export default Sidebar;
