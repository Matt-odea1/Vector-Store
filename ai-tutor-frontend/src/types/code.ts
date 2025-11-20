export interface CodeExecutionResult {
  output: string;
  error: string | null;
  executionTime?: number;
}

export interface CodeSnippet {
  id: string;
  code: string;
  language: string;
  output?: string;
  error?: string;
  timestamp: Date;
}

export interface CodeEditorState {
  code: string;
  isOpen: boolean;
  isMinimized: boolean;
  lastOutput: string | null;
  lastError: string | null;
  isExecuting: boolean;
}
