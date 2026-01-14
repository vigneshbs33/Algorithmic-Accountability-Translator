import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
    LayoutDashboard,
    Users,
    BarChart3,
    FileText,
    Settings,
    Bell
} from 'lucide-react'
import './Layout.css'

interface LayoutProps {
    children: ReactNode
}

const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/personas', label: 'Personas', icon: Users },
    { path: '/analysis', label: 'Analysis', icon: BarChart3 },
    { path: '/contracts', label: 'Contracts', icon: FileText },
]

export default function Layout({ children }: LayoutProps) {
    const location = useLocation()

    return (
        <div className="layout">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-header">
                    <div className="logo">
                        <div className="logo-icon">AAT</div>
                        <span className="logo-text">Algorithmic Accountability</span>
                    </div>
                </div>

                <nav className="sidebar-nav">
                    {navItems.map(({ path, label, icon: Icon }) => (
                        <Link
                            key={path}
                            to={path}
                            className={`nav-item ${location.pathname === path ? 'active' : ''}`}
                        >
                            <Icon size={20} />
                            <span>{label}</span>
                        </Link>
                    ))}
                </nav>

                <div className="sidebar-footer">
                    <Link to="/settings" className="nav-item">
                        <Settings size={20} />
                        <span>Settings</span>
                    </Link>
                </div>
            </aside>

            {/* Main content */}
            <div className="main-wrapper">
                {/* Top bar */}
                <header className="topbar">
                    <div className="topbar-left">
                        <h2 className="page-title">
                            {navItems.find(item => item.path === location.pathname)?.label || 'Dashboard'}
                        </h2>
                    </div>
                    <div className="topbar-right">
                        <button className="icon-btn">
                            <Bell size={20} />
                        </button>
                        <div className="user-menu">
                            <div className="user-avatar">U</div>
                        </div>
                    </div>
                </header>

                {/* Page content */}
                <main className="main-content">
                    <div className="container">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    )
}
