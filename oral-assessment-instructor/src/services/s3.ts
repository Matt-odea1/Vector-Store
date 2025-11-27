import { apiService } from './api';
import type { GetPresignedUrlRequest, PresignedUrlResponse } from '../../../shared/types/assessment';

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

class S3Service {
  /**
   * Upload audio file to S3 using pre-signed URL
   */
  async uploadAudio(
    assessmentId: string,
    studentId: string,
    questionId: string,
    audioFile: File,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<string> {
    try {
      // Step 1: Get pre-signed upload URL from backend
      const request: GetPresignedUrlRequest = {
        assessmentId,
        studentId,
        questionId,
        fileName: audioFile.name,
        contentType: audioFile.type || 'audio/webm',
      };

      const urlData: PresignedUrlResponse = await apiService.getPresignedUploadUrl(request);

      // Step 2: Upload directly to S3
      await this.uploadToS3(urlData.uploadUrl, audioFile, onProgress);

      // Step 3: Return the final file URL
      return urlData.fileUrl;
    } catch (error) {
      console.error('Error uploading audio to S3:', error);
      throw new Error('Failed to upload audio file. Please try again.');
    }
  }

  /**
   * Direct upload to S3 using pre-signed URL
   */
  private async uploadToS3(
    presignedUrl: string,
    file: File,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // Track upload progress
      if (onProgress) {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress: UploadProgress = {
              loaded: event.loaded,
              total: event.total,
              percentage: Math.round((event.loaded / event.total) * 100),
            };
            onProgress(progress);
          }
        });
      }

      // Handle completion
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve();
        } else {
          reject(new Error(`Upload failed with status ${xhr.status}`));
        }
      });

      // Handle errors
      xhr.addEventListener('error', () => {
        reject(new Error('Network error during upload'));
      });

      xhr.addEventListener('abort', () => {
        reject(new Error('Upload was aborted'));
      });

      // Initiate upload
      xhr.open('PUT', presignedUrl);
      xhr.setRequestHeader('Content-Type', file.type || 'audio/webm');
      xhr.send(file);
    });
  }

  /**
   * Generate a unique filename for audio recordings
   */
  generateFileName(studentId: string, questionId: string, extension: string = 'webm'): string {
    const timestamp = Date.now();
    return `${studentId}_${questionId}_${timestamp}.${extension}`;
  }

  /**
   * Validate audio file before upload
   */
  validateAudioFile(file: File): { valid: boolean; error?: string } {
    // Check file size (max 50MB)
    const MAX_SIZE = 50 * 1024 * 1024; // 50MB
    if (file.size > MAX_SIZE) {
      return {
        valid: false,
        error: 'Audio file is too large. Maximum size is 50MB.',
      };
    }

    // Check file type
    const validTypes = ['audio/webm', 'audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/ogg'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(webm|wav|mp3|ogg)$/i)) {
      return {
        valid: false,
        error: 'Invalid audio format. Supported formats: WebM, WAV, MP3, OGG.',
      };
    }

    return { valid: true };
  }
}

export const s3Service = new S3Service();
