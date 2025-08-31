# 📋 Phase 2-3 Implementation Plan: Core Content Repurposing

## 🎯 Overview
This document outlines the comprehensive implementation plan for Phase 2 (Text Repurposing) and Phase 3 (Video Features) of the Repostr platform. These phases form the core functionality of our content repurposing engine.

---

## 📅 Timeline
- **Phase 2**: Weeks 3-4 (10 business days)
- **Phase 3**: Weeks 5-6 (10 business days)
- **Total Duration**: 20 business days

---

## 🏗️ Phase 2: Text Repurposing (Weeks 3-4)

### 2.1 File Upload & Storage System

#### Frontend Components
```typescript
// Components to build:
- FileUploadZone.tsx        // Drag-and-drop upload interface
- UploadProgress.tsx        // Real-time upload progress
- FileList.tsx             // Display uploaded files
- ProjectCard.tsx          // Individual project display
```

#### Backend Implementation
```python
# Existing endpoints (see API_REFERENCE.md):
# ✅ POST   /projects/                      # Create project
# ✅ GET    /projects/                      # List projects
# ✅ GET    /projects/{project_id}          # Get project
# ✅ PATCH  /projects/{project_id}          # Update project
# ✅ DELETE /projects/{project_id}          # Delete project
# ✅ POST   /projects/{project_id}/upload   # Upload file
# ✅ GET    /projects/{project_id}/files    # List files
# ✅ DELETE /projects/{project_id}/files/{file_id}  # Delete file

# Endpoints to enhance/implement:
# 🔧 POST   /projects/{project_id}/transcribe  # Trigger transcription
# 🔧 GET    /projects/{project_id}/transcription  # Get transcription
```

#### Database Schema (Supabase)
```sql
-- Already implemented tables (see DATABASE_SCHEMA.md):
-- ✅ profiles (user profiles with preferences)
-- ✅ projects (content projects)
-- ✅ files (uploaded media)
-- ✅ outputs (generated content)
-- ✅ templates (custom templates)

-- Additional tables needed for Phase 2-3:

-- Transcriptions table (to be added)
CREATE TABLE transcriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID REFERENCES files(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,
    language TEXT DEFAULT 'en',
    confidence FLOAT,
    word_timestamps JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE transcriptions ENABLE ROW LEVEL SECURITY;

-- RLS Policy
CREATE POLICY transcriptions_owner_all
    ON transcriptions
    FOR ALL
    TO authenticated
    USING (auth.uid()::text = user_id)
    WITH CHECK (auth.uid()::text = user_id);
```

#### Storage Configuration
```typescript
// Supabase Storage Buckets:
- user-uploads/       // Raw uploaded files
  ├── {user_id}/
  │   └── {project_id}/
  │       └── {file_name}
- processed-files/    // Processed outputs
  ├── {user_id}/
  │   └── {project_id}/
  │       ├── transcripts/
  │       ├── clips/
  │       └── exports/
```

### 2.2 Transcription Service

#### Implementation Steps
```python
# services/transcription_service.py
class TranscriptionService:
    """
    Handles audio/video transcription using Whisper
    """
    def __init__(self):
        self.model = self._load_whisper_model()
    
    async def transcribe_file(
        self,
        file_path: str,
        language: str = "auto"
    ) -> TranscriptionResult:
        # 1. Extract audio if video
        # 2. Process with Whisper
        # 3. Generate timestamps
        # 4. Store in database
        # 5. Return transcription
```

#### Background Job Queue (Celery)
```python
# tasks/transcription_tasks.py
@celery_app.task(bind=True, max_retries=3)
def process_transcription(self, file_id: str):
    """
    Async task for transcription processing
    """
    try:
        # 1. Download file from storage
        # 2. Run transcription
        # 3. Update database
        # 4. Notify frontend via WebSocket
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * 2 ** self.request.retries)
```

### 2.3 AI Content Generation Engine

#### Content Types & Prompts
```python
# config/prompts.py
CONTENT_PROMPTS = {
    "blog_post": {
        "system": "You are an expert content writer...",
        "user_template": "Convert this transcript into a blog post...",
        "max_tokens": 2000,
        "temperature": 0.7
    },
    "linkedin_post": {
        "system": "You are a LinkedIn content strategist...",
        "user_template": "Create an engaging LinkedIn post...",
        "max_tokens": 500,
        "temperature": 0.8
    },
    "twitter_thread": {
        "system": "You are a Twitter thread expert...",
        "user_template": "Create a Twitter thread (5-7 tweets)...",
        "max_tokens": 1000,
        "temperature": 0.8
    },
    "instagram_caption": {
        "system": "You are an Instagram marketing expert...",
        "user_template": "Write an Instagram caption with hashtags...",
        "max_tokens": 300,
        "temperature": 0.9
    }
}
```

