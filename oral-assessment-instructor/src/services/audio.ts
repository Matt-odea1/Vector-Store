export interface AudioRecorderOptions {
  mimeType?: string;
  audioBitsPerSecond?: number;
}

export interface RecordingState {
  isRecording: boolean;
  isPaused: boolean;
  duration: number; // in seconds
  audioBlob: Blob | null;
  audioUrl: string | null;
}

export class AudioRecorder {
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private stream: MediaStream | null = null;
  private startTime: number = 0;
  private pausedDuration: number = 0;
  private pauseStartTime: number = 0;

  /**
   * Request microphone permission and initialize recorder
   */
  async initialize(options: AudioRecorderOptions = {}): Promise<void> {
    try {
      // Request microphone access
      this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Determine best MIME type
      const mimeType = this.getSupportedMimeType(options.mimeType);

      // Create MediaRecorder
      this.mediaRecorder = new MediaRecorder(this.stream, {
        mimeType,
        audioBitsPerSecond: options.audioBitsPerSecond || 128000,
      });

      // Handle data available event
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };
    } catch (error) {
      console.error('Error initializing audio recorder:', error);
      throw new Error('Failed to access microphone. Please check permissions.');
    }
  }

  /**
   * Start recording
   */
  startRecording(): void {
    if (!this.mediaRecorder) {
      throw new Error('Recorder not initialized. Call initialize() first.');
    }

    if (this.mediaRecorder.state === 'recording') {
      return;
    }

    this.audioChunks = [];
    this.startTime = Date.now();
    this.pausedDuration = 0;
    this.mediaRecorder.start();
  }

  /**
   * Pause recording
   */
  pauseRecording(): void {
    if (!this.mediaRecorder || this.mediaRecorder.state !== 'recording') {
      return;
    }

    this.pauseStartTime = Date.now();
    this.mediaRecorder.pause();
  }

  /**
   * Resume recording
   */
  resumeRecording(): void {
    if (!this.mediaRecorder || this.mediaRecorder.state !== 'paused') {
      return;
    }

    this.pausedDuration += Date.now() - this.pauseStartTime;
    this.mediaRecorder.resume();
  }

  /**
   * Stop recording and return audio blob
   */
  async stopRecording(): Promise<{ blob: Blob; duration: number }> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('Recorder not initialized'));
        return;
      }

      if (this.mediaRecorder.state === 'inactive') {
        reject(new Error('Recorder is not recording'));
        return;
      }

      this.mediaRecorder.onstop = () => {
        const blob = new Blob(this.audioChunks, { type: this.mediaRecorder!.mimeType });
        const duration = (Date.now() - this.startTime - this.pausedDuration) / 1000;

        resolve({ blob, duration });
      };

      this.mediaRecorder.stop();
    });
  }

  /**
   * Get current recording duration in seconds
   */
  getDuration(): number {
    if (!this.startTime) return 0;

    let elapsed = Date.now() - this.startTime - this.pausedDuration;

    if (this.mediaRecorder?.state === 'paused') {
      elapsed -= Date.now() - this.pauseStartTime;
    }

    return Math.floor(elapsed / 1000);
  }

  /**
   * Get current recording state
   */
  getState(): 'inactive' | 'recording' | 'paused' {
    return this.mediaRecorder?.state || 'inactive';
  }

  /**
   * Stop all audio tracks and clean up
   */
  cleanup(): void {
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }

    this.mediaRecorder = null;
    this.audioChunks = [];
    this.startTime = 0;
    this.pausedDuration = 0;
  }

  /**
   * Check if browser supports audio recording
   */
  static isSupported(): boolean {
    return !!(
      typeof window !== 'undefined' &&
      navigator.mediaDevices &&
      typeof navigator.mediaDevices.getUserMedia === 'function' &&
      typeof MediaRecorder !== 'undefined'
    );
  }

  /**
   * Get the best supported MIME type for recording
   */
  private getSupportedMimeType(preferred?: string): string {
    const types = [
      preferred,
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg;codecs=opus',
      'audio/ogg',
      'audio/wav',
    ].filter(Boolean) as string[];

    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        return type;
      }
    }

    // Fallback to default
    return '';
  }

  /**
   * Create audio URL from blob
   */
  static createAudioUrl(blob: Blob): string {
    return URL.createObjectURL(blob);
  }

  /**
   * Revoke audio URL to free memory
   */
  static revokeAudioUrl(url: string): void {
    URL.revokeObjectURL(url);
  }
}
