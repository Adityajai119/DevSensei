import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Code, Wand2, Copy, Download, Play } from 'lucide-react';
import Button from '../components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../config/api';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const CodeBuilderPage: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [language, setLanguage] = useState('javascript');
  const [framework, setFramework] = useState('');
  const [requirements, setRequirements] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');
  const [explanation, setExplanation] = useState('');
  const [error, setError] = useState('');

  const languages = [
    'javascript', 'typescript', 'python', 'java', 'csharp',
    'cpp', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin'
  ];

  const frameworks = {
    javascript: ['React', 'Vue', 'Angular', 'Express', 'Next.js'],
    typescript: ['React', 'Vue', 'Angular', 'Express', 'Next.js', 'Nest.js'],
    python: ['Django', 'FastAPI', 'Flask', 'PyTorch', 'TensorFlow'],
    java: ['Spring Boot', 'Spring', 'Hibernate', 'JavaFX'],
    csharp: ['ASP.NET Core', '.NET', 'Unity', 'Xamarin'],
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setGeneratedCode('');
    setExplanation('');

    try {
      const requirementsList = requirements
        .split('\n')
        .map(r => r.trim())
        .filter(r => r);

      const response = await axios.post(`${API_BASE_URL}${API_ENDPOINTS.code.generate}`, {
        prompt,
        language,
        framework: framework || undefined,
        requirements: requirementsList.length > 0 ? requirementsList : undefined,
        gemini_api_key: localStorage.getItem('gemini_api_key') || undefined,
      });

      setGeneratedCode(response.data.generated_code);
      setExplanation(response.data.explanation);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'An error occurred while generating code');
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedCode);
  };

  const downloadCode = () => {
    const blob = new Blob([generatedCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `generated-code.${language}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
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
            <div className="p-4 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl text-white">
              <Code className="w-12 h-12" />
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="gradient-text">Code Builder</span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Generate production-ready code from natural language descriptions
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
                  <Wand2 className="w-5 h-5" />
                  Code Generation
                </CardTitle>
                <CardDescription>
                  Describe what you want to build
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      What do you want to build?
                    </label>
                    <textarea
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-dark-800 focus:ring-2 focus:ring-primary-500"
                      rows={4}
                      placeholder="e.g., Create a REST API endpoint for user authentication with JWT tokens"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Language
                      </label>
                      <select
                        value={language}
                        onChange={(e) => {
                          setLanguage(e.target.value);
                          setFramework('');
                        }}
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
                        Framework (Optional)
                      </label>
                      <select
                        value={framework}
                        onChange={(e) => setFramework(e.target.value)}
                        aria-label="Select framework"
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-dark-800 focus:ring-2 focus:ring-primary-500"
                      >
                        <option value="">None</option>
                        {frameworks[language as keyof typeof frameworks]?.map(fw => (
                          <option key={fw} value={fw}>
                            {fw}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Requirements (Optional - one per line)
                    </label>
                    <textarea
                      value={requirements}
                      onChange={(e) => setRequirements(e.target.value)}
                      className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-dark-800 focus:ring-2 focus:ring-primary-500"
                      rows={3}
                      placeholder="Add error handling&#10;Use async/await&#10;Include type definitions"
                    />
                  </div>
                  <Button
                    type="submit"
                    className="w-full"
                    isLoading={isLoading}
                    icon={<Wand2 className="w-4 h-4" />}
                  >
                    Generate Code
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
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Code className="w-5 h-5" />
                    Generated Code
                  </span>
                  {generatedCode && (
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={copyToClipboard}
                        icon={<Copy className="w-4 h-4" />}
                      >
                        Copy
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={downloadCode}
                        icon={<Download className="w-4 h-4" />}
                      >
                        Download
                      </Button>
                    </div>
                  )}
                </CardTitle>
                <CardDescription>
                  Your AI-generated code
                </CardDescription>
              </CardHeader>
              <CardContent>
                {generatedCode ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="space-y-4"
                  >
                    <div className="rounded-lg overflow-hidden">
                      <SyntaxHighlighter
                        language={language}
                        style={vscDarkPlus}
                        customStyle={{
                          margin: 0,
                          borderRadius: '0.5rem',
                          maxHeight: '400px',
                        }}
                      >
                        {generatedCode}
                      </SyntaxHighlighter>
                    </div>
                    {explanation && (
                      <div className="mt-6">
                        <h4 className="font-medium mb-2">Explanation:</h4>
                        <div className="prose dark:prose-invert max-w-none">
                          <div className="whitespace-pre-wrap text-sm">{explanation}</div>
                        </div>
                      </div>
                    )}
                  </motion.div>
                ) : (
                  <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                    <Code className="w-16 h-16 mx-auto mb-4 opacity-20" />
                    <p>Generated code will appear here</p>
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

export default CodeBuilderPage; 