"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Copy, 
  Download, 
  Clock, 
  FileAudio, 
  CheckCircle, 
  AlertCircle,
  Loader2 
} from "lucide-react";

interface TranscriptionViewerProps {
  transcription: {
    id: string;
    filename: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    text?: string;
    duration?: number;
    created_at: string;
    updated_at: string;
    error_message?: string;
  };
}

export function TranscriptionViewer({ transcription }: TranscriptionViewerProps) {
  const [copied, setCopied] = useState(false);

  const getStatusBadge = () => {
    switch (transcription.status) {
      case 'completed':
        return (
          <Badge variant="default" className="bg-green-100 text-green-800">
            <CheckCircle className="h-3 w-3 mr-1" />
            Completed
          </Badge>
        );
      case 'processing':
        return (
          <Badge variant="default" className="bg-blue-100 text-blue-800">
            <Loader2 className="h-3 w-3 mr-1 animate-spin" />
            Processing
          </Badge>
        );
      case 'pending':
        return (
          <Badge variant="secondary">
            <Clock className="h-3 w-3 mr-1" />
            Pending
          </Badge>
        );
      case 'failed':
        return (
          <Badge variant="destructive">
            <AlertCircle className="h-3 w-3 mr-1" />
            Failed
          </Badge>
        );
      default:
        return null;
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'Unknown';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const copyToClipboard = async () => {
    if (!transcription.text) return;
    
    try {
      await navigator.clipboard.writeText(transcription.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const downloadTranscription = () => {
    if (!transcription.text) return;
    
    const blob = new Blob([transcription.text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${transcription.filename.replace(/\.[^/.]+$/, '')}_transcription.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FileAudio className="h-5 w-5 text-gray-500" />
            <div>
              <CardTitle className="text-lg">{transcription.filename}</CardTitle>
              <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                <span>Duration: {formatDuration(transcription.duration)}</span>
                <span>Created: {formatDate(transcription.created_at)}</span>
              </div>
            </div>
          </div>
          {getStatusBadge()}
        </div>
      </CardHeader>

      <CardContent>
        {transcription.status === 'failed' && transcription.error_message && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
              <span className="text-red-800 font-medium">Transcription Failed</span>
            </div>
            <p className="text-red-700 text-sm mt-1">{transcription.error_message}</p>
          </div>
        )}

        {transcription.status === 'processing' && (
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-4">
            <div className="flex items-center">
              <Loader2 className="h-5 w-5 text-blue-600 mr-2 animate-spin" />
              <span className="text-blue-800 font-medium">Processing Audio</span>
            </div>
            <p className="text-blue-700 text-sm mt-1">
              Your audio file is being transcribed. This may take a few minutes.
            </p>
          </div>
        )}

        {transcription.status === 'pending' && (
          <div className="bg-gray-50 border border-gray-200 rounded-md p-4 mb-4">
            <div className="flex items-center">
              <Clock className="h-5 w-5 text-gray-600 mr-2" />
              <span className="text-gray-800 font-medium">Queued for Processing</span>
            </div>
            <p className="text-gray-700 text-sm mt-1">
              Your audio file is in the queue and will be processed shortly.
            </p>
          </div>
        )}

        {transcription.status === 'completed' && transcription.text && (
          <Tabs defaultValue="formatted" className="w-full">
            <div className="flex items-center justify-between mb-4">
              <TabsList>
                <TabsTrigger value="formatted">Formatted</TabsTrigger>
                <TabsTrigger value="raw">Raw Text</TabsTrigger>
              </TabsList>
              
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={copyToClipboard}
                  disabled={!transcription.text}
                >
                  <Copy className="h-4 w-4 mr-2" />
                  {copied ? 'Copied!' : 'Copy'}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={downloadTranscription}
                  disabled={!transcription.text}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>
            </div>

            <TabsContent value="formatted" className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-6 max-h-96 overflow-y-auto">
                <div className="prose prose-sm max-w-none">
                  {transcription.text.split('\n\n').map((paragraph, index) => (
                    <p key={index} className="mb-4 leading-relaxed text-gray-800">
                      {paragraph}
                    </p>
                  ))}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="raw" className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-6 max-h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                  {transcription.text}
                </pre>
              </div>
            </TabsContent>
          </Tabs>
        )}

        {transcription.status === 'completed' && !transcription.text && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-yellow-600 mr-2" />
              <span className="text-yellow-800 font-medium">No Transcription Text</span>
            </div>
            <p className="text-yellow-700 text-sm mt-1">
              The transcription completed but no text was generated. The audio file may be empty or contain no speech.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}