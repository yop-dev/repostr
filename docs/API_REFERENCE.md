# 📚 Repostr API Reference

**Version:** 1.0  
**Base URL:** `http://localhost:8000` (development) / `https://api.repostr.com` (production)

## 🔐 Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```bash
Authorization: Bearer <your-jwt-token>
```

The JWT token is obtained from Clerk authentication and should be included in all requests to protected endpoints.

---

## 📋 Table of Contents

- [Authentication](#authentication-endpoints)
- [Anonymous Upload](#anonymous-upload-endpoints)
- [Users](#users-endpoints)
- [Projects](#projects-endpoints)
- [Files](#files-endpoints)
- [Content Generation](#content-generation-endpoints)
- [Outputs](#outputs-endpoints)
- [Templates](#templates-endpoints)
- [Billing](#billing-endpoints)
- [Admin](#admin-endpoints)

---

## Authentication Endpoints

### Get Current User Info
Returns user information from the verified Clerk JWT.

```http
GET /auth/me
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Response:** `200 OK`
```json
{
  "user_id": "clerk_user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Clerk Webhook
Handles Clerk webhooks for user lifecycle events (created/updated/deleted).

```http
POST /auth/webhook
```

**Note:** This endpoint verifies Svix signature when `CLERK_WEBHOOK_SECRET` is configured.

**Response:** `200 OK`
```json
{
  "status": "processed"
}
```

---

## Anonymous Upload Endpoints

**Note:** These endpoints allow file upload and transcription without authentication for "try for free" functionality.

### Upload File Anonymously
Upload an audio/video file without authentication and get a session token.

```http
POST /anonymous/upload
```

**Headers:**
- `Content-Type: multipart/form-data`

**Request Body (multipart/form-data):**
- `file` (binary, required): The audio/video file to upload
- `name` (string, required): Project name (1-100 characters)
- `description` (string, optional): Project description (max 500 characters)
- `language` (string, optional): Language code (ISO 639-1, default: "en")

**File Limits:**
- **Max size**: 10MB (smaller than authenticated users)
- **Max duration**: 15 minutes
- **Allowed formats**: `.mp3`, `.wav`, `.m4a`, `.aac`, `.ogg`

**Rate Limits:**
- **3 uploads per hour**
- **5 uploads per day**

**Response:** `200 OK`
```json
{
  "session_token": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_name": "podcast_episode.mp3",
  "file_size": 8388608,
  "status": "processing",
  "estimated_time_seconds": 45,
  "expires_at": "2024-02-07T00:00:00Z",
  "message": "File uploaded successfully. Processing will complete in approximately 45 seconds."
}
```

**Error Responses:**
```json
// Rate limit exceeded
{
  "error": "rate_limit_exceeded",
  "message": "Upload limit reached. Try again in 23 minutes or sign up for unlimited uploads.",
  "retry_after": 1380,
  "signup_suggestion": "Sign up for free to get unlimited uploads and advanced features!"
}

// File too large
{
  "error": "file_too_large",
  "message": "File size exceeds 10MB limit for anonymous uploads.",
  "details": {
    "file_size_mb": 15.2,
    "max_size_mb": 10
  },
  "signup_suggestion": "Sign up for free to upload files up to 25MB!"
}
```

### Check Processing Status
Check the processing status of an anonymous upload.

```http
GET /anonymous/{session_token}/status
```

**Path Parameters:**
- `session_token` (string, required): The session token from upload response

**Response:** `200 OK`
```json
{
  "session_token": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
  "status": "processing",
  "progress_percentage": 75,
  "estimated_time_remaining": 12,
  "file_name": "podcast_episode.mp3",
  "file_size": 8388608,
  "created_at": "2024-01-31T10:00:00Z",
  "expires_at": "2024-02-07T10:00:00Z",
  "is_expired": false,
  "error_message": null
}
```

**Status Values:**
- `uploaded` - File uploaded, processing not started
- `processing` - Transcription in progress
- `completed` - Transcription completed, ready for viewing
- `failed` - Processing failed
- `claimed` - Session claimed by authenticated user

### Get Transcription Results (Blurred)
Get blurred transcription results that require signup to view fully.

```http
GET /anonymous/{session_token}
```

**Path Parameters:**
- `session_token` (string, required): The session token from upload response

**Response:** `200 OK`
```json
{
  "session_token": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
  "status": "completed",
  "transcription_preview": {
    "preview_text": "Welcome to our podcast about AI and content creation. Today we're discussing how artificial intelligence is transforming the way creators produce and distribute content across multiple platforms...",
    "total_word_count": 2847,
    "duration_seconds": 1847.3,
    "language": "en",
    "confidence": 0.94,
    "processing_time_ms": 15420
  },
  "is_blurred": true,
  "signup_required": true,
  "expires_at": "2024-02-07T10:00:00Z",
  "conversion_message": "Your 31-minute audio has been transcribed into 2,847 words. Sign up free to view the complete transcription and unlock powerful repurposing features!",
  "file_info": {
    "file_name": "podcast_episode.mp3",
    "file_size_mb": 8.0,
    "duration_minutes": 30.8,
    "estimated_reading_time": 9.2
  },
  "usage_stats": {
    "total_users": "10,000+",
    "files_processed_today": "247",
    "average_satisfaction": "4.9/5",
    "time_saved_hours": "15,000+"
  }
}
```

**Error Responses:**
```json
// Session not found
{
  "error": "session_not_found",
  "message": "Session token not found or invalid.",
  "signup_suggestion": "Sign up to create an account and manage your transcriptions!"
}

