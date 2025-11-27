/**
 * Centralized logging utility with configurable log levels
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogConfig {
  level: LogLevel;
  enableConsole: boolean;
  enableRemote: boolean;
}

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

class Logger {
  private config: LogConfig;
  
  constructor(config?: Partial<LogConfig>) {
    const envLevel = (import.meta.env.VITE_LOG_LEVEL as LogLevel) || 'info';
    
    this.config = {
      level: envLevel,
      enableConsole: import.meta.env.DEV,
      enableRemote: import.meta.env.VITE_ENABLE_ERROR_TRACKING === 'true',
      ...config,
    };
  }

  private shouldLog(level: LogLevel): boolean {
    return LOG_LEVELS[level] >= LOG_LEVELS[this.config.level];
  }

  private formatMessage(level: LogLevel, message: string, context?: Record<string, unknown>): string {
    const timestamp = new Date().toISOString();
    const contextStr = context ? `\n${JSON.stringify(context, null, 2)}` : '';
    return `[${timestamp}] [${level.toUpperCase()}] ${message}${contextStr}`;
  }

  /**
   * Log a debug message (development only)
   */
  debug(message: string, context?: Record<string, unknown>): void {
    if (!this.shouldLog('debug')) return;
    
    if (this.config.enableConsole) {
      console.log(this.formatMessage('debug', message, context));
    }
  }

  /**
   * Log an informational message
   */
  info(message: string, context?: Record<string, unknown>): void {
    if (!this.shouldLog('info')) return;
    
    if (this.config.enableConsole) {
      console.info(this.formatMessage('info', message, context));
    }
  }

  /**
   * Log a warning message
   */
  warn(message: string, context?: Record<string, unknown>): void {
    if (!this.shouldLog('warn')) return;
    
    if (this.config.enableConsole) {
      console.warn(this.formatMessage('warn', message, context));
    }
    
    // Could send to remote monitoring service here
    if (this.config.enableRemote) {
      this.sendToRemote('warn', message, context);
    }
  }

  /**
   * Log an error message
   */
  error(message: string, error?: Error | unknown, context?: Record<string, unknown>): void {
    if (!this.shouldLog('error')) return;
    
    const errorInfo = error instanceof Error ? {
      name: error.name,
      message: error.message,
      stack: error.stack,
    } : { error };
    
    const fullContext = { ...context, ...errorInfo };
    
    if (this.config.enableConsole) {
      console.error(this.formatMessage('error', message, fullContext));
    }
    
    // Send critical errors to remote monitoring
    if (this.config.enableRemote) {
      this.sendToRemote('error', message, fullContext);
    }
  }

  /**
   * Send log to remote monitoring service
   * (placeholder for future implementation)
   */
  private sendToRemote(level: LogLevel, message: string, context?: Record<string, unknown>): void {
    // TODO: Implement remote logging service integration
    // Examples: Sentry, LogRocket, Datadog, etc.
    if (import.meta.env.DEV) {
      console.log('[Remote Log]', level, message, context);
    }
  }

  /**
   * Update logger configuration at runtime
   */
  setConfig(config: Partial<LogConfig>): void {
    this.config = { ...this.config, ...config };
  }
}

// Export a singleton instance
export const logger = new Logger();

// Export the Logger class for custom instances
export { Logger };
export type { LogLevel, LogConfig };
