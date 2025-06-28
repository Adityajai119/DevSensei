import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Github, Star, GitBranch, Languages, Search } from 'lucide-react';
import { githubApi } from '../services/api';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import GithubMark from '../assets/github-mark-white.svg';
import backGif from '../assets/back.gif';

interface Repository {
  name: string;
  full_name: string;
  description: string;
  language: string;
  stars: number;
  default_branch: string;
}

export const RepositoryExplorer: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await githubApi.getUserRepos(searchQuery.trim());
      setRepositories(response.repositories);
    } catch (err) {
      setError('Failed to fetch repositories for this user. Please check the username and try again.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRepositoryClick = (repo: Repository) => {
    const [owner, repoName] = repo.full_name.split('/');
    navigate(`/repository/${owner}/${repoName}`);
  };

  return (
    <Layout>
      <div className="relative min-h-screen w-full flex flex-col items-center justify-center py-8 px-2">
        {/* Background Animation */}
        <div className="fixed inset-0 w-full h-full z-0">
          <img
            src={backGif}
            alt="Background Animation"
            className="w-full h-full object-cover opacity-20"
          />
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-screen-2xl w-full mx-auto">
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-3 mb-4">
              <img src={GithubMark} alt="GitHub Logo" className="w-10 h-10" />
              <h1 className="text-3xl font-bold text-white">Repository Explorer</h1>
            </div>
            <p className="text-gray-300">Search and explore GitHub repositories</p>
          </div>

          <form onSubmit={handleSearch} className="mb-8 flex justify-center">
            <div className="flex gap-2 w-full max-w-xl">
              <div className="relative flex-1">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Enter GitHub username..."
                  className="w-full px-4 py-2 pl-10 bg-gray-900/80 backdrop-blur-sm border border-gray-800 rounded focus:outline-none focus:border-white text-white placeholder-gray-400"
                />
                <Search className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
              </div>
              <button
                type="submit"
                className="px-6 py-2 bg-white text-black rounded hover:bg-gray-200 font-bold transition-colors"
              >
                Search
              </button>
            </div>
          </form>

          {error && (
            <div className="bg-red-900/20 backdrop-blur-sm border border-red-800 text-red-400 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {repositories.map((repo) => (
                <motion.div
                  key={repo.name}
                  whileHover={{ scale: 1.02 }}
                  onClick={() => handleRepositoryClick(repo)}
                  className="bg-white/10 backdrop-blur-sm border border-gray-800 rounded-lg shadow-lg p-6 cursor-pointer hover:bg-white/20 transition-all flex flex-col justify-between h-full"
                >
                  <div className="flex items-center mb-2">
                    <Github className="text-white mr-2 w-5 h-5" />
                    <span className="font-bold text-lg text-white">{repo.name}</span>
                  </div>
                  <p className="text-gray-300 mb-4 flex-1">{repo.description || 'No description'}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-400 mb-2">
                    <div className="flex items-center">
                      <Star className="mr-1 w-4 h-4" />
                      <span>{repo.stars}</span>
                    </div>
                    {repo.language && (
                      <div className="flex items-center">
                        <Languages className="mr-1 w-4 h-4" />
                        <span>{repo.language}</span>
                      </div>
                    )}
                  </div>
                  <a
                    href={`https://github.com/${repo.full_name}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="text-gray-400 hover:text-white mt-4 inline-block transition-colors"
                  >
                    View on GitHub
                  </a>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};