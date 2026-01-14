import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import LandingPage from './components/LandingPage/LandingPage'
import Dashboard from './components/Dashboard/Dashboard'
import Personas from './components/Personas/Personas'
import Analysis from './components/Analysis/Analysis'
import Contracts from './components/Contracts/Contracts'
import './App.css'

function App() {
    return (
        <Routes>
            {/* Landing page without layout */}
            <Route path="/" element={<LandingPage />} />

            {/* Dashboard routes with layout */}
            <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
            <Route path="/personas" element={<Layout><Personas /></Layout>} />
            <Route path="/analysis" element={<Layout><Analysis /></Layout>} />
            <Route path="/contracts" element={<Layout><Contracts /></Layout>} />
        </Routes>
    )
}

export default App
