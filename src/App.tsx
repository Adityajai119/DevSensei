import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import Navbar from './components/layout/Navbar'
import Footer from './components/layout/Footer'
import Home from './pages/Home'
import RepositoryExplorer from './pages/RepositoryExplorer'
import CodePlayground from './pages/CodePlayground'
import FrontendPlayground from './pages/FrontendPlayground'
import Documentation from './pages/Documentation'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary-900 via-secondary-800 to-secondary-900">
      <Navbar />
      
      <motion.main
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="pt-16"
      >
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/repository" element={<RepositoryExplorer />} />
          <Route path="/playground" element={<CodePlayground />} />
          <Route path="/frontend" element={<FrontendPlayground />} />
          <Route path="/docs" element={<Documentation />} />
        </Routes>
      </motion.main>

      <Footer />
    </div>
  )
}

export default App