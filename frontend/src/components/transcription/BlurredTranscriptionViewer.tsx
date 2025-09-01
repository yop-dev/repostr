/**
 * Blurred Transcription Viewer Component
 * Shows blurred preview with conversion-optimized signup overlay
 * Following frontend best practices: accessibility, conversion optimization
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { anonymousApi, type AnonymousResultResponse } from "@/lib/api/anonymous-client";
import { useAnonymousSession } from "@/hooks/use-anonymous-session";
import { SignInButton, SignUpButton } from "@clerk/nextjs";
import { 
  CheckCircle, 
  Clock, 
  FileText, 
  Sparkles, 
  Users, 
  Zap,
  Eye,
  EyeOff,
  Star,
  ArrowRight,
  Loader2,
  X
} from "lucide-react";
import { cn } from "@/lib/utils";

interface BlurredTranscriptionViewerProps {
  sessionToken?: string;
  onSignupSuccess?: () => void;
  className?: string;
}

export function BlurredTranscriptionViewer({ 
  sessionToken, 
  onSignupSuccess: _onSignupSuccess,
  className 
}: BlurredTranscriptionViewerProps) {
  const [results, setResults] = useState<AnonymousResultResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [showSignupModal, setShowSignupModal] = useState(false);

  const { currentSession, formatTimeRemaining } = useAnonymousSession();

  // Use provided sessionToken or current session
  const activeSessionToken = sessionToken || currentSession?.sessionToken;

  // Fetch blurred results
  const fetchResults = useCallback(async () => {
    if (!activeSessionToken) {
      setError("No active session found");
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      
      const response = await anonymousApi.getBlurredResults(activeSessionToken);
      setResults(response);
    } catch (err) {
      console.error("Error fetching blurred results:", err);
      setError(err instanceof Error ? err.message : "Failed to load results");
    } finally {
      setIsLoading(false);
    }
  }, [activeSessionToken]);

  useEffect(() => {
    fetchResults();
  }, [fetchResults]);

  // Calculate estimated metrics for social proof
  const getEstimatedMetrics = useCallback(() => {
    if (!results || !currentSession) return null;

    const fileSizeKB = currentSession.fileSize / 1024;
    const estimatedDuration = Math.max(30, Math.round(fileSizeKB / 10)); // Rough estimate
    const estimatedWords = Math.max(50, Math.round(estimatedDuration * 2.5)); // ~150 WPM / 60 seconds

    return {
      duration: estimatedDuration,
      words: estimatedWords,
      pages: Math.ceil(estimatedWords / 250) // ~250 words per page
    };
  }, [results, currentSession]);

  const metrics = getEstimatedMetrics();

  if (isLoading) {
    return (
      <Card className={cn("w-full max-w-4xl mx-auto", className)}>
        <CardContent className="flex items-center justify-center py-12">
          <div className="text-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
            <p className="text-muted-foreground">Loading your transcription...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !results) {
    return (
      <Card className={cn("w-full max-w-4xl mx-auto", className)}>
        <CardContent className="text-center py-12">
          <div className="space-y-4">
            <FileText className="h-12 w-12 mx-auto text-muted-foreground" />
            <div>
              <h3 className="text-lg font-semibold">Unable to Load Results</h3>
              <p className="text-muted-foreground">{error}</p>
            </div>
            <Button onClick={fetchResults} variant="outline">
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className={cn("w-full max-w-4xl mx-auto space-y-6", className)}>
      {/* Success Header */}
      <Card className="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-950/20 dark:to-blue-950/20 border-green-200 dark:border-green-800">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-full">
              <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <CardTitle className="text-green-800 dark:text-green-200">
                Transcription Complete! 🎉
              </CardTitle>
              <p className="text-green-700 dark:text-green-300 text-sm">
                Your audio has been successfully processed
              </p>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Metrics & Social Proof */}
      {metrics && (
        <Card>
          <CardContent className="pt-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div className="space-y-1">
                <div className="text-2xl font-bold text-primary">
                  {results.transcription_preview?.duration_seconds ? 
                    Math.round(results.transcription_preview.duration_seconds) + 's' : 
                    metrics.duration + 's'}
                </div>
                <div className="text-xs text-muted-foreground">Audio Duration</div>
              </div>
              <div className="space-y-1">
                <div className="text-2xl font-bold text-primary">
                  ~{results.transcription_preview?.total_word_count || metrics.words}
                </div>
                <div className="text-xs text-muted-foreground">Words Transcribed</div>
              </div>
              <div className="space-y-1">
                <div className="text-2xl font-bold text-primary">{metrics.pages}</div>
                <div className="text-xs text-muted-foreground">Pages of Content</div>
              </div>
              <div className="space-y-1">
                <div className="text-2xl font-bold text-primary">
                  {results.transcription_preview?.confidence ? 
                    Math.round(results.transcription_preview.confidence * 100) + '%' : 
                    '95%'}
                </div>
                <div className="text-xs text-muted-foreground">Accuracy</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Blurred Preview */}
      <div className="relative">
        <Card className="relative overflow-hidden">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Your Transcription Preview
              </CardTitle>
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {currentSession && formatTimeRemaining(currentSession)}
                </Badge>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowPreview(!showPreview)}
                  className="text-xs"
                >
                  {showPreview ? (
                    <>
                      <EyeOff className="h-3 w-3 mr-1" />
                      Hide Preview
                    </>
                  ) : (
                    <>
                      <Eye className="h-3 w-3 mr-1" />
                      Show Preview
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {/* Blurred Content */}
            <div 
              className={cn(
                "relative transition-all duration-300",
                showPreview ? "filter-none" : "filter blur-sm select-none"
              )}
            >
              <div className="p-6 bg-muted/30 rounded-lg min-h-[200px]">
                <p className="text-sm leading-relaxed text-foreground/80">
                  {results.transcription_preview?.preview_text || 
                   results.demo_preview || 
                   "Your transcription is ready! The preview content will appear here once you sign up to view the full results."}
                </p>
                {!showPreview && (
                  <div className="mt-4 space-y-2">
                    <div className="h-4 bg-muted rounded w-3/4"></div>
                    <div className="h-4 bg-muted rounded w-1/2"></div>
                    <div className="h-4 bg-muted rounded w-5/6"></div>
                    <div className="h-4 bg-muted rounded w-2/3"></div>
                  </div>
                )}
              </div>
            </div>
            
            {/* View Full Transcription Button */}
            <div className="mt-6 text-center">
              <Button 
                onClick={() => setShowSignupModal(true)}
                size="lg" 
                className="group"
              >
                View Full Transcription
                <Sparkles className="h-4 w-4 ml-2 group-hover:scale-110 transition-transform" />
              </Button>
              <p className="text-xs text-muted-foreground mt-2">
                Sign up free to access the complete transcription
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Signup Modal - Now outside the card */}
        {showSignupModal && (
          <div 
            className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50"
            onClick={() => setShowSignupModal(false)}
          >
            <Card 
              className="w-full max-w-md mx-4 shadow-2xl border-2 border-primary/20 bg-background"
              onClick={(e) => e.stopPropagation()}
            >
              <CardHeader className="text-center pb-4 relative">
                <Button
                  variant="ghost"
                  size="sm"
                  className="absolute right-2 top-2 h-8 w-8 p-0 hover:bg-muted"
                  onClick={() => setShowSignupModal(false)}
                >
                  <X className="h-4 w-4" />
                </Button>
                <div className="mx-auto mb-4 p-3 bg-primary/10 rounded-full w-fit">
                  <Sparkles className="h-8 w-8 text-primary" />
                </div>
                <CardTitle className="text-xl">Ready to View Your Full Transcription?</CardTitle>
                <p className="text-muted-foreground text-sm">
                  {results.conversion_message || 
                   "Sign up free to access your complete transcription with timestamps and advanced features!"}
                </p>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Value Props */}
                <div className="space-y-3">
                  <div className="flex items-center gap-3 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                    <span>Complete transcription with timestamps</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm">
                    <Zap className="h-4 w-4 text-yellow-500 flex-shrink-0" />
                    <span>AI-powered content repurposing tools</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm">
                    <Users className="h-4 w-4 text-blue-500 flex-shrink-0" />
                    <span>Join 10,000+ creators using our platform</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm">
                    <Star className="h-4 w-4 text-purple-500 flex-shrink-0" />
                    <span>Export to multiple formats</span>
                  </div>
                </div>

                  {/* CTA Buttons */}
                  <div className="space-y-3 pt-2">
                    <SignUpButton mode="modal">
                      <Button size="lg" className="w-full group">
                        Sign Up Free - View Full Transcription
                        <ArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
                      </Button>
                    </SignUpButton>
                    
                    <SignInButton mode="modal">
                      <Button variant="outline" size="lg" className="w-full">
                        Already have an account? Sign In
                      </Button>
                    </SignInButton>
                  </div>

                {/* Trust Indicators */}
                <div className="text-center pt-2 border-t">
                  <p className="text-xs text-muted-foreground">
                    ✨ Free forever • No credit card required • 2-minute setup
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* Additional Features Teaser */}
      <Card className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 border-purple-200 dark:border-purple-800">
        <CardContent className="pt-6">
          <div className="text-center space-y-4">
            <h3 className="text-lg font-semibold text-purple-800 dark:text-purple-200">
              Unlock Powerful Features
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="flex flex-col items-center gap-2">
                <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-full">
                  <FileText className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                </div>
                <span className="font-medium">Smart Summaries</span>
                <span className="text-muted-foreground text-xs">AI-generated key points</span>
              </div>
              <div className="flex flex-col items-center gap-2">
                <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-full">
                  <Zap className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                </div>
                <span className="font-medium">Content Repurposing</span>
                <span className="text-muted-foreground text-xs">Blog posts, social media</span>
              </div>
              <div className="flex flex-col items-center gap-2">
                <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-full">
                  <Users className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                </div>
                <span className="font-medium">Team Collaboration</span>
                <span className="text-muted-foreground text-xs">Share and edit together</span>
              </div>
            </div>
            <SignUpButton mode="modal">
              <Button variant="outline" className="mt-4">
                Get Started Free
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </SignUpButton>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}