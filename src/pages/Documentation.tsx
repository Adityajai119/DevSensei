import React from 'react'
import { motion } from 'framer-motion'
import { 
  BookOpen, 
  Code2, 
  GitBranch, 
  Play, 
  Palette, 
  Zap, 
  Brain,
  MessageSquare,
  FileText,
  ExternalLink,
  ArrowRight
} from 'lucide-react'

const Documentation = () => {
  const sections = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      icon: Zap,
      content: [
        {
          title: 'Quick Start',
          description: 'Get up and running with DevSensei in minutes',
          items: [
            'Navigate to any feature from the main menu',
            'No setup required - everything runs in your browser',
            'Start with the Repository Explorer to analyze GitHub repos',
            'Try the Code Playground for instant code execution'
          ]
        }
      ]
    },
    {
      id: 'repository-explorer',
      title: 'Repository Explorer',
      icon: GitBranch,
      content: [
        {
          title: 'Analyzing Repositories',
          description: 'Explore and understand GitHub repositories with AI assistance',
          items: [
            'Enter any GitHub username to browse their repositories',
            'Select a repository to view detailed information',
            'Generate comprehensive PDF documentation',
            'Chat with the codebase using AI-powered analysis'
          ]
        },
        {
          title: 'Documentation Generation',
          description: 'Create professional documentation automatically',
          items: [
            'Setup instructions and requirements',
            'Architecture overview and design patterns',
            'Visual codebase maps and relationships',
            'API documentation and endpoints'
          ]
        }
      ]
    },
    {
      id: 'code-playground',
      title: 'Code Playground',
      icon: Play,
      content: [
        {
          title: 'Multi-Language Support',
          description: 'Execute code in multiple programming languages',
          items: [
            'Python, JavaScript, TypeScript, Java, C++, Go, Rust',
            'Real-time code execution with instant feedback',
            'Input/output handling for interactive programs',
            'Syntax highlighting and error detection'
          ]
        },
        {
          title: 'AI-Powered Features',
          description: 'Enhance your coding with AI assistance',
          items: [
            'Generate: Create code from natural language descriptions',
            'Explain: Get detailed explanations of code functionality',
            'Debug: Identify and fix bugs automatically',
            'Optimize: Improve code performance and readability'
          ]
        }
      ]
    },
    {
      id: 'frontend-playground',
      title: 'Frontend AI Playground',
      icon: Palette,
      content: [
        {
          title: 'Framework Support',
          description: 'Build frontend applications with popular frameworks',
          items: [
            'Vanilla JavaScript for maximum compatibility',
            'React, Vue.js, and Angular support',
            'Live preview with responsive design testing',
            'Download generated projects as files'
          ]
        },
        {
          title: 'AI Generation',
          description: 'Create beautiful UIs with AI assistance',
          items: [
            'Describe your project in natural language',
            'Generate HTML, CSS, and JavaScript automatically',
            'Modern design patterns and best practices',
            'Responsive layouts and animations'
          ]
        }
      ]
    }
  ]

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Advanced code understanding using Google Gemini AI and NLP technologies'
    },
    {
      icon: MessageSquare,
      title: 'RAG Technology',
      description: 'Chat with your codebase using Retrieval Augmented Generation for intelligent responses'
    },
    {
      icon: Code2,
      title: 'Multi-Language Support',
      description: 'Support for Python, JavaScript, TypeScript, Java, C++, Go, Rust, and more'
    },
    {
      icon: FileText,
      title: 'Smart Documentation',
      description: 'Generate comprehensive documentation with visual codebase maps automatically'
    }
  ]

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Documentation
          </h1>
          <p className="text-xl text-secondary-300 max-w-2xl mx-auto">
            Learn how to use DevSensei's powerful AI-driven features to enhance your development workflow
          </p>
        </motion.div>

        {/* Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card mb-12"
        >
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
            <BookOpen className="h-6 w-6 mr-2 text-primary-400" />
            What is DevSensei?
          </h2>
          <p className="text-secondary-300 mb-6">
            DevSensei is an AI-powered code understanding and generation platform that combines the power of 
            Google Gemini AI, RAG (Retrieval Augmented Generation), and NLP to help developers work more efficiently. 
            Whether you're exploring repositories, writing code, or building frontend applications, DevSensei provides 
            intelligent assistance every step of the way.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.1 * index }}
                  className="flex items-start space-x-3"
                >
                  <div className="flex-shrink-0">
                    <div className="p-2 bg-primary-600/20 rounded-lg">
                      <Icon className="h-5 w-5 text-primary-400" />
                    </div>
                  </div>
                  <div>
                    <h3 className="font-semibold text-white mb-1">{feature.title}</h3>
                    <p className="text-secondary-300 text-sm">{feature.description}</p>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </motion.div>

        {/* Documentation Sections */}
        <div className="space-y-8">
          {sections.map((section, sectionIndex) => {
            const Icon = section.icon
            return (
              <motion.div
                key={section.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + sectionIndex * 0.1 }}
                className="card"
              >
                <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
                  <Icon className="h-6 w-6 mr-2 text-primary-400" />
                  {section.title}
                </h2>
                
                <div className="space-y-6">
                  {section.content.map((subsection, index) => (
                    <div key={index}>
                      <h3 className="text-lg font-semibold text-white mb-3">
                        {subsection.title}
                      </h3>
                      <p className="text-secondary-300 mb-4">
                        {subsection.description}
                      </p>
                      <ul className="space-y-2">
                        {subsection.items.map((item, itemIndex) => (
                          <li key={itemIndex} className="flex items-start space-x-2">
                            <ArrowRight className="h-4 w-4 text-primary-400 mt-0.5 flex-shrink-0" />
                            <span className="text-secondary-300">{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* API Reference */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="card mt-12"
        >
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
            <Code2 className="h-6 w-6 mr-2 text-primary-400" />
            API Reference
          </h2>
          <p className="text-secondary-300 mb-6">
            DevSensei provides a comprehensive REST API for integrating AI-powered code analysis 
            into your own applications and workflows.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-secondary-900 border border-secondary-700 rounded-lg p-4">
              <h3 className="font-semibold text-white mb-2">Base URL</h3>
              <code className="text-primary-400 text-sm">http://localhost:8000/api</code>
            </div>
            <div className="bg-secondary-900 border border-secondary-700 rounded-lg p-4">
              <h3 className="font-semibold text-white mb-2">Documentation</h3>
              <a 
                href="http://localhost:8000/docs" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-primary-400 text-sm hover:text-primary-300 flex items-center"
              >
                Interactive API Docs
                <ExternalLink className="h-3 w-3 ml-1" />
              </a>
            </div>
          </div>
        </motion.div>

        {/* Support */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0 }}
          className="card mt-8"
        >
          <h2 className="text-2xl font-bold text-white mb-4">
            Need Help?
          </h2>
          <p className="text-secondary-300 mb-6">
            If you have questions or need assistance, here are some resources to help you get started:
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="block p-4 bg-secondary-900 border border-secondary-700 rounded-lg hover:border-primary-500/50 transition-colors"
            >
              <h3 className="font-semibold text-white mb-2">GitHub Repository</h3>
              <p className="text-secondary-300 text-sm">View source code and report issues</p>
            </a>
            <a
              href="mailto:support@devsensei.com"
              className="block p-4 bg-secondary-900 border border-secondary-700 rounded-lg hover:border-primary-500/50 transition-colors"
            >
              <h3 className="font-semibold text-white mb-2">Email Support</h3>
              <p className="text-secondary-300 text-sm">Get help from our team</p>
            </a>
            <a
              href="https://discord.gg/devsensei"
              target="_blank"
              rel="noopener noreferrer"
              className="block p-4 bg-secondary-900 border border-secondary-700 rounded-lg hover:border-primary-500/50 transition-colors"
            >
              <h3 className="font-semibold text-white mb-2">Community</h3>
              <p className="text-secondary-300 text-sm">Join our Discord community</p>
            </a>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default Documentation