// Session expired
{
  "error": "session_expired",
  "message": "This session has expired. Anonymous sessions are valid for 7 days.",
  "signup_suggestion": "Sign up to keep your transcriptions forever!"
}

// Still processing
{
  "error": "still_processing",
  "message": "Transcription is still being processed. Please check status endpoint.",
  "session_token": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz"
}
```

### Claim Anonymous Session
Associate an anonymous session with an authenticated user account.

```http
POST /anonymous/{session_token}/claim
```

**Headers:**
- `Authorization: Bearer <token>` (required)

**Path Parameters:**
- `session_token` (string, required): The session token to claim

**Request Body:**
```json
{}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "transcription_id": "cc0e8400-e29b-41d4-a716-446655440007",
  "full_content": "Welcome to our podcast about AI and content creation. Today we're discussing how artificial intelligence is transforming the way creators produce and distribute content across multiple platforms. [... full transcription content ...]",
  "claimed_at": "2024-01-31T10:30:00Z",
  "error": null,
  "project_data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user_2abcdef123456",
    "title": "My Podcast Episode",
    "description": "Episode about AI and content creation",
    "created_at": "2024-01-31T10:00:00Z",
    "updated_at": "2024-01-31T10:30:00Z"
  },
  "transcription_data": {
    "id": "cc0e8400-e29b-41d4-a716-446655440007",
    "content": "[full content]",
    "word_count": 2847,
    "duration_seconds": 1847.3,
    "confidence": 0.94,
    "language": "en",
    "provider": "groq",
    "created_at": "2024-01-31T10:15:00Z"
  }
}
```

**Error Responses:**
```json
// Session already claimed
{
  "success": false,
  "error": "already_claimed",
  "message": "This session has already been claimed by another user."
}

// Session expired
{
  "success": false,
  "error": "session_expired",
  "message": "This session has expired and cannot be claimed."
}

// Session not found
{
  "success": false,
  "error": "session_not_found",
  "message": "Session token not found or invalid."
}
```

### Get Rate Limit Info
Check current rate limit status for anonymous uploads.

```http
GET /anonymous/rate-limit
```

**Response:** `200 OK`
```json
{
  "uploads_used_hour": 2,
  "uploads_used_day": 4,
  "uploads_remaining_hour": 1,
  "uploads_remaining_day": 1,
  "reset_time_hour": "2024-01-31T11:00:00Z",
  "reset_time_day": "2024-02-01T00:00:00Z",
  "is_limited": false
}
```

---

## Users Endpoints

### Get User Profile
Fetch the logged-in user's profile and settings.

```http
GET /users/me
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Response:** `200 OK`
```json
{
  "user_id": "clerk_user_123",
  "name": "John Doe",
  "preferences": {
    "language": "en",
    "timezone": "UTC"
  },
  "tone_of_voice": "professional"
}
```

### Update User Profile
Update user profile including name, preferences, and tone of voice.

```http
PATCH /users/me
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Request Body:**
```json
{
  "name": "Jane Doe",
  "preferences": {
    "language": "en",
    "timezone": "EST"
  },
  "tone_of_voice": "casual"
}
```

**Response:** `200 OK`
```json
{
  "user_id": "clerk_user_123",
  "name": "Jane Doe",
  "preferences": {
    "language": "en",
    "timezone": "EST"
  },
  "tone_of_voice": "casual"
}
```

---

## Projects Endpoints

### Create Project
Create a new content repurposing project.

```http
POST /projects/
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Request Body:**
```json
{
  "title": "My Podcast Episode",
  "description": "Episode about AI and content creation"
}
```

