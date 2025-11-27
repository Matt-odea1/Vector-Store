/**
 * Main App component - Chat9021 Premium Theme with ChatGPT-style layout
 */
import { useEffect, useState } from 'react'
import './App.css'
import { ChatContainer } from './components/ChatContainer'
import { Sidebar } from './components/Sidebar'
import { ToastContainer } from './components/ToastContainer'
import { KeyboardShortcutsModal } from './components/KeyboardShortcutsModal'
import SEO from './components/SEO'
import { STORAGE_KEYS } from './config/constants'
import { useOnlineStatus } from './hooks/useOnlineStatus'
import { useToastStore } from './store/toastStore'
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'
import { useChatStore } from './store/chatStore'
import { webApplicationSchema, organizationSchema, injectStructuredData } from './utils/structuredData'

function App() {
  const isOnline = useOnlineStatus()
  const { addToast } = useToastStore()
  const { setEditorOpen, codeEditor } = useChatStore()
  const [showShortcuts, setShowShortcuts] = useState(false)

  // Clear session on mount to always start fresh
  useEffect(() => {
    localStorage.removeItem(STORAGE_KEYS.SESSION_ID)
  }, [])

  // Show toast when network status changes
  useEffect(() => {
    if (!isOnline) {
      addToast('You are currently offline. Some features may not work.', 'warning', 0)
    } else {
      addToast('Connection restored', 'success', 3000)
    }
  }, [isOnline, addToast])

  // Inject structured data for SEO
  useEffect(() => {
    const cleanupApp = injectStructuredData(webApplicationSchema)
    const cleanupOrg = injectStructuredData(organizationSchema)
    
    return () => {
      cleanupApp()
      cleanupOrg()
    }
  }, [])

  // Global keyboard shortcuts
  useKeyboardShortcuts([
    {
      key: '/',
      ctrl: true,
      action: () => setShowShortcuts(true),
      description: 'Show keyboard shortcuts',
    },
    {
      key: 'e',
      ctrl: true,
      action: () => setEditorOpen(!codeEditor.isOpen),
      description: 'Toggle code editor',
    },
    {
      key: 'Escape',
      action: () => setShowShortcuts(false),
      description: 'Close modal',
    },
  ]);

  return (
    <>
      {/* SEO Meta Tags */}
      <SEO
        title="Chat Interface"
        description="Interactive AI tutoring chat interface with code editor. Get help with programming, debug code, and learn through conversation."
        keywords="AI tutor, programming chat, code editor, Python learning, interactive coding"
      />

      {/* Skip to main content link for screen readers */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary-600 focus:text-white focus:rounded-lg focus:shadow-lg"
      >
        Skip to main content
      </a>

      <div className="app-container h-screen flex bg-[#f7f7f8]" role="application" aria-label="AI Tutor Chat Application">
        {/* Toast Notifications */}
        <ToastContainer />
        
        {/* Keyboard Shortcuts Modal */}
        {showShortcuts && <KeyboardShortcutsModal onClose={() => setShowShortcuts(false)} />}
        
        {/* Sidebar - ChatGPT Style */}
        <Sidebar />

      {/* Main Content Area - Full Width */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Chat Area - Full Height */}
        <main id="main-content" className="flex-1 overflow-hidden" role="main" aria-label="Chat conversation">
          <div className="h-full">
            <ChatContainer />
          </div>
        </main>
      </div>
    </div>
    </>
  )
}

export default App
