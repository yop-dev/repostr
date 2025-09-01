/**
 * Anonymous Session Management Hook
 * Handles localStorage persistence and session state for anonymous users
 * Following frontend best practices: local state management, type safety
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import { anonymousApi, type AnonymousUploadResponse } from "@/lib/api/anonymous-client";

export interface AnonymousSession {
  sessionToken: string;
  projectId: string;
  fileName: string;
  fileSize: number;
  status: string;
  createdAt: string;
  expiresAt: string;
}

const STORAGE_KEY = "anonymous_session_token";
const SESSION_DATA_KEY = "anonymous_session_data";

export function useAnonymousSession() {
  const [currentSession, setCurrentSession] = useState<AnonymousSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load session from localStorage on mount
  useEffect(() => {
    const loadSession = () => {
      try {
        const sessionToken = localStorage.getItem(STORAGE_KEY);
        const sessionData = localStorage.getItem(SESSION_DATA_KEY);
        
        if (sessionToken && sessionData) {
          const session: AnonymousSession = JSON.parse(sessionData);
          
          // Check if session is expired
          const now = new Date();
          const expiresAt = new Date(session.expiresAt);
          
          if (now < expiresAt) {
            setCurrentSession(session);
          } else {
            // Clean up expired session
            clearSession();
          }
        }
      } catch (error) {
        console.error("Error loading anonymous session:", error);
        clearSession();
      } finally {
        setIsLoading(false);
      }
    };

    loadSession();
  }, []);

  /**
   * Save a new anonymous session
   */
  const saveSession = useCallback((uploadResponse: AnonymousUploadResponse) => {
    const session: AnonymousSession = {
      sessionToken: uploadResponse.session_token,
      projectId: uploadResponse.project_id,
      fileName: uploadResponse.file_name,
      fileSize: uploadResponse.file_size,
      status: uploadResponse.status,
      createdAt: new Date().toISOString(),
      expiresAt: uploadResponse.expires_at,
    };

    try {
      localStorage.setItem(STORAGE_KEY, session.sessionToken);
      localStorage.setItem(SESSION_DATA_KEY, JSON.stringify(session));
      setCurrentSession(session);
    } catch (error) {
      console.error("Error saving anonymous session:", error);
      throw new Error("Failed to save session");
    }
  }, []);

  /**
   * Update session status (e.g., from 'processing' to 'completed')
   */
  const updateSessionStatus = useCallback((status: string) => {
    if (!currentSession) return;

    const updatedSession = {
      ...currentSession,
      status,
    };

    try {
      localStorage.setItem(SESSION_DATA_KEY, JSON.stringify(updatedSession));
      setCurrentSession(updatedSession);
    } catch (error) {
      console.error("Error updating session status:", error);
    }
  }, [currentSession]);

  /**
   * Clear the current session (e.g., after signup/claim)
   */
  const clearSession = useCallback(() => {
    try {
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(SESSION_DATA_KEY);
      setCurrentSession(null);
    } catch (error) {
      console.error("Error clearing session:", error);
    }
  }, []);

  /**
   * Check if session is expired
   */
  const isSessionExpired = useCallback((session?: AnonymousSession) => {
    const sessionToCheck = session || currentSession;
    if (!sessionToCheck) return true;

    const now = new Date();
    const expiresAt = new Date(sessionToCheck.expiresAt);
    return now >= expiresAt;
  }, [currentSession]);

  /**
   * Get time remaining until session expires
   */
  const getTimeRemaining = useCallback((session?: AnonymousSession) => {
    const sessionToCheck = session || currentSession;
    if (!sessionToCheck) return 0;

    const now = new Date();
    const expiresAt = new Date(sessionToCheck.expiresAt);
    return Math.max(0, expiresAt.getTime() - now.getTime());
  }, [currentSession]);

  /**
   * Format time remaining as human-readable string
   */
  const formatTimeRemaining = useCallback((session?: AnonymousSession) => {
    const timeRemaining = getTimeRemaining(session);
    
    if (timeRemaining <= 0) return "Expired";

    const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));

    if (days > 0) {
      return `${days} day${days > 1 ? 's' : ''} remaining`;
    } else if (hours > 0) {
      return `${hours} hour${hours > 1 ? 's' : ''} remaining`;
    } else {
      return `${minutes} minute${minutes > 1 ? 's' : ''} remaining`;
    }
  }, [getTimeRemaining]);

  /**
   * Poll session status until completion
   */
  const pollSessionStatus = useCallback(async (
    sessionToken: string,
    onStatusUpdate?: (status: string) => void,
    maxAttempts: number = 60, // 5 minutes with 5-second intervals
    intervalMs: number = 5000
  ) => {
    let attempts = 0;
    
    const poll = async (): Promise<void> => {
      try {
        const statusResponse = await anonymousApi.getSessionStatus(sessionToken);
        
        updateSessionStatus(statusResponse.status);
        onStatusUpdate?.(statusResponse.status);

        // Stop polling if completed or failed
        if (statusResponse.status === "completed" || statusResponse.status === "failed") {
          return;
        }

        // Continue polling if not max attempts reached
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, intervalMs);
        }
      } catch (error) {
        console.error("Error polling session status:", error);
        // Stop polling on error
      }
    };

    // Start polling
    poll();
  }, [updateSessionStatus]);

  return {
    // State
    currentSession,
    isLoading,
    hasActiveSession: !!currentSession && !isSessionExpired(),
    
    // Actions
    saveSession,
    updateSessionStatus,
    clearSession,
    pollSessionStatus,
    
    // Utilities
    isSessionExpired,
    getTimeRemaining,
    formatTimeRemaining,
  };
}