/**
 * Custom hook for chat functionality
 */
import { useCallback } from 'react'
import { useChatStore } from '../store/chatStore'
import { sendChatMessage } from '../api/chat'
import type { Message } from '../types/chat'

export const useChat = () => {
  const {
    messages,
    sessionId,
    pedagogyMode,
    isLoading,
    error,
    addMessage,
    setSessionId,
    setLoading,
    setError,
  } = useChatStore()

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return

      // Add user message immediately
      const userMessage: Message = {
        role: 'user',
        content: content.trim(),
        timestamp: new Date().toISOString(),
      }
      addMessage(userMessage)
      setError(null)
      setLoading(true)

      try {
        // Send to backend
        const response = await sendChatMessage({
          query: content.trim(),
          session_id: sessionId,
          include_history: true,
          pedagogy_mode: pedagogyMode,
          top_k: 5,
        })

        // Update session ID if new session
        if (response.is_new_session && response.session_id) {
          setSessionId(response.session_id)
        }

        // Add assistant response
        const assistantMessage: Message = {
          role: 'assistant',
          content: response.answer,
          timestamp: new Date().toISOString(),
          tokens: response.tokens_output || undefined,
          context_ids: response.context_ids,
        }
        addMessage(assistantMessage)
      } catch (err) {
        console.error('Failed to send message:', err)
        const errorMessage =
          err instanceof Error ? err.message : 'Failed to send message. Please try again.'
        
        setError(errorMessage)
        
        // Add error message to chat
        const errorMsg: Message = {
          role: 'assistant',
          content: `❌ Error: ${errorMessage}`,
          timestamp: new Date().toISOString(),
          isError: true,
        }
        addMessage(errorMsg)
      } finally {
        setLoading(false)
      }
    },
    [sessionId, pedagogyMode, isLoading, addMessage, setSessionId, setLoading, setError]
  )

  return {
    messages,
    sessionId,
    pedagogyMode,
    isLoading,
    error,
    sendMessage,
  }
}
