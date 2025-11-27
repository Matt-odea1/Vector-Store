import { useEffect, useRef, useState } from 'react';
import Editor from '@monaco-editor/react';
import { useChatStore } from '../store/chatStore';
import { useCodeExecution } from '../hooks/useCodeExecution';

interface CodeEditorProps {
  onSendMessage: (message: string) => void;
}

export const CodeEditor = ({ onSendMessage }: CodeEditorProps) => {
  const { codeEditor, setEditorCode, setEditorOpen, setEditorMinimized, setEditorOutput, setEditorExecuting, addToHistory, loadFromHistory, layoutMode, setLayoutMode } = useChatStore();
  const { runCode, isLoading } = useCodeExecution();
  const editorRef = useRef<HTMLDivElement>(null);
  const [showHistory, setShowHistory] = useState(false);

  const handleRunCode = async () => {
    setEditorExecuting(true);
    try {
      const result = await runCode(codeEditor.code);
      setEditorOutput(result.output, result.error);
      // Add to history after execution
      addToHistory(codeEditor.code, result.output, result.error);
    } finally {
      setEditorExecuting(false);
    }
  };

  const handleAskAI = () => {
    // Expand if minimized so user sees what they're asking about
    if (codeEditor.isMinimized) {
      setEditorMinimized(false);
    }
    
    let message = '';
    
    if (codeEditor.lastError) {
      // User has an error - format debugging help request
      message = `Help me debug this Python code:\n\n\`\`\`python\n${codeEditor.code}\n\`\`\`\n\nI'm getting this error:\n\`\`\`\n${codeEditor.lastError}\n\`\`\`\n\nWhat's wrong and how do I fix it?`;
    } else if (codeEditor.lastOutput) {
      // Code ran successfully but user wants feedback
      message = `Help me with this Python code:\n\n\`\`\`python\n${codeEditor.code}\n\`\`\`\n\nIt produces this output:\n\`\`\`\n${codeEditor.lastOutput}\n\`\`\`\n\nCan you review it and provide feedback?`;
    } else {
      // No execution yet - general help request
      message = `Help me with this Python code:\n\n\`\`\`python\n${codeEditor.code}\n\`\`\`\n\nCan you review it and provide feedback on how to improve it?`;
    }
    
    // Send the formatted message to chat
    onSendMessage(message);
  };

  const handleClose = () => {
    setEditorOpen(false);
  };

  const handleToggleMinimize = () => {
    setEditorMinimized(!codeEditor.isMinimized);
  };

  // Auto-scroll to editor when opened
  useEffect(() => {
    if (codeEditor.isOpen) {
      setTimeout(() => {
        editorRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 100);
    }
  }, [codeEditor.isOpen]);

  if (!codeEditor.isOpen) {
    return null;
  }

  // Count lines of code
  const lineCount = codeEditor.code.split('\n').length;

  // Determine status
  const hasError = !!codeEditor.lastError;
  const hasOutput = !!codeEditor.lastOutput;
  const status = hasError ? 'Error' : hasOutput ? 'Ready' : 'Not Run';
  const statusColor = hasError ? 'text-red-500' : hasOutput ? 'text-green-500' : 'text-gray-400';
  const statusIcon = hasError ? '⚠️' : hasOutput ? '✓' : '○';

  // Check if in split mode
  const isInSplitMode = layoutMode === 'split' && window.innerWidth >= 1024;

  return (
    <div 
      ref={editorRef}
      className={isInSplitMode ? "h-full flex flex-col" : "max-w-5xl mx-auto my-4 animate-fade-in"}
    >
      <div className={`overflow-hidden transition-all duration-300 ease-in-out ${
        isInSplitMode ? 'h-full flex flex-col bg-[#1e1e1e]' : 'bg-white rounded-2xl shadow-lg border border-gray-200'
      }`}>
        {codeEditor.isMinimized ? (
          // Minimized View - Compact Bar
          <div className="flex items-center justify-between px-6 py-4 bg-gradient-to-r from-green-50 to-emerald-50">
            <div className="flex items-center space-x-4">
              <span className="font-semibold text-gray-900">Python Editor</span>
              <span className="text-sm text-gray-500">•</span>
              <span className="text-sm text-gray-600">{lineCount} lines</span>
              <span className="text-sm text-gray-500">•</span>
              <span className={`text-sm font-medium ${statusColor} flex items-center space-x-1`}>
                <span>{statusIcon}</span>
                <span>{status}</span>
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={handleToggleMinimize}
                className="text-gray-600 hover:text-gray-900 transition-colors p-2 rounded-lg hover:bg-white"
                aria-label="Expand editor"
                title="Expand editor"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                </svg>
              </button>
              <button
                onClick={handleClose}
                className="text-gray-400 hover:text-gray-600 transition-colors p-2 rounded-lg hover:bg-white"
                aria-label="Close editor"
                title="Close editor"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        ) : (
          // Expanded View - Full Editor
          <>
            {/* Header - Compact */}
            <div className="flex items-center justify-between px-4 py-2 bg-gradient-to-r from-green-50 to-emerald-50 border-b border-gray-200">
              <div className="flex items-center space-x-2">
                <h3 className="text-sm font-semibold text-gray-900">Python Editor</h3>
              </div>
              <div className="flex items-center space-x-1">
                <button
                  onClick={handleToggleMinimize}
                  className="text-gray-400 hover:text-gray-600 transition-colors p-1.5 rounded hover:bg-white"
                  aria-label="Minimize editor"
                  title="Minimize editor"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                <button
                  onClick={handleClose}
                  className="text-gray-400 hover:text-gray-600 transition-colors p-1.5 rounded hover:bg-white"
                  aria-label="Close editor"
                  title="Close editor"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Editor */}
            <div className={isInSplitMode ? "flex-1 overflow-hidden" : "border-b border-gray-200"}>
              <Editor
                height={isInSplitMode ? "100%" : "350px"}
                language="python"
                theme="vs-dark"
                value={codeEditor.code}
                onChange={(value) => setEditorCode(value || '')}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  tabSize: 4,
                  wordWrap: 'on',
                  formatOnPaste: true,
                  formatOnType: true,
                  padding: { top: 16, bottom: 0 },
                }}
                loading={
                  <div className="flex items-center justify-center h-[350px] bg-[#1e1e1e]">
                    <div className="flex flex-col items-center space-y-2">
                      <svg className="animate-spin h-8 w-8 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      <div className="text-white text-sm">Loading editor...</div>
                    </div>
                  </div>
                }
              />
            </div>

            {/* Controls */}
            <div className="px-4 py-2.5 bg-[#2D2D2D] flex items-center justify-between">
              <div className="flex items-center space-x-2">
            <button
              onClick={handleRunCode}
              disabled={isLoading || codeEditor.isExecuting}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
            >
              {isLoading || codeEditor.isExecuting ? (
                <>
                  <svg className="animate-spin h-3.5 w-3.5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Running...</span>
                </>
              ) : (
                <>
                  <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                  <span>Run</span>
                </>
              )}
            </button>

              <button
                onClick={handleAskAI}
                className="flex items-center space-x-1.5 px-3 py-1.5 bg-gray-700 text-gray-200 rounded-lg hover:bg-gray-600 transition-colors text-sm font-medium"
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Ask AI</span>
              </button>

              {/* History Dropdown */}
              {codeEditor.history.length > 0 && (
                <div className="relative">
                  <button
                    onClick={() => setShowHistory(!showHistory)}
                    className="flex items-center space-x-1.5 px-3 py-1.5 bg-gray-700 text-gray-200 rounded-lg hover:bg-gray-600 transition-colors text-sm font-medium"
                    title="View execution history"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>History ({codeEditor.history.length})</span>
                  </button>

                  {showHistory && (
                    <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-gray-200 z-50 max-h-96 overflow-y-auto">
                      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
                        <h4 className="font-semibold text-gray-900 text-sm">Execution History</h4>
                        <p className="text-xs text-gray-500 mt-0.5">Last 5 runs</p>
                      </div>
                      <div className="py-2">
                        {codeEditor.history.map((entry, index) => {
                          const date = new Date(entry.timestamp);
                          const timeAgo = Math.floor((Date.now() - entry.timestamp) / 1000);
                          const timeStr = timeAgo < 60 ? 'Just now' : 
                                         timeAgo < 3600 ? `${Math.floor(timeAgo / 60)}m ago` :
                                         `${Math.floor(timeAgo / 3600)}h ago`;
                          
                          return (
                            <button
                              key={index}
                              onClick={() => {
                                loadFromHistory(index);
                                setShowHistory(false);
                              }}
                              className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-0"
                            >
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-xs text-gray-500">{timeStr}</span>
                                {entry.error ? (
                                  <span className="text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded font-medium">Error</span>
                                ) : (
                                  <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded font-medium">Success</span>
                                )}
                              </div>
                              <div className="text-xs font-mono text-gray-700 line-clamp-2 bg-gray-50 px-2 py-1 rounded">
                                {entry.code.split('\n')[0]}
                                {entry.code.split('\n').length > 1 && '...'}
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

            {/* Output Display */}
            {(codeEditor.lastOutput || codeEditor.lastError) && (
              <div className={`border-t border-gray-200 bg-gray-900 text-white ${isInSplitMode ? 'flex-1 flex flex-col overflow-hidden' : ''}`}>
                <div className="px-6 py-3 border-b border-gray-700 flex items-center justify-between flex-shrink-0">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Output</span>
                    {codeEditor.lastError && (
                      <span className="px-2 py-0.5 bg-red-500/20 text-red-400 text-xs font-semibold rounded">⚠️ Error</span>
                    )}
                    {codeEditor.lastOutput && !codeEditor.lastError && (
                      <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs font-semibold rounded">✓ Success</span>
                    )}
                  </div>
                  {codeEditor.lastError && (
                    <button
                      onClick={handleAskAI}
                      className="text-xs text-blue-400 hover:text-blue-300 transition-colors flex items-center space-x-1"
                    >
                      <span>💡</span>
                      <span>Get help with this error</span>
                    </button>
                  )}
                </div>
                
                <div className={`px-6 py-4 overflow-y-auto ${isInSplitMode ? 'flex-1' : 'max-h-80'}`}>
                  {codeEditor.lastOutput && (
                    <div>
                      <div className="text-xs text-gray-400 mb-2 font-semibold">STDOUT:</div>
                      <pre className="text-sm font-mono whitespace-pre-wrap text-green-400 leading-relaxed">
                        {codeEditor.lastOutput}
                      </pre>
                    </div>
                  )}
                  
                  {codeEditor.lastError && (
                    <div className={codeEditor.lastOutput ? 'mt-4' : ''}>
                      <div className="text-xs text-red-400 mb-2 font-semibold flex items-center space-x-2">
                        <span>ERROR DETAILS:</span>
                      </div>
                      <pre className="text-sm font-mono whitespace-pre-wrap text-red-400 leading-relaxed bg-red-900/10 p-4 rounded-lg border border-red-800/30">
                        {codeEditor.lastError}
                      </pre>
                      <div className="mt-3 text-xs text-gray-400 bg-gray-800/50 p-3 rounded-lg border border-gray-700">
                        <span className="font-semibold text-yellow-400">💡 Tip:</span> Read the error message carefully. 
                        The last line usually tells you what went wrong, and the lines above show where it happened in your code.
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
