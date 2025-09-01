/**
 * Anonymous API Client
 * Handles API requests for anonymous users (no authentication required)
 * Following frontend best practices: centralized fetch logic, typed responses
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface AnonymousUploadResponse {
  session_token: string;
  project_id: string;
  file_name: string;
  file_size: number;
  status: string;
  estimated_time_seconds: number;
  expires_at: string;
  message: string;
}

export interface AnonymousStatusResponse {
  session_token: string;
  status: string;
  progress_percentage?: number;
  estimated_time_remaining?: number;
  file_name: string;
  file_size: number;
  created_at: string;
  expires_at: string;
  is_expired: boolean;
  error_message?: string;
}

export interface TranscriptionPreview {
  preview_text: string;
  total_word_count: number;
  duration_seconds: number;
  language: string;
  confidence?: number;
  processing_time_ms?: number;
}

export interface AnonymousResultResponse {
  session_token: string;
  status: string;
  transcription_preview?: TranscriptionPreview;
  is_blurred: boolean;
  signup_required: boolean;
  expires_at: string;
  conversion_message: string;
  file_info?: Record<string, any>;
  usage_stats?: Record<string, any>;
  // For compatibility with simple demo API
  demo_preview?: string;
}

export interface AnonymousRateLimitInfo {
  uploads_used_hour: number;
  uploads_used_day: number;
  uploads_remaining_hour: number;
  uploads_remaining_day: number;
  reset_time_hour: string;
  reset_time_day: string;
  is_limited: boolean;
  demo_mode?: boolean;
}

export interface AnonymousApiError {
  error: string;
  message: string;
  details?: {
    file_size_mb?: number;
    max_size_mb?: number;
  };
  signup_suggestion?: string;
}

export class AnonymousApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const config: RequestInit = {
      ...options,
      headers: {
        // Note: No auth headers for anonymous requests
        ...options.headers,
      },
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      let error: AnonymousApiError;
      try {
        const errorData = await response.json();
        // Handle both nested detail object (FastAPI format) and direct error format
        if (errorData.detail) {
          error = {
            error: errorData.detail.error || "API_ERROR",
            message: errorData.detail.message || errorData.detail,
            signup_suggestion: errorData.detail.signup_suggestion
          };
        } else {
          error = errorData;
        }
      } catch {
        error = {
          error: "NETWORK_ERROR",
          message: `Request failed with status ${response.status}`,
          signup_suggestion: "Sign up for priority support and more reliable processing!"
        };
      }
      
      // Create a more detailed error for debugging
      const errorMessage = error.message || "Request failed";
      const detailedError = new Error(errorMessage);
      (detailedError as any).status = response.status;
      (detailedError as any).error = error;
      
      throw detailedError;
    }

    return response.json();
  }

  /**
   * Upload file anonymously
   */
  async uploadFile(
    file: File,
    projectName: string,
    description?: string,
    language: string = "en"
  ): Promise<AnonymousUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("name", projectName);
    if (description) {
      formData.append("description", description);
    }
    formData.append("language", language);

    return this.request<AnonymousUploadResponse>("/anonymous/upload", {
      method: "POST",
      body: formData,
    });
  }

  /**
   * Check processing status for anonymous session
   */
  async getSessionStatus(sessionToken: string): Promise<AnonymousStatusResponse> {
    return this.request<AnonymousStatusResponse>(`/anonymous/${sessionToken}/status`);
  }

  /**
   * Get blurred transcription results
   */
  async getBlurredResults(sessionToken: string): Promise<AnonymousResultResponse> {
    return this.request<AnonymousResultResponse>(`/anonymous/${sessionToken}`);
  }

  /**
   * Get rate limit information
   */
  async getRateLimitInfo(): Promise<AnonymousRateLimitInfo> {
    return this.request<AnonymousRateLimitInfo>("/anonymous/rate-limit");
  }

  /**
   * Health check for anonymous service
   */
  async healthCheck(): Promise<{ status: string; service: string; message: string }> {
    return this.request("/anonymous/health");
  }
}

// Singleton instance for anonymous API client
export const anonymousApi = new AnonymousApiClient();