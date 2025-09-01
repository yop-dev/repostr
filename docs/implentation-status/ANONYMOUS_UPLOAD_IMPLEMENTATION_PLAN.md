# 📋 Anonymous Upload Implementation Plan
**Feature**: "Try for Free" with Blurred Results Strategy  
**Date**: Current  
**Status**: Planning Phase

---

## 🎯 **Strategy Overview**

Implement a "freemium hook" where users can upload files anonymously, see blurred transcription results, and must sign up to view the full content. This maximizes conversion by demonstrating value before requiring commitment.

### **User Flow**
1. **Landing page** → "Get Started" button (no auth required)
2. **Anonymous upload** → File processes in background
3. **Blurred preview** → "Processing complete! Sign up to view"
4. **Sign up/Sign in** → Full transcription revealed + free tier limits

---

## 🔍 **Current State Analysis**

### ✅ **What We Have**
- **Complete transcription system** with Groq integration
- **Database schema** with transcriptions, projects, usage tracking
- **Frontend components** for file upload, transcription viewer
- **User authentication** via Clerk
- **Usage tracking** and tier limits

### ❌ **What's Missing for Anonymous Upload**

#### **1. Database Schema Gaps**
- **Anonymous sessions table** - Track anonymous uploads before signup
- **Session-to-user migration** - Associate anonymous data with new accounts
- **Temporary storage policies** - Allow anonymous uploads to specific bucket

#### **2. API Endpoints Missing**
- `POST /anonymous/upload` - Upload without authentication
- `GET /anonymous/{session_token}` - Get blurred results
- `POST /anonymous/{session_token}/claim` - Associate with user account
- `GET /anonymous/{session_token}/status` - Check processing status

#### **3. Frontend Components**
- **Blur overlay component** with signup CTA
- **Anonymous upload flow** without auth requirements
- **Session token management** for anonymous users
- **Conversion tracking** and analytics

---

## 🗄️ **Database Schema Extensions**

### **New Table: `anonymous_sessions`**
```sql
CREATE TABLE public.anonymous_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_token TEXT UNIQUE NOT NULL,
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    transcription_id UUID REFERENCES public.transcriptions(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    storage_path TEXT NOT NULL,
    status TEXT DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'processing', 'completed', 'failed', 'claimed')),
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '7 days'),
    claimed_by_user_id TEXT, -- Set when user claims the session
    claimed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_anonymous_sessions_token ON public.anonymous_sessions(session_token);
CREATE INDEX idx_anonymous_sessions_expires ON public.anonymous_sessions(expires_at);
CREATE INDEX idx_anonymous_sessions_status ON public.anonymous_sessions(status);

-- Auto-cleanup expired sessions
CREATE INDEX idx_anonymous_sessions_cleanup ON public.anonymous_sessions(expires_at) 
WHERE status != 'claimed';
```

### **Update Storage Policies**
```sql
-- Allow anonymous uploads to specific folder
CREATE POLICY "Anonymous uploads allowed"
ON storage.objects
FOR INSERT
TO anon
WITH CHECK (
    bucket_id = 'uploads' 
    AND (storage.foldername(name))[1] = 'anonymous'
);

-- Allow anonymous users to read their own uploads
CREATE POLICY "Anonymous can read own uploads"
ON storage.objects
FOR SELECT
TO anon
USING (
    bucket_id = 'uploads' 
    AND (storage.foldername(name))[1] = 'anonymous'
);
```

### **Update Projects Table**
```sql
-- Allow anonymous projects (user_id can be null temporarily)
ALTER TABLE public.projects 
ALTER COLUMN user_id DROP NOT NULL;

-- Add anonymous session reference
ALTER TABLE public.projects 
ADD COLUMN anonymous_session_id UUID REFERENCES public.anonymous_sessions(id);
```

---

## 🔌 **New API Endpoints**

### **1. Anonymous Upload**
```python
@router.post("/anonymous/upload", response_model=AnonymousUploadResponse)
async def upload_anonymous_file(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    request: Request = None
):
    """
    Upload file without authentication.
    Returns session token for later retrieval.
    """
    # Generate session token
    session_token = secrets.token_urlsafe(32)
    
    # Validate file (same as authenticated upload)
    # Upload to anonymous folder: anonymous/{session_token}/{filename}
    # Create anonymous_session record
    # Create project with anonymous_session_id
    # Start transcription in background
    
    return AnonymousUploadResponse(
        session_token=session_token,
        project_id=project_id,
        status="processing",
        estimated_time_seconds=30
    )
```

