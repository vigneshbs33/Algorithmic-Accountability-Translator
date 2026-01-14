import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './components/Dashboard/Dashboard'
import Personas from './components/Personas/Personas'
import Analysis from './components/Analysis/Analysis'
import Contracts from './components/Contracts/Contracts'
import './App.css'

function App() {
    return (
        <Layout>
            <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/personas" element={<Personas />} />
                <Route path="/analysis" element={<Analysis />} />
                <Route path="/contracts" element={<Contracts />} />
            </Routes>
        </Layout>
    )
}

export default App
