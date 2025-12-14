import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './styles/App.css'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="app">
          <header className="app-header">
            <h1>📚 StorAI-Booker</h1>
            <p>AI-Powered Storybook Generation - MVP</p>
          </header>

          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/generate" element={<GeneratePage />} />
            <Route path="/library" element={<LibraryPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

// Placeholder components
function HomePage() {
  return (
    <div className="page">
      <h2>Welcome to StorAI-Booker MVP</h2>
      <p>AI-powered storybook generation is coming soon!</p>
      <nav>
        <a href="/generate">Generate Story</a>
        <a href="/library">View Library</a>
        <a href="/settings">Settings</a>
      </nav>
    </div>
  )
}

function GeneratePage() {
  return (
    <div className="page">
      <h2>Generate Story</h2>
      <p>Story generation form will be here</p>
    </div>
  )
}

function LibraryPage() {
  return (
    <div className="page">
      <h2>Story Library</h2>
      <p>Your generated stories will appear here</p>
    </div>
  )
}

function SettingsPage() {
  return (
    <div className="page">
      <h2>Settings</h2>
      <p>LLM provider configuration will be here</p>
    </div>
  )
}

export default App
