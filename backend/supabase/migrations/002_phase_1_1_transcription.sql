-- Migration: Phase 1.1 - Add Transcription Support
-- Description: Adds tables and columns needed for file upload and transcription features
-- Date: 2024-01-31
-- Safe to run multiple times (idempotent)

begin;

-- ========== TRANSCRIPTIONS TABLE ==========
-- Store transcription results from Groq/OpenAI/Local Whisper
create table if not exists public.transcriptions (
    id UUID primary key default gen_random_uuid(),
    file_id UUID references public.files(id) on delete cascade,
    user_id TEXT not null,
    content TEXT not null,
    language TEXT default 'en',
    duration_seconds FLOAT,
    word_count INTEGER,
    confidence FLOAT,
    segments JSONB,  -- Detailed segments with timestamps from Whisper
    provider TEXT default 'groq',  -- 'groq', 'openai', 'local'
    processing_time_ms INTEGER,
    created_at TIMESTAMPTZ not null default now()
);

-- Create index for faster queries
create index if not exists idx_transcriptions_file_id on public.transcriptions(file_id);
create index if not exists idx_transcriptions_user_id on public.transcriptions(user_id);

-- Enable RLS
alter table public.transcriptions enable row level security;

-- RLS Policy: Users can only access their own transcriptions
do $$
begin
  if not exists (
    select 1 from pg_policies 
    where schemaname='public' 
    and tablename='transcriptions' 
    and policyname='transcriptions_owner_all'
  ) then
    create policy transcriptions_owner_all
      on public.transcriptions
      for all
      to authenticated
      using (auth.uid()::text = user_id)
      with check (auth.uid()::text = user_id);
  end if;
end$$;

-- ========== USAGE TRACKING TABLE ==========
-- Track usage for enforcing free tier limits
create table if not exists public.usage_tracking (
    id UUID primary key default gen_random_uuid(),
    user_id TEXT not null,
    resource_type TEXT not null,  -- 'transcription', 'generation', 'export', etc.
    resource_id UUID,  -- Reference to the resource (project_id, file_id, etc.)
    credits_used INTEGER default 1,
    metadata JSONB,  -- Additional info like duration, file size, etc.
    created_at TIMESTAMPTZ not null default now()
);

-- Index for quick monthly usage queries
create index if not exists idx_usage_tracking_user_date 
  on public.usage_tracking(user_id, created_at desc);

create index if not exists idx_usage_tracking_resource_type 
  on public.usage_tracking(resource_type, created_at desc);

-- Enable RLS
alter table public.usage_tracking enable row level security;

-- RLS Policy: Users can only see their own usage
do $$
begin
  if not exists (
    select 1 from pg_policies 
    where schemaname='public' 
    and tablename='usage_tracking' 
    and policyname='usage_tracking_owner_select'
  ) then
    create policy usage_tracking_owner_select
      on public.usage_tracking
      for select
      to authenticated
      using (auth.uid()::text = user_id);
  end if;
end$$;

-- ========== UPDATE PROJECTS TABLE ==========
-- Add status tracking fields for processing state
alter table public.projects 
  add column if not exists status TEXT default 'created',
  add column if not exists processing_started_at TIMESTAMPTZ,
  add column if not exists processing_completed_at TIMESTAMPTZ,
  add column if not exists error_message TEXT;

-- Add check constraint for valid status values
do $$
begin
  if not exists (
    select 1 from pg_constraint 
    where conname = 'projects_status_check'
  ) then
    alter table public.projects 
      add constraint projects_status_check 
      check (status in ('created', 'uploading', 'processing', 'completed', 'failed'));
  end if;
end$$;

-- ========== UPDATE FILES TABLE ==========
-- Add metadata fields for audio/video files
alter table public.files
  add column if not exists duration_seconds FLOAT,
  add column if not exists audio_codec TEXT,
  add column if not exists video_codec TEXT,
  add column if not exists is_compressed BOOLEAN default false,
  add column if not exists original_size_bytes BIGINT;

-- ========== USER PLANS TABLE ==========
-- Track user subscription plans (if not using Stripe yet)
create table if not exists public.user_plans (
    user_id TEXT primary key,
    plan_type TEXT not null default 'free',  -- 'free', 'pro', 'business'
    started_at TIMESTAMPTZ not null default now(),
    expires_at TIMESTAMPTZ,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    created_at TIMESTAMPTZ not null default now(),
    updated_at TIMESTAMPTZ not null default now()
);

