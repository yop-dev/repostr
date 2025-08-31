# 🗄️ Repostr Database Schema Reference

**Database:** PostgreSQL (Supabase)  
**Last Updated:** 2024-01-01  
**Version:** 1.0

## 📊 Overview

This document describes the complete database schema for the Repostr content repurposing platform. The schema is designed to work with Supabase (PostgreSQL), Clerk authentication, and FastAPI backend.

### Key Features:
- **Row Level Security (RLS)** enabled on all tables
- **Automatic timestamps** with trigger functions
- **UUID primary keys** for better scalability
- **JSONB fields** for flexible metadata storage
- **Cascading deletes** for data integrity
- **Optimized indexes** for query performance

---

## 🏗️ Database Structure

### Extensions Used
```sql
pgcrypto -- For UUID generation (gen_random_uuid())
```

### Custom Types (Enums)
```sql
-- Output types for generated content
CREATE TYPE output_kind AS ENUM ('blog', 'social', 'email');

-- Status tracking for generation tasks
CREATE TYPE output_status AS ENUM ('queued', 'processing', 'completed', 'failed');

-- Template types for content generation
CREATE TYPE template_type AS ENUM ('blog', 'linkedin', 'twitter', 'instagram', 'email');
```

---

## 📋 Tables

### 1. **profiles**
Stores user profiles linked to Clerk authentication.

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `user_id` | `TEXT` | PRIMARY KEY | Clerk user ID (e.g., "user_2abc...") |
| `name` | `TEXT` | NULL | User's display name |
| `preferences` | `JSONB` | NOT NULL, DEFAULT '{}' | User preferences and settings |
| `tone_of_voice` | `TEXT` | NULL | Default tone for content generation |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- Primary key on `user_id`

**Triggers:**
- `trg_profiles_updated_at` - Auto-updates `updated_at` on row modification

**RLS Policies:**
- `profiles_owner_select` - Users can SELECT their own profile
- `profiles_owner_upsert` - Users can INSERT their own profile
- `profiles_owner_update` - Users can UPDATE their own profile

**Example Data:**
```json
{
  "user_id": "user_2abcdef123456",
  "name": "John Doe",
  "preferences": {
    "language": "en",
    "timezone": "America/New_York",
    "email_notifications": true
  },
  "tone_of_voice": "professional",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### 2. **projects**
Content repurposing projects created by users.

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `id` | `UUID` | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique project identifier |
| `user_id` | `TEXT` | NOT NULL | Clerk user ID (owner) |
| `title` | `TEXT` | NOT NULL | Project title |
| `description` | `TEXT` | NULL | Project description |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Composite index on `(user_id, created_at DESC)` for user's projects listing

**Triggers:**
- `trg_projects_updated_at` - Auto-updates `updated_at` on row modification

**RLS Policies:**
- `projects_owner_all` - Users have full access to their own projects only

**Relationships:**
- One-to-many with `files` (project has many files)
- One-to-many with `outputs` (project has many outputs)

**Example Data:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user_2abcdef123456",
  "title": "Q4 2024 Podcast Episode",
  "description": "Discussion about AI trends and content creation",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

### 3. **files**
Uploaded media files associated with projects.

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `id` | `UUID` | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique file identifier |
| `user_id` | `TEXT` | NOT NULL | Clerk user ID (owner) |
| `project_id` | `UUID` | NOT NULL, REFERENCES projects(id) ON DELETE CASCADE | Associated project |
| `path` | `TEXT` | NOT NULL, UNIQUE | Storage path: `{user_id}/{project_id}/{uuid.ext}` |
| `mime_type` | `TEXT` | NULL | MIME type (e.g., "audio/mp3") |
| `size_bytes` | `BIGINT` | NULL | File size in bytes |
| `public_url` | `TEXT` | NULL | Public URL for file access |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Upload timestamp |

**Indexes:**
- Primary key on `id`
- Unique constraint on `path`
- Composite index on `(project_id, user_id)` for project file listings

**Foreign Keys:**
- `project_id` → `projects(id)` with CASCADE DELETE

**RLS Policies:**
- `files_owner_all` - Users have full access to their own files only

**Storage Integration:**
- Files are stored in Supabase Storage bucket `uploads`
- Path format: `{user_id}/{project_id}/{file_uuid}.{extension}`

**Example Data:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "user_2abcdef123456",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "path": "user_2abcdef123456/550e8400-e29b-41d4-a716-446655440000/660e8400.mp3",
  "mime_type": "audio/mpeg",
  "size_bytes": 10485760,
  "public_url": "https://xxx.supabase.co/storage/v1/object/public/uploads/...",
  "created_at": "2024-01-01T10:00:00Z"
}
```

---

