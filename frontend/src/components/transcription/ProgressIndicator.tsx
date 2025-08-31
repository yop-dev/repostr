"use client";

import { Progress } from "@/components/ui/progress";
import { CheckCircle, Clock, AlertCircle, Loader2 } from "lucide-react";

interface ProgressIndicatorProps {
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  message?: string;
}

export function ProgressIndicator({ status, progress = 0, message }: ProgressIndicatorProps) {
  const getStatusIcon = () => {
    switch (status) {
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'processing':
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'pending':
        return 'Queued for processing';
      case 'processing':
        return 'Processing audio...';
      case 'completed':
        return 'Transcription complete';
      case 'failed':
        return 'Transcription failed';
      default:
        return '';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'pending':
        return 'text-yellow-700';
      case 'processing':
        return 'text-blue-700';
      case 'completed':
        return 'text-green-700';
      case 'failed':
        return 'text-red-700';
      default:
        return 'text-gray-700';
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center space-x-3">
        {getStatusIcon()}
        <div className="flex-1">
          <p className={`font-medium ${getStatusColor()}`}>
            {getStatusText()}
          </p>
          {message && (
            <p className="text-sm text-gray-600">{message}</p>
          )}
        </div>
        {status === 'processing' && (
          <span className="text-sm text-gray-500">{progress}%</span>
        )}
      </div>
      
      {status === 'processing' && (
        <Progress value={progress} className="w-full" />
      )}
    </div>
  );
}