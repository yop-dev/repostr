"use client";

import { useState, useCallback, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useApi } from "@/hooks/use-api";
import { Upload, File, X, AlertCircle, CheckCircle } from "lucide-react";

interface FileUploadZoneProps {
  projectId: string;
  onUploadComplete: (transcription: any) => void;
  onUploadStart?: () => void;
}

interface UploadingFile {
  file: File;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
  transcriptionId?: string;
}

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

const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25MB

export function FileUploadZone({ 
  projectId, 
  onUploadComplete, 
  onUploadStart 
}: FileUploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const api = useApi();

  const validateFile = (file: File): string | null => {
    if (!ACCEPTED_AUDIO_TYPES.includes(file.type)) {
      return `Unsupported file type: ${file.type}. Please upload audio files only.`;
    }
    if (file.size > MAX_FILE_SIZE) {
      return `File too large: ${(file.size / 1024 / 1024).toFixed(1)}MB. Maximum size is 25MB.`;
    }
    return null;
  };

  const uploadFile = async (file: File) => {
    const uploadingFile: UploadingFile = {
      file,
      progress: 0,
      status: 'uploading'
    };

    setUploadingFiles(prev => [...prev, uploadingFile]);
    onUploadStart?.();

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadingFiles(prev => 
          prev.map(f => 
            f.file === file && f.status === 'uploading'
              ? { ...f, progress: Math.min(f.progress + 10, 90) }
              : f
          )
        );
      }, 200);

      // Check if transcription endpoints are available
      if (typeof api.uploadFile !== 'function') {
        throw new Error('Transcription endpoints not available yet. Please wait for backend setup to complete.');
      }
      
      const transcription = await api.uploadFile(projectId, file);

      clearInterval(progressInterval);

      setUploadingFiles(prev => 
        prev.map(f => 
          f.file === file 
            ? { 
                ...f, 
                progress: 100, 
                status: 'processing',
                transcriptionId: transcription.id 
              }
            : f
        )
      );

      // For now, just mark as completed after a delay since transcription endpoints aren't fully implemented
      setTimeout(() => {
        setUploadingFiles(prev => 
          prev.map(f => 
            f.transcriptionId === transcription.id
              ? { ...f, status: 'completed' }
              : f
          )
        );
        onUploadComplete({
          id: transcription.id,
          filename: file.name,
          status: 'completed',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        });
      }, 3000); // Simulate processing time

    } catch (error) {
      setUploadingFiles(prev => 
        prev.map(f => 
          f.file === file 
            ? { 
                ...f, 
                status: 'error', 
                error: error instanceof Error ? error.message : 'Upload failed' 
              }
            : f
        )
      );
    }
  };

  const handleFiles = useCallback((files: FileList | File[]) => {
    const fileArray = Array.from(files);
    
    for (const file of fileArray) {
      const error = validateFile(file);
      if (error) {
        // Show error for invalid file
        setUploadingFiles(prev => [...prev, {
          file,
          progress: 0,
          status: 'error',
          error
        }]);
        continue;
      }
      
      uploadFile(file);
    }
  }, [projectId]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFiles(files);
    }
  }, [handleFiles]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFiles(files);
    }
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [handleFiles]);

  const removeFile = (file: File) => {
    setUploadingFiles(prev => prev.filter(f => f.file !== file));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-4">
      <Card 
        className={`border-2 border-dashed transition-colors ${
          isDragOver 
            ? 'border-blue-400 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <CardContent className="flex flex-col items-center justify-center py-12 text-center">
          <Upload className="h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Upload Audio Files
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Drag and drop your audio files here, or click to browse
          </p>
          <p className="text-xs text-gray-500 mb-6">
            Supports MP3, WAV, M4A, AAC, OGG, WebM, FLAC (max 25MB each)
          </p>
          <Button 
            onClick={() => fileInputRef.current?.click()}
            variant="outline"
          >
            Choose Files
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept={ACCEPTED_AUDIO_TYPES.join(',')}
            onChange={handleFileSelect}
            className="hidden"
          />
        </CardContent>
      </Card>

      {uploadingFiles.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-medium text-gray-900">Upload Progress</h4>
          {uploadingFiles.map((uploadingFile, index) => (
            <Card key={index} className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3 flex-1">
                  <File className="h-5 w-5 text-gray-400" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {uploadingFile.file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(uploadingFile.file.size)}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {uploadingFile.status === 'uploading' && (
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{ width: `${uploadingFile.progress}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500">
                        {uploadingFile.progress}%
                      </span>
                    </div>
                  )}
                  
                  {uploadingFile.status === 'processing' && (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
                      <span className="text-xs text-blue-600">Processing...</span>
                    </div>
                  )}
                  
                  {uploadingFile.status === 'completed' && (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  )}
                  
                  {uploadingFile.status === 'error' && (
                    <div className="flex items-center space-x-2">
                      <AlertCircle className="h-5 w-5 text-red-600" />
                      <span className="text-xs text-red-600 max-w-48 truncate">
                        {uploadingFile.error}
                      </span>
                    </div>
                  )}
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(uploadingFile.file)}
                    disabled={uploadingFile.status === 'uploading'}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}