#### Generation Service
```python
# services/generation_service.py
class ContentGenerationService:
    def __init__(self):
        self.llm_client = self._initialize_llm()
    
    async def generate_content(
        self,
        transcript: str,
        content_type: str,
        user_preferences: dict = None
    ) -> GeneratedContent:
        # 1. Get appropriate prompt
        # 2. Apply user preferences (tone, style, etc.)
        # 3. Call LLM API
        # 4. Post-process output
        # 5. Store in database
        # 6. Return formatted content
```

### 2.4 Output Management System

#### Database Schema
```sql
-- Outputs table already exists with proper structure:
-- ✅ Uses output_kind enum ('blog', 'social', 'email')
-- ✅ Uses output_status enum ('queued', 'processing', 'completed', 'failed')
-- ✅ Includes request JSONB for original request
-- ✅ Includes body TEXT for generated content
-- ✅ Includes metadata JSONB for additional data

-- Additional table needed for edit history:
CREATE TABLE output_edits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    output_id UUID REFERENCES outputs(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    edited_content TEXT NOT NULL,
    edit_type TEXT, -- 'manual', 'regenerate', 'ai_improve'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE output_edits ENABLE ROW LEVEL SECURITY;

-- RLS Policy
CREATE POLICY output_edits_owner_all
    ON output_edits
    FOR ALL
    TO authenticated
    USING (auth.uid()::text = user_id)
    WITH CHECK (auth.uid()::text = user_id);
```

#### Frontend Output Display
```typescript
// components/outputs/
- OutputTabs.tsx           // Tab navigation for content types
- BlogPostOutput.tsx       // Blog post display/edit
- LinkedInOutput.tsx       // LinkedIn post display/edit
- TwitterThreadOutput.tsx  // Twitter thread display/edit
- InstagramOutput.tsx      // Instagram caption display/edit
- OutputActions.tsx        // Copy, download, regenerate buttons
```

### 2.5 Export & Download Features

#### Export Formats
```typescript
interface ExportOptions {
  format: 'txt' | 'md' | 'docx' | 'pdf';
  includeMetadata: boolean;
  customStyling: boolean;
}

// services/export_service.ts
class ExportService {
  async exportContent(
    outputId: string,
    options: ExportOptions
  ): Promise<Blob> {
    // Generate file in requested format
  }
}
```

---

## 🎬 Phase 3: Video Features (Weeks 5-6)

### 3.1 Video Processing Pipeline

#### Architecture
```python
# services/video_service.py
class VideoProcessingService:
    """
    Handles video analysis and processing
    """
    def __init__(self):
        self.ffmpeg = FFmpegWrapper()
        self.scene_detector = SceneDetector()
    
    async def process_video(self, video_path: str):
        # 1. Extract metadata (duration, resolution, fps)
        # 2. Extract audio track
        # 3. Detect scene changes
        # 4. Identify key moments
        # 5. Generate preview thumbnails
```

### 3.2 Subtitle Generation

#### SRT Generation
```python
# services/subtitle_service.py
class SubtitleService:
    def generate_srt(
        self,
        transcription: Transcription,
        max_chars_per_line: int = 42
    ) -> str:
        """
        Generate SRT format subtitles from transcription
        """
        # 1. Parse word timestamps
        # 2. Group into subtitle segments
        # 3. Apply timing adjustments
        # 4. Format as SRT
        # 5. Save to storage
```

#### Frontend Subtitle Editor
```typescript
// components/subtitles/
- SubtitleEditor.tsx      // Edit subtitle text and timing
- SubtitlePreview.tsx     // Preview with video
- SubtitleStyles.tsx      // Customize appearance
- SubtitleExport.tsx      // Export options (SRT, VTT, etc.)
```

### 3.3 Auto-Clip Detection

#### AI Clip Detection Algorithm
```python
# services/clip_detection_service.py
class ClipDetectionService:
    def detect_clips(
        self,
        transcription: Transcription,
        video_metadata: dict
    ) -> List[ClipSuggestion]:
        """
        Identify interesting segments for short clips
        """
        clips = []
        
        # Detection strategies:
        # 1. High engagement phrases
        # 2. Complete thoughts/stories
        # 3. Scene changes + audio peaks
        # 4. Sentiment analysis peaks
        # 5. Keyword density
        
        return self._rank_clips(clips)
```

