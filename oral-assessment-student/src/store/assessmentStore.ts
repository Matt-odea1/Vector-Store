/**
 * Zustand Store - Global state management for student assessment
 */

import { create } from 'zustand';
import type {
  Question,
  Progress,
  Results,
  Assessment,
  ApiError,
} from '../types';
import {
  getQuestions,
  submitAnswer,
  submitAssessment,
  getProgress,
  getResults,
} from '../services/api';
import { uploadAudio, validateAudioBlob } from '../services/s3';
import AudioRecorder from '../services/audio';

interface AssessmentStore {
  // Student info
  studentId: string | null;
  assessmentId: string | null;
  assessment: Assessment | null;

  // Questions
  questions: Question[];
  currentQuestionIndex: number;

  // Progress
  progress: Progress | null;

  // Recording state
  isRecording: boolean;
  isPaused: boolean;
  recordingDuration: number;
  recordedBlob: Blob | null;
  recordingStartTime: number | null;
  audioRecorder: AudioRecorder | null;

  // Playback
  isPlaying: boolean;
  playbackUrl: string | null;

  // Upload state
  isUploading: boolean;
  uploadProgress: number;

  // Results
  results: Results | null;
  isResultsReady: boolean;

  // Loading and error states
  isLoading: boolean;
  error: ApiError | null;

  // Actions
  setStudentInfo: (studentId: string, assessmentId: string) => void;
  loadQuestions: () => Promise<void>;
  loadProgress: () => Promise<void>;
  
  // Recording actions
  initializeRecorder: () => Promise<void>;
  startRecording: () => void;
  stopRecording: () => Promise<void>;
  pauseRecording: () => void;
  resumeRecording: () => void;
  cancelRecording: () => void;
  
  // Playback actions
  playRecording: () => void;
  stopPlayback: () => void;

  // Navigation
  nextQuestion: () => void;
  previousQuestion: () => void;
  goToQuestion: (index: number) => void;

  // Submission
  submitCurrentAnswer: () => Promise<void>;
  submitCompleteAssessment: () => Promise<void>;

  // Results
  loadResults: () => Promise<void>;

  // Utility
  clearError: () => void;
  reset: () => void;
}

