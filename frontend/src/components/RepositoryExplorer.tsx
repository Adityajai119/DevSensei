import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Github, Star, GitBranch, Languages } from 'lucide-react';
import { githubApi } from '../services/api';
import Layout from './Layout';

interface Repository {
  id: number;
  name: string;
  full_name: string;
  description: string;
  html_url: string;
  stargazers_count: number;
  forks_count: number;
  language: string;
  topics: string[];
}

const RepositoryExplorer: React.FC = () => {
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
      const response = await githubApi.searchRepositories(searchQuery);
      setRepositories(response.items);
    } catch (err) {
      setError('Failed to fetch repositories. Please try again.');
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
      <div className="bg-black min-h-screen w-full flex flex-col items-center justify-center py-8 px-2">
        <div className="max-w-screen-2xl w-full mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-4">Repository Explorer</h1>
            <p className="text-gray-300">Search and explore GitHub repositories</p>
          </div>

          <form onSubmit={handleSearch} className="mb-8 flex justify-center">
            <div className="flex gap-2 w-full max-w-xl">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search repositories..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-black text-black"
              />
              <button
                type="submit"
                className="px-6 py-2 bg-black text-white rounded hover:bg-gray-800 font-bold"
              >
                Search
              </button>
            </div>
          </form>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
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
                <div
                  key={repo.id}
                  onClick={() => handleRepositoryClick(repo)}
                  className="bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-lg transition-shadow flex flex-col justify-between h-full"
                >
                  <div className="flex items-center mb-2">
                    <Github className="text-gray-500 mr-2 w-5 h-5" />
                    <span className="font-bold text-lg text-black">{repo.name}</span>
                  </div>
                  <p className="text-gray-700 mb-4 flex-1">{repo.description}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-600 mb-2">
                    <div className="flex items-center">
                      <Star className="mr-1 w-4 h-4" />
                      <span>{repo.stargazers_count}</span>
                    </div>
                    <div className="flex items-center">
                      <GitBranch className="mr-1 w-4 h-4" />
                      <span>{repo.forks_count}</span>
                    </div>
                    {repo.language && (
                      <div className="flex items-center">
                        <Languages className="mr-1 w-4 h-4" />
                        <span>{repo.language}</span>
                      </div>
                    )}
                  </div>
                  {repo.topics && repo.topics.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {repo.topics.map((topic) => (
                        <span
                          key={topic}
                          className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  )}
                  <a
                    href={repo.html_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="text-gray-600 hover:text-black mt-4 inline-block"
                  >
                    View on GitHub
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default RepositoryExplorer; 