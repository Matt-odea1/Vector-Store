/**
 * Sidebar component for session management - ChatGPT style
 */
import { useChatStore } from '../store/chatStore'
import { useState } from 'react'

export const Sidebar = () => {
  const { sessionId, clearSession } = useChatStore()
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [sessions] = useState<Array<{ id: string; title: string; timestamp: string }>>([])

  // TODO: Load sessions from API
  // useEffect(() => {
  //   // Fetch sessions from /internal/chat/sessions
  // }, [])

  const handleNewChat = () => {
    clearSession()
    // Scroll to top if needed
    window.scrollTo(0, 0)
  }

  if (isCollapsed) {
    return (
      <div className="w-16 bg-gray-900 border-r border-gray-800 flex flex-col items-center py-4">
        <button
          onClick={() => setIsCollapsed(false)}
          className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          title="Expand sidebar"
        >
          <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    )
  }

  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col h-full">
      {/* Sidebar Header */}
      <div className="p-4 border-b border-gray-800 flex items-center justify-between">
        <button
          onClick={handleNewChat}
          className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 text-white rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span className="font-medium">New Chat</span>
        </button>
        <button
          onClick={() => setIsCollapsed(true)}
          className="ml-2 p-2 hover:bg-gray-800 rounded-lg transition-colors"
          title="Collapse sidebar"
        >
          <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-2">
        {sessions.length === 0 ? (
          <div className="px-3 py-8 text-center">
            <p className="text-sm text-gray-500">No previous sessions</p>
            <p className="text-xs text-gray-600 mt-1">Start a new chat to begin</p>
          </div>
        ) : (
          sessions.map((session) => (
            <button
              key={session.id}
              onClick={() => {
                // TODO: Load session history
              }}
              className={`w-full text-left px-3 py-3 rounded-lg transition-all duration-200 group ${
                sessionId === session.id
                  ? 'bg-gray-800 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{session.title}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{session.timestamp}</p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    // TODO: Delete session
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-gray-700 rounded transition-all"
                  title="Delete session"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </button>
          ))
        )}
      </div>

      {/* Sidebar Footer */}
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-800 cursor-pointer transition-colors">
          <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-bold">U</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">User</p>
            <p className="text-xs text-gray-500">Premium Plan</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
