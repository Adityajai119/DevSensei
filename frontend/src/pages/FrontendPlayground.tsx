import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Code, Play, Loader2, Layout } from 'lucide-react';
import { codeApi } from '../services/api';

interface Framework {
  id: string;
  name: string;
  icon: string;
}

const frameworks: Framework[] = [
  { id: 'vanilla', name: 'Vanilla JS', icon: '🟨' },
  { id: 'react', name: 'React', icon: '⚛️' },
  { id: 'vue', name: 'Vue.js', icon: '💚' },
  { id: 'angular', name: 'Angular', icon: '🔴' },
];

export const FrontendPlayground: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [framework, setFramework] = useState('vanilla');
  const [generatedCode, setGeneratedCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [error, setError] = useState('');

  const generateFrontendCode = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setError('');
    try {
      const result = await codeApi.generateFrontend(prompt, framework);
      setGeneratedCode(result.code);
      setShowPreview(true);
    } catch (err) {
      setError('Failed to generate frontend code');
    } finally {
      setLoading(false);
    }
  };

  const runCode = () => {
    if (framework === 'vanilla' && generatedCode) {
      // For vanilla JS, we can run it directly in an iframe
      setShowPreview(true);
    } else {
      setError('Live preview is currently only available for Vanilla JS');
    }
  };

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-7xl mx-auto"
      >
        <h1 className="text-4xl font-bold mb-8 text-center text-white">
          Frontend AI Playground
        </h1>

        {/* Prompt Input */}
        <div className="mb-6">
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">What would you like to build?</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe your frontend project... (e.g., Create a flappy bird game with score tracking)"
              className="w-full h-24 px-4 py-2 bg-gray-900 border border-gray-800 rounded-lg focus:outline-none focus:border-white"
            />
          </div>

          {/* Framework Selection */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Choose Framework</label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {frameworks.map((fw) => (
                <button
                  key={fw.id}
                  onClick={() => setFramework(fw.id)}
                  className={`p-3 rounded-lg border transition-all ${
                    framework === fw.id
                      ? 'bg-white text-black border-white'
                      : 'bg-gray-900 border-gray-800 hover:border-gray-700'
                  }`}
                >
                  <span className="text-2xl mr-2">{fw.icon}</span>
                  {fw.name}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={generateFrontendCode}
            disabled={loading || !prompt.trim()}
            className="w-full px-6 py-3 bg-white text-black hover:bg-gray-200 rounded-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50"
          >
            {loading ? <Loader2 className="animate-spin" /> : <Code />}
            Generate Frontend Code
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-900/50 border border-red-800 rounded-lg">
            {error}
          </div>
        )}

        {/* Generated Code and Preview */}
        {generatedCode && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Code View */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-4"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Generated Code</h2>
                <button
                  onClick={runCode}
                  className="px-4 py-2 bg-white text-black hover:bg-gray-200 rounded-lg flex items-center gap-2"
                >
                  <Play size={16} />
                  Run
                </button>
              </div>
              
              <div className="h-[600px] bg-gray-900 rounded-lg border border-gray-800 overflow-auto">
                <pre className="p-4 text-sm">
                  <code className="language-html">{generatedCode}</code>
                </pre>
              </div>
            </motion.div>

            {/* Preview */}
            {showPreview && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-4"
              >
                <div className="flex items-center gap-2">
                  <Layout />
                  <h2 className="text-xl font-semibold">Live Preview</h2>
                </div>
                
                <div className="h-[600px] bg-white rounded-lg border border-gray-800 overflow-hidden">
                  <iframe
                    srcDoc={generatedCode}
                    className="w-full h-full"
                    title="Preview"
                    sandbox="allow-scripts allow-same-origin"
                  />
                </div>
              </motion.div>
            )}
          </div>
        )}

        {/* Examples */}
        <div className="mt-12">
          <h3 className="text-lg font-semibold mb-4">Example Prompts</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              "Create a flappy bird game with score tracking",
              "Build a todo list app with add, delete, and mark complete features",
              "Design a modern landing page for a tech startup",
              "Create an interactive calculator with a beautiful UI",
              "Build a memory card game with flip animations",
              "Design a weather dashboard with animated icons"
            ].map((example, idx) => (
              <button
                key={idx}
                onClick={() => setPrompt(example)}
                className="p-3 bg-gray-900 hover:bg-gray-800 border border-gray-800 rounded-lg text-left text-sm transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}; 