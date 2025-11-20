/**
 * Date formatting utilities
 */
import { format, formatDistanceToNow, isToday, isYesterday } from 'date-fns'

/**
 * Format a timestamp for display
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
 * Format a date relative to now (e.g., "2 hours ago")
 */
export const formatRelative = (timestamp: string): string => {
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
}

/**
 * Format a full date
 */
export const formatFullDate = (timestamp: string): string => {
  return format(new Date(timestamp), 'MMMM d, yyyy h:mm a')
}
