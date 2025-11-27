/**
 * Chat input component - Premium design with mode selector
 */
import { useState, useRef, useEffect, type KeyboardEvent } from 'react'
import { useChatStore } from '../store/chatStore'
import { PEDAGOGY_MODES } from '../types/pedagogy'
import type { PedagogyMode } from '../types/pedagogy'

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

export const ChatInput = ({
  onSend,
  disabled = false,
  placeholder = 'Ask me anything...',
}: ChatInputProps) => {
  const [input, setInput] = useState('')
  const [isModeDropdownOpen, setIsModeDropdownOpen] = useState(false)
  const { pedagogyMode, setPedagogyMode, codeEditor, setEditorOpen } = useChatStore()
  const modeDropdownRef = useRef<HTMLDivElement>(null)

  const selectedMode = PEDAGOGY_MODES.find(mode => mode.id === pedagogyMode)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modeDropdownRef.current && !modeDropdownRef.current.contains(event.target as Node)) {
        setIsModeDropdownOpen(false)
      }
    }

    if (isModeDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isModeDropdownOpen])

  const handleSelectMode = (mode: PedagogyMode) => {
    setPedagogyMode(mode)
    setIsModeDropdownOpen(false)
  }

  const handleSend = () => {
    if (!input.trim() || disabled) return
    onSend(input)
    setInput('')
  }
  
  const toggleCodeEditor = () => {
    setEditorOpen(!codeEditor.isOpen)
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="border-t border-gray-200 bg-white px-6 py-4 shadow-inner">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-start space-x-3">
          {/* Code Editor Toggle */}
          <button
            onClick={toggleCodeEditor}
            className={`rounded-xl border-2 px-4 py-3 font-medium text-sm transition-all shadow-sm flex items-center space-x-2 flex-shrink-0 h-[56px] ${
              codeEditor.isOpen
                ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white border-transparent hover:from-green-600 hover:to-emerald-700'
                : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'
            }`}
            title={codeEditor.isOpen ? 'Close Code Editor' : 'Open Code Editor'}
          >
            <span className="text-lg">⚡</span>
            <span className="hidden sm:inline">{codeEditor.isOpen ? 'Editor Open' : 'Code'}</span>
          </button>
          
          {/* Mode Selector - Custom Dropdown */}
          <div className="relative flex-shrink-0" ref={modeDropdownRef}>
            <button
              type="button"
              onClick={() => setIsModeDropdownOpen(!isModeDropdownOpen)}
              className="flex items-center space-x-2 rounded-xl border-2 border-gray-200 bg-white px-4 pr-10 text-sm font-medium text-gray-900 hover:border-gray-300 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all shadow-sm h-[56px] cursor-pointer"
            >
              <span className="text-lg">{selectedMode?.icon}</span>
              <span className="hidden sm:inline">{selectedMode?.name}</span>
            </button>
            
            {/* Dropdown Icon */}
            <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
              <svg 
                className={`w-4 h-4 text-gray-400 transition-transform ${isModeDropdownOpen ? 'rotate-180' : ''}`}
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>

            {/* Dropdown Menu */}
            {isModeDropdownOpen && (
              <div className="absolute bottom-full left-0 mb-2 w-80 bg-white rounded-xl shadow-xl border border-gray-200 py-2 z-50 animate-fade-in">
                {PEDAGOGY_MODES.map((mode) => (
                  <button
                    key={mode.id}
                    type="button"
                    onClick={() => handleSelectMode(mode.id)}
                    className={`w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors ${
                      mode.id === pedagogyMode ? 'bg-primary-50' : ''
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <span className="text-2xl">{mode.icon}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <span className="font-semibold text-gray-900 text-sm">
                            {mode.name}
                          </span>
                          {mode.id === pedagogyMode && (
                            <svg className="w-4 h-4 text-primary-600" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                          {mode.description}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
          
          <div className="flex-1 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={disabled}
              placeholder={placeholder}
              rows={1}
              className="w-full resize-none rounded-xl border-2 border-gray-200 px-5 py-4 pr-12 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 disabled:bg-gray-50 disabled:cursor-not-allowed transition-all shadow-sm text-gray-900 placeholder-gray-400 overflow-hidden"
              style={{
                minHeight: '56px',
                maxHeight: '300px',
              }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement
                target.style.height = '56px'
                target.style.height = `${Math.min(target.scrollHeight, 300)}px`
              }}
            />
            {/* Character count or status */}
            {input.length > 0 && (
              <div className="absolute bottom-3 right-3 text-xs text-gray-400">
                {input.length} chars
              </div>
            )}
          </div>
          <button
            onClick={handleSend}
            disabled={disabled || !input.trim()}
            className="rounded-xl bg-gradient-to-r from-primary-600 to-primary-500 px-8 font-semibold text-white hover:from-primary-700 hover:to-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:from-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl disabled:shadow-none flex items-center justify-center space-x-2 flex-shrink-0 min-h-[56px]"
          >
            <span>{disabled ? 'Sending...' : 'Send'}</span>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>
        </div>
        <div className="flex items-center justify-between mt-3">
          <p className="text-xs text-gray-500">
            <kbd className="px-2 py-1 bg-gray-100 rounded text-xs font-semibold shadow-sm">Enter</kbd> to send • 
            <kbd className="px-2 py-1 bg-gray-100 rounded text-xs font-semibold shadow-sm ml-1">Shift + Enter</kbd> for new line
          </p>
          {disabled && (
            <div className="flex items-center space-x-2 text-xs text-primary-600">
              <div className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-pulse" />
              <span className="font-medium">AI is thinking...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
