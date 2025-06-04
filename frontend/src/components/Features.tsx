import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/Card';
import { GitBranch, Brain, Code, Palette, Zap, Shield } from 'lucide-react';

const Features: React.FC = () => {
  const features = [
    {
      icon: <GitBranch className="w-8 h-8" />,
      title: 'Code Scraping',
      description: 'Analyze GitHub repositories with intelligent code parsing and structure visualization.',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      icon: <Brain className="w-8 h-8" />,
      title: 'Doubt Resolution',
      description: 'Get instant AI-powered explanations for complex code, functions, and database queries.',
      color: 'from-purple-500 to-pink-500',
    },
    {
      icon: <Code className="w-8 h-8" />,
      title: 'Code Building',
      description: 'Generate production-ready code from natural language descriptions with best practices.',
      color: 'from-green-500 to-emerald-500',
    },
    {
      icon: <Palette className="w-8 h-8" />,
      title: 'UI Building',
      description: 'Create beautiful UI components and full projects with modern frameworks.',
      color: 'from-orange-500 to-red-500',
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: 'Code Optimization',
      description: 'Improve performance and readability with AI-suggested optimizations.',
      color: 'from-yellow-500 to-orange-500',
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: 'Code Review',
      description: 'Get comprehensive code reviews with security and best practice recommendations.',
      color: 'from-indigo-500 to-purple-500',
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
            <span className="gradient-text">Powerful Features</span>
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            Everything you need to understand, build, and optimize code with AI assistance
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
        >
          {features.map((feature, index) => (
            <motion.div key={index} variants={itemVariants}>
              <Card hover className="h-full">
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
                    <span className="text-sm font-medium">Learn more</span>
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