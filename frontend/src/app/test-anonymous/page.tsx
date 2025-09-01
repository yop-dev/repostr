/**
 * Anonymous Upload Test Page
 * Development page for testing the anonymous upload implementation
 * Following frontend best practices: development tools, debugging
 */

import { AnonymousFlowTest } from "@/components/transcription/AnonymousFlowTest";
import { AnonymousFlow } from "@/components/transcription/AnonymousFlow";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  TestTube, 
  Upload, 
  Code, 
  AlertTriangle 
} from "lucide-react";

export default function TestAnonymousPage() {
  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium mb-4">
            <AlertTriangle className="h-4 w-4" />
            Development Testing Page
          </div>
          <h1 className="text-3xl font-bold mb-2">Anonymous Upload Testing</h1>
          <p className="text-muted-foreground">
            Test and validate the anonymous upload implementation
          </p>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-green-100 rounded-full">
                  <Code className="h-4 w-4 text-green-600" />
                </div>
                <div>
                  <div className="font-semibold">Frontend</div>
                  <Badge variant="secondary" className="bg-green-100 text-green-800">Ready</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-blue-100 rounded-full">
                  <Upload className="h-4 w-4 text-blue-600" />
                </div>
                <div>
                  <div className="font-semibold">API Client</div>
                  <Badge variant="secondary" className="bg-blue-100 text-blue-800">Implemented</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-purple-100 rounded-full">
                  <TestTube className="h-4 w-4 text-purple-600" />
                </div>
                <div>
                  <div className="font-semibold">Components</div>
                  <Badge variant="secondary" className="bg-purple-100 text-purple-800">Complete</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Testing Tabs */}
        <Tabs defaultValue="test" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="test" className="flex items-center gap-2">
              <TestTube className="h-4 w-4" />
              API Tests
            </TabsTrigger>
            <TabsTrigger value="flow" className="flex items-center gap-2">
              <Upload className="h-4 w-4" />
              Full Flow
            </TabsTrigger>
          </TabsList>

          <TabsContent value="test" className="mt-6">
            <AnonymousFlowTest />
          </TabsContent>

          <TabsContent value="flow" className="mt-6">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Complete Anonymous Upload Flow</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Test the full user experience from upload to conversion
                  </p>
                </CardHeader>
              </Card>
              <AnonymousFlow />
            </div>
          </TabsContent>
        </Tabs>

        {/* Development Notes */}
        <Card className="mt-8 bg-muted/50">
          <CardHeader>
            <CardTitle className="text-lg">Development Notes</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">Backend Requirements</h4>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                <li>Backend server running on localhost:8000</li>
                <li>Anonymous routes enabled (anonymous_simple.py or anonymous.py)</li>
                <li>CORS configured for frontend domain</li>
                <li>Database migration applied (003_anonymous_upload_support.sql)</li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Frontend Implementation</h4>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                <li>✅ Anonymous API client with typed responses</li>
                <li>✅ Session management with localStorage persistence</li>
                <li>✅ Upload hook with file validation and progress tracking</li>
                <li>✅ Upload zone component with drag & drop</li>
                <li>✅ Blurred transcription viewer with conversion overlay</li>
                <li>✅ Complete flow orchestration component</li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Testing Checklist</h4>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                <li>🔍 API health check and rate limits</li>
                <li>📁 File validation (size, type, format)</li>
                <li>⬆️ Upload flow with progress tracking</li>
                <li>🔄 Status polling and session management</li>
                <li>👁️ Blurred results with conversion messaging</li>
                <li>🔗 Signup integration with Clerk</li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Next Steps</h4>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                <li>Resolve Python 3.13 audio dependency issue</li>
                <li>Test with real transcription processing</li>
                <li>Implement session claiming after signup</li>
                <li>Add analytics and conversion tracking</li>
                <li>Performance optimization and error handling</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}