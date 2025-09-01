/**
 * Anonymous Flow Component
 * Orchestrates the complete anonymous upload to conversion flow
 * Following frontend best practices: state management, user experience
 */

"use client";

import { useState, useCallback } from "react";
import { useAnonymousSession } from "@/hooks/use-anonymous-session";
import { AnonymousUploadZone } from "./AnonymousUploadZone";
import { BlurredTranscriptionViewer } from "./BlurredTranscriptionViewer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  ArrowLeft, 
  Sparkles, 
  Clock,
  CheckCircle,
  Users,
  Zap
} from "lucide-react";
import { cn } from "@/lib/utils";

type FlowStep = "upload" | "results" | "completed";

interface AnonymousFlowProps {
  onSignupSuccess?: () => void;
  className?: string;
}

export function AnonymousFlow({ onSignupSuccess, className }: AnonymousFlowProps) {
  const [currentStep, setCurrentStep] = useState<FlowStep>("upload");
  const [sessionToken, setSessionToken] = useState<string | null>(null);

  const { currentSession, hasActiveSession, clearSession } = useAnonymousSession();

  // Handle upload completion
  const handleUploadComplete = useCallback((token: string) => {
    setSessionToken(token);
    setCurrentStep("results");
  }, []);

  // Handle starting new upload
  const handleStartNew = useCallback(() => {
    clearSession();
    setSessionToken(null);
    setCurrentStep("upload");
  }, [clearSession]);

  // Handle signup success
  const handleSignupSuccess = useCallback(() => {
    setCurrentStep("completed");
    onSignupSuccess?.();
  }, [onSignupSuccess]);

  // Auto-detect if user has active session on mount
  const activeToken = sessionToken || currentSession?.sessionToken;
  const shouldShowResults = (currentStep === "results" || hasActiveSession) && activeToken;

  return (
    <div className={cn("w-full space-y-6", className)}>
      {/* Progress Indicator */}
      <div className="w-full max-w-4xl mx-auto pt-20 md:pt-24">
        <div className="flex items-center justify-center space-x-4 mb-8">
          <div className={cn(
            "flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium transition-colors",
            currentStep === "upload" 
              ? "bg-primary text-primary-foreground" 
              : "bg-muted text-muted-foreground"
          )}>
            <div className={cn(
              "w-2 h-2 rounded-full",
              currentStep === "upload" ? "bg-primary-foreground" : "bg-muted-foreground"
            )} />
            Upload
          </div>
          
          <div className="w-8 h-px bg-border" />
          
          <div className={cn(
            "flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium transition-colors",
            shouldShowResults
              ? "bg-primary text-primary-foreground" 
              : "bg-muted text-muted-foreground"
          )}>
            <div className={cn(
              "w-2 h-2 rounded-full",
              shouldShowResults ? "bg-primary-foreground" : "bg-muted-foreground"
            )} />
            Preview
          </div>
          
          <div className="w-8 h-px bg-border" />
          
          <div className={cn(
            "flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium transition-colors",
            currentStep === "completed"
              ? "bg-primary text-primary-foreground" 
              : "bg-muted text-muted-foreground"
          )}>
            <div className={cn(
              "w-2 h-2 rounded-full",
              currentStep === "completed" ? "bg-primary-foreground" : "bg-muted-foreground"
            )} />
            Full Access
          </div>
        </div>
      </div>

      {/* Main Content */}
      {shouldShowResults ? (
        <div className="space-y-6">
          {/* Back Button */}
          <div className="w-full max-w-4xl mx-auto">
            <Button
              variant="ghost"
              onClick={handleStartNew}
              className="mb-4"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Start New Upload
            </Button>
          </div>

          {/* Blurred Results */}
          <BlurredTranscriptionViewer
            sessionToken={activeToken}
            onSignupSuccess={handleSignupSuccess}
          />
        </div>
      ) : (
        <div className="space-y-8">
          {/* Hero Section */}
          <div className="text-center space-y-4 max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary rounded-full text-sm font-medium">
              <Sparkles className="h-4 w-4" />
              Try Our AI Transcription Free
            </div>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
              Turn Audio into Text in{" "}
              <span className="text-primary">Seconds</span>
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Upload any audio file and see our AI transcription in action. 
              No signup required to try - just upload and preview your results.
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-8">
            <Card className="text-center">
              <CardContent className="pt-6">
                <div className="mx-auto mb-4 p-3 bg-blue-100 dark:bg-blue-900 rounded-full w-fit">
                  <Clock className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
                <h3 className="font-semibold mb-2">Lightning Fast</h3>
                <p className="text-sm text-muted-foreground">
                  Get your transcription in under 30 seconds with our optimized AI models
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardContent className="pt-6">
                <div className="mx-auto mb-4 p-3 bg-green-100 dark:bg-green-900 rounded-full w-fit">
                  <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <h3 className="font-semibold mb-2">95% Accuracy</h3>
                <p className="text-sm text-muted-foreground">
                  Industry-leading accuracy with support for multiple languages and accents
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardContent className="pt-6">
                <div className="mx-auto mb-4 p-3 bg-purple-100 dark:bg-purple-900 rounded-full w-fit">
                  <Zap className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                </div>
                <h3 className="font-semibold mb-2">AI-Powered</h3>
                <p className="text-sm text-muted-foreground">
                  Advanced AI that understands context, punctuation, and speaker changes
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Upload Zone */}
          <AnonymousUploadZone onUploadComplete={handleUploadComplete} />

          {/* Social Proof */}
          <Card className="max-w-4xl mx-auto bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20 border-blue-200 dark:border-blue-800">
            <CardContent className="pt-6">
              <div className="text-center space-y-4">
                <div className="flex items-center justify-center gap-2">
                  <Users className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  <span className="font-semibold text-blue-800 dark:text-blue-200">
                    Trusted by 10,000+ creators
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">1M+</div>
                    <div className="text-muted-foreground">Hours Transcribed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">50+</div>
                    <div className="text-muted-foreground">Languages Supported</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">4.9★</div>
                    <div className="text-muted-foreground">User Rating</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* FAQ Section */}
          <Card className="max-w-4xl mx-auto">
            <CardHeader>
              <CardTitle className="text-center">Frequently Asked Questions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-2">Is it really free?</h4>
                  <p className="text-sm text-muted-foreground">
                    Yes! You can upload and preview transcriptions without any signup. 
                    Create a free account to access the full transcription and advanced features.
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">What file formats are supported?</h4>
                  <p className="text-sm text-muted-foreground">
                    We support MP3, WAV, M4A, AAC, OGG, WebM, and FLAC files up to 10MB 
                    for anonymous uploads (25MB for registered users).
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">How accurate is the transcription?</h4>
                  <p className="text-sm text-muted-foreground">
                    Our AI achieves 95%+ accuracy on clear audio. Accuracy may vary 
                    based on audio quality, background noise, and speaker clarity.
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Is my data secure?</h4>
                  <p className="text-sm text-muted-foreground">
                    Yes! All uploads are encrypted and anonymous sessions expire after 7 days. 
                    We never store your personal information without explicit consent.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}