"use client";

import React, { useState } from 'react';
import { anonymousApi } from '@/lib/api/anonymous-client';

export default function AnonymousApiDebug() {
  const [results, setResults] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const addResult = (message: string) => {
    setResults(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
  };

  const testHealthEndpoint = async () => {
    setLoading(true);
    try {
      addResult("🧪 Testing health endpoint...");
      const result = await anonymousApi.healthCheck();
      addResult(`✅ Health check successful: ${JSON.stringify(result)}`);
    } catch (error: any) {
      addResult(`❌ Health check failed: ${error.message}`);
      addResult(`   Status: ${error.status || 'unknown'}`);
      addResult(`   Error object: ${JSON.stringify(error.error || {})}`);
    }
    setLoading(false);
  };

  const testRateLimitEndpoint = async () => {
    setLoading(true);
    try {
      addResult("🧪 Testing rate limit endpoint...");
      const result = await anonymousApi.getRateLimitInfo();
      addResult(`✅ Rate limit check successful: ${JSON.stringify(result)}`);
    } catch (error: any) {
      addResult(`❌ Rate limit check failed: ${error.message}`);
      addResult(`   Status: ${error.status || 'unknown'}`);
      addResult(`   Error object: ${JSON.stringify(error.error || {})}`);
    }
    setLoading(false);
  };

  const testUploadEndpoint = async () => {
    setLoading(true);
    try {
      addResult("🧪 Testing upload endpoint...");
      
      // Create a test file
      const testContent = new Blob(['test audio content'], { type: 'audio/mp3' });
      const testFile = new File([testContent], 'test.mp3', { type: 'audio/mp3' });
      
      const result = await anonymousApi.uploadFile(testFile, "Debug Test Upload");
      addResult(`✅ Upload successful: ${JSON.stringify(result)}`);
      
      // Test status check with the returned token
      if (result.session_token) {
        addResult("🧪 Testing status endpoint with real token...");
        const statusResult = await anonymousApi.getSessionStatus(result.session_token);
        addResult(`✅ Status check successful: ${JSON.stringify(statusResult)}`);
      }
      
    } catch (error: any) {
      addResult(`❌ Upload failed: ${error.message}`);
      addResult(`   Status: ${error.status || 'unknown'}`);
      addResult(`   Error object: ${JSON.stringify(error.error || {})}`);
      
      // Log the full error for debugging
      console.error('Full upload error:', error);
    }
    setLoading(false);
  };

  const clearResults = () => {
    setResults([]);
  };

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4">Anonymous API Debug Tool</h2>
      
      <div className="mb-4 p-3 bg-gray-100 rounded">
        <strong>API URL:</strong> {apiUrl}
      </div>

      <div className="flex gap-2 mb-4">
        <button
          onClick={testHealthEndpoint}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          Test Health
        </button>
        
        <button
          onClick={testRateLimitEndpoint}
          disabled={loading}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
        >
          Test Rate Limit
        </button>
        
        <button
          onClick={testUploadEndpoint}
          disabled={loading}
          className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50"
        >
          Test Upload
        </button>
        
        <button
          onClick={clearResults}
          className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
        >
          Clear
        </button>
      </div>

      {loading && (
        <div className="mb-4 p-2 bg-yellow-100 text-yellow-800 rounded">
          Testing in progress...
        </div>
      )}

      <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-sm h-96 overflow-y-auto">
        {results.length === 0 && (
          <div className="text-gray-500">Click a test button to see results...</div>
        )}
        {results.map((result, index) => (
          <div key={index} className="mb-1">
            {result}
          </div>
        ))}
      </div>
    </div>
  );
}
