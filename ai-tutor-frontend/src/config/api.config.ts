/**
 * API configuration
 */

export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
} as const

export const API_ENDPOINTS = {
  CHAT: '/internal/chat',
  CHAT_HISTORY: (sessionId: string) => `/internal/chat/history/${sessionId}`,
  SESSIONS: '/internal/chat/sessions',
  DELETE_SESSION: (sessionId: string) => `/internal/chat/history/${sessionId}`,
  HEALTH: '/health',
} as const