-- Enable RLS
alter table public.user_plans enable row level security;

-- RLS Policy: Users can only see their own plan
do $$
begin
  if not exists (
    select 1 from pg_policies 
    where schemaname='public' 
    and tablename='user_plans' 
    and policyname='user_plans_owner_select'
  ) then
    create policy user_plans_owner_select
      on public.user_plans
      for select
      to authenticated
      using (auth.uid()::text = user_id);
  end if;
end$$;

-- ========== HELPER FUNCTIONS ==========

-- Function to get user's current usage for the month
create or replace function public.get_user_monthly_usage(
    p_user_id text,
    p_resource_type text default null
)
returns table(
    resource_type text,
    total_credits integer,
    count bigint
)
language plpgsql
security definer
as $$
begin
    return query
    select 
        ut.resource_type,
        sum(ut.credits_used)::integer as total_credits,
        count(*) as count
    from public.usage_tracking ut
    where 
        ut.user_id = p_user_id
        and ut.created_at >= date_trunc('month', current_timestamp)
        and (p_resource_type is null or ut.resource_type = p_resource_type)
    group by ut.resource_type;
end;
$$;

-- Function to check if user can create new project (based on plan limits)
create or replace function public.can_user_create_project(
    p_user_id text
)
returns json
language plpgsql
security definer
as $$
declare
    v_user_plan text;
    v_projects_this_month integer;
    v_limit integer;
    v_can_create boolean;
begin
    -- Get user's plan (default to 'free' if not found)
    select coalesce(up.plan_type, 'free') into v_user_plan
    from public.user_plans up
    where up.user_id = p_user_id;
    
    if v_user_plan is null then
        v_user_plan := 'free';
    end if;
    
    -- Count projects created this month
    select count(*) into v_projects_this_month
    from public.projects p
    where p.user_id = p_user_id
    and p.created_at >= date_trunc('month', current_timestamp);
    
    -- Determine limit based on plan
    v_limit := case v_user_plan
        when 'free' then 5
        when 'pro' then -1  -- unlimited
        when 'business' then -1  -- unlimited
        else 5  -- default to free tier
    end;
    
    -- Check if user can create project
    if v_limit = -1 then
        v_can_create := true;
    else
        v_can_create := v_projects_this_month < v_limit;
    end if;
    
    -- Return result as JSON
    return json_build_object(
        'can_create', v_can_create,
        'projects_used', v_projects_this_month,
        'projects_limit', v_limit,
        'user_plan', v_user_plan
    );
end;
$$;

-- ========== STORAGE POLICIES ==========
-- Ensure storage bucket policies are set up correctly

-- Policy for authenticated users to upload to their own folder
do $$
begin
  if not exists (
    select 1 from pg_policies 
    where schemaname='storage' 
    and tablename='objects' 
    and policyname='Users can upload to own folder'
  ) then
    create policy "Users can upload to own folder"
      on storage.objects
      for insert
      to authenticated
      with check (
        bucket_id = 'uploads' 
        and (storage.foldername(name))[1] = auth.uid()::text
      );
  end if;
end$$;

-- Policy for users to view their own files
do $$
begin
  if not exists (
    select 1 from pg_policies 
    where schemaname='storage' 
    and tablename='objects' 
    and policyname='Users can view own files'
  ) then
    create policy "Users can view own files"
      on storage.objects
      for select
      to authenticated
      using (
        bucket_id = 'uploads' 
        and (storage.foldername(name))[1] = auth.uid()::text
      );
  end if;
end$$;

-- Policy for users to delete their own files
do $$
begin
  if not exists (
    select 1 from pg_policies 
    where schemaname='storage' 
    and tablename='objects' 
    and policyname='Users can delete own files'
  ) then
    create policy "Users can delete own files"
      on storage.objects
      for delete
      to authenticated
      using (
        bucket_id = 'uploads' 
        and (storage.foldername(name))[1] = auth.uid()::text
      );
  end if;
end$$;

commit;

-- ========== MIGRATION COMPLETE ==========
-- To verify the migration:
-- 1. Check tables: select tablename from pg_tables where schemaname = 'public';
-- 2. Check policies: select * from pg_policies where schemaname = 'public';
-- 3. Check functions: select proname from pg_proc where pronamespace = 'public'::regnamespace;
