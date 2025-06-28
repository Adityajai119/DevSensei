import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send } from 'lucide-react';
import axios from 'axios';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

const RepoSearchPage: React.FC = () => {
  const [input, setInput] = useState('');
  const [chat, setChat] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chat]);

  const handleSend = async () => {
    if (!input.trim()) return;
    setChat((prev) => [...prev, { role: 'user', content: input }]);
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post('/api/repo-search', { prompt: input });
      const aiMsg = res.data.response;
      const repos = res.data.repos;
      let repoLinks = '';
      if (repos && Array.isArray(repos)) {
        repoLinks = repos
          .map((r: any) => `<a href="${r.url}" target="_blank" rel="noopener noreferrer">${r.name}</a>: ${r.description || ''}`)
          .join('<br/>');
      }
      setChat((prev) => [
        ...prev,
        { role: 'assistant', content: aiMsg + (repoLinks ? '<br/><br/>' + repoLinks : '') },
      ]);
    } catch (e: any) {
      setError('Failed to fetch repositories.');
    } finally {
      setLoading(false);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-black text-white">
      <div className="max-w-2xl mx-auto w-full flex-1 flex flex-col py-8 px-4">
        <h1 className="text-3xl font-bold mb-6 text-center">Repo Search</h1>
        <div className="flex-1 overflow-y-auto mb-4 rounded-lg bg-white/5 p-4 border border-white/10 shadow-inner">
          {chat.length === 0 && (
            <div className="text-gray-400 text-center mt-12">Ask for GitHub repos by topic, e.g. "Give 5 repos of face recognition"</div>
          )}
          {chat.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`mb-6 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] px-4 py-3 rounded-2xl shadow-lg ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white self-end'
                    : 'bg-white/10 text-white border border-white/10 self-start'
                }`}
                dangerouslySetInnerHTML={{ __html: msg.content.replace(/\n/g, '<br/>') }}
              />
            </motion.div>
          ))}
          <div ref={chatEndRef} />
        </div>
        {error && <div className="text-red-400 text-center mb-2">{error}</div>}
        <div className="flex items-center gap-2 mt-2">
          <input
            className="flex-1 px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white focus:outline-none focus:border-purple-500 placeholder-gray-400"
            placeholder="Type your repo search prompt..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="p-3 rounded-lg bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 transition-all duration-300 disabled:opacity-50"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default RepoSearchPage; 