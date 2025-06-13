import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  ArrowRight, 
  GitBranch, 
  Play, 
  Palette, 
  Sparkles, 
  Zap, 
  Brain, 
  Code2,
  FileText,
  MessageSquare,
  Cpu,
  Rocket
} from 'lucide-react'

const Home = () => {
  const features = [
    {
      icon: GitBranch,
      title: 'Repository Explorer',
      description: 'Analyze GitHub repositories, generate documentation, and chat with your codebase using AI.',
      href: '/repository',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: Play,
      title: 'Code Playground',
      description: 'Execute, debug, and optimize code in multiple languages with AI assistance.',
      href: '/playground',
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: Palette,
      title: 'Frontend AI',
      description: 'Generate beautiful frontend applications with live preview and AI guidance.',
      href: '/frontend',
      color: 'from-purple-500 to-pink-500'
    }
  ]

  const capabilities = [
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Advanced code understanding using Google Gemini AI and NLP'
    },
    {
      icon: MessageSquare,
      title: 'RAG Technology',
      description: 'Chat with your codebase using Retrieval Augmented Generation'
    },
    {
      icon: Cpu,
      title: 'Multi-Language Support',
      description: 'Python, JavaScript, TypeScript, Java, C++, Go, Rust, and more'
    },
    {
      icon: FileText,
      title: 'Smart Documentation',
      description: 'Generate comprehensive documentation with visual codebase maps'
    },
    {
      icon: Zap,
      title: 'Real-time Execution',
      description: 'Run and test code directly in your browser with instant feedback'
    },
    {
      icon: Rocket,
      title: 'Production Ready',
      description: 'Generate production-quality code with best practices built-in'
    }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 lg:py-32">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-600/20 via-accent-600/20 to-secondary-900/20" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="inline-flex items-center space-x-2 bg-gradient-to-r from-primary-500/20 to-accent-500/20 border border-primary-500/30 rounded-full px-6 py-3 mb-8"
            >
              <Sparkles className="h-5 w-5 text-primary-400" />
              <span className="text-primary-300 font-medium">AI-Powered Code Assistant</span>
            </motion.div>

            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-6">
              Meet{' '}
              <span className="gradient-text">DevSensei</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-secondary-300 mb-8 max-w-3xl mx-auto text-balance">
              The ultimate AI-powered platform for code understanding, generation, and optimization. 
              Combine the power of Google Gemini AI, RAG, and NLP to supercharge your development workflow.
            </p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            >
              <Link
                to="/repository"
                className="btn-primary text-lg px-8 py-4 group"
              >
                Get Started
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                to="/docs"
                className="btn-outline text-lg px-8 py-4"
              >
                View Documentation
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-secondary-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Powerful Features for Modern Development
            </h2>
            <p className="text-xl text-secondary-300 max-w-2xl mx-auto">
              Everything you need to understand, generate, and optimize code with AI assistance
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.2, duration: 0.8 }}
                  viewport={{ once: true }}
                  whileHover={{ y: -5 }}
                  className="group"
                >
                  <Link to={feature.href} className="block">
                    <div className="card h-full hover:border-primary-500/50 transition-all duration-300">
                      <div className={`inline-flex p-3 rounded-lg bg-gradient-to-r ${feature.color} mb-4`}>
                        <Icon className="h-6 w-6 text-white" />
                      </div>
                      <h3 className="text-xl font-semibold text-white mb-3 group-hover:text-primary-400 transition-colors">
                        {feature.title}
                      </h3>
                      <p className="text-secondary-300 mb-4">
                        {feature.description}
                      </p>
                      <div className="flex items-center text-primary-400 font-medium group-hover:translate-x-2 transition-transform">
                        Explore
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </div>
                    </div>
                  </Link>
                </motion.div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Capabilities Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Advanced AI Capabilities
            </h2>
            <p className="text-xl text-secondary-300 max-w-2xl mx-auto">
              Powered by cutting-edge AI technology and modern development practices
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {capabilities.map((capability, index) => {
              const Icon = capability.icon
              return (
                <motion.div
                  key={capability.title}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1, duration: 0.5 }}
                  viewport={{ once: true }}
                  className="flex items-start space-x-4 p-6 rounded-xl bg-secondary-800/30 border border-secondary-700/50 hover:border-primary-500/30 transition-all duration-300"
                >
                  <div className="flex-shrink-0">
                    <div className="p-2 bg-primary-600/20 rounded-lg">
                      <Icon className="h-6 w-6 text-primary-400" />
                    </div>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-2">
                      {capability.title}
                    </h3>
                    <p className="text-secondary-300">
                      {capability.description}
                    </p>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-600/20 to-accent-600/20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Ready to Transform Your Development Workflow?
            </h2>
            <p className="text-xl text-secondary-300 mb-8">
              Join thousands of developers who are already using DevSensei to write better code faster.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/repository"
                className="btn-primary text-lg px-8 py-4 group"
              >
                Start Exploring
                <Code2 className="ml-2 h-5 w-5 group-hover:rotate-12 transition-transform" />
              </Link>
              <Link
                to="/playground"
                className="btn-accent text-lg px-8 py-4 group"
              >
                Try Playground
                <Play className="ml-2 h-5 w-5 group-hover:scale-110 transition-transform" />
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

export default Home