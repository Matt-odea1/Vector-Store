/**
 * Session management API methods
 */
import { apiClient } from './client'
import { API_ENDPOINTS } from '../config/api.config'
import type { SessionListResponse, ChatHistoryResponse } from '../types/session'

/**
 * Get list of all chat sessions
 */
export const listSessions = async (): Promise<SessionListResponse> => {
  const response = await apiClient.get<SessionListResponse>(API_ENDPOINTS.SESSIONS)
  return response.data
}

/**
 * Get chat history for a specific session
 */
export const getSessionHistory = async (sessionId: string): Promise<ChatHistoryResponse> => {
  const response = await apiClient.get<ChatHistoryResponse>(
    API_ENDPOINTS.CHAT_HISTORY(sessionId)
  )
  return response.data
}

/**
 * Delete a session
 */
export const deleteSession = async (sessionId: string): Promise<void> => {
  await apiClient.delete(API_ENDPOINTS.DELETE_SESSION(sessionId))
}
