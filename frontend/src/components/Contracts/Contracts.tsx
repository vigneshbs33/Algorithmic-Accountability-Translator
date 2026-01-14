import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { FileText, Plus, Download, Eye } from 'lucide-react'
import { api } from '../../services/api'
import './Contracts.css'

// Mock contract for demo
const mockContract = {
    id: '1',
    platform: 'Reddit',
    title: 'Algorithmic Accountability Contract: Reddit Recommendation System',
    generation_date: new Date().toISOString(),
    executive_summary: `Based on 10,000 recommendation samples across 10 user profiles, this analysis reveals 
significant patterns in how the recommendation algorithm shapes user information exposure.

**Key Findings:**
- The algorithm prioritizes ENGAGEMENT over DIVERSITY
- 78% of recommended content matches the user's existing ideological stance
- Filter bubbles are actively reinforced through 89% ideologically consistent recommendations
- Alternative viewpoints appear in only 12% of top-10 recommendations`,
    sections: [
        {
            title: '1. Algorithmic Optimization Objectives',
            content: `The recommendation algorithm demonstrates clear optimization for user engagement metrics 
over information diversity. Analysis indicates the following priority hierarchy:

1. **Watch Time / Time on Platform** - Primary optimization target (correlation: 0.82)
2. **Click-Through Rate** - Secondary metric (correlation: 0.71)
3. **User Return Rate** - Tertiary metric (correlation: 0.65)
4. **Content Diversity** - Not optimized (correlation: -0.23)`
        },
        {
            title: '2. Filter Bubble Analysis',
            content: `The algorithm creates and maintains information filter bubbles through systematic 
reinforcement of existing user preferences and beliefs.

**Filter Bubble Characteristics:**
- Average topic diversity score: 0.34/1.0 (indicating low diversity)
- Echo chamber detection rate: 80% of analyzed personas
- Contradictory viewpoint suppression: 5x less likely than expected by chance`
        },
        {
            title: '3. Bias Quantification',
            content: `Multi-dimensional bias analysis reveals systematic patterns in content promotion:

**Political Bias:**
- Left-leaning content: Amplified for progressive personas (+45%)
- Right-leaning content: Amplified for conservative personas (+42%)
- Centrist content: Generally suppressed across all personas (-28%)

**Emotional Bias:**
- Fear-inducing content: +35% visibility boost
- Anger-inducing content: +28% visibility boost
- Neutral/factual content: -22% visibility penalty`
        }
    ]
}

export default function Contracts() {
    const [selectedContract, setSelectedContract] = useState(mockContract)
    const [isGenerating, setIsGenerating] = useState(false)

    const generateMutation = useMutation({
        mutationFn: () => api.generateContract({
            platform: 'reddit',
            persona_ids: ['progressive_activist', 'conservative_traditional'],
            include_evidence: true
        }),
        onSuccess: (data) => {
            setSelectedContract(data)
            setIsGenerating(false)
        }
    })

    const handleGenerate = () => {
        setIsGenerating(true)
        generateMutation.mutate()
    }

    return (
        <div className="contracts-page">
            <div className="page-header">
                <div>
                    <h1>Contracts</h1>
                    <p>Generated algorithmic accountability contracts in plain language.</p>
                </div>
                <button className="btn btn-primary" onClick={handleGenerate} disabled={isGenerating}>
                    <Plus size={16} />
                    {isGenerating ? 'Generating...' : 'Generate New Contract'}
                </button>
            </div>

            <div className="contracts-layout">
                {/* Contract List */}
                <div className="contracts-sidebar">
                    <div className="contract-list">
                        <div
                            className={`contract-item ${selectedContract.id === '1' ? 'active' : ''}`}
                            onClick={() => setSelectedContract(mockContract)}
                        >
                            <FileText size={20} />
                            <div className="contract-item-info">
                                <span className="contract-item-title">Reddit Analysis</span>
                                <span className="contract-item-date">Generated today</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Contract Viewer */}
                <div className="contract-viewer">
                    <div className="contract-header">
                        <div>
                            <h2>{selectedContract.title}</h2>
                            <span className="contract-meta">
                                Platform: {selectedContract.platform} • Generated: {new Date(selectedContract.generation_date).toLocaleDateString()}
                            </span>
                        </div>
                        <div className="contract-actions">
                            <button className="btn btn-secondary">
                                <Eye size={16} />
                                Preview
                            </button>
                            <button className="btn btn-primary">
                                <Download size={16} />
                                Export PDF
                            </button>
                        </div>
                    </div>

                    <div className="contract-content">
                        {/* Executive Summary */}
                        <div className="contract-section">
                            <h3>Executive Summary</h3>
                            <div className="contract-text" dangerouslySetInnerHTML={{
                                __html: selectedContract.executive_summary.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br/>')
                            }} />
                        </div>

                        {/* Sections */}
                        {selectedContract.sections.map((section, index) => (
                            <div key={index} className="contract-section">
                                <h3>{section.title}</h3>
                                <div className="contract-text" dangerouslySetInnerHTML={{
                                    __html: section.content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br/>')
                                }} />
                            </div>
                        ))}

                        {/* Methodology */}
                        <div className="contract-section methodology">
                            <h3>Methodology Note</h3>
                            <p>
                                This contract was generated using automated NLP analysis of 10,000+ content items
                                across 10 synthetic user personas. Analysis methods include BERTopic for topic modeling,
                                BERT-based stance detection, multi-faceted bias analysis, and semantic diversity metrics.
                                All claims represent inferred algorithmic behavior, not definitive statements about
                                platform intent. Statistical significance varies by metric.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
