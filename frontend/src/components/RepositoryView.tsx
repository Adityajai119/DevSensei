import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, File, Folder, Download, Map, Star, GitBranch, Code } from 'lucide-react';
import { githubApi } from '../services/api';
import type { RepoInfo } from '../services/api';
import Layout from './Layout';
import GithubMark from '../assets/github-mark-white.svg';
import { Github } from 'lucide-react';
import backGif from '../assets/back.gif';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  children?: FileNode[];
}

interface RepositoryDetails extends RepoInfo {
  full_name: string;
  html_url: string;
  clone_url: string;
}

// Helper function to convert base64 to blob
const base64ToBlob = (base64: string, type = 'application/pdf'): Blob => {
  const binaryString = window.atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return new Blob([bytes], { type });
};

const RepositoryView: React.FC = () => {
  const { username, repoName } = useParams();
  const navigate = useNavigate();
  const [fileTree, setFileTree] = useState<FileNode[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ role: string; content: string }>>([]);
  const [explanation, setExplanation] = useState('');
  const [technologies, setTechnologies] = useState<string[]>([]);
  const [repoDetails, setRepoDetails] = useState<RepositoryDetails | null>(null);
  const [details, setDetails] = useState('');
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [fileLoading, setFileLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'code' | 'image'>('code');

  useEffect(() => {
    if (username && repoName) {
      fetchRepositoryDetails();
      fetchRepositoryFiles();
      fetchRepositoryDetailsText();
    }
  }, [username, repoName]);

  const fetchRepositoryDetails = async () => {
    try {
      const response = await githubApi.getRepoInfo({
        owner: username!,
        repo: repoName!
      });
      setRepoDetails({
        ...response,
        full_name: `${username}/${repoName}`,
        html_url: `https://github.com/${username}/${repoName}`,
        clone_url: response.clone_url || `https://github.com/${username}/${repoName}.git`,
      });
    } catch (error) {
      console.error('Error fetching repository details:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRepositoryFiles = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/github/repo/structure`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          owner: username,
          repo: repoName,
          branch: 'main'
        })
      });
      const data = await response.json();
      // Convert the structure to FileNode format
      const convertToFileNodes = (structure: string[]): FileNode[] => {
        return structure.map(item => {
          const isDir = item.includes('📁');
          const name = item.trim().split(' ').pop()?.replace('/', '') || '';
          return {
            name,
            path: name,
            type: isDir ? 'directory' : 'file'
          };
        });
      };
      setFileTree(convertToFileNodes(data.structure));
    } catch (error) {
      console.error('Error fetching repository files:', error);
    }
  };

  const fetchRepositoryDetailsText = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/github/repo/chat-with-repo`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repo_name: `${username}/${repoName}`,
          query: "Explain this repository and list the main technologies used."
        })
      });
      const data = await response.json();
      setDetails(data.response);
      setTechnologies(Object.keys(data.context.languages));
    } catch (error) {
      console.error('Error fetching repository explanation:', error);
    }
  };

  const fetchFileContent = async (path: string) => {
    setFileLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/github/repo/files`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          owner: username,
          repo: repoName,
          branch: 'main',
          path: path
        })
      });
      const data = await response.json();
      setFileContent(data.content);
    } catch (error) {
      console.error('Error fetching file content:', error);
    } finally {
      setFileLoading(false);
    }
  };

  const handleFileClick = async (file: FileNode) => {
    if (file.type === 'directory') {
      setSelectedFile(null);
      setFileContent('');
    } else {
      setSelectedFile(file.path);
      setFileLoading(true);
      setViewMode('code'); // Reset view mode when opening a new file
      try {
        const response = await fetch(`http://localhost:8000/api/documentation/file-content?path=${encodeURIComponent(file.path)}`);
        if (!response.ok) throw new Error('Failed to fetch file content');
        const data = await response.json();
        setFileContent(data.content);
      } catch (error) {
        console.error('Error fetching file content:', error);
        setFileContent('Error loading file content');
      } finally {
        setFileLoading(false);
      }
    }
  };

  const handleBackToFiles = () => {
    setSelectedFile(null);
    setFileContent('');
  };

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;
    setChatHistory([...chatHistory, { role: 'user', content: chatMessage }]);
    setChatMessage('');
    try {
      const response = await fetch('http://localhost:8000/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [
            ...chatHistory,
            { role: 'user', content: chatMessage }
          ],
          repo_name: `${username}/${repoName}`,
          use_rag: true
        }),
      });
      const data = await response.json();
      setChatHistory(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('Error sending chat message:', error);
    }
  };

  const handleGeneratePDF = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/github/repo/generate-project-docs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          owner: username,
          repo: repoName,
          branch: 'main'
        })
      });
      const data = await response.json();
      const pdfBlob = base64ToBlob(data.pdf, 'application/pdf');
      const url = window.URL.createObjectURL(pdfBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${repoName}-documentation.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error generating PDF:', error);
    }
  };

  const handleViewCodebaseMap = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/github/repo/generate-codebase-map`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          owner: username,
          repo: repoName,
          branch: 'main'
        })
      });
      const data = await response.json();
      const imageBlob = base64ToBlob(data.image, 'image/png');
      const url = window.URL.createObjectURL(imageBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${repoName}-codebase-map.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error generating codebase map:', error);
    }
  };

  const handleCopy = () => {
    if (repoDetails?.clone_url) {
      navigator.clipboard.writeText(repoDetails.clone_url);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }
  };

  const isImageFile = (filename: string) => {
    const imageExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'];
    return imageExtensions.some(ext => filename.toLowerCase().endsWith(ext));
  };

  const renderFileContent = () => {
    if (fileLoading) {
      return (
        <div className="flex-1 flex justify-center items-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
      );
    }

    if (!selectedFile) return null;

    if (isImageFile(selectedFile)) {
      return (
        <div className="flex-1 flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <button
              onClick={() => setViewMode('code')}
              className={`px-3 py-1 rounded transition-colors ${
                viewMode === 'code'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              View Code
            </button>
            <button
              onClick={() => setViewMode('image')}
              className={`px-3 py-1 rounded transition-colors ${
                viewMode === 'image'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              View Image
            </button>
          </div>
          {viewMode === 'code' ? (
            <div className="flex-1 bg-gray-50 rounded-lg p-4 overflow-auto">
              <pre className="text-sm text-gray-800 whitespace-pre-wrap">{fileContent}</pre>
            </div>
          ) : (
            <div className="flex-1 bg-gray-50 rounded-lg p-4 overflow-auto flex justify-center items-center">
              <img 
                src={`data:image/png;base64,${fileContent}`} 
                alt={selectedFile.split('/').pop() || 'Image'} 
                className="max-w-full max-h-full object-contain"
              />
            </div>
          )}
        </div>
      );
    }

    return (
      <div className="flex-1 bg-gray-50 rounded-lg p-4 overflow-auto">
        <pre className="text-sm text-gray-800 whitespace-pre-wrap">{fileContent}</pre>
      </div>
    );
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-[calc(100vh-8rem)] bg-black w-full min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="relative min-h-screen w-full flex flex-col items-center justify-center py-2 px-2">
        {/* Background Animation */}
        <div className="fixed inset-0 w-full h-full z-0 overflow-hidden">
          <img
            src={backGif}
            alt="Background Animation"
            className="absolute inset-0 w-full h-full object-cover object-center opacity-20"
            style={{ minWidth: '100%', minHeight: '100%' }}
          />
        </div>

        {/* Content */}
        <div className="relative z-10 w-full max-w-screen-2xl">
          {/* Top Row: Back button at far left, Repository Name centered */}
          <div className="w-full flex items-center mb-4 gap-2">
            <button
              onClick={() => navigate(-1)}
              className="group flex items-center justify-center w-[100px] h-[3em] bg-white/10 backdrop-blur-sm text-white font-bold transition-all duration-200 cursor-pointer border border-gray-800 hover:bg-white/20 hover:shadow-lg hover:-translate-y-1"
              style={{ borderRadius: '3px', letterSpacing: '1px' }}
            >
              <ArrowLeft className="mr-[5px] ml-[5px] text-[20px] transition-all duration-300 group-hover:-translate-x-1 group-hover:scale-110" />
              <span>Back</span>
            </button>
            <div className="flex-1 flex justify-center">
              <div className="font-bold text-4xl text-white text-center">
                {repoDetails?.name || 'Repository Name'}
              </div>
            </div>
            <div style={{ width: '100px' }} />
          </div>

          {/* Main Content: Files & Chat */}
          <div className="flex w-full gap-4 mb-4" style={{height: '480px'}}>
            {/* Left column: Clone Link Card above Files Card */}
            <div className="flex flex-col flex-1 min-w-0 h-full">
              {/* Clone Link Card */}
              <div className="bg-white/10 backdrop-blur-sm border border-gray-800 rounded-lg shadow p-4 mb-4 flex items-center gap-2 w-full">
                <span className="font-bold text-base text-white">Git repository clone link</span>
                <button
                  onClick={handleCopy}
                  className="relative flex items-center justify-center w-7 h-7"
                  aria-label="Copy to clipboard"
                  type="button"
                  style={{ background: 'none', border: 'none', padding: 0, cursor: 'pointer' }}
                >
                  {!copied ? (
                    <svg viewBox="0 0 384 512" height="20" width="20" fill="#fff" className="clipboard transition-all duration-200">
                      <path d="M280 64h40c35.3 0 64 28.7 64 64V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V128C0 92.7 28.7 64 64 64h40 9.6C121 27.5 153.3 0 192 0s71 27.5 78.4 64H280zM64 112c-8.8 0-16 7.2-16 16V448c0 8.8 7.2 16 16 16H320c8.8 0 16-7.2 16-16V128c0-8.8-7.2-16-16-16H304v24c0 13.3-10.7 24-24 24H192 104c-13.3 0-24-10.7-24-24V112H64zm128-8a24 24 0 1 0 0-48 24 24 0 1 0 0 48z"></path>
                    </svg>
                  ) : (
                    <svg viewBox="0 0 384 512" height="20" width="20" fill="#22c55e" className="clipboard-check transition-all duration-200">
                      <path d="M192 0c-41.8 0-77.4 26.7-90.5 64H64C28.7 64 0 92.7 0 128V448c0 35.3 28.7 64 64 64H320c35.3 0 64-28.7 64-64V128c0-35.3-28.7-64-64-64H282.5C269.4 26.7 233.8 0 192 0zm0 64a32 32 0 1 1 0 64 32 32 0 1 1 0-64zM305 273L177 401c-9.4 9.4-24.6 9.4-33.9 0L79 337c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l47 47L271 239c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9z"></path>
                    </svg>
                  )}
                </button>
                <span className="break-all text-xs text-gray-300 w-full">{repoDetails?.clone_url}</span>
              </div>

              {/* Repository Files Section */}
              <div className="bg-white/10 backdrop-blur-sm border border-gray-800 rounded-lg shadow-md p-6 mb-6 flex-1 flex flex-col min-h-0">
                <div className="font-bold mb-4 text-white text-base">Repository Files</div>
                {selectedFile ? (
                  <div className="flex-1 flex flex-col min-h-0">
                    <div className="flex items-center gap-2 mb-4">
                      <button
                        onClick={handleBackToFiles}
                        className="flex items-center gap-2 px-3 py-1 bg-white/10 text-white rounded hover:bg-white/20 transition-colors"
                      >
                        <ArrowLeft className="text-lg" />
                        Back to Files
                      </button>
                      <span className="text-gray-300">{selectedFile}</span>
                    </div>
                    {renderFileContent()}
                  </div>
                ) : (
                  <div className="flex-1 space-y-2 overflow-y-auto pr-2 [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-track]:bg-gray-900/50 [&::-webkit-scrollbar-thumb]:bg-gray-700 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb:hover]:bg-gray-600">
                    {fileTree.map((file, index) => (
                      <div
                        key={index}
                        onClick={() => handleFileClick(file)}
                        className={`flex items-center gap-2 p-2 rounded cursor-pointer hover:bg-white/10 transition-colors ${
                          file.type === 'directory' ? 'text-blue-400' : 'text-gray-300'
                        }`}
                      >
                        {file.type === 'directory' ? (
                          <Folder className="text-lg" />
                        ) : (
                          <File className="text-lg" />
                        )}
                        <span>{file.name}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Right column (Chat Bot) */}
            <div className="w-1/3 bg-white/10 backdrop-blur-sm border border-gray-800 rounded-lg shadow-md p-6 flex flex-col">
              <div className="font-bold mb-4 text-white text-base">Chat with Repository</div>
              <div className="flex-1 overflow-y-auto mb-4 space-y-4 [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-track]:bg-gray-900/50 [&::-webkit-scrollbar-thumb]:bg-gray-700 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb:hover]:bg-gray-600">
                {chatHistory.map((msg, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-white/20 ml-4'
                        : 'bg-white/10 mr-4'
                    }`}
                  >
                    <p className="text-white text-sm">{msg.content}</p>
                  </div>
                ))}
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  placeholder="Ask about the repository..."
                  className="flex-1 px-4 py-2 bg-white/10 border border-gray-800 rounded-lg focus:outline-none focus:border-white text-white placeholder-gray-400"
                />
                <button
                  onClick={handleChatSubmit}
                  className="px-4 py-2 bg-white text-black rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Send
                </button>
              </div>
            </div>
          </div>

          {/* Repository Description & Analysis */}
          <div className="w-full mt-4">
            <div className="bg-white/10 backdrop-blur-sm border border-gray-800 rounded-lg shadow p-6">
              <div className="font-bold mb-2 text-white text-base">Repository Description & Analysis</div>
              <div className="text-gray-300 text-sm whitespace-pre-line">{details}</div>
              <div className="flex items-center gap-2 mb-4 mt-4">
                <button
                  onClick={handleViewCodebaseMap}
                  className="flex items-center gap-2 px-4 py-2 bg-white text-black rounded hover:bg-gray-200 transition-colors"
                >
                  <Map className="text-lg" />
                  View Codebase Map
                </button>
                <button
                  onClick={handleGeneratePDF}
                  className="flex items-center gap-2 px-4 py-2 bg-white text-black rounded hover:bg-gray-200 transition-colors"
                >
                  <Download className="text-lg" />
                  Generate PDF
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default RepositoryView; 