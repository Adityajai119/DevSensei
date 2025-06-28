import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Send, Code2, MessageSquare } from 'lucide-react';
import Button from '../components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../config/api';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const DoubtResolutionPage: React.FC = () => {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('javascript');
  const [context, setContext] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [explanation, setExplanation] = useState('');
  const [error, setError] = useState('');

  const languages = [
    'javascript', 'typescript', 'python', 'java', 'csharp',
    'cpp', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setExplanation('');

    try {
      const response = await axios.post(`${API_BASE_URL}${API_ENDPOINTS.gemini.explainCode}`, {
        code,
        language,
        context: context || undefined,
        gemini_api_key: localStorage.getItem('gemini_api_key') || undefined,
      });
      setExplanation(response.data.explanation);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'An error occurred while explaining the code');
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
            <div className="p-4 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl text-white">
              <Brain className="w-12 h-12" />
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="gradient-text">Doubt Resolution</span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Get instant AI-powered explanations for your code
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Code2 className="w-5 h-5" />
                  Your Code
                </CardTitle>
                <CardDescription>
                  Paste the code you want explained
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Programming Language
                    </label>
                    <select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      aria-label="Select programming language"
                      className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-dark-800 focus:ring-2 focus:ring-primary-500"
                    >
                      {languages.map(lang => (
                        <option key={lang} value={lang}>
                          {lang.charAt(0).toUpperCase() + lang.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Code Snippet
                    </label>
                    <textarea
                      value={code}
                      onChange={(e) => setCode(e.target.value)}
                      className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-dark-800 focus:ring-2 focus:ring-primary-500 font-mono text-sm"
                      rows={10}
                      placeholder="Paste your code here..."
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Additional Context (Optional)
                    </label>
                    <input
                      type="text"
                      value={context}
                      onChange={(e) => setContext(e.target.value)}
                      className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-dark-800 focus:ring-2 focus:ring-primary-500"
                      placeholder="e.g., This is a React component..."
                    />
                  </div>
                  <Button
                    type="submit"
                    className="w-full"
                    isLoading={isLoading}
                    icon={<Send className="w-4 h-4" />}
                  >
                    Explain Code
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

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="w-5 h-5" />
                  AI Explanation
                </CardTitle>
                <CardDescription>
                  Understanding your code made simple
                </CardDescription>
              </CardHeader>
              <CardContent>
                {explanation ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="space-y-4"
                  >
                    <div className="prose dark:prose-invert max-w-none">
                      <div className="whitespace-pre-wrap">{explanation}</div>
                    </div>
                    {code && (
                      <div className="mt-6">
                        <h4 className="font-medium mb-2">Highlighted Code:</h4>
                        <div className="rounded-lg overflow-hidden">
                          <SyntaxHighlighter
                            language={language}
                            style={vscDarkPlus}
                            customStyle={{
                              margin: 0,
                              borderRadius: '0.5rem',
                            }}
                          >
                            {code}
                          </SyntaxHighlighter>
                        </div>
                      </div>
                    )}
                  </motion.div>
                ) : (
                  <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                    <Brain className="w-16 h-16 mx-auto mb-4 opacity-20" />
                    <p>Paste your code and click "Explain Code" to get started</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default DoubtResolutionPage; 