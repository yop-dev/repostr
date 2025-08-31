import { auth } from "@clerk/nextjs/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: any;
  };
}

export class ApiClient {
  private baseUrl: string;
  private getToken: () => Promise<string | null>;

  constructor(getToken: () => Promise<string | null>) {
    this.baseUrl = API_URL;
    this.getToken = getToken;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = await this.getToken();
    
    const url = `${this.baseUrl}${endpoint}`;
    const config: RequestInit = {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      let error: ApiError;
      try {
        error = await response.json();
      } catch {
        error = {
          error: {
            code: "UNKNOWN",
            message: `Request failed with status ${response.status}`,
          },
        };
      }
      throw error;
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Auth endpoints
  async getMe() {
    return this.request("/auth/me");
  }

  // Projects endpoints
  async getProjects() {
    return this.request("/projects");
  }

  async getProject(id: string) {
    return this.request(`/projects/${id}`);
  }

  async createProject(data: { title: string; description?: string }) {
    return this.request("/projects", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateProject(id: string, data: { title?: string; description?: string }) {
    return this.request(`/projects/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async deleteProject(id: string) {
    return this.request(`/projects/${id}`, {
      method: "DELETE",
    });
  }

  // Files endpoints
  async uploadFile(projectId: string, file: File) {
    const token = await this.getToken();
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${this.baseUrl}/projects/${projectId}/upload`, {
      method: "POST",
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Upload failed");
    }

    return response.json();
  }

  async getFiles(projectId: string) {
    return this.request(`/projects/${projectId}/files`);
  }

  async deleteFile(projectId: string, fileId: string) {
    return this.request(`/projects/${projectId}/files/${fileId}`, {
      method: "DELETE",
    });
  }

  // Generation endpoints
  async generateBlog(projectId: string, data: any) {
    return this.request(`/projects/${projectId}/generate/blog`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async generateSocial(projectId: string, data: any) {
    return this.request(`/projects/${projectId}/generate/social`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async generateEmail(projectId: string, data: any) {
    return this.request(`/projects/${projectId}/generate/email`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Outputs endpoints
  async getOutputs(projectId: string) {
    return this.request(`/projects/${projectId}/outputs`);
  }

  async getOutput(projectId: string, outputId: string) {
    return this.request(`/projects/${projectId}/outputs/${outputId}`);
  }

  async updateOutput(projectId: string, outputId: string, data: any) {
    return this.request(`/projects/${projectId}/outputs/${outputId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async deleteOutput(projectId: string, outputId: string) {
    return this.request(`/projects/${projectId}/outputs/${outputId}`, {
      method: "DELETE",
    });
  }

  // Templates endpoints
  async getTemplates() {
    return this.request("/templates");
  }

  async createTemplate(data: { name: string; type: string; prompt: string }) {
    return this.request("/templates/custom", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async deleteTemplate(id: string) {
    return this.request(`/templates/${id}`, {
      method: "DELETE",
    });
  }

  // User profile endpoints
  async getUserProfile() {
    return this.request("/users/me");
  }

  async updateUserProfile(data: any) {
    return this.request("/users/me", {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }
}
