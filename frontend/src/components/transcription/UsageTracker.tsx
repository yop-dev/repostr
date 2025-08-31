"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Clock, FileAudio, Zap } from "lucide-react";

interface UsageTrackerProps {
  plan: 'free' | 'pro' | 'enterprise';
  usage: {
    transcriptionsUsed: number;
    transcriptionsLimit: number;
    minutesUsed: number;
    minutesLimit: number;
  };
}

export function UsageTracker({ plan, usage }: UsageTrackerProps) {
  const getPlanBadge = () => {
    switch (plan) {
      case 'free':
        return <Badge variant="secondary">Free Plan</Badge>;
      case 'pro':
        return <Badge variant="default" className="bg-blue-600">Pro Plan</Badge>;
      case 'enterprise':
        return <Badge variant="default" className="bg-purple-600">Enterprise</Badge>;
      default:
        return null;
    }
  };

  const transcriptionPercentage = (usage.transcriptionsUsed / usage.transcriptionsLimit) * 100;
  const minutesPercentage = (usage.minutesUsed / usage.minutesLimit) * 100;

  const getProgressColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center">
            <Zap className="h-5 w-5 mr-2" />
            Usage & Limits
          </CardTitle>
          {getPlanBadge()}
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Transcriptions Usage */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <FileAudio className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium">Transcriptions</span>
            </div>
            <span className="text-sm text-gray-600">
              {usage.transcriptionsUsed} / {usage.transcriptionsLimit}
            </span>
          </div>
          <div className="relative">
            <Progress value={transcriptionPercentage} className="h-2" />
            <div 
              className={`absolute top-0 left-0 h-2 rounded-full transition-all ${getProgressColor(transcriptionPercentage)}`}
              style={{ width: `${Math.min(transcriptionPercentage, 100)}%` }}
            />
          </div>
          {transcriptionPercentage >= 90 && (
            <p className="text-xs text-red-600">
              You're approaching your transcription limit
            </p>
          )}
        </div>

        {/* Minutes Usage */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium">Audio Minutes</span>
            </div>
            <span className="text-sm text-gray-600">
              {usage.minutesUsed} / {usage.minutesLimit} min
            </span>
          </div>
          <div className="relative">
            <Progress value={minutesPercentage} className="h-2" />
            <div 
              className={`absolute top-0 left-0 h-2 rounded-full transition-all ${getProgressColor(minutesPercentage)}`}
              style={{ width: `${Math.min(minutesPercentage, 100)}%` }}
            />
          </div>
          {minutesPercentage >= 90 && (
            <p className="text-xs text-red-600">
              You're approaching your audio minutes limit
            </p>
          )}
        </div>

        {/* Plan Limits Info */}
        <div className="pt-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Plan Limits</h4>
          <div className="space-y-1 text-xs text-gray-600">
            <div className="flex justify-between">
              <span>Max file size:</span>
              <span>{plan === 'free' ? '25MB' : plan === 'pro' ? '100MB' : 'Unlimited'}</span>
            </div>
            <div className="flex justify-between">
              <span>Supported formats:</span>
              <span>MP3, WAV, M4A, AAC, OGG, WebM, FLAC</span>
            </div>
            <div className="flex justify-between">
              <span>Transcription speed:</span>
              <span>{plan === 'free' ? 'Standard' : 'Priority'}</span>
            </div>
          </div>
        </div>

        {plan === 'free' && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-sm text-blue-800 font-medium">Upgrade to Pro</p>
            <p className="text-xs text-blue-700 mt-1">
              Get unlimited transcriptions, larger file uploads, and priority processing.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}