import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Play, 
  Code2, 
  Sparkles, 
  Bug, 
  Zap, 
  FileText,
  Loader2,
  Copy,
  Download,
  Settings
} from 'lucide-react'
import { useQuery } from 'react-query'
import toast from 'react-hot-toast'
import CodeEditor from '../components/CodeEditor'
import { codeService } from '../services/api'

const CodePlayground = () => {
  const [activeTab, setActiveTab] = useState<'generate' | 'execute' | 'explain' | 'debug' | 'optimize'>('generate')
  const [code, setCode] = useState('')
  const [language, setLanguage] = useState('python')
  const [input, setInput] = useState('')
  const [output, setOutput] = useState('')
  const [prompt, setPrompt] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Get supported languages
  const { data: supportedLanguages } = useQuery(
    'supported-languages',
    () => codeService.getSupportedLanguages(),
    {
      onError: () => {
        toast.error('Failed to fetch supported languages')
      }
    }
  )

  const tabs = [
    { id: 'generate', label: 'Generate', icon: Sparkles, color: 'text-purple-400' },
    { id: 'execute', label: 'Run', icon: Play, color: 'text-green-400' },
    { id: 'explain', label: 'Explain', icon: FileText, color: 'text-blue-400' },
    { id: 'debug', label: 'Debug', icon: Bug, color: 'text-red-400' },
    { id: 'optimize', label: 'Optimize', icon: Zap, color: 'text-yellow-400' },
  ]

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a description')
      return
    }

    setIsLoading(true)
    try {
      const response = await codeService.generateCode({
        prompt,
        language,
        context: ''
      })
      setCode(response.code)
      setOutput(`Generated ${language} code:\n\n${response.description}`)
      toast.success('Code generated successfully!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to generate code')
    } finally {
      setIsLoading(false)
    }
  }

  const handleExecute = async () => {
    if (!code.trim()) {
      toast.error('Please enter some code to execute')
      return
    }

    setIsLoading(true)
    try {
      const response = await codeService.executeCode({
        code,
        language,
        input_data: input
      })
      
      let outputText = ''
      if (response.output) {
        outputText += `Output:\n${response.output}\n\n`
      }
      if (response.error) {
        outputText += `Errors:\n${response.error}\n\n`
      }
      outputText += `Execution time: ${response.execution_time}s\n`
      outputText += `Status: ${response.status}`
      
      setOutput(outputText)
      
      if (response.status === 'success') {
        toast.success('Code executed successfully!')
      } else {
        toast.error('Code execution failed')
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to execute code')
    } finally {
      setIsLoading(false)
    }
  }

  const handleExplain = async () => {
    if (!code.trim()) {
      toast.error('Please enter some code to explain')
      return
    }

    setIsLoading(true)
    try {
      const response = await codeService.explainCode(code, language)
      setOutput(response.explanation)
      toast.success('Code explanation generated!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to explain code')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDebug = async () => {
    if (!code.trim()) {
      toast.error('Please enter some code to debug')
      return
    }

    setIsLoading(true)
    try {
      const response = await codeService.debugCode({
        code,
        language,
        error_message: '',
        expected_output: ''
      })
      setCode(response.fixed_code)
      setOutput(`Debug Report:\n\n${response.explanation}`)
      toast.success('Code debugged successfully!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to debug code')
    } finally {
      setIsLoading(false)
    }
  }

  const handleOptimize = async () => {
    if (!code.trim()) {
      toast.error('Please enter some code to optimize')
      return
    }

    setIsLoading(true)
    try {
      const response = await codeService.optimizeCode({
        code,
        language,
        optimization_type: 'performance'
      })
      setCode(response.optimized_code)
      setOutput(`Optimization Report:\n\n${response.explanation}`)
      toast.success('Code optimized successfully!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to optimize code')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAction = () => {
    switch (activeTab) {
      case 'generate':
        handleGenerate()
        break
      case 'execute':
        handleExecute()
        break
      case 'explain':
        handleExplain()
        break
      case 'debug':
        handleDebug()
        break
      case 'optimize':
        handleOptimize()
        break
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard!')
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Code Playground
          </h1>
          <p className="text-xl text-secondary-300 max-w-2xl mx-auto">
            Execute, debug, and optimize code in multiple languages with AI assistance
          </p>
        </motion.div>

        {/* Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card mb-6"
        >
          <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
            {/* Language Selector */}
            <div className="flex items-center space-x-4">
              <label className="text-sm font-medium text-secondary-300">Language:</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="select w-40"
              >
                {supportedLanguages?.languages.map((lang: string) => (
                  <option key={lang} value={lang}>
                    {lang.charAt(0).toUpperCase() + lang.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Action Tabs */}
            <div className="flex flex-wrap gap-2">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`btn text-sm ${
                      activeTab === tab.id
                        ? 'btn-primary'
                        : 'btn-outline'
                    }`}
                  >
                    <Icon className={`h-4 w-4 ${tab.color}`} />
                    <span className="ml-2">{tab.label}</span>
                  </button>
                )
              })}
            </div>
          </div>
        </motion.div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Panel - Code Editor */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="space-y-4"
          >
            {/* Prompt Input (for Generate tab) */}
            {activeTab === 'generate' && (
              <div className="card">
                <label className="block text-sm font-medium text-secondary-300 mb-2">
                  Describe what you want to build:
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="e.g., Create a function that calculates the factorial of a number"
                  className="textarea h-24"
                />
              </div>
            )}

            {/* Input Data (for Execute tab) */}
            {activeTab === 'execute' && (
              <div className="card">
                <label className="block text-sm font-medium text-secondary-300 mb-2">
                  Input Data (optional):
                </label>
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Enter input data for your program..."
                  className="textarea h-20"
                />
              </div>
            )}

            {/* Code Editor */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <Code2 className="h-5 w-5 mr-2 text-primary-400" />
                  Code Editor
                </h3>
                <div className="flex space-x-2">
                  <button
                    onClick={() => copyToClipboard(code)}
                    className="p-2 text-secondary-400 hover:text-white transition-colors"
                    title="Copy code"
                  >
                    <Copy className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      const blob = new Blob([code], { type: 'text/plain' })
                      const url = URL.createObjectURL(blob)
                      const a = document.createElement('a')
                      a.href = url
                      a.download = `code.${language}`
                      a.click()
                      URL.revokeObjectURL(url)
                    }}
                    className="p-2 text-secondary-400 hover:text-white transition-colors"
                    title="Download code"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <CodeEditor
                value={code}
                onChange={setCode}
                language={language}
                height="400px"
              />
            </div>

            {/* Action Button */}
            <button
              onClick={handleAction}
              disabled={isLoading}
              className="btn-primary w-full text-lg py-3"
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                tabs.find(tab => tab.id === activeTab)?.icon && 
                React.createElement(tabs.find(tab => tab.id === activeTab)!.icon, { className: "h-5 w-5" })
              )}
              <span className="ml-2">
                {isLoading ? 'Processing...' : tabs.find(tab => tab.id === activeTab)?.label}
              </span>
            </button>
          </motion.div>

          {/* Right Panel - Output */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="card"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">
                Output
              </h3>
              {output && (
                <button
                  onClick={() => copyToClipboard(output)}
                  className="p-2 text-secondary-400 hover:text-white transition-colors"
                  title="Copy output"
                >
                  <Copy className="h-4 w-4" />
                </button>
              )}
            </div>
            <div className="bg-secondary-900 border border-secondary-700 rounded-lg p-4 h-96 overflow-auto">
              {output ? (
                <pre className="text-secondary-100 text-sm whitespace-pre-wrap font-mono">
                  {output}
                </pre>
              ) : (
                <div className="flex items-center justify-center h-full text-secondary-500">
                  <div className="text-center">
                    <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Output will appear here</p>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Examples Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="mt-12"
        >
          <h2 className="text-2xl font-bold text-white mb-6">Example Prompts</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              'Create a function to sort an array using quicksort algorithm',
              'Build a simple calculator with basic operations',
              'Generate a REST API endpoint for user authentication',
              'Create a binary search tree implementation',
              'Build a web scraper for extracting data from websites',
              'Generate a machine learning model for classification'
            ].map((example, index) => (
              <motion.button
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 * index }}
                onClick={() => setPrompt(example)}
                className="card text-left hover:border-primary-500/50 transition-all duration-300 cursor-pointer"
              >
                <p className="text-secondary-300 text-sm">{example}</p>
              </motion.button>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default CodePlayground