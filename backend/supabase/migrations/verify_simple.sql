-- Simple Verification for Phase 1.1 Migration
-- Run each query separately in Supabase SQL Editor

-- 1. List all tables (should include transcriptions, usage_tracking, user_plans)
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- 2. Check new columns in projects table
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'projects'
AND column_name IN ('status', 'processing_started_at', 'processing_completed_at', 'error_message');

-- 3. Check new columns in files table  
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'files'
AND column_name IN ('duration_seconds', 'audio_codec', 'video_codec', 'is_compressed', 'original_size_bytes');

-- 4. Check functions exist
SELECT proname as function_name
FROM pg_proc 
WHERE pronamespace = 'public'::regnamespace
AND proname IN ('get_user_monthly_usage', 'can_user_create_project');

-- 5. Test the can_user_create_project function (replace with your actual user_id)
SELECT can_user_create_project('user_test123');

-- 6. Check transcriptions table structure
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'transcriptions'
ORDER BY ordinal_position;