### **2. Get Anonymous Results (Blurred)**
```python
@router.get("/anonymous/{session_token}", response_model=AnonymousResultResponse)
async def get_anonymous_result(session_token: str):
    """
    Get transcription results for anonymous session.
    Returns blurred/redacted content if not claimed.
    """
    # Validate session token and check expiry
    # Get transcription results
    # Return blurred content with signup CTA
    
    return AnonymousResultResponse(
        session_token=session_token,
        status="completed",
        transcription_preview="This is a preview of your transcription...",
        is_blurred=True,
        word_count=1247,
        duration_seconds=180,
        signup_required=True
    )
```

### **3. Claim Anonymous Session**
```python
@router.post("/anonymous/{session_token}/claim", response_model=ClaimSessionResponse)
async def claim_anonymous_session(
    session_token: str,
    current_user: UserPrincipal = Depends(get_current_user)
):
    """
    Associate anonymous session with authenticated user.
    Reveals full transcription content.
    """
    # Validate session and user
    # Update anonymous_session with user_id
    # Update project with user_id
    # Return full transcription content
    
    return ClaimSessionResponse(
        project_id=project_id,
        transcription_id=transcription_id,
        full_content=transcription.content,
        claimed=True
    )
```

### **4. Anonymous Status Check**
```python
@router.get("/anonymous/{session_token}/status", response_model=AnonymousStatusResponse)
async def get_anonymous_status(session_token: str):
    """
    Check processing status for anonymous upload.
    """
    return AnonymousStatusResponse(
        session_token=session_token,
        status="processing",  # uploaded, processing, completed, failed
        progress_percentage=75,
        estimated_time_remaining=10
    )
```

---

## 🎨 **Frontend Components**

### **1. Anonymous Upload Flow**
```typescript
// New component: AnonymousUploadZone.tsx
const AnonymousUploadZone = () => {
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'processing' | 'completed'>('idle');
  
  const handleUpload = async (file: File, projectName: string) => {
    // Upload without auth
    const response = await api.uploadAnonymous(file, projectName);
    setSessionToken(response.session_token);
    setUploadStatus('processing');
    
    // Poll for completion
    pollTranscriptionStatus(response.session_token);
  };
  
  return (
    <div>
      {uploadStatus === 'idle' && <FileDropZone onUpload={handleUpload} />}
      {uploadStatus === 'processing' && <ProcessingIndicator />}
      {uploadStatus === 'completed' && <BlurredResults sessionToken={sessionToken} />}
    </div>
  );
};
```

### **2. Blurred Results Component**
```typescript
// New component: BlurredTranscriptionViewer.tsx
const BlurredTranscriptionViewer = ({ sessionToken }: { sessionToken: string }) => {
  const [result, setResult] = useState<AnonymousResult | null>(null);
  
  useEffect(() => {
    fetchAnonymousResult(sessionToken).then(setResult);
  }, [sessionToken]);
  
  return (
    <div className="relative">
      {/* Blurred content */}
      <div className="filter blur-sm select-none">
        <div className="p-6 bg-gray-50 rounded-lg">
          <p className="text-gray-600">
            {result?.transcription_preview}
          </p>
        </div>
      </div>
      
      {/* Signup overlay */}
      <div className="absolute inset-0 flex items-center justify-center bg-white/90">
        <Card className="p-6 text-center max-w-md">
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">Transcription Complete! 🎉</h3>
          <p className="text-gray-600 mb-4">
            Your {Math.round(result?.duration_seconds / 60)} minute audio has been transcribed into {result?.word_count} words.
          </p>
          <div className="space-y-2">
            <Button 
              className="w-full" 
              size="lg"
              onClick={() => signUp({ sessionToken })}
            >
              Sign Up Free - View Full Transcription
            </Button>
            <Button 
              variant="outline" 
              className="w-full"
              onClick={() => signIn({ sessionToken })}
            >
              Already have an account? Sign In
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-4">
            Free forever • No credit card required
          </p>
        </Card>
      </div>
    </div>
  );
};
```