### 4. **outputs**
Generated content outputs (blog posts, social media posts, etc.).

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `id` | `UUID` | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique output identifier |
| `user_id` | `TEXT` | NOT NULL | Clerk user ID (owner) |
| `project_id` | `UUID` | NOT NULL, REFERENCES projects(id) ON DELETE CASCADE | Associated project |
| `kind` | `output_kind` | NOT NULL | Type: 'blog', 'social', or 'email' |
| `status` | `output_status` | NOT NULL, DEFAULT 'queued' | Processing status |
| `request` | `JSONB` | NULL | Original generation request payload |
| `body` | `TEXT` | NULL | Generated content text |
| `metadata` | `JSONB` | NOT NULL, DEFAULT '{}' | Additional metadata |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Composite index on `(project_id, user_id)` for project outputs
- Index on `status` for queue processing
- Index on `created_at DESC` for recent outputs

**Foreign Keys:**
- `project_id` → `projects(id)` with CASCADE DELETE

**Triggers:**
- `trg_outputs_updated_at` - Auto-updates `updated_at` on row modification

**RLS Policies:**
- `outputs_owner_all` - Users have full access to their own outputs only

**Status Workflow:**
```
queued → processing → completed
                  ↘ → failed
```

**Example Data:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "user_id": "user_2abcdef123456",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "kind": "blog",
  "status": "completed",
  "request": {
    "topic": "AI and Content Creation",
    "tone_of_voice": "professional",
    "target_length": 1500
  },
  "body": "# AI and Content Creation\n\nIn today's digital landscape...",
  "metadata": {
    "word_count": 1523,
    "reading_time": 6,
    "keywords": ["AI", "content", "automation"],
    "generated_at": "2024-01-01T10:30:00Z"
  },
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:30:00Z"
}
```

---

### 5. **templates**
Custom content generation templates created by users.

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `id` | `UUID` | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique template identifier |
| `user_id` | `TEXT` | NOT NULL | Clerk user ID (owner) |
| `name` | `TEXT` | NOT NULL | Template name |
| `type` | `template_type` | NOT NULL | Template type for specific platform |
| `prompt` | `TEXT` | NOT NULL | AI prompt template |
| `is_custom` | `BOOLEAN` | NOT NULL, DEFAULT TRUE | User-created vs system template |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes:**
- Primary key on `id`
- Index on `user_id` for user's templates
- Unique constraint on `(user_id, name)` - no duplicate names per user

**RLS Policies:**
- `templates_owner_all` - Users have full access to their own templates only

**Template Types:**
- `blog` - Blog post templates
- `linkedin` - LinkedIn post templates
- `twitter` - Twitter/X thread templates
- `instagram` - Instagram caption templates
- `email` - Email newsletter templates

**Example Data:**
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "user_id": "user_2abcdef123456",
  "name": "Tech Blog Deep Dive",
  "type": "blog",
  "prompt": "Create a comprehensive blog post about {topic}. Include:\n1. Introduction with hook\n2. 3-5 main points with examples\n3. Actionable takeaways\n4. Conclusion with CTA\n\nTone: {tone_of_voice}\nTarget audience: Tech professionals",
  "is_custom": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## 🗂️ Storage Configuration

### Storage Bucket: `uploads`

**Configuration:**
- **Name:** `uploads`
- **Public:** `true` (allows public URL access)
- **Path Structure:** `{user_id}/{project_id}/{file_uuid}.{extension}`

**Storage Policies:**
- `Public read uploads` - Allows public SELECT on all objects in the bucket

**Example Paths:**
```
uploads/
├── user_2abcdef123456/
│   ├── 550e8400-e29b-41d4-a716-446655440000/
│   │   ├── 660e8400-e29b-41d4-a716-446655440001.mp3
│   │   ├── 770e8400-e29b-41d4-a716-446655440002.mp4
│   │   └── 880e8400-e29b-41d4-a716-446655440003.pdf
│   └── 990e8400-e29b-41d4-a716-446655440004/
│       └── aa0e8400-e29b-41d4-a716-446655440005.wav
```

---

## 🔧 Utility Functions

### set_updated_at()
Trigger function that automatically updates the `updated_at` timestamp.

```sql
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;
```

**Used by triggers:**
- `trg_profiles_updated_at`
- `trg_projects_updated_at`
- `trg_outputs_updated_at`

---

## 🔒 Security Features

### Row Level Security (RLS)

All tables have RLS enabled with the following pattern:
- **Users can only access their own data**
- **Service role bypasses RLS** (for backend operations)
- **Authenticated users** must match the `user_id` field

### Policy Naming Convention
```
{table_name}_owner_{action}
```

Examples:
- `profiles_owner_select`
- `projects_owner_all`
- `files_owner_all`

### Authentication Flow
1. User authenticates with Clerk
2. Clerk JWT contains user ID
3. Backend validates JWT
4. Database operations use Clerk user ID
5. RLS policies enforce access control

---

## 📈 Query Optimization

### Indexes Strategy

**Primary Indexes:**
- All tables use UUID primary keys with B-tree indexes

**Composite Indexes:**
- `projects(user_id, created_at DESC)` - User's projects sorted by date
- `files(project_id, user_id)` - Files within a project
- `outputs(project_id, user_id)` - Outputs within a project

**Single Column Indexes:**
- `outputs(status)` - Queue processing queries
- `outputs(created_at DESC)` - Recent outputs
- `templates(user_id)` - User's templates

### Common Query Patterns

**Get user's recent projects:**
```sql
SELECT * FROM projects 
WHERE user_id = $1 
ORDER BY created_at DESC 
LIMIT 10;
```

**Get project with files and outputs:**
```sql
SELECT 
  p.*,
  COALESCE(json_agg(DISTINCT f.*) FILTER (WHERE f.id IS NOT NULL), '[]') as files,
  COALESCE(json_agg(DISTINCT o.*) FILTER (WHERE o.id IS NOT NULL), '[]') as outputs
