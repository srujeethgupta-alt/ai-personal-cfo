import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import NotificationBell from './NotificationBell';
import { useState } from 'react';

function Layout() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="app-layout">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
      <main className={`main-content ${collapsed ? 'sidebar-collapsed' : ''}`}>
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
          <NotificationBell />
        </div>
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;
