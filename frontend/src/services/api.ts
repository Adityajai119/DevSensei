import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Chat interfaces
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatRequest {
  messages: ChatMessage[];
  repo_name?: string;
  use_rag?: boolean;
}

export interface ChatResponse {
  response: string;
  sources?: Array<{
    content: string;
    metadata: {
      file_path: string;
      file_name: string;
      language: string;
    };
  }>;
}

// Code Analysis interfaces
export interface CodeAnalysisRequest {
  code: string;
  language?: string;
  analysis_type?: 'full' | 'entities' | 'complexity' | 'patterns';
}

export interface CodeAnalysisResponse {
  entities?: {
    functions: string[];
    classes: string[];
    variables: string[];
    imports: string[];
    comments: string[];
  };
  complexity?: {
    cyclomatic_complexity: Array<{
      name: string;
      complexity: number;
      rank: string;
    }>;
    maintainability_index: number;
    lines_of_code: {
      total: number;
      code: number;
      comments: number;
      blank: number;
    };
  };
  patterns?: {
    design_patterns: string[];
    anti_patterns: string[];
    code_smells: string[];
  };
  summary?: string;
  keywords?: Array<[string, number]>;
  quality_analysis?: {
    analysis: string;
    language: string;
  };
}

// Repository interfaces
export interface RepoRequest {
  owner: string;
  repo: string;
  branch?: string;
  index_for_rag?: boolean;
}

export interface RepoInfo {
  name: string;
  description: string;
  stars: number;
  forks: number;
  language: string;
  topics: string[];
  default_branch: string;
}

export interface FileContent {
  path: string;
  content: string;
  size: number;
  language?: string;
}

// API functions
export const chatApi = {
  // Chat with AI using Gemini and optional RAG
  chat: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/api/ai/chat', request);
    return response.data;
  },

  // Analyze code with NLP
  analyzeCode: async (request: CodeAnalysisRequest): Promise<CodeAnalysisResponse> => {
    const response = await api.post<CodeAnalysisResponse>('/api/ai/analyze-code', request);
    return response.data;
  },

  // Generate code using AI
  generateCode: async (prompt: string, language: string = 'python', context?: string) => {
    const response = await api.post('/api/ai/generate-code', {
      prompt,
      language,
      context,
    });
    return response.data;
  },

  // Explain code using AI and NLP
  explainCode: async (code: string, language: string = 'python') => {
    const response = await api.post('/api/ai/explain-code', {
      code,
      language,
    });
    return response.data;
  },
};

export const githubApi = {
  // Get repository information
  getRepoInfo: async (request: RepoRequest): Promise<RepoInfo> => {
    const response = await api.post<RepoInfo>('/api/github/repo/info', request);
    return response.data;
  },

  // Get repository files and index for RAG
  getRepoFiles: async (request: RepoRequest): Promise<FileContent[]> => {
    const response = await api.post<FileContent[]>('/api/github/repo/files', request);
    return response.data;
  },

  // Get repository structure
  getRepoStructure: async (request: RepoRequest) => {
    const response = await api.post('/api/github/repo/structure', request);
    return response.data;
  },

  // Search code in indexed repository
  searchCode: async (repo_name: string, query: string, k: number = 5) => {
    const response = await api.post('/api/github/repo/search-code', {
      repo_name,
      query,
      k,
    });
    return response.data;
  },

  // Get user repositories
  getUserRepos: async (username: string) => {
    const response = await api.get(`/api/github/user/repos?username=${username}`);
    return response.data;
  },
};

export const documentationApi = {
  // Generate project documentation with PDF
  generateDocs: async (request: {
    owner: string;
    repo: string;
    branch?: string;
    include_setup?: boolean;
    include_architecture?: boolean;
    include_codebase_map?: boolean;
  }) => {
    const response = await api.post('/api/documentation/generate-project-docs', request);
    return response.data;
  },

  // Generate codebase map
  generateCodebaseMap: async (request: { owner: string; repo: string; branch?: string }) => {
    const response = await api.post('/api/documentation/generate-codebase-map', request);
    return response.data;
  },

  // Chat with repository
  chatWithRepo: async (repo_name: string, query: string) => {
    const response = await api.post('/api/documentation/chat-with-repo', { repo_name, query });
    return response.data;
  },
};

// Code execution API
export const codeApi = {
  // Execute code
  execute: async (code: string, language: string, input_data?: string) => {
    const response = await api.post('/api/code/execute', { code, language, input_data });
    return response.data;
  },

  // Generate code
  generate: async (prompt: string, language: string = 'python', context?: string) => {
    const response = await api.post('/api/code/generate', { prompt, language, context });
    return response.data;
  },

  // Optimize code
  optimize: async (code: string, language: string, optimization_type: string = 'performance') => {
    const response = await api.post('/api/code/optimize', { code, language, optimization_type });
    return response.data;
  },

  // Debug code
  debug: async (code: string, language: string, error_message?: string, expected_output?: string) => {
    const response = await api.post('/api/code/debug', { code, language, error_message, expected_output });
    return response.data;
  },

  // Explain code
  explain: async (code: string, language: string) => {
    const response = await api.post('/api/code/explain', { code, language });
    return response.data;
  },

  // Generate frontend code
  generateFrontend: async (prompt: string, framework: string = 'vanilla') => {
    const response = await api.post('/api/code/generate-frontend', { prompt, framework });
    return response.data;
  },

  // Get supported languages
  getSupportedLanguages: async () => {
    const response = await api.get('/api/code/supported-languages');
    return response.data;
  },
};

export default api; 