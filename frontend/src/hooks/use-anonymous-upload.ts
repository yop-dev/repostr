/**
 * Anonymous Upload Hook
 * Manages the complete anonymous upload flow with state management
 * Following frontend best practices: single responsibility, error handling
 */

"use client";

import { useState, useCallback } from "react";
import { anonymousApi, type AnonymousRateLimitInfo } from "@/lib/api/anonymous-client";
import { useAnonymousSession } from "./use-anonymous-session";

export type UploadStatus = 
  | "idle" 
  | "uploading" 
  | "processing" 
  | "completed" 
  | "error";

export interface UploadProgress {
  status: UploadStatus;
  progress: number; // 0-100
  message: string;
  estimatedTimeRemaining?: number;
}

export interface UploadError {
  code: string;
  message: string;
  signupSuggestion?: string;
  details?: {
    fileSizeMb?: number;
    maxSizeMb?: number;
  };
}

// File validation constants
const ACCEPTED_AUDIO_TYPES = [
  'audio/mpeg',
  'audio/mp3', 
  'audio/wav',
  'audio/m4a',
  'audio/aac',
  'audio/ogg',
  'audio/webm',
  'audio/flac'
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB for anonymous users
const ALLOWED_EXTENSIONS = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.webm', '.flac'];

export function useAnonymousUpload() {
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({
    status: "idle",
    progress: 0,
    message: "Ready to upload"
  });
  const [uploadError, setUploadError] = useState<UploadError | null>(null);
  const [rateLimitInfo, setRateLimitInfo] = useState<AnonymousRateLimitInfo | null>(null);

  const { saveSession, pollSessionStatus } = useAnonymousSession();

  /**
   * Validate file before upload
   */
  const validateFile = useCallback((file: File): UploadError | null => {
    // Check file type
    if (!ACCEPTED_AUDIO_TYPES.includes(file.type)) {
      const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      if (!ALLOWED_EXTENSIONS.includes(extension)) {
        return {
          code: "INVALID_FILE_TYPE",
          message: `Unsupported file type: ${file.type || extension}. Please upload audio files only.`,
          signupSuggestion: "Sign up for support for more file formats!"
        };
      }
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return {
        code: "FILE_TOO_LARGE",
        message: `File size exceeds 10MB limit for anonymous uploads.`,
        signupSuggestion: "Sign up for free to upload files up to 25MB!",
        details: {
          fileSizeMb: Math.round(file.size / (1024 * 1024) * 100) / 100,
          maxSizeMb: 10
        }
      };
    }

    // Check if file is empty
    if (file.size === 0) {
      return {
        code: "EMPTY_FILE",
        message: "The selected file is empty. Please choose a valid audio file.",
        signupSuggestion: "Sign up for file validation assistance!"
      };
    }

    return null;
  }, []);

  /**
   * Check rate limits before upload
   */
  const checkRateLimits = useCallback(async (): Promise<boolean> => {
    try {
      const rateLimits = await anonymousApi.getRateLimitInfo();
      setRateLimitInfo(rateLimits);

      if (rateLimits.is_limited || rateLimits.uploads_remaining_day <= 0) {
        setUploadError({
          code: "RATE_LIMITED",
          message: `You've reached the daily upload limit for anonymous users (${rateLimits.uploads_used_day} uploads).`,
          signupSuggestion: "Sign up for free to get higher upload limits!"
        });
        return false;
      }

      return true;
    } catch (error) {
      console.error("Error checking rate limits:", error);
      // Allow upload to proceed if rate limit check fails
      return true;
    }
  }, []);

  /**
   * Upload file anonymously
   */
  const uploadFile = useCallback(async (
    file: File,
    projectName: string,
    description?: string,
    language: string = "en"
  ): Promise<{ success: boolean; sessionToken?: string }> => {
    // Reset state
    setUploadError(null);
    setUploadProgress({
      status: "uploading",
      progress: 0,
      message: "Preparing upload..."
    });

    try {
      // Validate file
      const validationError = validateFile(file);
      if (validationError) {
        setUploadError(validationError);
        setUploadProgress({
          status: "error",
          progress: 0,
          message: validationError.message
        });
        return { success: false };
      }

      // Check rate limits
      const canUpload = await checkRateLimits();
      if (!canUpload) {
        setUploadProgress({
          status: "error", 
          progress: 0,
          message: "Upload limit reached"
        });
        return { success: false };
      }

      // Update progress
      setUploadProgress({
        status: "uploading",
        progress: 25,
        message: "Uploading file..."
      });

      // Upload file
      const uploadResponse = await anonymousApi.uploadFile(
        file,
        projectName,
        description,
        language
      );

      // Save session
      saveSession(uploadResponse);

      // Update progress
      setUploadProgress({
        status: "processing",
        progress: 50,
        message: "Processing audio...",
        estimatedTimeRemaining: uploadResponse.estimated_time_seconds
      });

      // Start polling for completion
      pollSessionStatus(
        uploadResponse.session_token,
        (status) => {
          if (status === "completed") {
            setUploadProgress({
              status: "completed",
              progress: 100,
              message: "Transcription complete!"
            });
          } else if (status === "failed") {
            setUploadProgress({
              status: "error",
              progress: 0,
              message: "Processing failed"
            });
            setUploadError({
              code: "PROCESSING_FAILED",
              message: "Audio processing failed. Please try again.",
              signupSuggestion: "Sign up for priority processing and support!"
            });
          } else {
            // Update progress during processing
            const progressValue = status === "processing" ? 75 : 50;
            setUploadProgress(prev => ({
              ...prev,
              progress: progressValue,
              message: "Processing audio..."
            }));
          }
        }
      );

      return { success: true, sessionToken: uploadResponse.session_token };

    } catch (error: any) {
      console.error("Upload error:", error);
      
      // Extract detailed error information
      let errorMessage = "Upload failed";
      let errorCode = "UPLOAD_FAILED";
      let signupSuggestion = "Sign up for priority support and more reliable processing!";
      
      if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      // Check if it's an API error object with additional details
      if (error && typeof error === 'object') {
        // Handle different error structures
        if (error.error && typeof error.error === 'object') {
          errorMessage = error.error.message || errorMessage;
          signupSuggestion = error.error.signup_suggestion || signupSuggestion;
          errorCode = error.error.error || errorCode;
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        // Add HTTP status if available
        if (error.status) {
          errorMessage = `${errorMessage} (HTTP ${error.status})`;
        }
      }
      
      // Log additional debug information
      console.error("Detailed upload error:", {
        message: errorMessage,
        status: error?.status,
        error: error?.error,
        fullError: error
      });
      
      setUploadError({
        code: errorCode,
        message: errorMessage,
        signupSuggestion
      });
      
      setUploadProgress({
        status: "error",
        progress: 0,
        message: errorMessage
      });
      
      return { success: false };
    }
  }, [validateFile, checkRateLimits, saveSession, pollSessionStatus]);

  /**
   * Reset upload state
   */
  const resetUpload = useCallback(() => {
    setUploadProgress({
      status: "idle",
      progress: 0,
      message: "Ready to upload"
    });
    setUploadError(null);
  }, []);

  /**
   * Format file size for display
   */
  const formatFileSize = useCallback((bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  }, []);

  /**
   * Get upload limits for display
   */
  const getUploadLimits = useCallback(() => {
    return {
      maxFileSize: MAX_FILE_SIZE,
      maxFileSizeFormatted: formatFileSize(MAX_FILE_SIZE),
      acceptedTypes: ACCEPTED_AUDIO_TYPES,
      acceptedExtensions: ALLOWED_EXTENSIONS
    };
  }, [formatFileSize]);

  return {
    // State
    uploadProgress,
    uploadError,
    rateLimitInfo,
    isUploading: uploadProgress.status === "uploading",
    isProcessing: uploadProgress.status === "processing", 
    isCompleted: uploadProgress.status === "completed",
    hasError: uploadProgress.status === "error",
    
    // Actions
    uploadFile,
    resetUpload,
    validateFile,
    checkRateLimits,
    
    // Utilities
    formatFileSize,
    getUploadLimits,
  };
}