/**
 * Main App component - Chat9021 Premium Theme with ChatGPT-style layout
 */
import { useEffect } from 'react'
import './App.css'
import { ChatContainer } from './components/ChatContainer'
import { Sidebar } from './components/Sidebar'
import { STORAGE_KEYS } from './config/constants'

function App() {
  // Clear session on mount to always start fresh
  useEffect(() => {
    localStorage.removeItem(STORAGE_KEYS.SESSION_ID)
  }, [])

  return (
    <div className="app-container h-screen flex bg-[#f7f7f8]">
      {/* Sidebar - ChatGPT Style */}
      <Sidebar />

      {/* Main Content Area - Full Width */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Premium Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-3 flex-shrink-0 shadow-sm">
          <div className="flex items-center justify-between">
            {/* Logo - Smaller in header */}
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-br from-primary-500 to-primary-600 w-9 h-9 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white text-lg font-bold">C9</span>
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">Chat9021</h1>
                <p className="text-xs text-gray-500">Learn smarter, not harder</p>
              </div>
            </div>

            {/* Online Status */}
            <div className="flex items-center space-x-2 px-3 py-1.5 bg-green-50 rounded-lg">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium text-green-700">Online</span>
            </div>
          </div>
        </header>

        {/* Chat Area - Full Width */}
        <main className="flex-1 overflow-hidden">
          <div className="h-full">
            <ChatContainer />
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