FROM projects p
LEFT JOIN files f ON f.project_id = p.id
LEFT JOIN outputs o ON o.project_id = p.id
WHERE p.id = $1 AND p.user_id = $2
GROUP BY p.id;
```

**Process output queue:**
```sql
SELECT * FROM outputs 
WHERE status = 'queued' 
ORDER BY created_at ASC 
LIMIT 1 
FOR UPDATE SKIP LOCKED;
```

---

## 🔄 Migration Strategy

### Safe Migration Principles
1. **Idempotent operations** - Can run multiple times safely
2. **IF NOT EXISTS** clauses prevent duplicate objects
3. **Wrapped in transactions** for atomicity
4. **No data loss** - Only additive changes

### Running Migrations
```sql
-- Run the entire schema file
psql -U postgres -d your_database -f schema.sql

-- Or in Supabase SQL Editor
-- Copy and paste the entire schema
```

### Version Control
```sql
-- Track schema version (optional)
CREATE TABLE IF NOT EXISTS schema_versions (
  version TEXT PRIMARY KEY,
  applied_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO schema_versions (version) 
VALUES ('1.0.0') 
ON CONFLICT DO NOTHING;
```

---

## 📊 Database Metrics

### Table Size Estimates

| Table | Avg Row Size | Est. Rows/User/Month | Est. Storage/User/Month |
|-------|-------------|---------------------|------------------------|
| profiles | 1 KB | 1 | 1 KB |
| projects | 0.5 KB | 10 | 5 KB |
| files | 0.5 KB | 30 | 15 KB |
| outputs | 10 KB | 100 | 1 MB |
| templates | 2 KB | 5 | 10 KB |

**Total estimated storage per active user:** ~1.03 MB/month (excluding file storage)

### Performance Considerations

**Expected Query Times:**
- Simple SELECT by ID: < 1ms
- User's project list: < 5ms
- Project with files/outputs: < 10ms
- Complex aggregations: < 50ms

**Scaling Limits:**
- PostgreSQL can handle millions of rows per table
- UUID keys prevent ID exhaustion
- Indexes maintain performance at scale
- Consider partitioning outputs table at 10M+ rows

---

## 🛠️ Maintenance Tasks

### Regular Maintenance

**Daily:**
```sql
-- Check for stuck processing jobs
SELECT * FROM outputs 
WHERE status = 'processing' 
AND updated_at < NOW() - INTERVAL '1 hour';
```

**Weekly:**
```sql
-- Vacuum and analyze for query optimization
VACUUM ANALYZE projects;
VACUUM ANALYZE files;
VACUUM ANALYZE outputs;
```

**Monthly:**
```sql
-- Clean up orphaned files
DELETE FROM files f
WHERE NOT EXISTS (
  SELECT 1 FROM storage.objects o 
  WHERE o.name = f.path
);

-- Archive old completed outputs
INSERT INTO outputs_archive 
SELECT * FROM outputs 
WHERE status = 'completed' 
AND created_at < NOW() - INTERVAL '90 days';
```

### Monitoring Queries

**Database Size:**
```sql
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Active Users:**
```sql
SELECT 
  DATE(created_at) as date,
  COUNT(DISTINCT user_id) as active_users,
  COUNT(*) as total_projects
FROM projects
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

---

## 🔗 Related Documentation

- [API Reference](/docs/API_REFERENCE.md)
- [Phase 2-3 Implementation Plan](/docs/PHASE_2_3_IMPLEMENTATION_PLAN.md)
- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## 📝 Notes

### Future Enhancements
1. **Transcriptions table** - Store transcription data separately
2. **Clips table** - Video clip suggestions and exports
3. **Billing tables** - Subscription and usage tracking
4. **Analytics tables** - User behavior and content performance
5. **Team collaboration** - Shared projects and permissions

### Best Practices
- Always use prepared statements to prevent SQL injection
- Use transactions for multi-table operations
- Monitor slow query logs
- Regular backups via Supabase dashboard
- Test migrations on staging first

---

*Last Updated: 2024-01-01*  
*Schema Version: 1.0*
