/**
 * Session management API methods
 */
import { apiClient } from './client'
import { API_ENDPOINTS } from '../config/api.config'
import type { SessionListResponse } from '../types/session'

/**
 * Get list of all chat sessions
 */
export const listSessions = async (): Promise<SessionListResponse> => {
  const response = await apiClient.get<SessionListResponse>(API_ENDPOINTS.SESSIONS)
  return response.data
}
