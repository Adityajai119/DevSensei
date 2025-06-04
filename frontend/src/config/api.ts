export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // GitHub endpoints
  github: {
    scrape: '/api/github/scrape',
    fileContent: '/api/github/file-content',
    analyze: '/api/github/analyze',
  },
  
  // Gemini AI endpoints
  gemini: {
    explainCode: '/api/gemini/explain-code',
    analyzeFunctions: '/api/gemini/analyze-functions',
    explainQuery: '/api/gemini/explain-database-query',
    optimizeCode: '/api/gemini/optimize-code',
    reviewCode: '/api/gemini/code-review',
  },
  
  // Code builder endpoints
  code: {
    generate: '/api/code/generate',
    debug: '/api/code/debug',
    generateTests: '/api/code/generate-tests',
    execute: '/api/code/execute',
    refactor: '/api/code/refactor',
    convert: '/api/code/convert',
  },
  
  // UI builder endpoints
  ui: {
    generateUI: '/api/ui/generate-ui',
    generateComponent: '/api/ui/generate-component',
    preview: '/api/ui/preview',
    designSystem: '/api/ui/generate-design-system',
  },
} as const; 