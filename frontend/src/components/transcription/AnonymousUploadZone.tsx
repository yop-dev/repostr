/**
 * Anonymous Upload Zone Component
 * File upload interface for anonymous users with drag & drop
 * Following frontend best practices: accessibility, type safety, user experience
 */

"use client";

import { useState, useCallback, useRef, DragEvent, ChangeEvent } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useAnonymousUpload } from "@/hooks/use-anonymous-upload";
import { useAnonymousSession } from "@/hooks/use-anonymous-session";
import { 
  Upload, 
  File as FileIcon, 
  AlertCircle, 
  CheckCircle, 
  Clock,
  Loader2,
  Music,
  Mic
} from "lucide-react";
import { cn } from "@/lib/utils";

interface AnonymousUploadZoneProps {
  onUploadComplete?: (sessionToken: string) => void;
  onUploadStart?: () => void;
  className?: string;
}

export function AnonymousUploadZone({ 
  onUploadComplete, 
  onUploadStart,
  className 
}: AnonymousUploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [projectName, setProjectName] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { 
    uploadProgress, 
    uploadError, 
    rateLimitInfo,
    isUploading, 
    isProcessing, 
    isCompleted,
    hasError,
    uploadFile, 
    resetUpload,
    formatFileSize,
    getUploadLimits 
  } = useAnonymousUpload();

  const { currentSession } = useAnonymousSession();

  const uploadLimits = getUploadLimits();

  // Handle drag events
  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      const file = files[0];
      setSelectedFile(file);
      setProjectName(file.name.replace(/\.[^/.]+$/, "")); // Remove extension
    }
  }, []);

  // Handle file input change
  const handleFileChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      setSelectedFile(file);
      setProjectName(file.name.replace(/\.[^/.]+$/, "")); // Remove extension
    }
  }, []);

  // Handle upload
  const handleUpload = useCallback(async () => {
    if (!selectedFile || !projectName.trim()) return;

    onUploadStart?.();

    const result = await uploadFile(
      selectedFile,
      projectName.trim(),
      undefined, // description
      "en" // language
    );

    // If successful and we have a session token, call completion callback immediately
    if (result.success && result.sessionToken) {
      onUploadComplete?.(result.sessionToken);
    }
  }, [selectedFile, projectName, uploadFile, onUploadStart, onUploadComplete]);

  // Reset state
  const handleReset = useCallback(() => {
    setSelectedFile(null);
    setProjectName("");
    resetUpload();
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }, [resetUpload]);

  // Open file picker
  const openFilePicker = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  // Render upload status
  const renderUploadStatus = () => {
    if (hasError && uploadError) {
      return (
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-destructive">
            <AlertCircle className="h-5 w-5" />
            <span className="font-medium">Upload Failed</span>
          </div>
          <p className="text-sm text-muted-foreground">{uploadError.message}</p>
          {uploadError.signupSuggestion && (
            <p className="text-sm text-primary font-medium">
              💡 {uploadError.signupSuggestion}
            </p>
          )}
          <Button onClick={handleReset} variant="outline" size="sm">
            Try Again
          </Button>
        </div>
      );
    }

    if (isCompleted) {
      return (
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle className="h-5 w-5" />
            <span className="font-medium">Upload Complete!</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Your audio has been processed. View your transcription below.
          </p>
        </div>
      );
    }

    if (isProcessing || isUploading) {
      return (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span className="font-medium">
              {isUploading ? "Uploading..." : "Processing Audio..."}
            </span>
          </div>
          <div className="space-y-2">
            <Progress value={uploadProgress.progress} className="h-2" />
            <p className="text-sm text-muted-foreground">{uploadProgress.message}</p>
            {uploadProgress.estimatedTimeRemaining && (
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                <span>~{uploadProgress.estimatedTimeRemaining} seconds remaining</span>
              </div>
            )}
          </div>
        </div>
      );
    }

    return null;
  };

  // If upload is in progress or completed, show status
  if (isUploading || isProcessing || isCompleted || hasError) {
    return (
      <Card className={cn("w-full max-w-2xl mx-auto", className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Music className="h-5 w-5" />
            Anonymous Upload
          </CardTitle>
        </CardHeader>
        <CardContent>
          {selectedFile && (
            <div className="mb-6 p-4 bg-muted rounded-lg">
              <div className="flex items-center gap-3">
                <FileIcon className="h-8 w-8 text-muted-foreground" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{selectedFile.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
              </div>
            </div>
          )}
          {renderUploadStatus()}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("w-full max-w-2xl mx-auto", className)}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Mic className="h-5 w-5" />
          Try for Free - No Signup Required
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Upload an audio file to see our transcription in action. Sign up to view the full results.
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Rate limit info */}
        {rateLimitInfo && (
          <div className="text-xs text-muted-foreground bg-muted p-3 rounded-lg">
            <p>
              Anonymous uploads: {rateLimitInfo.uploads_remaining_day} remaining today
              {rateLimitInfo.demo_mode && " (Demo mode)"}
            </p>
          </div>
        )}

        {/* File drop zone */}
        <div
          className={cn(
            "border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer",
            isDragOver 
              ? "border-primary bg-primary/5" 
              : "border-muted-foreground/25 hover:border-primary/50 hover:bg-accent/50",
            selectedFile && "border-primary bg-primary/5"
          )}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={openFilePicker}
          role="button"
          tabIndex={0}
          aria-label="Upload audio file"
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              openFilePicker();
            }
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept={uploadLimits.acceptedTypes.join(",")}
            onChange={handleFileChange}
            className="hidden"
            aria-hidden="true"
          />
          
          {selectedFile ? (
            <div className="space-y-4">
              <div className="flex items-center justify-center gap-3">
                <FileIcon className="h-12 w-12 text-primary" />
                <div className="text-left">
                  <p className="font-medium">{selectedFile.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
              </div>
              <Button variant="outline" size="sm" onClick={(e) => {
                e.stopPropagation();
                handleReset();
              }}>
                Choose Different File
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <Upload className="h-12 w-12 mx-auto text-muted-foreground" />
              <div className="space-y-2">
                <p className="text-lg font-medium">
                  Drop your audio file here, or click to browse
                </p>
                <p className="text-sm text-muted-foreground">
                  Supports: {uploadLimits.acceptedExtensions.join(", ")}
                </p>
                <p className="text-xs text-muted-foreground">
                  Max file size: {uploadLimits.maxFileSizeFormatted}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Project name input */}
        {selectedFile && (
          <div className="space-y-2">
            <label htmlFor="project-name" className="text-sm font-medium">
              Project Name
            </label>
            <input
              id="project-name"
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="Enter a name for your transcription"
              className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
              maxLength={100}
            />
            <p className="text-xs text-muted-foreground">
              This helps you identify your transcription later
            </p>
          </div>
        )}

        {/* Upload button */}
        {selectedFile && (
          <Button 
            onClick={handleUpload}
            disabled={!projectName.trim() || isUploading}
            size="lg"
            className="w-full"
          >
            {isUploading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Start Free Transcription
              </>
            )}
          </Button>
        )}

        {/* Benefits */}
        <div className="text-center space-y-2 pt-4 border-t">
          <p className="text-sm font-medium">What you'll get:</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>AI-powered transcription</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Preview in seconds</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>No credit card required</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}