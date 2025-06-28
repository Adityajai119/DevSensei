import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Github, Code, Layout, Home, Menu, X } from 'lucide-react';
import { RepositoryExplorer } from './pages/RepositoryExplorer';
import { CodePlayground } from './pages/CodePlayground';
import { FrontendPlayground } from './pages/FrontendPlayground';
import AnimatedBackground from './components/AnimatedBackground';
import styled from 'styled-components';
import RepositoryView from './components/RepositoryView';
import LayoutComponent from './components/Layout';
import VideoModal from './components/VideoModal';
import repositoryVideo from './assets/repository.mp4';
import IntroPage from './pages/IntroPage';
import CodeIntroPage from './pages/CodeIntroPage';
import FrontendIntroPage from './pages/FrontendIntroPage';
import LoginPage from './pages/LoginPage';
import RepoSearchPage from './pages/RepoSearchPage';
import Features from './components/Features';

const AppContainer = styled.div`
  position: relative;
  min-height: 100vh;
  color: white;
  overflow-x: hidden;
  background-color: black;
`;

const NavContainer = styled.nav`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.95);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
`;

const NavContent = styled.div`
  max-width: 1280px;
  margin: 0 auto;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const NavLink = styled(motion(Link))`
  color: #e5e7eb;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: all 0.2s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
`;

const MobileMenu = styled(motion.div)`
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 300px;
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(10px);
  padding: 2rem;
  z-index: 1000;
`;

const HomePage: React.FC = () => {
  const [isVideoModalOpen, setIsVideoModalOpen] = useState(false);

  return (
    <div className="min-h-screen bg-black text-white py-20 px-4">
      <VideoModal
        isOpen={isVideoModalOpen}
        onClose={() => setIsVideoModalOpen(false)}
        videoSrc={repositoryVideo}
      />
      <div className="max-w-screen-2xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Welcome to <span className="text-white">DevSensei</span>
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Your AI-powered development companion for code analysis, generation, and optimization
          </p>
        </motion.div>
        <Features />
      </div>
    </div>
  );
};

const App: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

  return (
    <Router>
      <AppContainer>
        <NavContainer>
          <NavContent>
            <Link to="/" className="flex items-center gap-2 text-xl font-bold text-white">
              <Home size={24} />
              <span className="text-white">DevSensei</span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-6">
              <NavLink
                to="/intro"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex items-center gap-2"
              >
                <Github size={20} />
                Repositories
              </NavLink>
              <NavLink
                to="/code-intro"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex items-center gap-2"
              >
                <Code size={20} />
                Code
              </NavLink>
              <NavLink
                to="/frontend-intro"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex items-center gap-2"
              >
                <Layout size={20} />
                Frontend
              </NavLink>
            </div>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden text-white p-2"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </NavContent>
        </NavContainer>

        {/* Mobile Menu */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <MobileMenu
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 20 }}
            >
              <div className="flex flex-col gap-4">
                <Link
                  to="/intro"
                  className="flex items-center gap-2 text-white hover:text-gray-300"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <Github size={20} />
                  Repositories
                </Link>
                <Link
                  to="/code-intro"
                  className="flex items-center gap-2 text-white hover:text-gray-300"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <Code size={20} />
                  Code
                </Link>
                <Link
                  to="/frontend-intro"
                  className="flex items-center gap-2 text-white hover:text-gray-300"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <Layout size={20} />
                  Frontend
                </Link>
              </div>
            </MobileMenu>
          )}
        </AnimatePresence>

        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/home" element={<HomePage />} />
          <Route path="/intro" element={<IntroPage />} />
          <Route path="/code-intro" element={<CodeIntroPage />} />
          <Route path="/frontend-intro" element={<FrontendIntroPage />} />
          <Route path="/repository-explorer" element={<RepositoryExplorer />} />
          <Route path="/code-playground" element={<CodePlayground />} />
          <Route path="/frontend-playground" element={<FrontendPlayground />} />
          <Route path="/repository/:username/:repoName" element={<RepositoryView />} />
          <Route path="/repo-search" element={<RepoSearchPage />} />
        </Routes>
      </AppContainer>
    </Router>
  );
};

export default App;
