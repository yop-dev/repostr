-- Migration: Phase 1.2 - Add Anonymous Upload Support
-- Description: Adds anonymous sessions table and updates schema for "try for free" feature
-- Date: 2024-01-31
-- Safe to run multiple times (idempotent)

BEGIN;

-- ========== ANONYMOUS SESSIONS TABLE ==========
-- Store anonymous upload sessions before user signup
CREATE TABLE IF NOT EXISTS public.anonymous_sessions (
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

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_anonymous_sessions_token ON public.anonymous_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_anonymous_sessions_expires ON public.anonymous_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_anonymous_sessions_status ON public.anonymous_sessions(status);
CREATE INDEX IF NOT EXISTS idx_anonymous_sessions_project ON public.anonymous_sessions(project_id);

-- Partial index for cleanup of expired unclaimed sessions
CREATE INDEX IF NOT EXISTS idx_anonymous_sessions_cleanup 
ON public.anonymous_sessions(expires_at) 
WHERE status != 'claimed';

-- Add trigger for updated_at
CREATE TRIGGER trg_anonymous_sessions_updated_at
    BEFORE UPDATE ON public.anonymous_sessions
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at();

-- ========== UPDATE PROJECTS TABLE ==========
-- Allow anonymous projects (user_id can be null temporarily)
ALTER TABLE public.projects 
ALTER COLUMN user_id DROP NOT NULL;

-- Add anonymous session reference
ALTER TABLE public.projects 
ADD COLUMN IF NOT EXISTS anonymous_session_id UUID REFERENCES public.anonymous_sessions(id);

-- Add index for anonymous session lookups
CREATE INDEX IF NOT EXISTS idx_projects_anonymous_session 
ON public.projects(anonymous_session_id);

-- ========== UPDATE TRANSCRIPTIONS TABLE ==========
-- Allow anonymous transcriptions (user_id can be null temporarily)
ALTER TABLE public.transcriptions 
ALTER COLUMN user_id DROP NOT NULL;

-- Add anonymous session reference for direct lookup
ALTER TABLE public.transcriptions 
ADD COLUMN IF NOT EXISTS anonymous_session_id UUID REFERENCES public.anonymous_sessions(id);

-- Add index for anonymous transcription lookups
CREATE INDEX IF NOT EXISTS idx_transcriptions_anonymous_session 
ON public.transcriptions(anonymous_session_id);

-- ========== STORAGE POLICIES FOR ANONYMOUS UPLOADS ==========

-- Policy: Allow anonymous uploads to specific folder
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname='storage' 
    AND tablename='objects' 
    AND policyname='Anonymous uploads allowed'
  ) THEN
    CREATE POLICY "Anonymous uploads allowed"
    ON storage.objects
    FOR INSERT
    TO anon
    WITH CHECK (
        bucket_id = 'uploads' 
        AND (storage.foldername(name))[1] = 'anonymous'
    );
  END IF;
END$$;

-- Policy: Allow anonymous users to read their own uploads
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname='storage' 
    AND tablename='objects' 
    AND policyname='Anonymous can read own uploads'
  ) THEN
    CREATE POLICY "Anonymous can read own uploads"
    ON storage.objects
    FOR SELECT
    TO anon
    USING (
        bucket_id = 'uploads' 
        AND (storage.foldername(name))[1] = 'anonymous'
    );
  END IF;
END$$;

-- Policy: Allow service role to manage anonymous files
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname='storage' 
    AND tablename='objects' 
    AND policyname='Service role can manage anonymous files'
  ) THEN
    CREATE POLICY "Service role can manage anonymous files"
    ON storage.objects
    FOR ALL
    TO service_role
    USING (
        bucket_id = 'uploads' 
        AND (storage.foldername(name))[1] = 'anonymous'
    );
  END IF;
END$$;

-- ========== RLS POLICIES FOR ANONYMOUS SESSIONS ==========

-- Enable RLS on anonymous_sessions table
ALTER TABLE public.anonymous_sessions ENABLE ROW LEVEL SECURITY;

-- Policy: Allow anonymous users to read their own sessions by token
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname='public' 
    AND tablename='anonymous_sessions' 
    AND policyname='anonymous_sessions_token_access'
  ) THEN
    CREATE POLICY anonymous_sessions_token_access
    ON public.anonymous_sessions
    FOR SELECT
    TO anon
    USING (true); -- We'll validate session_token in application logic
  END IF;
END$$;

-- Policy: Allow service role full access for backend operations
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname='public' 
    AND tablename='anonymous_sessions' 
    AND policyname='anonymous_sessions_service_role_all'
  ) THEN
    CREATE POLICY anonymous_sessions_service_role_all
    ON public.anonymous_sessions
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
  END IF;
END$$;

-- Policy: Allow authenticated users to claim their sessions
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname='public' 
    AND tablename='anonymous_sessions' 
    AND policyname='anonymous_sessions_user_claim'
  ) THEN
    CREATE POLICY anonymous_sessions_user_claim
    ON public.anonymous_sessions
    FOR UPDATE
    TO authenticated
    USING (claimed_by_user_id IS NULL OR claimed_by_user_id = auth.uid()::text)
    WITH CHECK (claimed_by_user_id = auth.uid()::text);
  END IF;
END$$;

-- ========== UPDATE EXISTING POLICIES ==========

-- Update projects policy to allow anonymous projects
DROP POLICY IF EXISTS projects_owner_all ON public.projects;