export const useAssessmentStore = create<AssessmentStore>((set, get) => ({
  // Initial state
  studentId: null,
  assessmentId: null,
  assessment: null,
  questions: [],
  currentQuestionIndex: 0,
  progress: null,
  isRecording: false,
  isPaused: false,
  recordingDuration: 0,
  recordedBlob: null,
  recordingStartTime: null,
  audioRecorder: null,
  isPlaying: false,
  playbackUrl: null,
  isUploading: false,
  uploadProgress: 0,
  results: null,
  isResultsReady: false,
  isLoading: false,
  error: null,

  // Set student and assessment IDs
  setStudentInfo: (studentId: string, assessmentId: string) => {
    set({ studentId, assessmentId, error: null });
  },

  // Load questions from backend
  loadQuestions: async () => {
    const { studentId, assessmentId } = get();
    if (!studentId || !assessmentId) {
      set({ error: { message: 'Student ID or Assessment ID not set' } });
      return;
    }

    set({ isLoading: true, error: null });

    try {
      const questions = await getQuestions(studentId, assessmentId);
      set({ questions, isLoading: false });
    } catch (error) {
      set({ error: error as ApiError, isLoading: false });
    }
  },

  // Load progress
  loadProgress: async () => {
    const { studentId, assessmentId } = get();
    if (!studentId || !assessmentId) return;

    try {
      const progress = await getProgress(studentId, assessmentId);
      set({ progress });
    } catch (error) {
      console.error('Failed to load progress:', error);
    }
  },

  // Initialize audio recorder
  initializeRecorder: async () => {
    try {
      const recorder = new AudioRecorder();
      await recorder.initialize();
      set({ audioRecorder: recorder, error: null });
    } catch (error) {
      set({ 
        error: { 
          message: error instanceof Error ? error.message : 'Failed to initialize recorder' 
        } 
      });
      throw error;
    }
  },

  // Start recording
  startRecording: () => {
    const { audioRecorder } = get();
    if (!audioRecorder) {
      set({ error: { message: 'Recorder not initialized' } });
      return;
    }

    try {
      audioRecorder.start();
      set({
        isRecording: true,
        isPaused: false,
        recordingStartTime: Date.now(),
        recordedBlob: null,
        playbackUrl: null,
        error: null,
      });

      // Update duration every second
      const interval = setInterval(() => {
        const { isRecording, audioRecorder } = get();
        if (!isRecording || !audioRecorder) {
          clearInterval(interval);
          return;
        }
        set({ recordingDuration: audioRecorder.getDuration() });
      }, 1000);
    } catch (error) {
      set({ 
        error: { 
          message: error instanceof Error ? error.message : 'Failed to start recording' 
        } 
      });
    }
  },

  // Stop recording
  stopRecording: async () => {
    const { audioRecorder } = get();
    if (!audioRecorder) return;

    try {
      const blob = await audioRecorder.stop();
      const duration = audioRecorder.getDuration();
      
      set({
        isRecording: false,
        isPaused: false,
        recordedBlob: blob,
        recordingDuration: duration,
      });
    } catch (error) {
      set({ 
        error: { 
          message: error instanceof Error ? error.message : 'Failed to stop recording' 
        },
        isRecording: false,
      });
    }
  },

  // Pause recording
  pauseRecording: () => {
    const { audioRecorder } = get();
    if (!audioRecorder) return;

    audioRecorder.pause();
    set({ isPaused: true });
  },

  // Resume recording
  resumeRecording: () => {
    const { audioRecorder } = get();
    if (!audioRecorder) return;

    audioRecorder.resume();
    set({ isPaused: false });
  },

  // Cancel recording
  cancelRecording: () => {
    const { audioRecorder } = get();
    if (!audioRecorder) return;

    try {
      if (audioRecorder.getState() !== 'inactive') {
        audioRecorder.stop();
      }
    } catch (error) {
      console.error('Error stopping recorder:', error);
    }

    set({
      isRecording: false,
      isPaused: false,
      recordedBlob: null,
      recordingDuration: 0,
      recordingStartTime: null,
      playbackUrl: null,
    });
  },

  // Play recorded audio
  playRecording: () => {
    const { recordedBlob, audioRecorder } = get();
    if (!recordedBlob || !audioRecorder) return;

    const url = audioRecorder.createAudioUrl(recordedBlob);
    const audio = new Audio(url);
    
    audio.onended = () => {
      set({ isPlaying: false });
      audioRecorder.releaseAudioUrl(url);
    };

    audio.play();
    set({ isPlaying: true, playbackUrl: url });
  },

  // Stop playback
  stopPlayback: () => {
    set({ isPlaying: false });
  },

  // Navigate to next question
  nextQuestion: () => {
    const { currentQuestionIndex, questions } = get();
    if (currentQuestionIndex < questions.length - 1) {
      set({ 
        currentQuestionIndex: currentQuestionIndex + 1,
        recordedBlob: null,
        recordingDuration: 0,
        playbackUrl: null,
        error: null,
      });
    }
  },

  // Navigate to previous question
  previousQuestion: () => {
    const { currentQuestionIndex } = get();
    if (currentQuestionIndex > 0) {
      set({ 
        currentQuestionIndex: currentQuestionIndex - 1,
        recordedBlob: null,
        recordingDuration: 0,
        playbackUrl: null,
        error: null,
      });
    }
  },

  // Go to specific question
  goToQuestion: (index: number) => {
    const { questions } = get();
    if (index >= 0 && index < questions.length) {
      set({ 
        currentQuestionIndex: index,
        recordedBlob: null,
        recordingDuration: 0,
        playbackUrl: null,
        error: null,
      });
    }
  },

  // Submit current answer
  submitCurrentAnswer: async () => {
    const {
      studentId,
      recordedBlob,
      recordingDuration,
      questions,
      currentQuestionIndex,
    } = get();

    if (!studentId || !recordedBlob) {
      set({ error: { message: 'No recording to submit' } });
      return;
    }

    const currentQuestion = questions[currentQuestionIndex];
    if (!currentQuestion) {
      set({ error: { message: 'Invalid question' } });
      return;
    }

    set({ isUploading: true, uploadProgress: 0, error: null });

    try {
      // Validate audio
      validateAudioBlob(recordedBlob);

      // Upload to S3
      const audioUrl = await uploadAudio(
        recordedBlob,
        studentId,
        currentQuestion.id,
        (progress) => {
          set({ uploadProgress: progress.percentage });
        }
      );

      // Submit answer to backend
      await submitAnswer(studentId, currentQuestion.id, audioUrl, recordingDuration);

      // Reload progress
      await get().loadProgress();

      set({
        isUploading: false,
        uploadProgress: 0,
        recordedBlob: null,
        recordingDuration: 0,
        playbackUrl: null,
      });

      // Auto-advance to next question if not last
      if (currentQuestionIndex < questions.length - 1) {
        get().nextQuestion();
      }
    } catch (error) {
      set({
        error: error as ApiError,
        isUploading: false,
        uploadProgress: 0,
      });
    }
  },

  // Submit complete assessment
  submitCompleteAssessment: async () => {
    const { studentId, assessmentId } = get();
    if (!studentId || !assessmentId) return;

    set({ isLoading: true, error: null });

    try {
      await submitAssessment(studentId, assessmentId);
      await get().loadProgress();
      set({ isLoading: false });
    } catch (error) {
      set({ error: error as ApiError, isLoading: false });
    }
  },

  // Load results
  loadResults: async () => {
    const { studentId, assessmentId } = get();
    if (!studentId || !assessmentId) return;

    set({ isLoading: true, error: null });

    try {
      const results = await getResults(studentId, assessmentId);
      set({ results, isResultsReady: true, isLoading: false });
    } catch (error) {
      set({ 
        error: error as ApiError, 
        isResultsReady: false,
        isLoading: false 
      });
    }
  },

  // Clear error
  clearError: () => {
    set({ error: null });
  },

  // Reset store
  reset: () => {
    const { audioRecorder } = get();
    if (audioRecorder) {
      audioRecorder.cleanup();
    }

    set({
      studentId: null,
      assessmentId: null,
      assessment: null,
      questions: [],
      currentQuestionIndex: 0,
      progress: null,
      isRecording: false,
      isPaused: false,
      recordingDuration: 0,
      recordedBlob: null,
      recordingStartTime: null,
      audioRecorder: null,
      isPlaying: false,
      playbackUrl: null,
      isUploading: false,
      uploadProgress: 0,
      results: null,
      isResultsReady: false,
      isLoading: false,
      error: null,
    });
  },
}));

export default useAssessmentStore;
