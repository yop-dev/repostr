"use client";

import { useAuth, useUser, UserButton } from "@clerk/nextjs";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ProjectCreationModal } from "@/components/transcription/ProjectCreationModal";
import { FileUploadZone } from "@/components/transcription/FileUploadZone";
import { TranscriptionViewer } from "@/components/transcription/TranscriptionViewer";
import { UsageTracker } from "@/components/transcription/UsageTracker";
import { useApi } from "@/hooks/use-api";
import { Plus, FolderOpen, FileAudio, Trash2 } from "lucide-react";

interface Project {
  id: string;
  title: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

interface Transcription {
  id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  text?: string;
  duration?: number;
  created_at: string;
  updated_at: string;
  error_message?: string;
}

export default function DashboardPage() {
  const { isLoaded, isSignedIn } = useAuth();
  const { user } = useUser();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [transcriptions, setTranscriptions] = useState<Transcription[]>([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [transcriptionsLoading, setTranscriptionsLoading] = useState(false);
  
  const api = useApi();

  // Mock usage data - in real app this would come from API
  const mockUsage = {
    transcriptionsUsed: 3,
    transcriptionsLimit: 10,
    minutesUsed: 45,
    minutesLimit: 120,
  };

  // Load projects on mount
  useEffect(() => {
    if (isSignedIn) {
      loadProjects();
    }
  }, [isSignedIn]);

  // Load transcriptions when project is selected
  useEffect(() => {
    if (selectedProject) {
      loadTranscriptions(selectedProject.id);
    }
  }, [selectedProject]);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const projectsData = await api.getProjects() as Project[];
      setProjects(projectsData);
      
      // Auto-select first project if available
      if (projectsData.length > 0 && !selectedProject) {
        setSelectedProject(projectsData[0]);
      }
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTranscriptions = async (projectId: string) => {
    try {
      setTranscriptionsLoading(true);
      // Use files endpoint for now - in the future this would be a dedicated transcriptions endpoint
      const filesData = await api.getFiles(projectId) as any[];
      // Transform files data to transcriptions format if needed
      const transcriptionsData = filesData.map(file => ({
        id: file.id,
        filename: file.name || file.filename,
        status: file.transcription_status || 'pending',
        text: file.transcription_text,
        duration: file.duration,
        created_at: file.created_at,
        updated_at: file.updated_at,
        error_message: file.error_message
      })) as Transcription[];
      setTranscriptions(transcriptionsData);
    } catch (error) {
      console.error('Failed to load transcriptions:', error);
      setTranscriptions([]);
    } finally {
      setTranscriptionsLoading(false);
    }
  };

  const handleProjectCreated = (newProject: Project) => {
    setProjects(prev => [newProject, ...prev]);
    setSelectedProject(newProject);
  };

  const handleUploadComplete = (transcription: Transcription) => {
    setTranscriptions(prev => {
      const existing = prev.find(t => t.id === transcription.id);
      if (existing) {
        return prev.map(t => t.id === transcription.id ? transcription : t);
      }
      return [transcription, ...prev];
    });
  };

  const handleDeleteProject = async (projectId: string) => {
    if (!confirm('Are you sure you want to delete this project? This will also delete all transcriptions.')) {
      return;
    }
    
    try {
      await api.deleteProject(projectId);
      setProjects(prev => prev.filter(p => p.id !== projectId));
      
      if (selectedProject?.id === projectId) {
        const remainingProjects = projects.filter(p => p.id !== projectId);
        setSelectedProject(remainingProjects.length > 0 ? remainingProjects[0] : null);
      }
    } catch (error) {
      console.error('Failed to delete project:', error);
    }
  };

  if (!isLoaded) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  if (!isSignedIn) return <div className="min-h-screen flex items-center justify-center">Not signed in</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Repostr Dashboard</h1>
              <p className="text-gray-600">Audio transcription and content generation</p>
            </div>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs defaultValue="transcriptions" className="space-y-6">
          <TabsList>
            <TabsTrigger value="transcriptions">Transcriptions</TabsTrigger>
            <TabsTrigger value="projects">Projects</TabsTrigger>
            <TabsTrigger value="usage">Usage</TabsTrigger>
          </TabsList>

          <TabsContent value="transcriptions" className="space-y-6">
            {/* Project Selection & Upload */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Project Sidebar */}
              <div className="lg:col-span-1">
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center">
                        <FolderOpen className="h-5 w-5 mr-2" />
                        Projects
                      </CardTitle>
                      <Button
                        size="sm"
                        onClick={() => setIsCreateModalOpen(true)}
                      >
                        <Plus className="h-4 w-4 mr-2" />
                        New
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {loading ? (
                      <div className="text-center py-4">Loading projects...</div>
                    ) : projects.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <FolderOpen className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                        <p>No projects yet</p>
                        <p className="text-sm">Create your first project to get started</p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {projects.map((project) => (
                          <div
                            key={project.id}
                            className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                              selectedProject?.id === project.id
                                ? 'bg-blue-50 border-blue-200'
                                : 'hover:bg-gray-50'
                            }`}
                            onClick={() => setSelectedProject(project)}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex-1 min-w-0">
                                <h3 className="font-medium text-sm truncate">{project.title}</h3>
                                {project.description && (
                                  <p className="text-xs text-gray-500 truncate">{project.description}</p>
                                )}
                              </div>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteProject(project.id);
                                }}
                                className="ml-2 h-6 w-6 p-0"
                              >
                                <Trash2 className="h-3 w-3" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Main Content */}
              <div className="lg:col-span-2">
                {selectedProject ? (
                  <div className="space-y-6">
                    {/* Upload Zone */}
                    <Card>
                      <CardHeader>
                        <CardTitle>Upload Audio Files</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <FileUploadZone
                          projectId={selectedProject.id}
                          onUploadComplete={handleUploadComplete}
                        />
                      </CardContent>
                    </Card>

                    {/* Transcriptions */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center">
                          <FileAudio className="h-5 w-5 mr-2" />
                          Transcriptions
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        {transcriptionsLoading ? (
                          <div className="text-center py-8">Loading transcriptions...</div>
                        ) : transcriptions.length === 0 ? (
                          <div className="text-center py-8 text-gray-500">
                            <FileAudio className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                            <p>No transcriptions yet</p>
                            <p className="text-sm">Upload an audio file to get started</p>
                          </div>
                        ) : (
                          <div className="space-y-4">
                            {transcriptions.map((transcription) => (
                              <TranscriptionViewer
                                key={transcription.id}
                                transcription={transcription}
                              />
                            ))}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                ) : (
                  <Card>
                    <CardContent className="text-center py-12">
                      <FolderOpen className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Project</h3>
                      <p className="text-gray-500 mb-4">
                        Choose a project from the sidebar or create a new one to start transcribing audio files.
                      </p>
                      <Button onClick={() => setIsCreateModalOpen(true)}>
                        <Plus className="h-4 w-4 mr-2" />
                        Create New Project
                      </Button>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="projects" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">All Projects</h2>
              <Button onClick={() => setIsCreateModalOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                New Project
              </Button>
            </div>

            {loading ? (
              <div className="text-center py-12">Loading projects...</div>
            ) : projects.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <FolderOpen className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Projects Yet</h3>
                  <p className="text-gray-500 mb-4">
                    Create your first project to organize your transcriptions and content.
                  </p>
                  <Button onClick={() => setIsCreateModalOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create First Project
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {projects.map((project) => (
                  <Card key={project.id} className="hover:shadow-md transition-shadow">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg">{project.title}</CardTitle>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteProject(project.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                      {project.description && (
                        <p className="text-sm text-gray-600">{project.description}</p>
                      )}
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-500">
                          Created {new Date(project.created_at).toLocaleDateString()}
                        </span>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedProject(project);
                            // Switch to transcriptions tab
                            const tabsTrigger = document.querySelector('[value="transcriptions"]') as HTMLElement;
                            tabsTrigger?.click();
                          }}
                        >
                          Open
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="usage" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <UsageTracker
                plan="free"
                usage={mockUsage}
              />
              <Card>
                <CardHeader>
                  <CardTitle>Account Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Email</label>
                    <p className="text-gray-900">{user?.primaryEmailAddress?.emailAddress}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">User ID</label>
                    <p className="text-gray-900 font-mono text-sm">{user?.id}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Plan</label>
                    <p className="text-gray-900">Free Tier</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Project Creation Modal */}
      <ProjectCreationModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onProjectCreated={handleProjectCreated}
      />
    </div>
  );
}
