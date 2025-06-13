import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Search, 
  GitBranch, 
  Star, 
  Download, 
  MessageSquare, 
  FileText,
  Loader2,
  ExternalLink,
  Code2,
  Users,
  Calendar,
  Eye
} from 'lucide-react'
import { useQuery } from 'react-query'
import toast from 'react-hot-toast'
import { githubService } from '../services/api'

interface Repository {
  name: string
  full_name: string
  description: string
  language: string
  stars: number
  forks: number
  private: boolean
  default_branch: string
  url: string
}

const RepositoryExplorer = () => {
  const [username, setUsername] = useState('')
  const [selectedRepo, setSelectedRepo] = useState<Repository | null>(null)
  const [chatQuery, setChatQuery] = useState('')
  const [isGeneratingDocs, setIsGeneratingDocs] = useState(false)
  const [isChatting, setIsChatting] = useState(false)

  const { data: repositories, isLoading, error, refetch } = useQuery(
    ['repositories', username],
    () => githubService.getUserRepos(username),
    {
      enabled: false,
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to fetch repositories')
      }
    }
  )

  const handleSearch = () => {
    if (!username.trim()) {
      toast.error('Please enter a GitHub username')
      return
    }
    refetch()
  }

  const handleGenerateDocs = async () => {
    if (!selectedRepo) return

    setIsGeneratingDocs(true)
    try {
      const [owner, repo] = selectedRepo.full_name.split('/')
      const response = await githubService.generateProjectDocs({
        owner,
        repo,
        branch: selectedRepo.default_branch,
        include_setup: true,
        include_architecture: true,
        include_api_docs: true,
        include_codebase_map: true
      })

      // Create download link for PDF
      const blob = new Blob([atob(response.pdf)], { type: 'application/pdf' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${selectedRepo.name}-documentation.pdf`
      a.click()
      URL.revokeObjectURL(url)

      toast.success('Documentation generated successfully!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to generate documentation')
    } finally {
      setIsGeneratingDocs(false)
    }
  }

  const handleChat = async () => {
    if (!selectedRepo || !chatQuery.trim()) return

    setIsChatting(true)
    try {
      const [owner, repo] = selectedRepo.full_name.split('/')
      const response = await githubService.chatWithRepo({
        username: owner,
        repo,
        query: chatQuery
      })

      // Display chat response (you can implement a chat UI here)
      toast.success('Chat response received!')
      console.log('Chat response:', response)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to chat with repository')
    } finally {
      setIsChatting(false)
    }
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Repository Explorer
          </h1>
          <p className="text-xl text-secondary-300 max-w-2xl mx-auto">
            Analyze GitHub repositories, generate comprehensive documentation, and chat with your codebase using AI
          </p>
        </motion.div>

        {/* Search Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card mb-8"
        >
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <label htmlFor="username" className="block text-sm font-medium text-secondary-300 mb-2">
                GitHub Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Enter GitHub username..."
                className="input"
              />
            </div>
            <div className="flex items-end">
              <button
                onClick={handleSearch}
                disabled={isLoading}
                className="btn-primary w-full md:w-auto"
              >
                {isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Search className="h-5 w-5" />
                )}
                <span className="ml-2">Search</span>
              </button>
            </div>
          </div>
        </motion.div>

        {/* Error State */}
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="card bg-red-900/20 border-red-500/50 text-center"
          >
            <p className="text-red-300">Failed to fetch repositories. Please check the username and try again.</p>
          </motion.div>
        )}

        {/* Repositories Grid */}
        {repositories && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8"
          >
            {repositories.repositories.map((repo: Repository, index: number) => (
              <motion.div
                key={repo.full_name}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -5 }}
                className={`card cursor-pointer transition-all duration-300 ${
                  selectedRepo?.full_name === repo.full_name
                    ? 'border-primary-500 bg-primary-900/20'
                    : 'hover:border-primary-500/50'
                }`}
                onClick={() => setSelectedRepo(repo)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <GitBranch className="h-5 w-5 text-primary-400" />
                    <h3 className="font-semibold text-white truncate">{repo.name}</h3>
                  </div>
                  <a
                    href={repo.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="p-1 text-secondary-400 hover:text-white transition-colors"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </div>

                <p className="text-secondary-300 text-sm mb-4 line-clamp-2">
                  {repo.description || 'No description available'}
                </p>

                <div className="flex items-center justify-between text-sm text-secondary-400">
                  <div className="flex items-center space-x-4">
                    {repo.language && (
                      <div className="flex items-center space-x-1">
                        <Code2 className="h-4 w-4" />
                        <span>{repo.language}</span>
                      </div>
                    )}
                    <div className="flex items-center space-x-1">
                      <Star className="h-4 w-4" />
                      <span>{repo.stars}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Users className="h-4 w-4" />
                      <span>{repo.forks}</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* Selected Repository Actions */}
        {selectedRepo && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card"
          >
            <h2 className="text-2xl font-bold text-white mb-4">
              Selected: {selectedRepo.name}
            </h2>
            <p className="text-secondary-300 mb-6">
              {selectedRepo.description || 'No description available'}
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Generate Documentation */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-primary-400" />
                  Generate Documentation
                </h3>
                <p className="text-secondary-300 text-sm">
                  Create comprehensive PDF documentation including setup instructions, 
                  architecture overview, and codebase visualization.
                </p>
                <button
                  onClick={handleGenerateDocs}
                  disabled={isGeneratingDocs}
                  className="btn-primary w-full"
                >
                  {isGeneratingDocs ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Download className="h-5 w-5" />
                  )}
                  <span className="ml-2">
                    {isGeneratingDocs ? 'Generating...' : 'Generate PDF'}
                  </span>
                </button>
              </div>

              {/* Chat with Repository */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <MessageSquare className="h-5 w-5 mr-2 text-accent-400" />
                  Chat with Repository
                </h3>
                <p className="text-secondary-300 text-sm">
                  Ask questions about the codebase using AI-powered analysis 
                  and get intelligent responses.
                </p>
                <div className="space-y-2">
                  <input
                    type="text"
                    value={chatQuery}
                    onChange={(e) => setChatQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleChat()}
                    placeholder="Ask about the codebase..."
                    className="input"
                  />
                  <button
                    onClick={handleChat}
                    disabled={isChatting || !chatQuery.trim()}
                    className="btn-accent w-full"
                  >
                    {isChatting ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <MessageSquare className="h-5 w-5" />
                    )}
                    <span className="ml-2">
                      {isChatting ? 'Analyzing...' : 'Ask Question'}
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Empty State */}
        {repositories && repositories.repositories.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="card text-center"
          >
            <GitBranch className="h-16 w-16 text-secondary-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No Repositories Found</h3>
            <p className="text-secondary-300">
              The user "{username}" doesn't have any public repositories or the username doesn't exist.
            </p>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default RepositoryExplorer