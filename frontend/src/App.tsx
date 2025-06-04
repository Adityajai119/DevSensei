import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Github, Code, Layout, Home } from 'lucide-react';
import { RepositoryExplorer } from './pages/RepositoryExplorer';
import { CodePlayground } from './pages/CodePlayground';
import { FrontendPlayground } from './pages/FrontendPlayground';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto"
      >
        <h1 className="text-5xl font-bold mb-4 text-center bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          DevSensei
        </h1>
        <p className="text-xl text-center mb-12 text-gray-300">
          AI-powered code understanding and generation platform
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link to="/repository-explorer">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="p-6 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors cursor-pointer"
            >
              <Github className="w-12 h-12 mb-4 text-purple-400" />
              <h3 className="text-xl font-semibold mb-2">Repository Explorer</h3>
              <p className="text-gray-400">
                Explore GitHub repos, generate docs, and chat with codebases using RAG
              </p>
            </motion.div>
          </Link>

          <Link to="/code-playground">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="p-6 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors cursor-pointer"
            >
              <Code className="w-12 h-12 mb-4 text-blue-400" />
              <h3 className="text-xl font-semibold mb-2">Code Playground</h3>
              <p className="text-gray-400">
                Write, run, debug, and optimize code in multiple languages
              </p>
            </motion.div>
          </Link>

          <Link to="/frontend-playground">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="p-6 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors cursor-pointer"
            >
              <Layout className="w-12 h-12 mb-4 text-green-400" />
              <h3 className="text-xl font-semibold mb-2">Frontend AI</h3>
              <p className="text-gray-400">
                Generate and preview frontend code with AI assistance
              </p>
            </motion.div>
          </Link>
        </div>
      </motion.div>
    </div>
  );
};

const Navigation: React.FC = () => {
  return (
    <nav className="bg-gray-900 border-b border-gray-800 p-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 text-xl font-bold text-white">
          <Home size={24} />
          DevSensei
        </Link>
        <div className="flex gap-6">
          <Link
            to="/repository-explorer"
            className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors"
          >
            <Github size={20} />
            Repositories
          </Link>
          <Link
            to="/code-playground"
            className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors"
          >
            <Code size={20} />
            Code
          </Link>
          <Link
            to="/frontend-playground"
            className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors"
          >
            <Layout size={20} />
            Frontend
          </Link>
        </div>
      </div>
    </nav>
  );
};

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-900">
        <Navigation />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/repository-explorer" element={<RepositoryExplorer />} />
          <Route path="/code-playground" element={<CodePlayground />} />
          <Route path="/frontend-playground" element={<FrontendPlayground />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
