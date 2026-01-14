import { Link } from 'react-router-dom'
import {
    Sparkles,
    Shield,
    BarChart3,
    FileText,
    Users,
    ArrowRight,
    Github,
    ExternalLink,
    Play,
    CheckCircle,
    Zap,
    Eye,
    Lock
} from 'lucide-react'
import './LandingPage.css'

export default function LandingPage() {
    const features = [
        {
            icon: Shield,
            title: 'Filter Bubble Detection',
            description: 'Identify when recommendation algorithms are trapping users in echo chambers.'
        },
        {
            icon: BarChart3,
            title: 'Bias Analysis',
            description: 'Measure political bias, sensationalism, and emotional manipulation in content.'
        },
        {
            icon: FileText,
            title: 'Plain Language Reports',
            description: 'AI-generated contracts explain algorithm behavior in terms anyone can understand.'
        },
        {
            icon: Users,
            title: 'Persona Testing',
            description: '10 synthetic user profiles test how different people experience the same platform.'
        },
        {
            icon: Eye,
            title: 'Transparency First',
            description: 'See exactly how algorithms prioritize engagement over diversity and accuracy.'
        },
        {
            icon: Lock,
            title: 'Privacy Focused',
            description: 'No real user data - only synthetic personas for ethical algorithm analysis.'
        }
    ]

    const stats = [
        { value: '10,000+', label: 'Content Items Analyzed' },
        { value: '10', label: 'User Personas' },
        { value: '78%', label: 'Bubble Detection Rate' },
        { value: '100%', label: 'Open Source' }
    ]

    const howItWorks = [
        {
            step: 1,
            title: 'Collect Data',
            description: 'Synthetic personas interact with platforms to see what gets recommended to different user types.'
        },
        {
            step: 2,
            title: 'Analyze Patterns',
            description: 'NLP and ML models detect topics, bias, stance, and echo chamber effects in the recommendations.'
        },
        {
            step: 3,
            title: 'Generate Reports',
            description: 'AI translates complex findings into plain-language "contracts" anyone can understand.'
        }
    ]

    return (
        <div className="landing-page">
            {/* Navigation */}
            <nav className="landing-nav">
                <div className="landing-container">
                    <div className="landing-logo">
                        <Sparkles size={24} />
                        <span>AlgoTranslator</span>
                    </div>
                    <div className="landing-nav-links">
                        <a href="#features">Features</a>
                        <a href="#how-it-works">How It Works</a>
                        <a href="https://github.com/vigneshbs33/Algorithmic-Accountability-Translator" target="_blank" rel="noopener noreferrer">
                            <Github size={16} />
                            GitHub
                        </a>
                        <Link to="/dashboard" className="btn btn-primary btn-sm">
                            Launch App
                            <ArrowRight size={14} />
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="hero-section">
                <div className="hero-content">
                    <div className="hero-badge">
                        <Zap size={14} />
                        Open Source NLP Product
                    </div>
                    <h1>
                        Understand the Algorithms<br />
                        <span className="gradient-text">That Shape Your Reality</span>
                    </h1>
                    <p className="hero-description">
                        AlgoTranslator reverse-engineers social media recommendation algorithms and translates
                        their behavior into plain language. See how filter bubbles form, detect bias, and
                        understand what these invisible systems are really doing.
                    </p>
                    <div className="hero-actions">
                        <Link to="/dashboard" className="btn btn-primary btn-lg">
                            <Play size={18} />
                            Try the Demo
                        </Link>
                        <a href="https://github.com/vigneshbs33/Algorithmic-Accountability-Translator" target="_blank" rel="noopener noreferrer" className="btn btn-secondary btn-lg">
                            <Github size={18} />
                            View Source
                        </a>
                    </div>
                    <div className="hero-credit">
                        Created by <a href="https://vigneshbs.xyz" target="_blank" rel="noopener noreferrer">Vignesh B S</a>
                    </div>
                </div>
                <div className="hero-visual">
                    <div className="hero-card">
                        <div className="hero-card-header">
                            <span className="status-dot green"></span>
                            <span>Analysis Complete</span>
                        </div>
                        <div className="hero-card-content">
                            <div className="hero-metric">
                                <span className="hero-metric-value">0.34</span>
                                <span className="hero-metric-label">Diversity Score</span>
                            </div>
                            <div className="hero-metric danger">
                                <span className="hero-metric-value">78%</span>
                                <span className="hero-metric-label">Echo Chamber</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Stats Bar */}
            <section className="stats-bar">
                <div className="landing-container">
                    {stats.map((stat, index) => (
                        <div key={index} className="stat-item">
                            <span className="stat-value">{stat.value}</span>
                            <span className="stat-label">{stat.label}</span>
                        </div>
                    ))}
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="features-section">
                <div className="landing-container">
                    <div className="section-header">
                        <h2>Powerful Analysis Features</h2>
                        <p>Everything you need to understand recommendation algorithms</p>
                    </div>
                    <div className="features-grid">
                        {features.map((feature, index) => (
                            <div key={index} className="feature-card">
                                <div className="feature-icon">
                                    <feature.icon size={24} />
                                </div>
                                <h3>{feature.title}</h3>
                                <p>{feature.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* How It Works Section */}
            <section id="how-it-works" className="how-section">
                <div className="landing-container">
                    <div className="section-header">
                        <h2>How AlgoTranslator Works</h2>
                        <p>Three simple steps to algorithmic transparency</p>
                    </div>
                    <div className="how-steps">
                        {howItWorks.map((step, index) => (
                            <div key={index} className="how-step">
                                <div className="step-number">{step.step}</div>
                                <div className="step-content">
                                    <h3>{step.title}</h3>
                                    <p>{step.description}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="cta-section">
                <div className="landing-container">
                    <div className="cta-content">
                        <h2>Ready to See Behind the Algorithm?</h2>
                        <p>Try the demo with pre-loaded analysis data - no API keys required</p>
                        <div className="cta-actions">
                            <Link to="/dashboard" className="btn btn-primary btn-lg">
                                Launch Dashboard
                                <ArrowRight size={18} />
                            </Link>
                        </div>
                        <div className="cta-features">
                            <span><CheckCircle size={16} /> No signup required</span>
                            <span><CheckCircle size={16} /> Free & open source</span>
                            <span><CheckCircle size={16} /> Demo data included</span>
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="landing-footer">
                <div className="landing-container">
                    <div className="footer-content">
                        <div className="footer-brand">
                            <div className="landing-logo">
                                <Sparkles size={20} />
                                <span>AlgoTranslator</span>
                            </div>
                            <p>Making AI algorithms transparent for everyone.</p>
                            <p className="footer-credit">
                                © 2026 <a href="https://vigneshbs.xyz" target="_blank" rel="noopener noreferrer">Vignesh B S</a>. MIT License.
                            </p>
                        </div>
                        <div className="footer-links">
                            <div className="footer-column">
                                <h4>Product</h4>
                                <Link to="/dashboard">Dashboard</Link>
                                <Link to="/personas">Personas</Link>
                                <Link to="/analysis">Analysis</Link>
                                <Link to="/contracts">Contracts</Link>
                            </div>
                            <div className="footer-column">
                                <h4>Resources</h4>
                                <a href="https://github.com/vigneshbs33/Algorithmic-Accountability-Translator" target="_blank" rel="noopener noreferrer">GitHub</a>
                                <a href="https://github.com/vigneshbs33/Algorithmic-Accountability-Translator#readme" target="_blank" rel="noopener noreferrer">Documentation</a>
                                <a href="https://github.com/vigneshbs33/Algorithmic-Accountability-Translator/issues" target="_blank" rel="noopener noreferrer">Report Bug</a>
                            </div>
                            <div className="footer-column">
                                <h4>Creator</h4>
                                <a href="https://vigneshbs.xyz" target="_blank" rel="noopener noreferrer">Portfolio</a>
                                <a href="https://github.com/vigneshbs33" target="_blank" rel="noopener noreferrer">GitHub Profile</a>
                            </div>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    )
}
