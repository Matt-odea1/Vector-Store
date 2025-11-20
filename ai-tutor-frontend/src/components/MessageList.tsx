/**
 * List of messages in the chat - Premium design
 */
import { useEffect, useRef } from 'react'
import { MessageBubble } from './MessageBubble'
import { CodeEditor } from './CodeEditor'
import { useChatStore } from '../store/chatStore'
import type { Message } from '../types/chat'

interface MessageListProps {
  messages: Message[]
  isLoading: boolean
  onSendMessage: (message: string) => void
}

export const MessageList = ({ messages, isLoading, onSendMessage }: MessageListProps) => {
  const bottomRef = useRef<HTMLDivElement>(null)
  const lastMessageRef = useRef<HTMLDivElement>(null)
  const prevIsLoadingRef = useRef(isLoading)
  const prevMessageCountRef = useRef(messages.length)
  const { codeEditor, setEditorMinimized } = useChatStore()

  // Smart scroll: When new message arrives, scroll to show the TOP of the last message
  useEffect(() => {
    const messageCountIncreased = messages.length > prevMessageCountRef.current
    
    if (messageCountIncreased && messages.length > 0) {
      const lastMessage = messages[messages.length - 1]
      
      // If last message is from assistant, scroll to show the START of the message
      if (lastMessage.role === 'assistant') {
        setTimeout(() => {
          lastMessageRef.current?.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' // Show the TOP of the message
          })
        }, 100)
      } else {
        // For user messages, scroll to bottom as usual
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
      }
    } else if (codeEditor.isOpen || codeEditor.lastOutput || codeEditor.lastError) {
      // For code editor state changes, scroll to bottom
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
    
    prevMessageCountRef.current = messages.length
  }, [messages, codeEditor.isOpen, codeEditor.lastOutput, codeEditor.lastError])

  // Smart auto-minimize: When AI finishes responding, auto-minimize editor after short delay
  useEffect(() => {
    const aiJustResponded = prevIsLoadingRef.current === true && isLoading === false
    
    if (aiJustResponded && codeEditor.isOpen && !codeEditor.isMinimized) {
      // Auto-minimize after AI responds so user can see the response
      setTimeout(() => setEditorMinimized(true), 500)
    }
    
    prevIsLoadingRef.current = isLoading
  }, [isLoading, codeEditor.isOpen, codeEditor.isMinimized, setEditorMinimized])

  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <div className="text-center max-w-3xl animate-fade-in">
          {/* Large decorative icon */}
          <div className="mb-8 flex justify-center">
            <div className="bg-gradient-to-br from-primary-500 to-primary-600 w-24 h-24 rounded-3xl flex items-center justify-center shadow-2xl">
              <span className="text-white text-5xl font-bold">C9</span>
            </div>
          </div>
          
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Welcome to Chat9021!</h2>
          <p className="text-xl text-gray-600 mb-10 leading-relaxed">
            Your personal learning companion. Choose a teaching mode and start your learning journey.
          </p>

          {/* Feature cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm hover:shadow-md transition-all">
              <div className="text-2xl mb-2">🤔</div>
              <div className="text-sm font-semibold text-gray-900">Socratic Mode</div>
              <div className="text-xs text-gray-500 mt-1">Learn through questions</div>
            </div>
            <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm hover:shadow-md transition-all">
              <div className="text-2xl mb-2">�</div>
              <div className="text-sm font-semibold text-gray-900">Explanatory Mode</div>
              <div className="text-xs text-gray-500 mt-1">Clear, direct teaching</div>
            </div>
            <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm hover:shadow-md transition-all">
              <div className="text-2xl mb-2">🐛</div>
              <div className="text-sm font-semibold text-gray-900">Debugging Mode</div>
              <div className="text-xs text-gray-500 mt-1">Guided problem solving</div>
            </div>
          </div>

          {/* Example prompts */}
          <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-2xl p-6 text-left border border-primary-200">
            <p className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
              <span className="mr-2">💡</span>
              Try asking me:
            </p>
            <div className="space-y-2">
              {[
                "Explain how recursion works in Python",
                "Help me debug this code snippet",
                "Test my understanding of data structures",
                "Review what I learned about sorting algorithms",
              ].map((prompt, i) => (
                <div key={i} className="bg-white rounded-lg px-4 py-3 text-sm text-gray-700 shadow-sm hover:shadow-md transition-all cursor-pointer">
                  "{prompt}"
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto px-8 py-8">
      <div className="max-w-4xl mx-auto">
        {messages.map((message, index) => {
          const isLastMessage = index === messages.length - 1
          return (
            <div 
              key={`${message.timestamp}-${index}`}
              ref={isLastMessage ? lastMessageRef : null}
            >
              <MessageBubble message={message} />
            </div>
          )
        })}

        {/* Code Editor - appears inline with messages */}
        <CodeEditor onSendMessage={onSendMessage} />

        {/* Typing indicator */}
        {isLoading && (
          <div className="flex justify-start mb-6 animate-fade-in">
            <div className="flex space-x-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-md">
                <span className="text-white text-sm font-semibold">AI</span>
              </div>
              <div className="bg-white rounded-2xl px-5 py-4 shadow-message border border-gray-200">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Scroll anchor */}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
