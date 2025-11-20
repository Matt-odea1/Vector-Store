/**
 * Type definitions for chat-related entities
 */

export interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  tokens?: number
  context_ids?: string[]
  isError?: boolean
}

export interface ChatRequest {
  query: string
  top_k?: number
  session_id?: string | null
  include_history?: boolean
  pedagogy_mode?: string
}

export interface ChatResponse {
  answer: string
  session_id: string
  is_new_session: boolean
  history_length: number
  pedagogy_mode: string
  context_ids: string[]
  tokens_input: number | null
  tokens_output: number | null
  model_id: string | null
  error?: string | null
}
