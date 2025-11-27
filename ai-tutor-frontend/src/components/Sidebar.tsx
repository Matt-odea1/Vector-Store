/**
 * Sidebar component for session management - ChatGPT style
 */
import { useChatStore } from '../store/chatStore'
import { useState, useEffect } from 'react'
import { useSessions } from '../hooks/useSessions'
import { formatRelativeTime } from '../utils/formatTime'
import { getSessionTitleFromInfo } from '../utils/sessionUtils'
import { DeleteConfirmModal } from './DeleteConfirmModal'
import { SessionSkeletonList } from './SessionSkeleton'

export const Sidebar = () => {
  const { sessionId, clearSession } = useChatStore()
  const {
    sessions,
    isLoadingSessions,
    fetchSessions,
    loadSessionHistory,
    handleDeleteSession,
  } = useSessions()
  
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState<{
    sessionId: string
    title: string
  } | null>(null)
  const [loadingSessionId, setLoadingSessionId] = useState<string | null>(null)

  // Load sessions on mount
  useEffect(() => {
    fetchSessions()
  }, [fetchSessions])

  const handleNewChat = () => {
    clearSession()
    // Refresh sessions list to show the new empty state
    fetchSessions()
    // Scroll to top if needed
    window.scrollTo(0, 0)
  }

  const handleLoadSession = async (sid: string) => {
    if (sid === sessionId) return // Already loaded
    
    setLoadingSessionId(sid)
    try {
      await loadSessionHistory(sid)
      // Scroll chat to top
      window.scrollTo(0, 0)
    } catch (error) {
      console.error('Error loading session:', error)
    } finally {
      setLoadingSessionId(null)
    }
  }

  const handleDeleteClick = (sid: string, title: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setDeleteConfirm({ sessionId: sid, title })
  }

  const executeDelete = async () => {
    if (!deleteConfirm) return
    
    try {
      await handleDeleteSession(deleteConfirm.sessionId)
      // Refresh sessions list
      fetchSessions()
    } catch (error) {
      console.error('Error deleting session:', error)
    } finally {
      setDeleteConfirm(null)
    }
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
      {/* Branding & Collapse */}
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center justify-between mb-4">
          {/* Logo & Title */}
          <div className="flex items-center space-x-2">
            <div className="bg-gradient-to-br from-primary-500 to-primary-600 w-8 h-8 rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white text-sm font-bold">C9</span>
            </div>
            <div>
              <h1 className="text-sm font-bold text-white">Chat9021</h1>
              <p className="text-[10px] text-gray-400">Learn smarter, not harder</p>
            </div>
          </div>
          
          {/* Collapse Button */}
          <button
            onClick={() => setIsCollapsed(true)}
            className="p-1.5 hover:bg-gray-800 rounded-lg transition-colors"
            title="Collapse sidebar"
          >
            <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        </div>

        {/* Online Status */}
        <div className="flex items-center space-x-2 px-2 py-1.5 bg-green-900/30 rounded-lg mb-4">
          <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
          <span className="text-xs font-medium text-green-400">Online</span>
        </div>

        {/* New Chat Button */}
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 text-white rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span className="text-sm font-medium">New Chat</span>
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-2">
        {isLoadingSessions ? (
          <SessionSkeletonList count={5} />
        ) : sessions.length === 0 ? (
          <div className="px-3 py-8 text-center">
            <svg
              className="w-12 h-12 mx-auto text-gray-600 mb-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <p className="text-sm text-gray-500">No previous sessions</p>
            <p className="text-xs text-gray-600 mt-1">Start a new chat to begin</p>
          </div>
        ) : (
          sessions.map((session) => {
            const title = getSessionTitleFromInfo(session)
            const isActive = sessionId === session.session_id
            const isLoading = loadingSessionId === session.session_id

            return (
              <button
                key={session.session_id}
                onClick={() => handleLoadSession(session.session_id)}
                disabled={isLoading}
                className={`w-full text-left px-3 py-3 rounded-lg transition-all duration-200 group relative ${
                  isActive
                    ? 'bg-gray-800 text-white'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                } ${isLoading ? 'opacity-50 cursor-wait' : ''}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0 pr-2">
                    <div className="flex items-center space-x-2">
                      <p className="text-sm font-medium truncate">{title}</p>
                      {isLoading && (
                        <div className="animate-spin h-3 w-3 border-2 border-primary-500 border-t-transparent rounded-full" />
                      )}
                    </div>
                    <div className="flex items-center space-x-2 mt-0.5">
                      <p className="text-xs text-gray-500">
                        {formatRelativeTime(session.last_accessed)}
                      </p>
                      <span className="text-gray-600">•</span>
                      <p className="text-xs text-gray-600">
                        {session.message_count} message{session.message_count !== 1 ? 's' : ''}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleDeleteClick(session.session_id, title, e)}
                    disabled={isLoading}
                    className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-gray-700 rounded transition-all flex-shrink-0"
                    title="Delete session"
                  >
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                  </button>
                </div>
              </button>
            )
          })
        )}
      </div>

      {/* Delete Confirmation Modal */}
      <DeleteConfirmModal
        isOpen={deleteConfirm !== null}
        onConfirm={executeDelete}
        onCancel={() => setDeleteConfirm(null)}
        sessionTitle={deleteConfirm?.title}
      />

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
