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
        {/* Chat Area - Full Height */}
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