**Response:** `200 OK`
```json
{
  "id": "project_123",
  "user_id": "clerk_user_123",
  "title": "My Podcast Episode",
  "description": "Episode about AI and content creation",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### List Projects
Get all projects for the authenticated user.

```http
GET /projects/
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Response:** `200 OK`
```json
[
  {
    "id": "project_123",
    "user_id": "clerk_user_123",
    "title": "My Podcast Episode",
    "description": "Episode about AI and content creation",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### Get Project
Get a specific project by ID.

```http
GET /projects/{project_id}
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Path Parameters:**
- `project_id` (string, required): The project ID

**Response:** `200 OK`
```json
{
  "id": "project_123",
  "user_id": "clerk_user_123",
  "title": "My Podcast Episode",
  "description": "Episode about AI and content creation",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Update Project
Update project details.

```http
PATCH /projects/{project_id}
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Path Parameters:**
- `project_id` (string, required): The project ID

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description"
}
```

**Response:** `200 OK`
```json
{
  "id": "project_123",
  "user_id": "clerk_user_123",
  "title": "Updated Title",
  "description": "Updated description",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Delete Project
Delete a project and all associated files.

```http
DELETE /projects/{project_id}
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Path Parameters:**
- `project_id` (string, required): The project ID

**Response:** `204 No Content`

---

## Files Endpoints

### Upload File
Upload an audio/video/text file for processing.

```http
POST /projects/{project_id}/upload
```

**Headers:**
- `Authorization: Bearer <token>` (optional)
- `Content-Type: multipart/form-data`

**Path Parameters:**
- `project_id` (string, required): The project ID

**Request Body (multipart/form-data):**
- `file` (binary, required): The file to upload

**Supported Formats:**
- Audio: `.mp3`, `.wav`, `.m4a`, `.aac`
- Video: `.mp4`, `.mov`, `.avi`, `.mkv`
- Text: `.txt`, `.docx`, `.pdf`

**Response:** `200 OK`
```json
{
  "file_id": "file_456",
  "filename": "episode.mp3",
  "size": 10485760,
  "duration": 3600,
  "status": "uploaded",
  "storage_path": "uploads/user_123/project_123/file_456.mp3"
}
```

### List Files
Get all files associated with a project.

```http
GET /projects/{project_id}/files
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Path Parameters:**
- `project_id` (string, required): The project ID

**Response:** `200 OK`
```json
[
  {
    "file_id": "file_456",
    "filename": "episode.mp3",
    "size": 10485760,
    "duration": 3600,
    "status": "processed",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Delete File
Delete a specific file from a project.

```http
DELETE /projects/{project_id}/files/{file_id}
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Path Parameters:**
- `project_id` (string, required): The project ID
- `file_id` (string, required): The file ID

**Response:** `204 No Content`

---

## Content Generation Endpoints

### Generate Blog Post
Generate a blog post from the project's transcribed content.

```http
POST /projects/{project_id}/generate/blog
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Path Parameters:**
- `project_id` (string, required): The project ID

**Request Body:**
```json
{
  "topic": "AI and Content Creation",
  "prompt_overrides": "Focus on practical tips",
  "tone_of_voice": "professional",
  "extras": {
    "include_quotes": true,
    "target_length": 1500
  }
}
```

**Response:** `202 Accepted`
```json
{
  "task_id": "task_789",
  "status": "processing",
  "estimated_time": 30
}
```

### Generate Social Media Content
Generate social media posts (LinkedIn, Twitter, Instagram).

```http
POST /projects/{project_id}/generate/social
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Path Parameters:**
- `project_id` (string, required): The project ID

**Request Body:**
```json
{
  "topic": "Key takeaways from the episode",
  "prompt_overrides": "Make it engaging and shareable",
  "tone_of_voice": "casual",
  "extras": {
    "platforms": ["linkedin", "twitter", "instagram"],
    "include_hashtags": true
  }
}
```

**Response:** `202 Accepted`
```json
{
  "task_id": "task_790",
  "status": "processing",
  "estimated_time": 20
}
```

### Generate Email Newsletter
Generate an email newsletter from the content.

```http
POST /projects/{project_id}/generate/email
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Path Parameters:**
- `project_id` (string, required): The project ID

**Request Body:**
```json
{
  "topic": "Weekly Newsletter",
  "prompt_overrides": "Include call-to-action",
  "tone_of_voice": "friendly",
  "extras": {
    "subject_line": true,
    "preview_text": true
  }
}
```

**Response:** `202 Accepted`
```json
{
  "task_id": "task_791",
  "status": "processing",
  "estimated_time": 25
}
```

---

## Outputs Endpoints

### List Outputs
Get all generated outputs for a project.

```http
GET /projects/{project_id}/outputs
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Path Parameters:**
- `project_id` (string, required): The project ID

**Response:** `200 OK`
```json
[
  {
    "output_id": "output_101",
    "type": "blog",
    "title": "AI and Content Creation: A Deep Dive",
    "content": "...",
    "word_count": 1500,
    "created_at": "2024-01-01T00:00:00Z"
  },
  {
    "output_id": "output_102",
    "type": "linkedin",
    "content": "...",
    "character_count": 450,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Get Output
Get a specific output by ID.

```http
GET /projects/{project_id}/outputs/{output_id}
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Path Parameters:**
- `project_id` (string, required): The project ID
- `output_id` (string, required): The output ID

**Response:** `200 OK`
```json
{
  "output_id": "output_101",
  "type": "blog",
  "title": "AI and Content Creation: A Deep Dive",
  "content": "Full blog post content...",
  "metadata": {
    "word_count": 1500,
    "reading_time": 6,
    "keywords": ["AI", "content", "automation"]
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Update Output
Edit or modify generated output.

```http
PATCH /projects/{project_id}/outputs/{output_id}
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Path Parameters:**
- `project_id` (string, required): The project ID
- `output_id` (string, required): The output ID

**Request Body:**
```json
{
  "body": "Updated content here...",
  "metadata": {
    "edited": true,
    "edit_notes": "Fixed typos and improved flow"
  }
}
```

**Response:** `200 OK`
```json
{
  "output_id": "output_101",
  "status": "updated"
}
```

### Delete Output
Delete a generated output.

```http
DELETE /projects/{project_id}/outputs/{output_id}
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Path Parameters:**
- `project_id` (string, required): The project ID
- `output_id` (string, required): The output ID

**Response:** `204 No Content`

---

## Templates Endpoints

### List Templates
Get all available content templates.

```http
GET /templates
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Response:** `200 OK`
```json
[
  {
    "template_id": "template_001",
    "name": "Tech Blog Post",
    "type": "blog",
    "description": "Template for technical blog posts",
    "is_custom": false
  },
  {
    "template_id": "template_002",
    "name": "LinkedIn Thought Leadership",
    "type": "social",
    "description": "Template for LinkedIn posts",
    "is_custom": false
  }
]
```

### Create Custom Template
Create a custom content template.

```http
POST /templates/custom
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Request Body:**
```json
{
  "name": "My Custom Template",
  "type": "blog",
  "prompt": "Generate a blog post that focuses on..."
}
```

**Response:** `200 OK`
```json
{
  "template_id": "template_custom_123",
  "name": "My Custom Template",
  "type": "blog",
  "prompt": "Generate a blog post that focuses on...",
  "is_custom": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Delete Template
Delete a custom template.

```http
DELETE /templates/{template_id}
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Path Parameters:**
- `template_id` (string, required): The template ID

**Response:** `204 No Content`

---

## Billing Endpoints

### Get Available Plans
Get list of available subscription plans.

```http
GET /billing/plans
```

**Response:** `200 OK`
```json
[
  {
    "plan_id": "free",
    "name": "Free",
    "price": 0,
    "limits": {
      "projects_per_month": 3,
      "file_size_mb": 50,
      "features": ["transcription", "basic_text"]
    }
  },
  {
    "plan_id": "pro",
    "name": "Pro",
    "price": 29,
    "limits": {
      "projects_per_month": "unlimited",
      "file_size_mb": 500,
      "features": ["transcription", "all_text", "video_clips", "subtitles"]
    }
  },
  {
    "plan_id": "business",
    "name": "Business",
    "price": 99,
    "limits": {
      "projects_per_month": "unlimited",
      "file_size_mb": 2000,
      "features": ["all", "api_access", "white_label", "priority_support"]
    }
  }
]
```

### Subscribe to Plan
Create or update subscription.

```http
POST /billing/subscribe
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Request Body:**
```json
{
  "plan_id": "pro",
  "payment_method_id": "pm_123456"
}
```

**Response:** `200 OK`
```json
{
  "subscription_id": "sub_123",
  "status": "active",
  "plan": "pro",
  "current_period_end": "2024-02-01T00:00:00Z"
}
```

### Get Subscription Status
Get current subscription status and usage.

```http
GET /billing/status
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Response:** `200 OK`
```json
{
  "subscription_id": "sub_123",
  "plan": "pro",
  "status": "active",
  "current_period_start": "2024-01-01T00:00:00Z",
  "current_period_end": "2024-02-01T00:00:00Z",
  "usage": {
    "projects_this_month": 12,
    "storage_used_mb": 1024
  }
}
```

### Billing Webhook
Handle Stripe webhook events.

```http
POST /billing/webhook
```

**Note:** This endpoint handles Stripe webhooks for subscription events.

**Response:** `200 OK`
```json
{
  "status": "processed"
}
```

---

## Admin Endpoints

**Note:** Admin endpoints require admin privileges.

### List All Users
Get list of all users (admin only).

```http
GET /admin/users
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Response:** `200 OK`
```json
[
  {
    "user_id": "clerk_user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "plan": "pro",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### List All Projects
Get list of all projects across all users (admin only).

```http
GET /admin/projects
```

**Headers:**
- `Authorization: Bearer <token>` (optional)

**Response:** `200 OK`
```json
[
  {
    "project_id": "project_123",
    "user_id": "clerk_user_123",
    "title": "Project Title",
    "file_count": 3,
    "output_count": 12,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

## System Endpoints

### Health Check
Basic health check endpoint.

```http
GET /
```

**Response:** `200 OK`
```json
{
  "status": "ok",
  "env": "development"
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or missing authentication token"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

API rate limits are enforced based on subscription tier:

- **Free**: 100 requests per hour
- **Pro**: 1000 requests per hour  
- **Business**: 10000 requests per hour

Rate limit information is included in response headers:
- `X-RateLimit-Limit`: Maximum requests per hour
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Webhooks

### Webhook Security

All webhooks include a signature header for verification:
- Clerk webhooks: `svix-signature`
- Stripe webhooks: `stripe-signature`

### Webhook Events

**Clerk Events:**
- `user.created`
- `user.updated`
- `user.deleted`

**Stripe Events:**
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`

---

## Data Models

### Project Model
```typescript
interface Project {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  created_at: string;
  updated_at: string;
}
```

### User Profile Model
```typescript
interface UserProfile {
  user_id: string;
  name?: string;
  preferences: Record<string, any>;
  tone_of_voice?: string;
}
```

### Generate Request Model
```typescript
interface GenerateRequest {
  topic?: string;
  prompt_overrides?: string;
  tone_of_voice?: string;
  extras?: Record<string, any>;
}
```

### Output Update Model
```typescript
interface OutputUpdate {
  body?: string;
  metadata?: Record<string, any>;
}
```

### Template Create Model
```typescript
interface TemplateCreate {
  name: string;
  type: string;
  prompt: string;
}
```

---

## SDK Examples

### JavaScript/TypeScript
```typescript
// Initialize client
const client = new RepostrClient({
  apiKey: 'your-jwt-token',
  baseUrl: 'https://api.repostr.com'
});

// Create project
const project = await client.projects.create({
  title: 'My Podcast Episode',
  description: 'Episode about AI'
});

// Upload file
const file = await client.files.upload(project.id, fileBlob);

// Generate content
const blogPost = await client.generate.blog(project.id, {
  tone_of_voice: 'professional'
});
```

### Python
```python
# Initialize client
client = RepostrClient(
    api_key='your-jwt-token',
    base_url='https://api.repostr.com'
)

# Create project
project = client.projects.create(
    title='My Podcast Episode',
    description='Episode about AI'
)

# Upload file
file = client.files.upload(project.id, file_path)

# Generate content
blog_post = client.generate.blog(
    project.id,
    tone_of_voice='professional'
)
```

### cURL
```bash
# Create project
curl -X POST https://api.repostr.com/projects/ \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Podcast Episode"}'

# Upload file
curl -X POST https://api.repostr.com/projects/project_123/upload \
  -H "Authorization: Bearer your-jwt-token" \
  -F "file=@/path/to/file.mp3"

# Generate blog post
curl -X POST https://api.repostr.com/projects/project_123/generate/blog \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{"tone_of_voice": "professional"}'
```

---

## Support

For API support and questions:
- Email: api@repostr.com
- Documentation: https://docs.repostr.com
- Status Page: https://status.repostr.com

---

*Last Updated: 2024-01-01*  
*API Version: 1.0*