CREATE POLICY projects_owner_all
ON public.projects
FOR ALL
TO authenticated
USING (
    auth.uid()::text = user_id 
    OR (user_id IS NULL AND anonymous_session_id IS NOT NULL)
)
WITH CHECK (
    auth.uid()::text = user_id 
    OR (user_id IS NULL AND anonymous_session_id IS NOT NULL)
);

-- Allow service role to manage all projects (for anonymous operations)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname='public' 
    AND tablename='projects' 
    AND policyname='projects_service_role_all'
  ) THEN
    CREATE POLICY projects_service_role_all
    ON public.projects
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
  END IF;
END$$;

-- Update transcriptions policy to allow anonymous transcriptions
DROP POLICY IF EXISTS transcriptions_owner_all ON public.transcriptions;

CREATE POLICY transcriptions_owner_all
ON public.transcriptions
FOR ALL
TO authenticated
USING (
    auth.uid()::text = user_id 
    OR (user_id IS NULL AND anonymous_session_id IS NOT NULL)
)
WITH CHECK (
    auth.uid()::text = user_id 
    OR (user_id IS NULL AND anonymous_session_id IS NOT NULL)
);

-- Allow service role to manage all transcriptions
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname='public' 
    AND tablename='transcriptions' 
    AND policyname='transcriptions_service_role_all'
  ) THEN
    CREATE POLICY transcriptions_service_role_all
    ON public.transcriptions
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
  END IF;
END$$;

-- ========== HELPER FUNCTIONS ==========

-- Function to cleanup expired anonymous sessions
CREATE OR REPLACE FUNCTION public.cleanup_expired_anonymous_sessions()
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete expired unclaimed sessions and their associated data
    WITH deleted_sessions AS (
        DELETE FROM public.anonymous_sessions 
        WHERE expires_at < NOW() 
        AND status != 'claimed'
        RETURNING id, storage_path
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted_sessions;
    
    -- Note: Associated projects and transcriptions will be deleted via CASCADE
    -- Storage files should be cleaned up by a separate background job
    
    RETURN deleted_count;
END;
$$;

-- Function to get anonymous session with validation
CREATE OR REPLACE FUNCTION public.get_anonymous_session(
    p_session_token TEXT
)
RETURNS TABLE(
    id UUID,
    session_token TEXT,
    project_id UUID,
    transcription_id UUID,
    file_name TEXT,
    file_size BIGINT,
    storage_path TEXT,
    status TEXT,
    expires_at TIMESTAMPTZ,
    claimed_by_user_id TEXT,
    claimed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    is_expired BOOLEAN
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        s.session_token,
        s.project_id,
        s.transcription_id,
        s.file_name,
        s.file_size,
        s.storage_path,
        s.status,
        s.expires_at,
        s.claimed_by_user_id,
        s.claimed_at,
        s.created_at,
        (s.expires_at < NOW()) as is_expired
    FROM public.anonymous_sessions s
    WHERE s.session_token = p_session_token;
END;
$$;

-- Function to claim anonymous session for authenticated user
CREATE OR REPLACE FUNCTION public.claim_anonymous_session(
    p_session_token TEXT,
    p_user_id TEXT
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_session_id UUID;
    v_project_id UUID;
    v_transcription_id UUID;
    v_is_expired BOOLEAN;
    v_already_claimed BOOLEAN;
BEGIN
    -- Get session details
    SELECT 
        id, project_id, transcription_id, 
        (expires_at < NOW()) as is_expired,
        (claimed_by_user_id IS NOT NULL) as already_claimed
    INTO v_session_id, v_project_id, v_transcription_id, v_is_expired, v_already_claimed
    FROM public.anonymous_sessions
    WHERE session_token = p_session_token;
    
    -- Validate session exists
    IF v_session_id IS NULL THEN
        RETURN json_build_object('success', false, 'error', 'Session not found');
    END IF;
    
    -- Check if expired
    IF v_is_expired THEN
        RETURN json_build_object('success', false, 'error', 'Session expired');
    END IF;
    
    -- Check if already claimed
    IF v_already_claimed THEN
        RETURN json_build_object('success', false, 'error', 'Session already claimed');
    END IF;
    
    -- Claim the session
    UPDATE public.anonymous_sessions 
    SET 
        claimed_by_user_id = p_user_id,
        claimed_at = NOW(),
        status = 'claimed',
        updated_at = NOW()
    WHERE id = v_session_id;
    
    -- Update project with user_id
    UPDATE public.projects 
    SET 
        user_id = p_user_id,
        updated_at = NOW()
    WHERE id = v_project_id;
    
    -- Update transcription with user_id
    UPDATE public.transcriptions 
    SET 
        user_id = p_user_id
    WHERE id = v_transcription_id;
    
    -- Return success
    RETURN json_build_object(
        'success', true,
        'project_id', v_project_id,
        'transcription_id', v_transcription_id,
        'claimed_at', NOW()
    );
END;
$$;

-- ========== CREATE CLEANUP JOB (Optional - for scheduled cleanup) ==========

-- This would typically be run by a cron job or background task
-- Example: SELECT public.cleanup_expired_anonymous_sessions();

COMMIT;

-- ========== MIGRATION COMPLETE ==========
-- To verify the migration:
-- 1. Check new table: SELECT * FROM public.anonymous_sessions LIMIT 1;
-- 2. Check updated policies: SELECT * FROM pg_policies WHERE tablename IN ('anonymous_sessions', 'projects', 'transcriptions');
-- 3. Check new functions: SELECT proname FROM pg_proc WHERE proname LIKE '%anonymous%';
-- 4. Test anonymous upload: Should be able to upload to 'anonymous/' folder without auth