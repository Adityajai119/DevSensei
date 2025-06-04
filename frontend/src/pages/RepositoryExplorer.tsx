import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Github, MessageSquare, Map, FileText, Loader2 } from 'lucide-react';
import { githubApi, documentationApi, chatApi } from '../services/api';
import type { ChatMessage } from '../services/api';

interface Repository {
  name: string;
  full_name: string;
  description: string;
  language: string;
  stars: number;
  default_branch: string;
}

export const RepositoryExplorer: React.FC = () => {
  const [username, setUsername] = useState('');
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [selectedRepo, setSelectedRepo] = useState<Repository | null>(null);
  const [loading, setLoading] = useState(false);
  const [generatingPdf, setGeneratingPdf] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [codebaseMap, setCodebaseMap] = useState<string | null>(null);

  const fetchRepositories = async () => {
    if (!username) return;
    
    setLoading(true);
    try {
      const response = await githubApi.getUserRepos(username);
      setRepositories(response.repositories);
    } catch (error) {
      console.error('Error fetching repositories:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectRepository = async (repo: Repository) => {
    setSelectedRepo(repo);
    
    // Index the repository for RAG
    try {
      const [owner, repoName] = repo.full_name.split('/');
      await githubApi.getRepoFiles({ owner, repo: repoName, index_for_rag: true });
    } catch (error) {
      console.error('Error indexing repository:', error);
    }
  };

  const generatePDF = async () => {
    if (!selectedRepo) return;
    
    setGeneratingPdf(true);
    try {
      const [owner, repoName] = selectedRepo.full_name.split('/');
      const response = await documentationApi.generateDocs({
        owner,
        repo: repoName,
        include_setup: true,
        include_architecture: true,
        include_codebase_map: true
      });
      
      // Download PDF
      const pdfBlob = new Blob([Buffer.from(response.pdf, 'base64')], { type: 'application/pdf' });
      const url = URL.createObjectURL(pdfBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${repoName}-documentation.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      
      // Set codebase map if available
      if (response.codebase_map) {
        setCodebaseMap(response.codebase_map.image);
      }
    } catch (error) {
      console.error('Error generating PDF:', error);
    } finally {
      setGeneratingPdf(false);
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim() || !selectedRepo) return;
    
    const newMessage: ChatMessage = { role: 'user', content: chatInput };
    setChatMessages([...chatMessages, newMessage]);
    setChatInput('');
    
    try {
      const response = await chatApi.chat({
        messages: [...chatMessages, newMessage],
        repo_name: selectedRepo.full_name,
        use_rag: true
      });
      
      setChatMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
    } catch (error) {
      console.error('Error sending chat message:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-6xl mx-auto"
      >
        <h1 className="text-4xl font-bold mb-8 text-center bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          Repository Explorer
        </h1>

        {/* GitHub Username Input */}
        <div className="mb-8">
          <div className="flex gap-4">
            <input
              type="text"
              placeholder="Enter GitHub username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && fetchRepositories()}
              className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-purple-500"
            />
            <button
              onClick={fetchRepositories}
              disabled={loading}
              className="px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center gap-2 transition-colors"
            >
              {loading ? <Loader2 className="animate-spin" /> : <Github />}
              Search
            </button>
          </div>
        </div>

        {/* Repository List */}
        {repositories.length > 0 && (
          <div className="mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {repositories.map((repo) => (
              <motion.div
                key={repo.name}
                whileHover={{ scale: 1.02 }}
                onClick={() => selectRepository(repo)}
                className={`p-4 bg-gray-800 rounded-lg cursor-pointer transition-all ${
                  selectedRepo?.name === repo.name ? 'ring-2 ring-purple-500' : ''
                }`}
              >
                <h3 className="font-semibold text-lg mb-1">{repo.name}</h3>
                <p className="text-gray-400 text-sm mb-2">{repo.description || 'No description'}</p>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-yellow-400">⭐ {repo.stars}</span>
                  <span className="text-blue-400">{repo.language || 'Unknown'}</span>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Selected Repository Actions */}
        {selectedRepo && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-gray-800 rounded-lg p-6 mb-8"
          >
            <h2 className="text-2xl font-bold mb-4">{selectedRepo.name}</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={generatePDF}
                disabled={generatingPdf}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center justify-center gap-2 transition-colors"
              >
                {generatingPdf ? <Loader2 className="animate-spin" /> : <FileText />}
                Generate PDF
              </button>
              
              <button
                onClick={() => setChatOpen(!chatOpen)}
                className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg flex items-center justify-center gap-2 transition-colors"
              >
                <MessageSquare />
                Chat with Repo
              </button>
              
              <button
                disabled={!codebaseMap}
                className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                <Map />
                View Codebase Map
              </button>
            </div>
          </motion.div>
        )}

        {/* Chat Interface */}
        {chatOpen && selectedRepo && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gray-800 rounded-lg p-6"
          >
            <h3 className="text-xl font-semibold mb-4">Chat with {selectedRepo.name}</h3>
            
            <div className="h-96 overflow-y-auto mb-4 p-4 bg-gray-900 rounded-lg">
              {chatMessages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`mb-4 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}
                >
                  <div
                    className={`inline-block p-3 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-700 text-gray-200'
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                placeholder="Ask about the codebase..."
                className="flex-1 px-4 py-2 bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <button
                onClick={sendChatMessage}
                className="px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg"
              >
                Send
              </button>
            </div>
          </motion.div>
        )}

        {/* Codebase Map */}
        {codebaseMap && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-8 bg-gray-800 rounded-lg p-6"
          >
            <h3 className="text-xl font-semibold mb-4">Codebase Map</h3>
            <img
              src={`data:image/png;base64,${codebaseMap}`}
              alt="Codebase Map"
              className="w-full rounded-lg"
            />
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}; 