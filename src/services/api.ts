import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add API key if available
api.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('devsensei_api_key')
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey
  }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('devsensei_api_key')
    }
    return Promise.reject(error)
  }
)

// GitHub Service
export const githubService = {
  getUserRepos: async (username: string) => {
    const response = await api.get(`/api/github/user/repos?username=${username}`)
    return response.data
  },

  getFileContent: async (username: string, repo: string, filePath: string) => {
    const response = await api.get('/api/github/file-content', {
      params: { username, repo, file_path: filePath }
    })
    return response.data
  },

  generateProjectDocs: async (data: {
    owner: string
    repo: string
    branch?: string
    include_setup?: boolean
    include_architecture?: boolean
    include_api_docs?: boolean
    include_codebase_map?: boolean
  }) => {
    const response = await api.post('/api/documentation/generate-project-docs', data)
    return response.data
  },

  chatWithRepo: async (data: {
    username: string
    repo: string
    query: string
  }) => {
    const response = await api.post('/api/github/chat-with-repo', data)
    return response.data
  },

  analyzeRepository: async (data: {
    username: string
    repositories: string[]
  }) => {
    const response = await api.post('/api/github/analyze', data)
    return response.data
  }
}

// Code Service
export const codeService = {
  executeCode: async (data: {
    code: string
    language: string
    input_data?: string
  }) => {
    const response = await api.post('/api/code/execute', data)
    return response.data
  },

  generateCode: async (data: {
    prompt: string
    language: string
    context?: string
  }) => {
    const response = await api.post('/api/code/generate', data)
    return response.data
  },

  optimizeCode: async (data: {
    code: string
    language: string
    optimization_type: string
  }) => {
    const response = await api.post('/api/code/optimize', data)
    return response.data
  },

  debugCode: async (data: {
    code: string
    language: string
    error_message?: string
    expected_output?: string
  }) => {
    const response = await api.post('/api/code/debug', data)
    return response.data
  },

  explainCode: async (code: string, language: string) => {
    const response = await api.post('/api/gemini/explain-code', {
      code,
      language
    })
    return response.data
  },

  getSupportedLanguages: async () => {
    const response = await api.get('/api/code/supported-languages')
    return response.data
  }
}

// AI Chat Service
export const aiService = {
  chat: async (data: {
    messages: Array<{ role: string; content: string }>
    repo_name?: string
    use_rag?: boolean
  }) => {
    const response = await api.post('/api/ai/chat', data)
    return response.data
  },

  analyzeCode: async (data: {
    code: string
    language: string
    analysis_type?: string
  }) => {
    const response = await api.post('/api/ai/analyze-code', data)
    return response.data
  },

  generateCode: async (prompt: string, language: string, context?: string) => {
    const response = await api.post('/api/ai/generate-code', {
      prompt,
      language,
      context
    })
    return response.data
  }
}

// Frontend Service
export const frontendService = {
  generateUI: async (data: {
    project_name: string
    description: string
    framework: string
    styling?: string
    components?: string[]
    features?: string[]
  }) => {
    const response = await api.post('/api/ui/generate-ui', data)
    return response.data
  },

  generateComponent: async (data: {
    component_name: string
    description: string
    framework: string
    props?: object
    styling?: string
  }) => {
    const response = await api.post('/api/ui/generate-component', data)
    return response.data
  },

  previewUI: async (data: {
    html: string
    css: string
    javascript?: string
  }) => {
    const response = await api.post('/api/ui/preview', data)
    return response.data
  }
}

export default api