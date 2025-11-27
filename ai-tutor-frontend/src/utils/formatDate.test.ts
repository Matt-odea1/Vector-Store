/**
 * Tests for formatDate utilities
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { formatTimestamp, formatRelative, formatFullDate } from './formatDate'

describe('formatDate utilities', () => {
  beforeEach(() => {
    // Mock the current date
    vi.setSystemTime(new Date('2024-01-15T12:00:00Z'))
  })

  describe('formatTimestamp', () => {
    it('should format today\'s date with time only', () => {
      const timestamp = '2024-01-15T10:30:00Z'
      const result = formatTimestamp(timestamp)
      expect(result).toMatch(/\d{1,2}:\d{2}\s[AP]M/i)
    })

    it('should format yesterday with "Yesterday" prefix', () => {
      const timestamp = '2024-01-14T10:30:00Z'
      const result = formatTimestamp(timestamp)
      expect(result).toContain('Yesterday')
    })

    it('should format older dates with month and day', () => {
      const timestamp = '2024-01-10T10:30:00Z'
      const result = formatTimestamp(timestamp)
      expect(result).toMatch(/Jan\s\d{1,2}/)
    })
  })

  describe('formatRelative', () => {
    it('should format recent times as relative', () => {
      const timestamp = '2024-01-15T11:30:00Z'
      const result = formatRelative(timestamp)
      expect(result).toMatch(/\d+\s(minutes?|hours?)\sago/)
    })

    it('should handle dates in the past', () => {
      const timestamp = '2024-01-10T10:00:00Z'
      const result = formatRelative(timestamp)
      expect(result).toContain('ago')
    })
  })

  describe('formatFullDate', () => {
    it('should format a full date', () => {
      const timestamp = '2024-01-15T10:30:00Z'
      const result = formatFullDate(timestamp)
      expect(result).toMatch(/January\s15,\s2024/)
    })
  })
})
