/**
 * S3 Upload Service - Handles audio file uploads
 */

import { getUploadUrl, uploadAudioToS3 } from './api';

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

/**
 * Upload audio blob to S3 and return the file URL
 */
export async function uploadAudio(
  audioBlob: Blob,
  studentId: string,
  questionId: string,
  onProgress?: (progress: UploadProgress) => void
): Promise<string> {
  try {
    // Generate filename
    const timestamp = Date.now();
    const filename = `audio/${studentId}/${questionId}_${timestamp}.webm`;

    // Get presigned URL from backend
    const { uploadUrl, fileUrl } = await getUploadUrl(filename, audioBlob.type);

    // Upload to S3
    await uploadAudioToS3(uploadUrl, audioBlob, (percentage) => {
      if (onProgress) {
        onProgress({
          loaded: (audioBlob.size * percentage) / 100,
          total: audioBlob.size,
          percentage,
        });
      }
    });

    return fileUrl;
  } catch (error) {
    console.error('Failed to upload audio:', error);
    throw new Error('Failed to upload audio file. Please try again.');
  }
}

/**
 * Validate audio blob before upload
 */
export function validateAudioBlob(blob: Blob, maxSizeMB: number = 50): boolean {
  if (!blob || blob.size === 0) {
    throw new Error('Audio recording is empty');
  }

  const maxSizeBytes = maxSizeMB * 1024 * 1024;
  if (blob.size > maxSizeBytes) {
    throw new Error(`Audio file is too large. Maximum size is ${maxSizeMB}MB`);
  }

  if (!blob.type.includes('audio')) {
    throw new Error('Invalid audio format');
  }

  return true;
}

/**
 * Format file size for display
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

export default {
  uploadAudio,
  validateAudioBlob,
  formatFileSize,
};
