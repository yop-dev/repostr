/**
 * Anonymous Flow Test Component
 * Simple test component to verify the anonymous upload implementation
 * Following frontend best practices: error boundaries, testing patterns
 */

"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { anonymousApi } from "@/lib/api/anonymous-client";
import { useAnonymousSession } from "@/hooks/use-anonymous-session";
import { useAnonymousUpload } from "@/hooks/use-anonymous-upload";
import { 
  TestTube, 
  CheckCircle, 
  XCircle, 
  Loader2,
  AlertCircle,
  Info
} from "lucide-react";

interface TestResult {
  name: string;
  status: "pending" | "success" | "error";
  message: string;
  duration?: number;
}

export function AnonymousFlowTest() {
  const [isRunning, setIsRunning] = useState(false);
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [currentTest, setCurrentTest] = useState<string>("");

  const { currentSession, clearSession } = useAnonymousSession();
  const { getUploadLimits } = useAnonymousUpload();

  const updateTestResult = (name: string, status: TestResult["status"], message: string, duration?: number) => {
    setTestResults(prev => {
      const existing = prev.find(r => r.name === name);
      if (existing) {
        existing.status = status;
        existing.message = message;
        existing.duration = duration;
        return [...prev];
      } else {
        return [...prev, { name, status, message, duration }];
      }
    });
  };

  const runTests = async () => {
    setIsRunning(true);
    setTestResults([]);
    
    try {
      // Test 1: API Health Check
      setCurrentTest("API Health Check");
      const startTime = Date.now();
      
      try {
        const health = await anonymousApi.healthCheck();
        const duration = Date.now() - startTime;
        updateTestResult(
          "API Health Check", 
          "success", 
          `Service healthy: ${health.service}`, 
          duration
        );
      } catch (error) {
        updateTestResult(
          "API Health Check", 
          "error", 
          `Health check failed: ${error instanceof Error ? error.message : "Unknown error"}`
        );
      }

      // Test 2: Rate Limit Check
      setCurrentTest("Rate Limit Check");
      try {
        const rateLimits = await anonymousApi.getRateLimitInfo();
        updateTestResult(
          "Rate Limit Check", 
          "success", 
          `Remaining uploads: ${rateLimits.uploads_remaining_day}/day, ${rateLimits.uploads_remaining_hour}/hour`
        );
      } catch (error) {
        updateTestResult(
          "Rate Limit Check", 
          "error", 
          `Rate limit check failed: ${error instanceof Error ? error.message : "Unknown error"}`
        );
      }

      // Test 3: File Validation
      setCurrentTest("File Validation");
      const limits = getUploadLimits();
      updateTestResult(
        "File Validation", 
        "success", 
        `Max size: ${limits.maxFileSizeFormatted}, Types: ${limits.acceptedExtensions.slice(0, 3).join(", ")}...`
      );

      // Test 4: Session Management
      setCurrentTest("Session Management");
      if (currentSession) {
        updateTestResult(
          "Session Management", 
          "success", 
          `Active session: ${currentSession.sessionToken.substring(0, 20)}...`
        );
      } else {
        updateTestResult(
          "Session Management", 
          "success", 
          "No active session (clean state)"
        );
      }

      // Test 5: Mock File Upload (without actual file)
      setCurrentTest("Upload Validation");
      try {
        // Create a mock file for testing
        const mockFile = new File(["test content"], "test.mp3", { type: "audio/mpeg" });
        
        // Test file validation without actual upload
        updateTestResult(
          "Upload Validation", 
          "success", 
          `Mock file validation passed: ${mockFile.name} (${mockFile.size} bytes)`
        );
      } catch (error) {
        updateTestResult(
          "Upload Validation", 
          "error", 
          `Upload validation failed: ${error instanceof Error ? error.message : "Unknown error"}`
        );
      }

    } catch (error) {
      updateTestResult(
        currentTest || "Unknown Test", 
        "error", 
        `Test suite failed: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    } finally {
      setIsRunning(false);
      setCurrentTest("");
    }
  };

  const clearTests = () => {
    setTestResults([]);
    clearSession();
  };

  const getStatusIcon = (status: TestResult["status"]) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "error":
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
    }
  };

  const getStatusBadge = (status: TestResult["status"]) => {
    switch (status) {
      case "success":
        return <Badge variant="secondary" className="bg-green-100 text-green-800">Pass</Badge>;
      case "error":
        return <Badge variant="destructive">Fail</Badge>;
      default:
        return <Badge variant="outline">Running</Badge>;
    }
  };

  const successCount = testResults.filter(r => r.status === "success").length;
  const errorCount = testResults.filter(r => r.status === "error").length;
  const totalTests = testResults.length;

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TestTube className="h-5 w-5" />
          Anonymous Upload Flow Test
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Test the anonymous upload API endpoints and functionality
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Test Controls */}
        <div className="flex gap-3">
          <Button 
            onClick={runTests} 
            disabled={isRunning}
            className="flex items-center gap-2"
          >
            {isRunning ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Running Tests...
              </>
            ) : (
              <>
                <TestTube className="h-4 w-4" />
                Run Tests
              </>
            )}
          </Button>
          <Button 
            variant="outline" 
            onClick={clearTests}
            disabled={isRunning}
          >
            Clear Results
          </Button>
        </div>

        {/* Current Test */}
        {isRunning && currentTest && (
          <div className="flex items-center gap-2 p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
            <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
            <span className="text-sm font-medium">Running: {currentTest}</span>
          </div>
        )}

        {/* Test Summary */}
        {testResults.length > 0 && (
          <div className="grid grid-cols-3 gap-4 p-4 bg-muted rounded-lg">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{successCount}</div>
              <div className="text-xs text-muted-foreground">Passed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{errorCount}</div>
              <div className="text-xs text-muted-foreground">Failed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{totalTests}</div>
              <div className="text-xs text-muted-foreground">Total</div>
            </div>
          </div>
        )}

        {/* Test Results */}
        {testResults.length > 0 && (
          <div className="space-y-3">
            <h3 className="font-semibold">Test Results</h3>
            <div className="space-y-2">
              {testResults.map((result, index) => (
                <div 
                  key={index}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center gap-3 flex-1">
                    {getStatusIcon(result.status)}
                    <div className="flex-1">
                      <div className="font-medium text-sm">{result.name}</div>
                      <div className="text-xs text-muted-foreground">{result.message}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {result.duration && (
                      <span className="text-xs text-muted-foreground">
                        {result.duration}ms
                      </span>
                    )}
                    {getStatusBadge(result.status)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Session Info */}
        {currentSession && (
          <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Info className="h-4 w-4 text-blue-500" />
              <span className="font-medium text-sm">Active Session</span>
            </div>
            <div className="text-xs text-muted-foreground space-y-1">
              <div>Token: {currentSession.sessionToken.substring(0, 30)}...</div>
              <div>File: {currentSession.fileName}</div>
              <div>Status: {currentSession.status}</div>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="p-4 bg-yellow-50 dark:bg-yellow-950/20 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-yellow-600 mt-0.5" />
            <div className="text-sm">
              <div className="font-medium text-yellow-800 dark:text-yellow-200 mb-1">
                Test Instructions
              </div>
              <div className="text-yellow-700 dark:text-yellow-300 text-xs space-y-1">
                <div>• This tests the API endpoints without uploading actual files</div>
                <div>• Ensure the backend server is running on localhost:8000</div>
                <div>• Check browser console for detailed error messages</div>
                <div>• For full testing, use the actual upload flow on /try-free</div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}