#### Clip Data Model
```sql
-- Suggested clips table
CREATE TABLE clip_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    file_id UUID REFERENCES files(id) ON DELETE CASCADE,
    title TEXT,
    start_time FLOAT NOT NULL,
    end_time FLOAT NOT NULL,
    transcript_segment TEXT,
    confidence_score FLOAT,
    clip_type TEXT, -- 'highlight', 'story', 'tip', 'quote'
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Exported clips table
CREATE TABLE exported_clips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    suggestion_id UUID REFERENCES clip_suggestions(id),
    storage_path TEXT NOT NULL UNIQUE,
    public_url TEXT,
    format TEXT, -- 'mp4', 'mov', 'webm'
    resolution TEXT, -- '1080x1920', '1080x1080', etc.
    has_subtitles BOOLEAN DEFAULT FALSE,
    exported_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on both tables
ALTER TABLE clip_suggestions ENABLE ROW LEVEL SECURITY;
ALTER TABLE exported_clips ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY clip_suggestions_owner_all
    ON clip_suggestions FOR ALL TO authenticated
    USING (auth.uid()::text = user_id)
    WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY exported_clips_owner_all
    ON exported_clips FOR ALL TO authenticated
    USING (auth.uid()::text = user_id)
    WITH CHECK (auth.uid()::text = user_id);
```

### 3.4 Video Export with FFmpeg

#### Export Service
```python
# services/export_service.py
class VideoExportService:
    def export_clip(
        self,
        source_video: str,
        start_time: float,
        end_time: float,
        options: ExportOptions
    ) -> str:
        """
        Export video clip with specified options
        """
        command = self._build_ffmpeg_command(
            source_video,
            start_time,
            end_time,
            options
        )
        
        # Execute FFmpeg command
        # Monitor progress
        # Upload to storage
        # Return download URL
```

#### Export Options
```typescript
interface VideoExportOptions {
  format: 'mp4' | 'mov' | 'webm';
  resolution: '1080x1920' | '1080x1080' | '1920x1080';
  includeSubtitles: boolean;
  subtitleStyle: SubtitleStyle;
  addWatermark: boolean;
  watermarkPosition: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
}
```

---

## 🔧 Technical Implementation Details

### API Endpoints Structure

#### Phase 2 Endpoints
```yaml
# Already Implemented (see API_REFERENCE.md):
✅ POST   /projects/                           # Create project
✅ GET    /projects/                           # List projects
✅ GET    /projects/{project_id}               # Get project
✅ PATCH  /projects/{project_id}               # Update project
✅ DELETE /projects/{project_id}               # Delete project
✅ POST   /projects/{project_id}/upload        # Upload file
✅ GET    /projects/{project_id}/files         # List files
✅ DELETE /projects/{project_id}/files/{file_id}  # Delete file
✅ POST   /projects/{project_id}/generate/blog    # Generate blog
✅ POST   /projects/{project_id}/generate/social  # Generate social
✅ POST   /projects/{project_id}/generate/email   # Generate email
✅ GET    /projects/{project_id}/outputs          # List outputs
✅ GET    /projects/{project_id}/outputs/{output_id}  # Get output
✅ PATCH  /projects/{project_id}/outputs/{output_id}  # Update output
✅ DELETE /projects/{project_id}/outputs/{output_id}  # Delete output

# To Implement/Enhance:
🔧 POST   /projects/{project_id}/transcribe    # Start transcription
🔧 GET    /projects/{project_id}/transcription # Get transcription
🔧 POST   /outputs/{output_id}/regenerate      # Regenerate content
🔧 POST   /outputs/{output_id}/export          # Export in various formats
```

#### Phase 3 Endpoints
```yaml
# To Implement:
🔧 POST   /projects/{project_id}/analyze       # Analyze video/audio
🔧 GET    /projects/{project_id}/metadata      # Get file metadata

# Subtitles
🔧 POST   /projects/{project_id}/subtitles/generate  # Generate subtitles
🔧 GET    /projects/{project_id}/subtitles          # Get subtitles
🔧 PATCH  /projects/{project_id}/subtitles/{id}     # Edit subtitles
🔧 POST   /projects/{project_id}/subtitles/export   # Export SRT/VTT

# Clips
🔧 GET    /projects/{project_id}/clips/suggestions  # Get clip suggestions
🔧 POST   /projects/{project_id}/clips/export       # Export video clip
🔧 GET    /projects/{project_id}/clips              # List exported clips
🔧 DELETE /projects/{project_id}/clips/{clip_id}    # Delete clip
```

