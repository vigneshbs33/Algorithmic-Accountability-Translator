import { useQuery } from '@tanstack/react-query'
import {
    Users,
    FileText,
    AlertTriangle,
    TrendingUp,
    ArrowUpRight,
    ArrowDownRight,
    Sparkles,
    Play,
    CheckCircle,
    Clock,
    Zap
} from 'lucide-react'
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Legend,
    AreaChart,
    Area
} from 'recharts'
import { api } from '../../services/api'
import './Dashboard.css'

const COLORS = ['#8b5cf6', '#6366f1', '#3b82f6', '#10b981', '#f59e0b']

export default function Dashboard() {
    // Stats data
    const stats = [
        {
            label: 'Personas Analyzed',
            value: '10',
            change: '+2 this week',
            changeType: 'positive',
            icon: Users,
            iconColor: 'purple',
            description: 'Unique user profiles tested'
        },
        {
            label: 'Content Collected',
            value: '10,234',
            change: '+1,234 today',
            changeType: 'positive',
            icon: FileText,
            iconColor: 'blue',
            description: 'Posts and videos analyzed'
        },
        {
            label: 'Filter Bubbles Found',
            value: '8/10',
            change: '80% detection rate',
            changeType: 'warning',
            icon: AlertTriangle,
            iconColor: 'orange',
            description: 'Personas trapped in bubbles'
        },
        {
            label: 'Avg Diversity Score',
            value: '0.34',
            change: 'Below healthy (0.6)',
            changeType: 'negative',
            icon: TrendingUp,
            iconColor: 'green',
            description: 'Higher is more diverse'
        }
    ]

    const diversityData = [
        { name: 'Progressive', diversity: 0.28, ecoChamber: 0.82 },
        { name: 'Conservative', diversity: 0.31, ecoChamber: 0.79 },
        { name: 'Tech', diversity: 0.45, ecoChamber: 0.55 },
        { name: 'Health', diversity: 0.52, ecoChamber: 0.48 },
        { name: 'Moderate', diversity: 0.67, ecoChamber: 0.33 },
    ]

    const biasDistribution = [
        { name: 'Left-leaning', value: 35 },
        { name: 'Center', value: 20 },
        { name: 'Right-leaning', value: 30 },
        { name: 'Neutral', value: 15 },
    ]

    const timelineData = [
        { day: 'Day 1', score: 0.65 },
        { day: 'Day 2', score: 0.58 },
        { day: 'Day 3', score: 0.48 },
        { day: 'Day 4', score: 0.42 },
        { day: 'Day 5', score: 0.35 },
        { day: 'Day 6', score: 0.31 },
        { day: 'Day 7', score: 0.28 },
    ]

    const recentActivity = [
        {
            type: 'analysis',
            title: 'Bias analysis completed',
            persona: 'Progressive Activist',
            time: '2 minutes ago',
            status: 'success'
        },
        {
            type: 'scrape',
            title: 'Reddit data collection',
            persona: 'Conservative Traditional',
            time: '15 minutes ago',
            status: 'success'
        },
        {
            type: 'contract',
            title: 'Contract generated',
            persona: 'All Personas',
            time: '1 hour ago',
            status: 'success'
        },
        {
            type: 'analysis',
            title: 'Echo chamber detection',
            persona: 'Tech Enthusiast',
            time: '2 hours ago',
            status: 'running'
        },
    ]

    const keyFindings = [
        {
            severity: 'high',
            title: 'Strong Filter Bubble Effect',
            description: '78% of content matches user\'s existing ideological stance across all personas.'
        },
        {
            severity: 'high',
            title: 'Low Topic Diversity',
            description: 'Average diversity score of 0.34/1.0 indicates severely limited content variety.'
        },
        {
            severity: 'medium',
            title: 'Engagement Over Accuracy',
            description: 'Sensational content ranks 2.3x higher than neutral, factual content.'
        },
        {
            severity: 'medium',
            title: 'Rapid Bubble Formation',
            description: 'Filter bubbles fully form within 7 days of consistent usage patterns.'
        }
    ]

    return (
        <div className="dashboard">
            {/* Welcome Banner */}
            <div className="welcome-banner">
                <div className="welcome-content">
                    <h1>Welcome to AlgoTranslator</h1>
                    <p>Analyze how recommendation algorithms shape your information diet</p>
                </div>
                <div className="welcome-actions">
                    <button className="btn btn-primary">
                        <Play size={16} />
                        Start New Analysis
                    </button>
                    <button className="btn btn-secondary">
                        <Sparkles size={16} />
                        Generate Report
                    </button>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="dashboard-grid">
                {stats.map((stat, index) => (
                    <div key={index} className="stat-card animate-fade-in" style={{ animationDelay: `${index * 0.1}s` }}>
                        <div className="stat-card-header">
                            <div className={`icon ${stat.iconColor}`}>
                                <stat.icon size={24} />
                            </div>
                            <div className={`stat-trend ${stat.changeType}`}>
                                {stat.changeType === 'positive' && <ArrowUpRight size={14} />}
                                {stat.changeType === 'negative' && <ArrowDownRight size={14} />}
                                {stat.changeType === 'warning' && <AlertTriangle size={14} />}
                            </div>
                        </div>
                        <div className="metric">
                            <span className="metric-value">{stat.value}</span>
                            <span className="metric-label">{stat.label}</span>
                            <span className={`metric-change ${stat.changeType}`}>{stat.change}</span>
                        </div>
                        <p className="stat-description">{stat.description}</p>
                    </div>
                ))}
            </div>

            {/* Filter Bubble Timeline */}
            <div className="card timeline-card">
                <div className="card-header">
                    <div>
                        <h3 className="card-title">Filter Bubble Formation</h3>
                        <p className="card-subtitle">How quickly users get trapped in echo chambers</p>
                    </div>
                    <span className="badge badge-danger">Critical Insight</span>
                </div>
                <div className="viz-container" style={{ height: '200px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={timelineData}>
                            <defs>
                                <linearGradient id="diversityGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis dataKey="day" stroke="#6b6b80" fontSize={12} />
                            <YAxis stroke="#6b6b80" domain={[0, 1]} fontSize={12} />
                            <Tooltip
                                contentStyle={{
                                    background: '#1e1e32',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px'
                                }}
                            />
                            <Area
                                type="monotone"
                                dataKey="score"
                                stroke="#8b5cf6"
                                fillOpacity={1}
                                fill="url(#diversityGradient)"
                                strokeWidth={2}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
                <div className="timeline-insight">
                    <Zap size={16} />
                    <span>Diversity drops <strong>57%</strong> within the first week of usage</span>
                </div>
            </div>

            {/* Charts Section */}
            <div className="charts-section">
                {/* Diversity Bar Chart */}
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Diversity by Persona</h3>
                    </div>
                    <div className="viz-container">
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={diversityData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                <XAxis dataKey="name" stroke="#6b6b80" fontSize={12} />
                                <YAxis stroke="#6b6b80" domain={[0, 1]} fontSize={12} />
                                <Tooltip
                                    contentStyle={{
                                        background: '#1e1e32',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Legend />
                                <Bar dataKey="diversity" name="Diversity" fill="#10b981" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="ecoChamber" name="Echo Chamber" fill="#ef4444" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Bias Distribution */}
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Political Bias Distribution</h3>
                    </div>
                    <div className="viz-container">
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={biasDistribution}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={90}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {biasDistribution.map((_, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{
                                        background: '#1e1e32',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Bottom Section */}
            <div className="bottom-section">
                {/* Key Findings */}
                <div className="card findings-card">
                    <div className="card-header">
                        <h3 className="card-title">🔍 Key Findings</h3>
                        <span className="badge badge-warning">Requires Attention</span>
                    </div>
                    <div className="findings-list">
                        {keyFindings.map((finding, index) => (
                            <div key={index} className={`finding-item severity-${finding.severity}`}>
                                <div className="finding-indicator"></div>
                                <div className="finding-content">
                                    <h4>{finding.title}</h4>
                                    <p>{finding.description}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Recent Activity */}
                <div className="card activity-card">
                    <div className="card-header">
                        <h3 className="card-title">Recent Activity</h3>
                        <button className="btn-link">View All</button>
                    </div>
                    <div className="activity-list">
                        {recentActivity.map((activity, index) => (
                            <div key={index} className="activity-item">
                                <div className={`activity-icon ${activity.status}`}>
                                    {activity.status === 'success' && <CheckCircle size={16} />}
                                    {activity.status === 'running' && <Clock size={16} />}
                                </div>
                                <div className="activity-content">
                                    <span className="activity-title">{activity.title}</span>
                                    <span className="activity-persona">{activity.persona}</span>
                                </div>
                                <span className="activity-time">{activity.time}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}
