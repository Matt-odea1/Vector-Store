/**
 * Application constants
 */

export const APP_NAME = 'AI Tutor'
export const APP_VERSION = '1.0.0'

export const DEFAULT_PEDAGOGY_MODE = 'explanatory'
export const DEFAULT_TOP_K = 5

export const STORAGE_KEYS = {
  SESSION_ID: 'ai-tutor-session-id',
  PEDAGOGY_MODE: 'ai-tutor-pedagogy-mode',
  THEME: 'ai-tutor-theme',
} as const

export const API_TIMEOUT = 30000 // 30 seconds
