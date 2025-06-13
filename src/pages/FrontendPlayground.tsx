import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Palette, 
  Eye, 
  Code2, 
  Sparkles, 
  Download,
  Loader2,
  Copy,
  RefreshCw,
  Monitor,
  Smartphone,
  Tablet
} from 'lucide-react'
import toast from 'react-hot-toast'
import CodeEditor from '../components/CodeEditor'

const FrontendPlayground = () => {
  const [prompt, setPrompt] = useState('')
  const [framework, setFramework] = useState('vanilla')
  const [htmlCode, setHtmlCode] = useState('')
  const [cssCode, setCssCode] = useState('')
  const [jsCode, setJsCode] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [activeTab, setActiveTab] = useState<'html' | 'css' | 'js'>('html')
  const [previewMode, setPreviewMode] = useState<'desktop' | 'tablet' | 'mobile'>('desktop')

  const frameworks = [
    { value: 'vanilla', label: 'Vanilla JS' },
    { value: 'react', label: 'React' },
    { value: 'vue', label: 'Vue.js' },
    { value: 'angular', label: 'Angular' }
  ]

  const examples = [
    'Create a modern landing page with hero section and features',
    'Build a todo list application with add/remove functionality',
    'Design a responsive navigation menu with dropdown',
    'Create a image gallery with lightbox effect',
    'Build a contact form with validation',
    'Design a pricing table with hover effects',
    'Create a dashboard with charts and metrics',
    'Build a blog layout with sidebar',
    'Design a portfolio website',
    'Create a weather app interface'
  ]

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a description')
      return
    }

    setIsGenerating(true)
    try {
      // Simulate API call - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Generate sample code based on prompt
      const sampleHTML = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated App</title>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>Welcome to Your App</h1>
            <p>Generated from: ${prompt}</p>
        </header>
        <main class="main">
            <div class="card">
                <h2>Feature Section</h2>
                <p>This is a sample generated based on your prompt.</p>
                <button class="btn" onclick="handleClick()">Click Me</button>
            </div>
        </main>
    </div>
</body>
</html>`

      const sampleCSS = `* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

.header {
    text-align: center;
    margin-bottom: 3rem;
    color: white;
}

.header h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.main {
    display: flex;
    justify-content: center;
    align-items: center;
}

.card {
    background: white;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    text-align: center;
    max-width: 400px;
    transform: translateY(0);
    transition: transform 0.3s ease;
}

.card:hover {
    transform: translateY(-10px);
}

.card h2 {
    color: #667eea;
    margin-bottom: 1rem;
}

.btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 25px;
    cursor: pointer;
    font-size: 1rem;
    margin-top: 1rem;
    transition: transform 0.2s ease;
}

.btn:hover {
    transform: scale(1.05);
}

@media (max-width: 768px) {
    .container {
        padding: 1rem;
    }
    
    .header h1 {
        font-size: 2rem;
    }
    
    .card {
        padding: 1.5rem;
    }
}`

      const sampleJS = `function handleClick() {
    alert('Button clicked! This is generated JavaScript.');
    
    // Add some interactive behavior
    const card = document.querySelector('.card');
    card.style.background = '#f0f8ff';
    
    setTimeout(() => {
        card.style.background = 'white';
    }, 1000);
}

