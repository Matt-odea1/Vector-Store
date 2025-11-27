/**
 * Date formatting utilities
 */
import { format, formatDistanceToNow, isToday, isYesterday } from 'date-fns'

/**
 * Format a timestamp for display in a user-friendly way
 * 
 * @param timestamp - ISO 8601 timestamp string
 * @returns Formatted time string based on recency:
 *   - Today: "3:45 PM"
 *   - Yesterday: "Yesterday 3:45 PM"
 *   - Older: "Jan 15, 3:45 PM"
 * 
 * @example
 * ```ts
 * formatTimestamp('2024-01-15T15:45:00Z')
 * // => "Jan 15, 3:45 PM"
 * 
 * formatTimestamp(new Date().toISOString())
 * // => "3:45 PM"
 * ```
 */
export const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp)
  
  if (isToday(date)) {
    return format(date, 'h:mm a')
  } else if (isYesterday(date)) {
    return `Yesterday ${format(date, 'h:mm a')}`
  } else {
    return format(date, 'MMM d, h:mm a')
  }
}

/**
 * Format a date relative to now using natural language
 * 
 * @param timestamp - ISO 8601 timestamp string
 * @returns Human-readable relative time (e.g., "2 hours ago", "5 minutes ago")
 * 
 * @example
 * ```ts
 * formatRelative('2024-01-15T10:30:00Z')
 * // => "2 hours ago"
 * ```
 */
export const formatRelative = (timestamp: string): string => {
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
}

/**
 * Format a timestamp as a complete date and time string
 * 
 * @param timestamp - ISO 8601 timestamp string
 * @returns Full date format (e.g., "January 15, 2024 3:45 PM")
 * 
 * @example
 * ```ts
 * formatFullDate('2024-01-15T15:45:00Z')
 * // => "January 15, 2024 3:45 PM"
 * ```
 */
export const formatFullDate = (timestamp: string): string => {
  return format(new Date(timestamp), 'MMMM d, yyyy h:mm a')
}
