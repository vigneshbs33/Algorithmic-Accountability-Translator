import { useQuery } from '@tanstack/react-query'
import {
    Users,
    FileText,
    AlertTriangle,
    TrendingUp,
    ArrowUpRight,
    ArrowDownRight
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
    Legend
} from 'recharts'
import { api } from '../../services/api'
import './Dashboard.css'

const COLORS = ['#8b5cf6', '#6366f1', '#3b82f6', '#10b981', '#f59e0b']

export default function Dashboard() {
    // Fetch analysis summary
    const { data: summary } = useQuery({
        queryKey: ['analysis-summary'],
        queryFn: () => api.getAnalysisSummary()
    })

    // Mock data for demo
    const stats = [
        {
            label: 'Personas Analyzed',
            value: '10',
            change: '+2',
            changeType: 'positive',
            icon: Users,
            iconColor: 'purple'
        },
        {
            label: 'Content Collected',
            value: '10,234',
            change: '+1,234',
            changeType: 'positive',
            icon: FileText,
            iconColor: 'blue'
        },
        {
            label: 'Filter Bubbles Detected',
            value: '8',
            change: '80%',
            changeType: 'negative',
            icon: AlertTriangle,
            iconColor: 'orange'
        },
        {
            label: 'Avg Diversity Score',
            value: '0.34',
            change: '-12%',
            changeType: 'negative',
            icon: TrendingUp,
            iconColor: 'green'
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

    const keyFindings = summary?.key_findings || [
        '78% of content matches user\'s existing ideological stance',
        'Average topic diversity score: 0.34/1.0 (low)',
        'Filter bubbles detected in 8/10 personas',
        'Sensational content ranks 2.3x higher than neutral content'
    ]

    return (
        <div className="dashboard">
            {/* Stats Grid */}
            <div className="dashboard-grid">
                {stats.map((stat, index) => (
                    <div key={index} className="stat-card animate-fade-in" style={{ animationDelay: `${index * 0.1}s` }}>
                        <div className={`icon ${stat.iconColor}`}>
                            <stat.icon size={24} />
                        </div>
                        <div className="metric">
                            <span className="metric-value">{stat.value}</span>
                            <span className="metric-label">{stat.label}</span>
                            <span className={`metric-change ${stat.changeType}`}>
                                {stat.changeType === 'positive' ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                                {stat.change}
                            </span>
                        </div>
                    </div>
                ))}
            </div>

            {/* Charts Section */}
            <div className="charts-section">
                {/* Diversity Bar Chart */}
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Diversity Scores by Persona</h3>
                    </div>
                    <div className="viz-container">
                        <ResponsiveContainer width="100%" height={350}>
                            <BarChart data={diversityData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                <XAxis dataKey="name" stroke="#6b6b80" />
                                <YAxis stroke="#6b6b80" domain={[0, 1]} />
                                <Tooltip
                                    contentStyle={{
                                        background: '#1e1e32',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Legend />
                                <Bar dataKey="diversity" name="Diversity Score" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="ecoChamber" name="Echo Chamber Score" fill="#ef4444" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Bias Distribution Pie Chart */}
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Political Bias Distribution</h3>
                    </div>
                    <div className="viz-container">
                        <ResponsiveContainer width="100%" height={350}>
                            <PieChart>
                                <Pie
                                    data={biasDistribution}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={5}
                                    dataKey="value"
                                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                    labelLine={false}
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
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Key Findings */}
            <div className="card" style={{ marginTop: 'var(--space-xl)' }}>
                <div className="card-header">
                    <h3 className="card-title">Key Findings</h3>
                    <span className="badge badge-warning">Attention Required</span>
                </div>
                <div className="findings-list">
                    {keyFindings.map((finding, index) => (
                        <div key={index} className="finding-item">
                            <AlertTriangle size={16} className="finding-icon" />
                            <span>{finding}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