### Frontend State Management

#### Redux Store Structure
```typescript
interface AppState {
  user: UserState;
  projects: ProjectsState;
  files: FilesState;
  outputs: OutputsState;
  transcriptions: TranscriptionsState;
  clips: ClipsState;
  ui: UIState;
}

interface ProjectsState {
  items: Project[];
  currentProject: Project | null;
  loading: boolean;
  error: string | null;
}

interface OutputsState {
  items: Output[];  // All outputs for current project
  byType: {
    blog: Output[];
    social: Output[];
    email: Output[];
  };
  currentOutput: Output | null;
  loading: boolean;
  regenerating: string | null;
}

interface TranscriptionsState {
  byFileId: Record<string, Transcription>;
  loading: boolean;
  processing: string | null; // file_id being processed
}
```

### WebSocket Implementation

#### Real-time Updates
```typescript
// services/websocket.ts
class WebSocketService {
  private ws: WebSocket;
  
  connect(userId: string) {
    this.ws = new WebSocket(`${WS_URL}/ws/${userId}`);
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch(data.type) {
        case 'transcription_complete':
          // Update UI
          break;
        case 'generation_complete':
          // Update outputs
          break;
        case 'processing_error':
          // Show error
          break;
      }
    };
  }
}
```

### Error Handling Strategy

#### Backend Error Classes
```python
# core/exceptions.py
class RepostrException(Exception):
    """Base exception class"""
    pass

class FileProcessingError(RepostrException):
    """Raised when file processing fails"""
    pass

class TranscriptionError(RepostrException):
    """Raised when transcription fails"""
    pass

class GenerationError(RepostrException):
    """Raised when content generation fails"""
    pass

class QuotaExceededError(RepostrException):
    """Raised when user exceeds plan limits"""
    pass
```

#### Frontend Error Handling
```typescript
// utils/error-handler.ts
export class ErrorHandler {
  static handle(error: any): void {
    if (error.response?.status === 429) {
      toast.error('You have exceeded your plan limits');
    } else if (error.response?.status === 413) {
      toast.error('File size too large');
    } else if (error.response?.status === 415) {
      toast.error('Unsupported file format');
    } else {
      toast.error('An unexpected error occurred');
    }
  }
}
```

---

## 🧪 Testing Strategy

### Unit Tests
```python
# tests/test_transcription.py
def test_whisper_transcription():
    """Test Whisper transcription accuracy"""
    pass

def test_subtitle_generation():
    """Test SRT format generation"""
    pass

# tests/test_generation.py
def test_blog_generation():
    """Test blog post generation from transcript"""
    pass

def test_social_media_generation():
    """Test social media content generation"""
    pass
```

### Integration Tests
```python
# tests/integration/test_workflow.py
def test_complete_workflow():
    """
    Test complete workflow:
    1. Upload file
    2. Transcribe
    3. Generate content
    4. Export
    """
    pass
```

### Frontend Tests
```typescript
// __tests__/FileUpload.test.tsx
describe('FileUpload', () => {
  it('should accept valid file formats', () => {});
  it('should reject invalid formats', () => {});
  it('should show upload progress', () => {});
});

// __tests__/OutputGeneration.test.tsx
describe('OutputGeneration', () => {
  it('should display all content types', () => {});
  it('should allow editing', () => {});
  it('should handle regeneration', () => {});
});
```

---

## 📊 Performance Optimization

### Caching Strategy
```python
# Redis caching for frequently accessed data
CACHE_CONFIG = {
    'transcriptions': 3600,  # 1 hour
    'generated_content': 7200,  # 2 hours
    'user_projects': 300,  # 5 minutes
    'clip_suggestions': 1800,  # 30 minutes
}
```

### Database Optimization
```sql
-- Indexes for performance
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_files_project_id ON files(project_id);
CREATE INDEX idx_outputs_project_id ON outputs(project_id);
CREATE INDEX idx_clips_project_id ON clip_suggestions(project_id);

-- Materialized view for user statistics
CREATE MATERIALIZED VIEW user_statistics AS
SELECT 
    user_id,
    COUNT(DISTINCT projects.id) as total_projects,
    COUNT(DISTINCT files.id) as total_files,
    SUM(files.duration_seconds) as total_duration
FROM projects
LEFT JOIN files ON projects.id = files.project_id
GROUP BY user_id;
```

