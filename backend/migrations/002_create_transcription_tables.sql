-- Migration: Create transcription-related tables
-- Version: 002
-- Description: Add tables for transcription projects and results

BEGIN;

-- Required extension for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Drop any existing objects if needed (for clean re-runs)
DROP TABLE IF EXISTS transcriptions CASCADE;
DROP TABLE IF EXISTS usage_tracking CASCADE;
DROP TABLE IF EXISTS user_plans CASCADE;
DROP VIEW IF EXISTS user_usage_stats CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;

-- Create projects table if not exists
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Enable RLS on projects table
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- First drop any existing project policies to avoid conflicts
DROP POLICY IF EXISTS "Users can view own projects" ON projects;
DROP POLICY IF EXISTS "Users can create own projects" ON projects;
DROP POLICY IF EXISTS "Users can update own projects" ON projects;
DROP POLICY IF EXISTS "Users can delete own projects" ON projects;

-- Project RLS Policies
CREATE POLICY "Users can view own projects" ON projects
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can create own projects" ON projects
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update own projects" ON projects
    FOR UPDATE USING (auth.uid()::text = user_id);

CREATE POLICY "Users can delete own projects" ON projects
    FOR DELETE USING (auth.uid()::text = user_id);

-- Add transcription-related columns
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS language VARCHAR(10),
ADD COLUMN IF NOT EXISTS tags TEXT[],
ADD COLUMN IF NOT EXISTS file_name TEXT,
ADD COLUMN IF NOT EXISTS file_size BIGINT,
ADD COLUMN IF NOT EXISTS file_url TEXT,
ADD COLUMN IF NOT EXISTS storage_path TEXT,
ADD COLUMN IF NOT EXISTS duration_seconds NUMERIC,
ADD COLUMN IF NOT EXISTS transcription_id UUID,
ADD COLUMN IF NOT EXISTS transcription_status VARCHAR(20),
ADD COLUMN IF NOT EXISTS transcription_error TEXT,
ADD COLUMN IF NOT EXISTS transcribed_at TIMESTAMP WITH TIME ZONE;

-- Create index for status queries
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_transcription_status ON projects(transcription_status);
CREATE INDEX IF NOT EXISTS idx_projects_user_created ON projects(user_id, created_at DESC);

-- Create transcriptions table
CREATE TABLE IF NOT EXISTS transcriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    
    -- Transcription content
    text TEXT NOT NULL,
    language VARCHAR(10) NOT NULL,
    duration NUMERIC,
    word_count INTEGER NOT NULL,
    
    -- Segments with timestamps (JSONB for flexible schema)
    segments JSONB,
    
    -- Provider information
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    
    -- Processing information
    chunks_processed INTEGER,
    processing_time_seconds NUMERIC,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for transcriptions
CREATE INDEX IF NOT EXISTS idx_transcriptions_project ON transcriptions(project_id);
CREATE INDEX IF NOT EXISTS idx_transcriptions_user ON transcriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_transcriptions_created ON transcriptions(created_at DESC);

-- Create user_usage_stats view for tracking limits
CREATE OR REPLACE VIEW user_usage_stats AS
SELECT 
    user_id,
    COUNT(*) FILTER (WHERE created_at >= date_trunc('month', CURRENT_DATE)) as projects_this_month,
    COUNT(*) as total_projects,
    COALESCE(SUM(duration_seconds) / 60, 0) as total_duration_minutes,
    COALESCE(SUM(duration_seconds) FILTER (WHERE created_at >= date_trunc('month', CURRENT_DATE)) / 60, 0) as duration_this_month_minutes
FROM projects
GROUP BY user_id;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for projects table
DROP TRIGGER IF EXISTS update_projects_updated_at ON projects;
CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for transcriptions table
DROP TRIGGER IF EXISTS update_transcriptions_updated_at ON transcriptions;
CREATE TRIGGER update_transcriptions_updated_at
    BEFORE UPDATE ON transcriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust based on your Supabase setup)
GRANT ALL ON projects TO authenticated;
GRANT ALL ON transcriptions TO authenticated;
GRANT SELECT ON user_usage_stats TO authenticated;

-- Add RLS (Row Level Security) policies
ALTER TABLE transcriptions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own transcriptions
CREATE POLICY "Users can view own transcriptions" ON transcriptions
    FOR SELECT USING (auth.uid()::text = user_id);

-- Policy: Users can create transcriptions for their projects
CREATE POLICY "Users can create own transcriptions" ON transcriptions
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

-- Policy: Users can update their own transcriptions
CREATE POLICY "Users can update own transcriptions" ON transcriptions
    FOR UPDATE USING (auth.uid()::text = user_id);

-- Policy: Users can delete their own transcriptions
CREATE POLICY "Users can delete own transcriptions" ON transcriptions
    FOR DELETE USING (auth.uid()::text = user_id);

-- Create user_plans table for subscription management
CREATE TABLE IF NOT EXISTS user_plans (
    user_id TEXT PRIMARY KEY,
    plan_type TEXT NOT NULL DEFAULT 'free',
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Enable RLS on user_plans
ALTER TABLE user_plans ENABLE ROW LEVEL SECURITY;

-- User plans RLS policies
CREATE POLICY "Users can view own plan" ON user_plans
    FOR SELECT USING (auth.uid()::text = user_id);

-- Create usage_tracking table
CREATE TABLE IF NOT EXISTS usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id UUID,
    credits_used INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Enable RLS on usage_tracking
ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;

-- Usage tracking RLS policies
CREATE POLICY "Users can view own usage" ON usage_tracking
    FOR SELECT USING (auth.uid()::text = user_id);

-- Add indexes for usage tracking
CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_date ON usage_tracking(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_resource ON usage_tracking(resource_type, created_at DESC);

-- Create trigger for user_plans table
DROP TRIGGER IF EXISTS update_user_plans_updated_at ON user_plans;
CREATE TRIGGER update_user_plans_updated_at
    BEFORE UPDATE ON user_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT SELECT ON user_plans TO authenticated;
GRANT SELECT ON usage_tracking TO authenticated;

COMMIT;
