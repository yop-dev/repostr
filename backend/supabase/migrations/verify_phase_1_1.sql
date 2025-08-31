-- Verification Script for Phase 1.1 Migration
-- Run this in Supabase SQL Editor to verify all tables and functions were created

-- 1. Check if new tables exist
SELECT 
    'Tables Created' as check_type,
    COUNT(*) as count,
    string_agg(tablename, ', ') as items
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('transcriptions', 'usage_tracking', 'user_plans');

-- 2. Check if columns were added to projects table
SELECT 
    'Project Columns Added' as check_type,
    COUNT(*) as count,
    string_agg(column_name, ', ') as items
FROM information_schema.columns 
WHERE table_schema = 'public'
AND table_name = 'projects' 
AND column_name IN ('status', 'processing_started_at', 'processing_completed_at', 'error_message');

-- 3. Check if columns were added to files table
SELECT 
    'Files Columns Added' as check_type,
    COUNT(*) as count,
    string_agg(column_name, ', ') as items
FROM information_schema.columns 
WHERE table_schema = 'public'
AND table_name = 'files' 
AND column_name IN ('duration_seconds', 'audio_codec', 'video_codec', 'is_compressed', 'original_size_bytes');

-- 4. Check if functions were created
SELECT 
    'Functions Created' as check_type,
    COUNT(*) as count,
    string_agg(proname, ', ') as items
FROM pg_proc 
WHERE pronamespace = 'public'::regnamespace
AND proname IN ('get_user_monthly_usage', 'can_user_create_project');

-- 5. Check RLS policies
SELECT 
    'RLS Policies' as check_type,
    COUNT(*) as count,
    string_agg(policyname, ', ') as items
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN ('transcriptions', 'usage_tracking', 'user_plans');

-- 6. Summary of all tables with row counts
SELECT 
    schemaname,
    tablename,
    n_live_tup as estimated_rows,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY tablename;