### File Processing Optimization
- Use streaming for large files
- Implement chunked uploads
- Process video in segments
- Cache transcription segments
- Use CDN for static assets

---

## 🚀 Deployment Considerations

### Environment Variables
```env
# Already configured (from existing setup):
SUPABASE_URL=xxx
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx
CLERK_SECRET_KEY=xxx
CLERK_WEBHOOK_SECRET=xxx

# Phase 2-3 specific configs to add:
WHISPER_MODEL_SIZE=base
MAX_FILE_SIZE_MB=500
MAX_VIDEO_DURATION_MINUTES=60
OPENAI_API_KEY=xxx
ANTHROPIC_API_KEY=xxx
FFMPEG_PATH=/usr/bin/ffmpeg
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0

# Storage bucket names
STORAGE_BUCKET_UPLOADS=uploads
STORAGE_BUCKET_EXPORTS=exports
```

### Infrastructure Requirements
- **CPU**: 4+ cores for video processing
- **RAM**: 16GB minimum (32GB recommended)
- **Storage**: 100GB+ for file storage
- **GPU**: Optional but recommended for Whisper

### Monitoring & Logging
```python
# Implement comprehensive logging
import structlog

logger = structlog.get_logger()

logger.info(
    "transcription_started",
    file_id=file_id,
    file_size=file_size,
    user_id=user_id
)
```

---

## 📈 Success Metrics

### Phase 2 Metrics
- Average transcription time < 2 minutes
- Content generation time < 30 seconds
- User satisfaction > 4.5/5
- Export success rate > 99%

### Phase 3 Metrics
- Subtitle accuracy > 95%
- Clip suggestion relevance > 80%
- Video export time < 5 minutes
- Storage optimization > 50% compression

---

## 🎯 Deliverables Checklist

### Phase 2 Deliverables
- [ ] File upload interface with progress tracking
- [ ] Transcription service with Whisper integration
- [ ] Content generation for 4 platforms
- [ ] Output management with editing
- [ ] Export functionality (text formats)
- [ ] Background job processing
- [ ] WebSocket real-time updates

### Phase 3 Deliverables
- [ ] Video metadata extraction
- [ ] Subtitle generation (SRT format)
- [ ] Auto-clip detection algorithm
- [ ] Video clip export with FFmpeg
- [ ] Subtitle editor interface
- [ ] Clip preview and selection UI
- [ ] Batch export functionality

---

## 🔄 Risk Mitigation

### Technical Risks
1. **Large file processing**: Implement chunking and streaming
2. **AI API costs**: Cache results, offer self-hosted option
3. **Video processing time**: Use queue system, show progress
4. **Storage costs**: Implement retention policies, compression

### Business Risks
1. **User adoption**: Focus on UX, provide tutorials
2. **Competition**: Differentiate with speed and simplicity
3. **Scalability**: Design for horizontal scaling from start

---

## 📚 Documentation Requirements

### API Documentation
- OpenAPI/Swagger specification
- Postman collection
- Code examples in multiple languages

### User Documentation
- Getting started guide
- Video tutorials
- FAQ section
- Troubleshooting guide

### Developer Documentation
- Architecture overview
- Database schema
- Deployment guide
- Contributing guidelines

---

## 🏁 Definition of Done

### Phase 2 Completion Criteria
1. User can upload audio/video files
2. Files are automatically transcribed
3. Content is generated for all 4 platforms
4. User can edit and export content
5. All features work within plan limits
6. 90% test coverage achieved

### Phase 3 Completion Criteria
1. Subtitles generated with 95% accuracy
2. Relevant clips identified automatically
3. Videos exported in multiple formats
4. All video features integrated in UI
5. Performance meets target metrics
6. Documentation complete

---

## 📞 Support & Resources

### Team Contacts
- Technical Lead: [Contact]
- Product Manager: [Contact]
- DevOps Lead: [Contact]

### External Resources
- [Whisper Documentation](https://github.com/openai/whisper)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [Supabase Documentation](https://supabase.com/docs)
- [OpenAI API Reference](https://platform.openai.com/docs)

---

*Last Updated: [Current Date]*
*Version: 1.0*
