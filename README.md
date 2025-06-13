# DevSensei Frontend 🧙‍♂️

A modern, responsive frontend for the DevSensei AI-powered code understanding and generation platform.

![DevSensei](https://img.shields.io/badge/DevSensei-Frontend-purple)
![React](https://img.shields.io/badge/React-18.2+-61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-3178C6)
![Tailwind](https://img.shields.io/badge/Tailwind-3.3+-38B2AC)

## 🚀 Features

### 🏠 Home Page
- Beautiful hero section with gradient backgrounds
- Feature showcase with interactive cards
- Responsive design with smooth animations
- Call-to-action sections

### 📁 Repository Explorer
- GitHub username search and repository browsing
- Repository selection with detailed information
- PDF documentation generation
- AI-powered codebase chat functionality
- Visual repository statistics

### 💻 Code Playground
- Multi-language code editor with Monaco Editor
- Real-time code execution
- AI-powered features:
  - **Generate**: Create code from descriptions
  - **Execute**: Run code with input/output
  - **Explain**: Get detailed code explanations
  - **Debug**: Identify and fix bugs
  - **Optimize**: Improve code performance
- Syntax highlighting and error detection
- Copy and download functionality

### 🎨 Frontend AI Playground
- Framework selection (Vanilla JS, React, Vue, Angular)
- AI-powered UI generation
- Live preview with responsive testing
- Code editor for HTML, CSS, and JavaScript
- Download generated projects
- Mobile/tablet/desktop preview modes

### 📚 Documentation
- Comprehensive feature documentation
- Getting started guides
- API reference
- Support resources

## 🛠️ Technology Stack

- **React 18** - Modern React with hooks and concurrent features
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations and transitions
- **Monaco Editor** - VS Code editor in the browser
- **React Query** - Data fetching and caching
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Lucide React** - Beautiful icons
- **React Hot Toast** - Toast notifications

## 📋 Prerequisites

- Node.js 16 or higher
- npm or yarn package manager

## 🔧 Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/DevSensei.git
cd DevSensei/frontend
```

2. **Install dependencies**
```bash
npm install
# or
yarn install
```

3. **Environment setup**
```bash
cp .env.example .env
```

Edit `.env` file:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=DevSensei
```

4. **Start development server**
```bash
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:5173`

## 🏗️ Project Structure

```
src/
├── components/          # Reusable components
│   ├── layout/         # Layout components (Navbar, Footer)
│   └── CodeEditor.tsx  # Monaco code editor wrapper
├── pages/              # Page components
│   ├── Home.tsx        # Landing page
│   ├── RepositoryExplorer.tsx
│   ├── CodePlayground.tsx
│   ├── FrontendPlayground.tsx
│   └── Documentation.tsx
├── services/           # API services
│   └── api.ts          # API client and service functions
├── utils/              # Utility functions
│   └── cn.ts           # Class name utility
├── App.tsx             # Main app component
├── main.tsx            # App entry point
└── index.css           # Global styles
```

## 🎨 Design System

### Colors
- **Primary**: Blue gradient (`#0ea5e9` to `#0284c7`)
- **Secondary**: Slate grays (`#1e293b` to `#f8fafc`)
- **Accent**: Purple gradient (`#d946ef` to `#c026d3`)

### Typography
- **Font Family**: Inter (sans-serif), JetBrains Mono (monospace)
- **Scale**: Responsive typography with proper line heights

### Components
- **Buttons**: Primary, secondary, accent, and outline variants
- **Cards**: Glass morphism effect with subtle borders
- **Inputs**: Consistent styling with focus states
- **Code Blocks**: Dark theme with syntax highlighting

## 🔌 API Integration

The frontend communicates with the DevSensei backend through a REST API:

- **Base URL**: `http://localhost:8000`
- **Services**: GitHub, Code Execution, AI Chat, Frontend Generation
- **Authentication**: API key-based (optional)
- **Error Handling**: Automatic retry and user-friendly error messages

## 📱 Responsive Design

- **Mobile First**: Designed for mobile devices first
- **Breakpoints**: 
  - `sm`: 640px
  - `md`: 768px
  - `lg`: 1024px
  - `xl`: 1280px
- **Components**: All components are fully responsive
- **Navigation**: Collapsible mobile menu

## ⚡ Performance

- **Code Splitting**: Automatic route-based code splitting
- **Lazy Loading**: Components loaded on demand
- **Caching**: React Query for efficient data caching
- **Optimizations**: Vite build optimizations

## 🧪 Development

### Available Scripts

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Code Style

- **ESLint**: Configured for React and TypeScript
- **Prettier**: Code formatting (recommended)
- **TypeScript**: Strict mode enabled
- **Conventions**: 
  - PascalCase for components
  - camelCase for functions and variables
  - kebab-case for file names

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.

### Deploy to Netlify

1. Connect your GitHub repository to Netlify
2. Set build command: `npm run build`
3. Set publish directory: `dist`
4. Add environment variables in Netlify dashboard

### Deploy to Vercel

```bash
npm install -g vercel
vercel
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **React Team** for the amazing framework
- **Tailwind CSS** for the utility-first approach
- **Monaco Editor** for the VS Code experience
- **Framer Motion** for smooth animations
- **Lucide** for beautiful icons

---

Built with ❤️ by the DevSensei Team