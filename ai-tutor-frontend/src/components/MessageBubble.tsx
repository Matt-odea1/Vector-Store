/**
 * Individual message bubble component - Premium design
 */
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { Message } from '../types/chat'
import { formatTimestamp } from '../utils/formatDate'

interface MessageBubbleProps {
  message: Message
}

// Clean up markdown formatting issues
const cleanMarkdown = (text: string): string => {
  return text
    // Remove standalone punctuation paragraphs after code blocks
    .replace(/```\n\n([.,!?;:])\n/g, '```$1\n')
    .replace(/```\n\n([.,!?;:])\s/g, '```$1 ')
    // Remove standalone punctuation at start of line
    .replace(/\n\n([.,!?;:])\n/g, '$1\n')
    // Fix spacing around code blocks - ensure blank lines
    .replace(/([^\n])\n```/g, '$1\n\n```')
    .replace(/```\n([^\n`])/g, '```\n\n$1')
    // Remove excessive blank lines (more than 2)
    .replace(/\n{3,}/g, '\n\n')
}

export const MessageBubble = ({ message }: MessageBubbleProps) => {
  const isUser = message.role === 'user'
  const isError = message.isError
  
  // Clean markdown for assistant messages
  const cleanedContent = !isUser ? cleanMarkdown(message.content) : message.content

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6 message-enter`}>
      <div className="flex max-w-4xl w-full space-x-3">
        {/* Avatar for assistant */}
        {!isUser && (
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-md">
            <span className="text-white text-sm font-semibold">AI</span>
          </div>
        )}

        {/* Message Content */}
        <div
          className={`flex-1 rounded-2xl px-5 py-4 shadow-message transition-all duration-200 hover:shadow-message-hover ${
            isUser
              ? 'bg-gradient-to-br from-primary-600 to-primary-500 text-white ml-auto'
              : isError
              ? 'bg-red-50 text-red-900 border-2 border-red-200'
              : 'bg-white text-gray-900 border border-gray-200'
          }`}
        >
          {isUser ? (
            <p className="text-white leading-relaxed m-0 whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="markdown-content prose prose-sm max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  p: ({ children }) => {
                    // Skip paragraphs that are just standalone punctuation
                    const text = String(children).trim()
                    if (text.length === 1 && /[.,!?;:]/.test(text)) {
                      return <>{children}</>
                    }
                    return <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>
                  },
                  code: ({ inline, children, ...props }: any) =>
                    inline ? (
                      <code className="bg-pink-50 text-pink-600 px-2 py-0.5 rounded text-sm font-medium" {...props}>
                        {children}
                      </code>
                    ) : (
                      <pre className="bg-gray-900 text-gray-100 rounded-xl p-4 overflow-x-auto my-3 shadow-inner">
                        <code className="text-sm" {...props}>
                          {children}
                        </code>
                      </pre>
                    ),
                  ul: ({ children }) => <ul className="ml-4 mb-3 space-y-1 list-disc">{children}</ul>,
                  ol: ({ children }) => <ol className="ml-4 mb-3 space-y-1 list-decimal">{children}</ol>,
                  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                  a: ({ children, ...props }) => (
                    <a className="text-primary-600 hover:text-primary-700 underline font-medium" target="_blank" rel="noopener noreferrer" {...props}>
                      {children}
                    </a>
                  ),
                }}
              >
                {cleanedContent}
              </ReactMarkdown>
            </div>
          )}

          {/* Metadata */}
          <div
            className={`flex items-center space-x-2 text-xs mt-3 pt-2 border-t ${
              isUser 
                ? 'text-primary-100 border-primary-400/30' 
                : isError 
                ? 'text-red-600 border-red-200' 
                : 'text-gray-500 border-gray-200'
            }`}
          >
            <span>{formatTimestamp(message.timestamp)}</span>
            {message.tokens && (
              <>
                <span>•</span>
                <span className="font-medium">{message.tokens} tokens</span>
              </>
            )}
          </div>
        </div>

        {/* Avatar for user */}
        {isUser && (
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center shadow-md">
            <span className="text-white text-sm font-semibold">You</span>
          </div>
        )}
      </div>
    </div>
  )
}
