import { useQuery } from '@tanstack/react-query'
import { api } from '../../services/api'
import './Personas.css'

// Mock personas data for demo
const mockPersonas = [
    {
        id: 'progressive_activist',
        name: 'Progressive Activist',
        description: 'Passionate about social justice, climate action, and progressive policies.',
        interests: ['climate change', 'social justice', 'progressive politics', 'renewable energy'],
        ideological_leaning: 'left',
        subreddits: ['r/politics', 'r/climate', 'r/progressive'],
    },
    {
        id: 'conservative_traditional',
        name: 'Conservative Traditional',
        description: 'Values traditional family structures, religious principles, and conservative economic policies.',
        interests: ['traditional values', 'religious freedom', 'free market', 'gun rights'],
        ideological_leaning: 'right',
        subreddits: ['r/Conservative', 'r/Republican', 'r/progun'],
    },
    {
        id: 'tech_enthusiast',
        name: 'Tech Enthusiast',
        description: 'Fascinated by technology, AI, startups, and innovation.',
        interests: ['artificial intelligence', 'programming', 'startups', 'tech industry'],
        ideological_leaning: 'neutral',
        subreddits: ['r/technology', 'r/programming', 'r/MachineLearning'],
    },
    {
        id: 'health_focused',
        name: 'Health Focused',
        description: 'Dedicated to fitness, nutrition, and overall wellness.',
        interests: ['fitness', 'nutrition', 'mental health', 'yoga'],
        ideological_leaning: 'neutral',
        subreddits: ['r/Fitness', 'r/nutrition', 'r/Meditation'],
    },
    {
        id: 'political_moderate',
        name: 'Political Moderate',
        description: 'Seeks balanced news coverage and centrist perspectives.',
        interests: ['balanced news', 'bipartisan policy', 'political analysis'],
        ideological_leaning: 'center',
        subreddits: ['r/NeutralPolitics', 'r/moderatepolitics', 'r/centrist'],
    },
    {
        id: 'entertainment_seeker',
        name: 'Entertainment Seeker',
        description: 'Primarily interested in entertainment content including movies, music, games.',
        interests: ['movies', 'music', 'video games', 'TV shows'],
        ideological_leaning: 'neutral',
        subreddits: ['r/movies', 'r/gaming', 'r/Music'],
    },
]

const leaningColors: Record<string, string> = {
    left: '#3b82f6',
    'center-left': '#6366f1',
    center: '#8b5cf6',
    'center-right': '#f59e0b',
    right: '#ef4444',
    neutral: '#6b7280',
}

export default function Personas() {
    const { data: personasResponse, isLoading } = useQuery({
        queryKey: ['personas'],
        queryFn: () => api.getPersonas()
    })

    const personas = personasResponse?.personas || mockPersonas

    if (isLoading) {
        return (
            <div className="loading">
                <div className="loading-spinner" />
            </div>
        )
    }

    return (
        <div className="personas-page">
            <div className="page-header">
                <h1>User Personas</h1>
                <p>
                    10 distinct synthetic user personas representing different ideological and interest profiles
                    for testing recommendation algorithm behavior.
                </p>
            </div>

            <div className="persona-grid">
                {personas.map((persona, index) => (
                    <div
                        key={persona.id}
                        className="persona-card animate-fade-in"
                        style={{ animationDelay: `${index * 0.05}s` }}
                    >
                        <div className="persona-header">
                            <div className="persona-avatar">
                                {persona.name.split(' ').map(w => w[0]).join('')}
                            </div>
                            <div>
                                <h3>{persona.name}</h3>
                                <span
                                    className="leaning-badge"
                                    style={{
                                        backgroundColor: `${leaningColors[persona.ideological_leaning]}20`,
                                        color: leaningColors[persona.ideological_leaning]
                                    }}
                                >
                                    {persona.ideological_leaning}
                                </span>
                            </div>
                        </div>

                        <p className="persona-description">{persona.description}</p>

                        <div className="persona-interests">
                            {persona.interests.slice(0, 4).map((interest, i) => (
                                <span key={i} className="interest-tag">{interest}</span>
                            ))}
                            {persona.interests.length > 4 && (
                                <span className="interest-tag more">+{persona.interests.length - 4}</span>
                            )}
                        </div>

                        <div className="persona-subreddits">
                            <span className="subreddits-label">Active in:</span>
                            <span className="subreddits-list">
                                {persona.subreddits.slice(0, 3).join(', ')}
                            </span>
                        </div>

                        <button className="btn btn-secondary persona-action">
                            View Analysis
                        </button>
                    </div>
                ))}
            </div>
        </div>
    )
}