// Add some dynamic content
document.addEventListener('DOMContentLoaded', function() {
    console.log('App loaded successfully!');
    
    // Animate elements on load
    const card = document.querySelector('.card');
    card.style.opacity = '0';
    card.style.transform = 'translateY(50px)';
    
    setTimeout(() => {
        card.style.transition = 'all 0.5s ease';
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
    }, 100);
});`

      setHtmlCode(sampleHTML)
      setCssCode(sampleCSS)
      setJsCode(sampleJS)
      
      toast.success('Frontend code generated successfully!')
    } catch (error) {
      toast.error('Failed to generate code')
    } finally {
      setIsGenerating(false)
    }
  }

  const getPreviewCode = () => {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview</title>
    <style>${cssCode}</style>
</head>
<body>
    ${htmlCode.replace(/<html[^>]*>|<\/html>|<head[^>]*>[\s\S]*?<\/head>|<body[^>]*>|<\/body>/gi, '')}
    <script>${jsCode}</script>
</body>
</html>`
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard!')
  }

  const downloadProject = () => {
    const zip = {
      'index.html': htmlCode,
      'styles.css': cssCode,
      'script.js': jsCode
    }
    
    // Create download links for each file
    Object.entries(zip).forEach(([filename, content]) => {
      const blob = new Blob([content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      URL.revokeObjectURL(url)
    })
    
    toast.success('Project files downloaded!')
  }

  const getPreviewWidth = () => {
    switch (previewMode) {
      case 'mobile': return '375px'
      case 'tablet': return '768px'
      default: return '100%'
    }
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
            Frontend AI Playground
          </h1>
          <p className="text-xl text-secondary-300 max-w-2xl mx-auto">
            Generate beautiful frontend applications with live preview and AI guidance
          </p>
        </motion.div>

        {/* Generation Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card mb-6"
        >
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 items-end">
            <div className="lg:col-span-2">
              <label className="block text-sm font-medium text-secondary-300 mb-2">
                Describe your frontend project:
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="e.g., Create a modern landing page with hero section and features"
                className="textarea h-20"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary-300 mb-2">
                Framework:
              </label>
              <select
                value={framework}
                onChange={(e) => setFramework(e.target.value)}
                className="select"
              >
                {frameworks.map((fw) => (
                  <option key={fw.value} value={fw.value}>
                    {fw.label}
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="btn-primary h-fit"
            >
              {isGenerating ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Sparkles className="h-5 w-5" />
              )}
              <span className="ml-2">
                {isGenerating ? 'Generating...' : 'Generate'}
              </span>
            </button>
          </div>
        </motion.div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Code Editor Panel */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="space-y-4"
          >
            {/* Code Tabs */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <div className="flex space-x-2">
                  {[
                    { id: 'html', label: 'HTML', color: 'text-orange-400' },
                    { id: 'css', label: 'CSS', color: 'text-blue-400' },
                    { id: 'js', label: 'JavaScript', color: 'text-yellow-400' }
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                        activeTab === tab.id
                          ? 'bg-primary-600 text-white'
                          : 'text-secondary-300 hover:text-white hover:bg-secondary-700'
                      }`}
                    >
                      <span className={tab.color}>●</span>
                      <span className="ml-2">{tab.label}</span>
                    </button>
                  ))}
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => {
                      const code = activeTab === 'html' ? htmlCode : activeTab === 'css' ? cssCode : jsCode
                      copyToClipboard(code)
                    }}
                    className="p-2 text-secondary-400 hover:text-white transition-colors"
                    title="Copy code"
                  >
                    <Copy className="h-4 w-4" />
                  </button>
                  <button
                    onClick={downloadProject}
                    className="p-2 text-secondary-400 hover:text-white transition-colors"
                    title="Download project"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <CodeEditor
                value={
                  activeTab === 'html' ? htmlCode :
                  activeTab === 'css' ? cssCode : jsCode
                }
                onChange={(value) => {
                  if (activeTab === 'html') setHtmlCode(value)
                  else if (activeTab === 'css') setCssCode(value)
                  else setJsCode(value)
                }}
                language={activeTab === 'js' ? 'javascript' : activeTab}
                height="500px"
              />
            </div>
          </motion.div>

          {/* Preview Panel */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="card"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                <Eye className="h-5 w-5 mr-2 text-primary-400" />
                Live Preview
              </h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setPreviewMode('desktop')}
                  className={`p-2 rounded transition-colors ${
                    previewMode === 'desktop' ? 'bg-primary-600 text-white' : 'text-secondary-400 hover:text-white'
                  }`}
                  title="Desktop view"
                >
                  <Monitor className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setPreviewMode('tablet')}
                  className={`p-2 rounded transition-colors ${
                    previewMode === 'tablet' ? 'bg-primary-600 text-white' : 'text-secondary-400 hover:text-white'
                  }`}
                  title="Tablet view"
                >
                  <Tablet className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setPreviewMode('mobile')}
                  className={`p-2 rounded transition-colors ${
                    previewMode === 'mobile' ? 'bg-primary-600 text-white' : 'text-secondary-400 hover:text-white'
                  }`}
                  title="Mobile view"
                >
                  <Smartphone className="h-4 w-4" />
                </button>
              </div>
            </div>

            <div className="bg-white rounded-lg overflow-hidden" style={{ height: '500px' }}>
              {htmlCode ? (
                <div className="flex justify-center h-full">
                  <iframe
                    srcDoc={getPreviewCode()}
                    style={{ 
                      width: getPreviewWidth(),
                      height: '100%',
                      border: 'none',
                      transition: 'width 0.3s ease'
                    }}
                    title="Preview"
                  />
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-secondary-500">
                  <div className="text-center">
                    <Palette className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Generate code to see preview</p>
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
          <h2 className="text-2xl font-bold text-white mb-6">Example Projects</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {examples.map((example, index) => (
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

export default FrontendPlayground