import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { GitBranch, Search, FileCode, FolderTree } from 'lucide-react';
import Button from '../components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../config/api';

interface FileInfo {
  path: string;
  name: string;
  size: number;
  type: string;
  language?: string;
}

interface RepoStructure {
  name: string;
  description?: string;
  stars: number;
  language?: string;
  files: FileInfo[];
  structure: Record<string, unknown>;
}

const CodeScrapingPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [repositories, setRepositories] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<RepoStructure[] | null>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setResults(null);

    try {
      const repoList = repositories.split(',').map(r => r.trim()).filter(r => r);
      const response = await axios.post(`${API_BASE_URL}${API_ENDPOINTS.github.scrape}`, {
        username,
        repositories: repoList,
        github_token: localStorage.getItem('github_token') || undefined,
      });
      setResults(response.data);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'An error occurred while scraping repositories');
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-dark-900 dark:to-dark-800">
      <div className="max-w-7xl mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <div className="flex justify-center mb-6">
            <div className="p-4 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl text-white">
              <GitBranch className="w-12 h-12" />
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="gradient-text">Code Scraping</span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Analyze and document GitHub repositories with intelligent code parsing
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card className="max-w-2xl mx-auto mb-8">
            <CardHeader>
              <CardTitle>Repository Information</CardTitle>
              <CardDescription>
                Enter the GitHub username and repositories to analyze
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    GitHub Username
                  </label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-dark-800 focus:ring-2 focus:ring-primary-500"
                    placeholder="e.g., octocat"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Repository Names (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={repositories}
                    onChange={(e) => setRepositories(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-dark-800 focus:ring-2 focus:ring-primary-500"
                    placeholder="e.g., repo1, repo2, repo3"
                    required
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full"
                  isLoading={isLoading}
                  icon={<Search className="w-4 h-4" />}
                >
                  Analyze Repositories
                </Button>
              </form>

              {error && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-4 p-4 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-lg"
                >
                  {error}
                </motion.div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {results && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="grid grid-cols-1 lg:grid-cols-2 gap-6"
          >
            {results.map((repo: RepoStructure, index: number) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>{repo.name}</CardTitle>
                      <span className="text-yellow-500">⭐ {repo.stars}</span>
                    </div>
                    <CardDescription>{repo.description || 'No description'}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center gap-2">
                        <FileCode className="w-5 h-5 text-primary-500" />
                        <span className="font-medium">{repo.files.length} files</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <FolderTree className="w-5 h-5 text-primary-500" />
                        <span className="font-medium">Language: {repo.language || 'Multiple'}</span>
                      </div>
                      <div className="mt-4">
                        <h4 className="font-medium mb-2">File Structure:</h4>
                        <div className="bg-gray-100 dark:bg-dark-800 rounded-lg p-4 max-h-64 overflow-y-auto">
                          <pre className="text-sm">
                            {JSON.stringify(repo.structure, null, 2)}
                          </pre>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default CodeScrapingPage; 