### **3. Session Management**
```typescript
// Hook: useAnonymousSession.ts
export const useAnonymousSession = () => {
  const [sessionToken, setSessionToken] = useState<string | null>(
    localStorage.getItem('anonymous_session_token')
  );
  
  const saveSession = (token: string) => {
    setSessionToken(token);
    localStorage.setItem('anonymous_session_token', token);
  };
  
  const claimSession = async () => {
    if (!sessionToken) return;
    
    const response = await api.claimAnonymousSession(sessionToken);
    localStorage.removeItem('anonymous_session_token');
    return response;
  };
  
  return { sessionToken, saveSession, claimSession };
};
```

---

## 🔧 **Implementation Steps**

### **Phase 1: Database Setup (Day 1)**
1. **Create migration file**: `003_anonymous_upload_support.sql`
2. **Add anonymous_sessions table** with proper indexes
3. **Update storage policies** for anonymous uploads
4. **Modify projects table** to support anonymous sessions
5. **Test migration** on development database

### **Phase 2: Backend API (Day 2-3)**
1. **Create new models** for anonymous upload responses
2. **Implement anonymous upload endpoint** with file validation
3. **Add session token management** and expiry logic
4. **Create blurred content endpoint** with preview generation
5. **Implement claim session endpoint** for user association
6. **Add background cleanup** for expired sessions

### **Phase 3: Frontend Components (Day 4-5)**
1. **Build anonymous upload flow** without auth requirements
2. **Create blurred results viewer** with signup overlay
3. **Implement session management** with localStorage
4. **Add conversion tracking** and analytics
5. **Update landing page** with "Get Started" flow

### **Phase 4: Integration & Testing (Day 6-7)**
1. **End-to-end testing** of anonymous flow
2. **Conversion funnel optimization** and A/B testing
3. **Performance testing** with concurrent anonymous uploads
4. **Security review** of anonymous endpoints
5. **Analytics implementation** for conversion tracking

---

## 🛡️ **Security Considerations**

### **Rate Limiting**
```python
# Stricter limits for anonymous users
ANONYMOUS_RATE_LIMITS = {
    "uploads_per_hour": 3,
    "uploads_per_day": 5,
    "max_file_size_mb": 10,  # Smaller than authenticated users
}
```

### **Abuse Prevention**
- **IP-based rate limiting** for anonymous uploads
- **File type validation** and virus scanning
- **Session expiry** (7 days) with automatic cleanup
- **Captcha integration** for suspicious activity

### **Data Privacy**
- **Automatic cleanup** of unclaimed sessions
- **No personal data collection** for anonymous users
- **Clear data retention policy** in terms of service

---

## 📊 **Success Metrics**

### **Conversion Funnel**
1. **Landing page visits** → "Get Started" clicks
2. **File uploads** → Successful processing
3. **Blur overlay views** → Sign up attempts
4. **Sign ups** → Account activation
5. **Claimed sessions** → First paid project

### **Target Metrics**
- **Upload-to-signup conversion**: 25-35%
- **Anonymous upload completion**: 90%+
- **Session claim rate**: 80%+ of signups
- **Time to signup**: < 5 minutes from upload

---

## 🚀 **Launch Strategy**

### **Soft Launch (Week 1)**
- **Internal testing** with team members
- **Limited beta** with 10-20 external users
- **Conversion optimization** based on feedback

### **Public Launch (Week 2)**
- **Landing page update** with new flow
- **Social media campaign** highlighting free trial
- **Content marketing** about the new feature

### **Post-Launch (Week 3+)**
- **A/B testing** of blur effects and CTAs
- **Conversion rate optimization** 
- **Feature iteration** based on user behavior

---

## 🔄 **Future Enhancements**

### **Advanced Blur Effects**
- **Redacted document style** with black bars
- **Pixelated preview** for video content
- **Gradient fade** with teaser content

### **Social Proof**
- **User testimonials** on blur overlay
- **Usage statistics** ("Join 10,000+ creators")
- **Recent activity feed** ("Sarah just transcribed...")

### **Conversion Optimization**
- **Exit-intent popups** with special offers
- **Email capture** before file processing
- **Progressive disclosure** of features

---

## ✅ **Ready to Implement**

This plan provides a complete roadmap for implementing the anonymous upload feature with maximum conversion potential. The strategy balances user experience with business goals while maintaining security and scalability.

**Next steps:**
1. **Review and approve** this implementation plan
2. **Set up development environment** with database migration
3. **Begin Phase 1** database setup
4. **Parallel frontend mockups** for user testing

Would you like me to start implementing any specific phase of this plan?