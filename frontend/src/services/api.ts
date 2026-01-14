import axios from 'axios'

const API_BASE = '/api'

const client = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Types
interface PersonaResponse {
    personas: Array<{
        id: string
        name: string
        description: string
        interests: string[]
        ideological_leaning: string
        subreddits: string[]
        youtube_channels: string[]
        search_terms: string[]
    }>
    total: number
}

interface AnalysisSummary {
    platform: string
    total_content_analyzed: number
    personas_analyzed: number
    key_findings: string[]
    analysis_date: string
}

interface ContractRequest {
    platform: string
    persona_ids: string[]
    include_evidence?: boolean
    format?: string
}

interface Contract {
    id: string
    platform: string
    title: string
    generation_date: string
    executive_summary: string
    sections: Array<{
        title: string
        content: string
    }>
}

// API Functions
export const api = {
    // Personas
    getPersonas: async (): Promise<PersonaResponse> => {
        const { data } = await client.get('/personas/')
        return data
    },

    getPersona: async (id: string) => {
        const { data } = await client.get(`/personas/${id}`)
        return data
    },

    // Analysis
    getAnalysisSummary: async (): Promise<AnalysisSummary> => {
        const { data } = await client.get('/analysis/summary')
        return data
    },

    getTopicAnalysis: async (platform = 'reddit') => {
        const { data } = await client.get('/analysis/topics', { params: { platform } })
        return data
    },

    getBiasAnalysis: async (personaId: string, platform = 'reddit') => {
        const { data } = await client.get(`/analysis/bias/${personaId}`, { params: { platform } })
        return data
    },

    getDiversityAnalysis: async (personaId: string, platform = 'reddit') => {
        const { data } = await client.get(`/analysis/diversity/${personaId}`, { params: { platform } })
        return data
    },

    // Contracts
    getContracts: async () => {
        const { data } = await client.get('/contracts/')
        return data
    },

    getContract: async (id: string): Promise<Contract> => {
        const { data } = await client.get(`/contracts/${id}`)
        return data
    },

    generateContract: async (request: ContractRequest): Promise<Contract> => {
        const { data } = await client.post('/contracts/generate', request)
        return data
    },

    // Scraping
    startRedditScrape: async (personaIds: string[], maxItems = 100) => {
        const { data } = await client.post('/scrape/reddit', {
            persona_ids: personaIds,
            platform: 'reddit',
            max_items: maxItems,
        })
        return data
    },

    startYouTubeScrape: async (personaIds: string[], maxItems = 100) => {
        const { data } = await client.post('/scrape/youtube', {
            persona_ids: personaIds,
            platform: 'youtube',
            max_items: maxItems,
        })
        return data
    },

    getScrapeJobs: async () => {
        const { data } = await client.get('/scrape/jobs')
        return data
    },

    getScrapeJob: async (jobId: string) => {
        const { data } = await client.get(`/scrape/jobs/${jobId}`)
        return data
    },

    // Health
    healthCheck: async () => {
        const { data } = await client.get('/health')
        return data
    },
}

export default api
