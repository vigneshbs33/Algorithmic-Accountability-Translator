import { ReactNode, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
    LayoutDashboard,
    Users,
    BarChart3,
    FileText,
    Settings,
    Bell,
    Menu,
    X,
    Sparkles,
    HelpCircle,
    ExternalLink
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
    const [sidebarOpen, setSidebarOpen] = useState(false)
    const [showNotifications, setShowNotifications] = useState(false)

    // Demo mode indicator
    const isDemoMode = true // Would check if connected to real APIs

    return (
        <div className="layout">
            {/* Mobile menu toggle */}
            <button
                className="mobile-menu-toggle"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                aria-label="Toggle menu"
            >
                {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            {/* Sidebar */}
            <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    <div className="logo">
                        <div className="logo-icon">
                            <Sparkles size={20} />
                        </div>
                        <div className="logo-text-wrapper">
                            <span className="logo-text">AlgoTranslator</span>
                            <span className="logo-tagline">by Vignesh B S</span>
                        </div>
                    </div>
                </div>

                {/* Demo Mode Badge */}
                {isDemoMode && (
                    <div className="demo-badge">
                        <span className="demo-dot"></span>
                        Demo Mode
                    </div>
                )}

                <nav className="sidebar-nav">
                    <div className="nav-section-label">Main</div>
                    {navItems.map(({ path, label, icon: Icon }) => (
                        <Link
                            key={path}
                            to={path}
                            className={`nav-item ${location.pathname === path ? 'active' : ''}`}
                            onClick={() => setSidebarOpen(false)}
                        >
                            <Icon size={20} />
                            <span>{label}</span>
                        </Link>
                    ))}

                    <div className="nav-section-label" style={{ marginTop: '24px' }}>Resources</div>
                    <a href="https://vigneshbs.xyz" target="_blank" rel="noopener noreferrer" className="nav-item">
                        <ExternalLink size={20} />
                        <span>Portfolio</span>
                    </a>
                    <Link to="/help" className="nav-item">
                        <HelpCircle size={20} />
                        <span>Help & Docs</span>
                    </Link>
                </nav>

                <div className="sidebar-footer">
                    <Link to="/settings" className="nav-item">
                        <Settings size={20} />
                        <span>Settings</span>
                    </Link>

                    <div className="version-info">
                        <span>v1.0.0</span>
                        <span className="separator">•</span>
                        <a href="https://github.com/vigneshbs33/Algorithmic-Accountability-Translator" target="_blank" rel="noopener noreferrer">
                            GitHub
                        </a>
                    </div>
                </div>
            </aside>

            {/* Mobile overlay */}
            {sidebarOpen && (
                <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
            )}

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
                        {/* Quick Actions */}
                        <button className="btn btn-primary btn-sm">
                            <Sparkles size={14} />
                            Generate Report
                        </button>

                        {/* Notifications */}
                        <div className="notification-wrapper">
                            <button
                                className="icon-btn"
                                onClick={() => setShowNotifications(!showNotifications)}
                            >
                                <Bell size={20} />
                                <span className="notification-dot"></span>
                            </button>

                            {showNotifications && (
                                <div className="notification-dropdown">
                                    <div className="notification-header">
                                        <span>Notifications</span>
                                        <button className="btn-link">Mark all read</button>
                                    </div>
                                    <div className="notification-list">
                                        <div className="notification-item unread">
                                            <div className="notification-icon success">
                                                <BarChart3 size={14} />
                                            </div>
                                            <div className="notification-content">
                                                <p>Analysis complete for Progressive Activist</p>
                                                <span className="notification-time">2 min ago</span>
                                            </div>
                                        </div>
                                        <div className="notification-item">
                                            <div className="notification-icon info">
                                                <FileText size={14} />
                                            </div>
                                            <div className="notification-content">
                                                <p>New contract generated</p>
                                                <span className="notification-time">1 hour ago</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* User menu */}
                        <div className="user-menu">
                            <div className="user-avatar">V</div>
                            <span className="user-name">Demo User</span>
                        </div>
                    </div>
                </header>

                {/* Page content */}
                <main className="main-content">
                    <div className="container">
                        {children}
                    </div>
                </main>

                {/* Footer */}
                <footer className="main-footer">
                    <p>© 2026 <a href="https://vigneshbs.xyz" target="_blank" rel="noopener noreferrer">Vignesh B S</a>. AlgoTranslator - Making AI Algorithms Transparent.</p>
                </footer>
            </div>
        </div>
    )
}
