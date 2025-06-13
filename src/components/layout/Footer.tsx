import React from 'react'
import { motion } from 'framer-motion'
import { Github, Twitter, Heart, Code2 } from 'lucide-react'

const Footer = () => {
  return (
    <footer className="bg-secondary-900 border-t border-secondary-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="p-2 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg">
                <Code2 className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-bold gradient-text">DevSensei</span>
            </div>
            <p className="text-secondary-400 mb-4 max-w-md">
              AI-powered code understanding and generation platform that combines the power of 
              Google Gemini AI, RAG, and NLP to help developers work more efficiently.
            </p>
            <div className="flex space-x-4">
              <motion.a
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                href="https://github.com"
                className="p-2 bg-secondary-800 rounded-lg text-secondary-400 hover:text-white hover:bg-secondary-700 transition-colors"
              >
                <Github className="h-5 w-5" />
              </motion.a>
              <motion.a
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                href="https://twitter.com"
                className="p-2 bg-secondary-800 rounded-lg text-secondary-400 hover:text-white hover:bg-secondary-700 transition-colors"
              >
                <Twitter className="h-5 w-5" />
              </motion.a>
            </div>
          </div>

          {/* Features */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Features</h3>
            <ul className="space-y-2">
              <li><a href="/repository" className="text-secondary-400 hover:text-white transition-colors">Repository Explorer</a></li>
              <li><a href="/playground" className="text-secondary-400 hover:text-white transition-colors">Code Playground</a></li>
              <li><a href="/frontend" className="text-secondary-400 hover:text-white transition-colors">Frontend AI</a></li>
              <li><a href="/docs" className="text-secondary-400 hover:text-white transition-colors">Documentation</a></li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Resources</h3>
            <ul className="space-y-2">
              <li><a href="#" className="text-secondary-400 hover:text-white transition-colors">API Documentation</a></li>
              <li><a href="#" className="text-secondary-400 hover:text-white transition-colors">Getting Started</a></li>
              <li><a href="#" className="text-secondary-400 hover:text-white transition-colors">Examples</a></li>
              <li><a href="#" className="text-secondary-400 hover:text-white transition-colors">Support</a></li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-secondary-700 flex flex-col md:flex-row justify-between items-center">
          <p className="text-secondary-400 text-sm">
            © 2024 DevSensei. All rights reserved.
          </p>
          <div className="flex items-center space-x-1 text-secondary-400 text-sm mt-4 md:mt-0">
            <span>Built with</span>
            <Heart className="h-4 w-4 text-red-500" />
            <span>by the DevSensei Team</span>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer