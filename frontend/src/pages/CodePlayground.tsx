import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Loader2, Code, Bug, Zap, MessageSquare } from 'lucide-react';
import Editor from '@monaco-editor/react';
import { codeApi } from '../services/api';

interface Language {
  id: string;
  name: string;
  monacoId: string;
}

const languageMap: Record<string, Language> = {
  python: { id: 'python', name: 'Python', monacoId: 'python' },
  javascript: { id: 'javascript', name: 'JavaScript', monacoId: 'javascript' },
  typescript: { id: 'typescript', name: 'TypeScript', monacoId: 'typescript' },
  java: { id: 'java', name: 'Java', monacoId: 'java' },
  cpp: { id: 'cpp', name: 'C++', monacoId: 'cpp' },
  c: { id: 'c', name: 'C', monacoId: 'c' },
  go: { id: 'go', name: 'Go', monacoId: 'go' },
  rust: { id: 'rust', name: 'Rust', monacoId: 'rust' },
  ruby: { id: 'ruby', name: 'Ruby', monacoId: 'ruby' },
  php: { id: 'php', name: 'PHP', monacoId: 'php' },
};

export const CodePlayground: React.FC = () => {
  const [code, setCode] = useState('# Write your code here\nprint("Hello, World!")');
  const [language, setLanguage] = useState('python');
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [showExplanation, setShowExplanation] = useState(false);
  const [explanation, setExplanation] = useState('');

  const executeCode = async () => {
    setLoading(true);
    setError('');
    setOutput('');
    
    try {
      const result = await codeApi.execute(code, language, input);
      setOutput(result.output);
      setError(result.error);
    } catch {
      setError('Failed to execute code');
    } finally {
      setLoading(false);
    }
  };

  const generateCode = async () => {
    if (!prompt.trim()) return;
    
    setLoading(true);
    try {
      const result = await codeApi.generate(prompt, language);
      setCode(result.code);
      setPrompt('');
    } catch {
      setError('Failed to generate code');
    } finally {
      setLoading(false);
    }
  };

  const explainCode = async () => {
    setLoading(true);
    try {
      const result = await codeApi.explain(code, language);
      setExplanation(result.explanation);
      setShowExplanation(true);
    } catch {
      setError('Failed to explain code');
    } finally {
      setLoading(false);
    }
  };

  const debugCode = async () => {
    setLoading(true);
    try {
      const result = await codeApi.debug(code, language, error);
      setCode(result.fixed_code);
      if (result.explanation) {
        setExplanation(result.explanation);
        setShowExplanation(true);
      }
    } catch {
      setError('Failed to debug code');
    } finally {
      setLoading(false);
    }
  };

  const optimizeCode = async () => {
    setLoading(true);
    try {
      const result = await codeApi.optimize(code, language);
      setCode(result.optimized_code);
      if (result.explanation) {
        setExplanation(result.explanation);
        setShowExplanation(true);
      }
    } catch {
      setError('Failed to optimize code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-7xl mx-auto"
      >
        <h1 className="text-4xl font-bold mb-8 text-center bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          Code Playground
        </h1>

        {/* Code Generation Prompt */}
        <div className="mb-6">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Describe what code you want to generate..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && generateCode()}
              className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-purple-500"
            />
            <button
              onClick={generateCode}
              disabled={loading || !prompt.trim()}
              className="px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50"
            >
              <Code size={20} />
              Generate
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Code Editor */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Code Editor</h2>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none"
                title="Select programming language"
              >
                {Object.values(languageMap).map((lang) => (
                  <option key={lang.id} value={lang.id}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="h-96 rounded-lg overflow-hidden border border-gray-700">
              <Editor
                height="100%"
                theme="vs-dark"
                language={languageMap[language].monacoId}
                value={code}
                onChange={(value: string | undefined) => setCode(value || '')}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  wordWrap: 'on',
                }}
              />
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <button
                onClick={executeCode}
                disabled={loading}
                className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg flex items-center justify-center gap-2 transition-colors"
              >
                {loading ? <Loader2 className="animate-spin" size={20} /> : <Play size={20} />}
                Run
              </button>
              <button
                onClick={explainCode}
                disabled={loading}
                className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center justify-center gap-2 transition-colors"
              >
                <MessageSquare size={20} />
                Explain
              </button>
              <button
                onClick={debugCode}
                disabled={loading || !error}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                <Bug size={20} />
                Debug
              </button>
              <button
                onClick={optimizeCode}
                disabled={loading}
                className="flex-1 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded-lg flex items-center justify-center gap-2 transition-colors"
              >
                <Zap size={20} />
                Optimize
              </button>
            </div>

            {/* Input */}
            <div>
              <h3 className="text-sm font-medium mb-2 text-gray-400">Input</h3>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Enter input for your program..."
                className="w-full h-24 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-purple-500 font-mono text-sm"
              />
            </div>
          </div>

          {/* Output and Explanation */}
          <div className="space-y-4">
            {/* Output */}
            <div>
              <h2 className="text-xl font-semibold mb-4">Output</h2>
              <div className="h-48 p-4 bg-gray-900 rounded-lg border border-gray-700 overflow-auto">
                {output && (
                  <pre className="text-green-400 font-mono text-sm whitespace-pre-wrap">{output}</pre>
                )}
                {error && (
                  <pre className="text-red-400 font-mono text-sm whitespace-pre-wrap">{error}</pre>
                )}
                {!output && !error && !loading && (
                  <p className="text-gray-500">Output will appear here...</p>
                )}
                {loading && (
                  <div className="flex items-center gap-2 text-gray-400">
                    <Loader2 className="animate-spin" size={16} />
                    Processing...
                  </div>
                )}
              </div>
            </div>

            {/* Explanation */}
            {showExplanation && explanation && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="flex items-center justify-between mb-2">
                  <h2 className="text-xl font-semibold">Explanation</h2>
                  <button
                    onClick={() => setShowExplanation(false)}
                    className="text-gray-400 hover:text-white"
                  >
                    ✕
                  </button>
                </div>
                <div className="h-64 p-4 bg-gray-900 rounded-lg border border-gray-700 overflow-auto">
                  <div className="prose prose-invert max-w-none">
                    <pre className="whitespace-pre-wrap text-sm">{explanation}</pre>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}; 