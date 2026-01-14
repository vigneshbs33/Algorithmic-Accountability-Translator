import { useState } from 'react'
import {
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar,
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend
} from 'recharts'
import './Analysis.css'

type TabType = 'topics' | 'bias' | 'diversity' | 'stance'

const radarData = [
    { subject: 'Topic Diversity', Progressive: 0.28, Conservative: 0.31, Moderate: 0.67 },
    { subject: 'Stance Diversity', Progressive: 0.22, Conservative: 0.25, Moderate: 0.58 },
    { subject: 'Source Diversity', Progressive: 0.35, Conservative: 0.38, Moderate: 0.72 },
    { subject: 'Semantic Diversity', Progressive: 0.31, Conservative: 0.29, Moderate: 0.61 },
    { subject: 'Echo Chamber', Progressive: 0.82, Conservative: 0.79, Moderate: 0.33 },
]

const timelineData = [
    { day: 'Day 1', diversity: 0.45, echoChamber: 0.55 },
    { day: 'Day 2', diversity: 0.42, echoChamber: 0.58 },
    { day: 'Day 3', diversity: 0.38, echoChamber: 0.62 },
    { day: 'Day 4', diversity: 0.35, echoChamber: 0.68 },
    { day: 'Day 5', diversity: 0.32, echoChamber: 0.72 },
    { day: 'Day 6', diversity: 0.30, echoChamber: 0.75 },
    { day: 'Day 7', diversity: 0.28, echoChamber: 0.78 },
]

export default function Analysis() {
    const [activeTab, setActiveTab] = useState<TabType>('diversity')

    const tabs: { id: TabType; label: string }[] = [
        { id: 'topics', label: 'Topics' },
        { id: 'bias', label: 'Bias Analysis' },
        { id: 'diversity', label: 'Diversity' },
        { id: 'stance', label: 'Stance' },
    ]

    return (
        <div className="analysis-page">
            <div className="page-header">
                <h1>Analysis</h1>
                <p>Deep dive into recommendation patterns, filter bubbles, and algorithmic behavior.</p>
            </div>

            <div className="analysis-tabs">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`analysis-tab ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            <div className="analysis-content">
                {activeTab === 'diversity' && (
                    <div className="diversity-view">
                        <div className="grid grid-cols-2">
                            {/* Radar Chart */}
                            <div className="card">
                                <div className="card-header">
                                    <h3 className="card-title">Diversity Comparison</h3>
                                </div>
                                <div className="viz-container">
                                    <ResponsiveContainer width="100%" height={400}>
                                        <RadarChart data={radarData}>
                                            <PolarGrid stroke="rgba(255,255,255,0.1)" />
                                            <PolarAngleAxis dataKey="subject" stroke="#6b6b80" tick={{ fontSize: 12 }} />
                                            <PolarRadiusAxis stroke="#6b6b80" domain={[0, 1]} />
                                            <Radar name="Progressive" dataKey="Progressive" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                                            <Radar name="Conservative" dataKey="Conservative" stroke="#ef4444" fill="#ef4444" fillOpacity={0.3} />
                                            <Radar name="Moderate" dataKey="Moderate" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} />
                                            <Legend />
                                            <Tooltip
                                                contentStyle={{
                                                    background: '#1e1e32',
                                                    border: '1px solid rgba(255,255,255,0.1)',
                                                    borderRadius: '8px'
                                                }}
                                            />
                                        </RadarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Timeline Chart */}
                            <div className="card">
                                <div className="card-header">
                                    <h3 className="card-title">Filter Bubble Formation Over Time</h3>
                                </div>
                                <div className="viz-container">
                                    <ResponsiveContainer width="100%" height={400}>
                                        <LineChart data={timelineData}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                            <XAxis dataKey="day" stroke="#6b6b80" />
                                            <YAxis stroke="#6b6b80" domain={[0, 1]} />
                                            <Tooltip
                                                contentStyle={{
                                                    background: '#1e1e32',
                                                    border: '1px solid rgba(255,255,255,0.1)',
                                                    borderRadius: '8px'
                                                }}
                                            />
                                            <Legend />
                                            <Line
                                                type="monotone"
                                                dataKey="diversity"
                                                name="Diversity Score"
                                                stroke="#10b981"
                                                strokeWidth={2}
                                                dot={{ fill: '#10b981' }}
                                            />
                                            <Line
                                                type="monotone"
                                                dataKey="echoChamber"
                                                name="Echo Chamber Score"
                                                stroke="#ef4444"
                                                strokeWidth={2}
                                                dot={{ fill: '#ef4444' }}
                                            />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </div>

                        {/* Insights */}
                        <div className="card" style={{ marginTop: 'var(--space-lg)' }}>
                            <div className="card-header">
                                <h3 className="card-title">Analysis Insights</h3>
                            </div>
                            <div className="insights-grid">
                                <div className="insight-card">
                                    <span className="insight-label">Filter Bubble Speed</span>
                                    <span className="insight-value">7 days</span>
                                    <span className="insight-desc">Time to reach 80% echo chamber</span>
                                </div>
                                <div className="insight-card">
                                    <span className="insight-label">Most Affected Persona</span>
                                    <span className="insight-value">Progressive Activist</span>
                                    <span className="insight-desc">Highest echo chamber score</span>
                                </div>
                                <div className="insight-card">
                                    <span className="insight-label">Most Resilient Persona</span>
                                    <span className="insight-value">Political Moderate</span>
                                    <span className="insight-desc">Lowest echo chamber score</span>
                                </div>
                                <div className="insight-card">
                                    <span className="insight-label">Diversity Drop</span>
                                    <span className="insight-value">-38%</span>
                                    <span className="insight-desc">Average diversity decrease</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'topics' && (
                    <div className="topics-view">
                        <div className="card">
                            <div className="card-header">
                                <h3 className="card-title">Discovered Topics</h3>
                            </div>
                            <p className="text-muted">Topic modeling analysis will appear here.</p>
                        </div>
                    </div>
                )}

                {activeTab === 'bias' && (
                    <div className="bias-view">
                        <div className="card">
                            <div className="card-header">
                                <h3 className="card-title">Bias Analysis</h3>
                            </div>
                            <p className="text-muted">Bias detection results will appear here.</p>
                        </div>
                    </div>
                )}

                {activeTab === 'stance' && (
                    <div className="stance-view">
                        <div className="card">
                            <div className="card-header">
                                <h3 className="card-title">Stance Detection</h3>
                            </div>
                            <p className="text-muted">Stance analysis results will appear here.</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
