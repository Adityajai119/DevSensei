import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/Card';
import { Search, GitBranch, Code, Layout } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Features: React.FC = () => {
  const navigate = useNavigate();
  const features = [
    {
      icon: <Search className="w-8 h-8" />,
      title: 'Repo Search',
      description: 'Chatbot-style search for GitHub repositories. Ask for repos by topic and get instant links.',
      color: 'from-pink-500 to-purple-500',
      route: '/repo-search',
    },
    {
      icon: <GitBranch className="w-8 h-8" />,
      title: 'Interact with Repo',
      description: 'Explore user repositories, generate project PDFs, and chat with repo context using RAG.',
      color: 'from-blue-500 to-cyan-500',
      route: '/repository-explorer',
    },
    {
      icon: <Code className="w-8 h-8" />,
      title: 'AI Compiler',
      description: 'Generate, edit, and run code in 10+ languages with AI. Edit, copy, clear, and execute instantly.',
      color: 'from-green-500 to-emerald-500',
      route: '/code-playground',
    },
    {
      icon: <Layout className="w-8 h-8" />,
      title: 'Frontend Playground',
      description: 'Select a tech stack, prompt for code (e.g., "generate flappy bird"), and run it live.',
      color: 'from-orange-500 to-red-500',
      route: '/frontend-playground',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
      },
    },
  };

  return (
    <section className="py-20 px-4 bg-gray-50 dark:bg-dark-900">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="gradient-text">DevSensei Features</span>
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            Your AI-powered toolkit for code, repos, and frontend magic
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8"
        >
          {features.map((feature, index) => (
            <motion.div key={index} variants={itemVariants}>
              <Card hover className="h-full" onClick={() => feature.route && navigate(feature.route)} style={feature.route ? { cursor: 'pointer' } : {}}>
                <CardHeader>
                  <motion.div
                    className={`w-16 h-16 rounded-xl bg-gradient-to-br ${feature.color} p-4 flex items-center justify-center text-white mb-4`}
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.5 }}
                  >
                    {feature.icon}
                  </motion.div>
                  <CardTitle>{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <motion.div
                    className="flex items-center gap-2 text-primary-600 dark:text-primary-400 cursor-pointer"
                    whileHover={{ x: 5 }}
                  >
                    <span className="text-sm font-medium">Explore</span>
                    <motion.span
                      animate={{ x: [0, 5, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      →
                    </motion.span>
                  </motion.div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default Features; 