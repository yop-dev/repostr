# Backend Best Practices

Scope: FastAPI (Python) or Node (TypeScript) backend, Postgres (Supabase), async jobs (Celery/queue), media processing (FFmpeg), transcription (Whisper), deployed on Railway/Vercel/Supabase. Prefer FastAPI for the MVP per PRD; Node guidance provided where applicable.

---

## 1) Core Principles
- Clear separation of concerns: API layer, service layer, data layer, workers.
- Strong typing (Pydantic v2 in Python; TypeScript in Node) at module boundaries.
- Idempotent background jobs; resumability and observability by design.
- Security, privacy, and cost control as first-class requirements.

---

## 2) Service Architecture
- API: REST (versioned) with OpenAPI schema.
- Workers: handle long-running tasks (transcription, clipping, generation).
- Storage: Postgres for metadata; object storage (Supabase Storage) for media and artifacts.
- Communication: API creates jobs; workers update status; frontend subscribes to progress via polling, SSE, or Supabase Realtime.

---

## 3) Project Structure
A) FastAPI (recommended)
```
/backend
  app/
    api/
      deps.py
      errors.py
      v1/
        routes/
          uploads.py
          jobs.py
          content.py
        __init__.py
    core/
      config.py
      security.py
      logging.py
    db/
      base.py
      session.py
      migrations/  (Alembic)
      repositories/
        uploads.py
        jobs.py
        content.py
    models/
      user.py
      upload.py
      job.py
      transcript.py
      clip.py
      content.py
    schemas/
      upload.py
      job.py
      transcript.py
      clip.py
      content.py
    services/
      uploads.py
      jobs.py
      transcription.py
      repurpose.py
      clipping.py
      subtitles.py
    workers/
      celery_app.py
      tasks/
        transcribe.py
        repurpose_text.py
        detect_clips.py
        export_clip.py
        subtitles.py
    utils/
      ffmpeg.py
      storage.py
      timecode.py
    main.py
  tests/
    api/
    services/
    workers/
  pyproject.toml
```

B) Node (Express/Nest)
```
/backend
  src/
    api/
      v1/
        uploads.controller.ts
        jobs.controller.ts
        content.controller.ts
        middlewares/
        validators/
    config/
      env.ts
      logger.ts
    db/
      prisma/
        schema.prisma
      migrations/
      repositories/
    domain/
      models/
      services/
    workers/
      queues/
      processors/
    utils/
      ffmpeg.ts
      storage.ts
    app.ts
  tests/
    api/
    services/
    workers/
  package.json
```

---

## 4) API Design
- Version endpoints under /api/v1.
- Resource-oriented URLs: /uploads, /uploads/{id}, /jobs, /content.
- Use standard methods and status codes; 202 Accepted for async job creation.
- Consistent error envelope: { "error": { "code": string, "message": string, "details"?: any } }
- Pagination: limit + cursor/offset; return nextCursor when applicable.
- OpenAPI generated from code; publish schema for frontend typegen.

Auth
- Verify Clerk tokens on protected routes. Use RBAC/ABAC for multi-tenant (workspace) access.
- Prefer short-lived tokens; never trust client role claims without server validation.

Rate limiting
- Apply IP + user-based limits (e.g., 100 rpm) via Redis.

CORS
- Restrict origins to known domains; allow necessary methods/headers only.

---

## 5) Data Model (suggested)
- users (external via Clerk; store minimal shadow record: id, email, created_at)
- workspaces (id, name, owner_user_id)
- workspace_members (workspace_id, user_id, role)
- uploads (id, workspace_id, user_id, status, media_uri, duration_ms, kind, created_at)
- transcripts (id, upload_id, text, words_json, language, created_at)
- contents (id, upload_id, kind: 'blog'|'linkedin'|'twitter'|'instagram', body, metadata_json)
- clips (id, upload_id, start_ms, end_ms, caption_srt_uri, video_uri, metadata_json)
- jobs (id, upload_id, type, status, attempt, error_json, created_at, updated_at)
- usage (id, workspace_id, month, uploads_count, minutes_processed, plan)

Conventions
- snake_case table and column names; plural table names.
- Foreign keys with ON DELETE CASCADE where appropriate.
- Timestamps: created_at, updated_at (trigger), soft delete columns if needed (deleted_at).
- Index frequent filters (workspace_id, created_at), composite indexes for lookups.

---

## 6) Database & Migrations
- FastAPI: SQLAlchemy 2.x + Alembic; async engine (asyncpg). Pydantic for schemas.
- Node: Prisma or Drizzle ORM; enable strict type checking.
- Migrations are mandatory and reviewed in PRs.
- Use Testcontainers for integration tests against Postgres.

---

## 7) Background Jobs & Media Pipeline
- Use Celery (Python) or BullMQ/Cloud queues (Node) for job orchestration.
- Broker: Redis; Result backend: Redis/Postgres.
- Job types: TRANSCRIBE, REPURPOSE_TEXT, DETECT_CLIPS, GENERATE_SUBTITLES, EXPORT_CLIP.
- Idempotency: derive deterministic job keys (e.g., uploadId + jobType + params hash). Workers should check for existing completed artifacts before reprocessing.
- Progress: persist state transitions (QUEUED -> RUNNING -> COMPLETED/FAILED) with timestamps; include progress_pct when possible.
- Concurrency limits: bound FFmpeg jobs to avoid CPU saturation; prefer container isolation for FFmpeg.
- Resource safety: do not execute arbitrary user binaries; sanitize file names; scan and reject unsupported media.

FFmpeg
- Keep invocations explicit and auditable; avoid shell injection; pass args as arrays.
- Standardize outputs: H.264/AAC MP4 for clips; SRT for subtitles; store in Supabase Storage with content-type and metadata.

Whisper
- Support both local and API modes. For local, ensure model caching and GPU availability checks.
- Split long audio into chunks; stitch transcripts; persist word-level timestamps for clip suggestions.

---

## 8) Storage & Object Naming
- Buckets: uploads/, transcripts/, clips/, subtitles/.
- Naming: {workspaceId}/{uploadId}/{artifact}/{uuid}.{ext}
- Access: use signed URLs; never proxy large media through the API when avoidable.
- Lifecycle: define retention for intermediates; keep final outputs longer.

---

## 9) Security
- Inputs: validate all request bodies and query params (Pydantic/Zod).
- AuthZ: verify workspace membership on every resource access.
- Secrets: loaded from env; never log or echo. Use placeholders in docs: {{DATABASE_URL}}, {{SUPABASE_URL}}.
- Limit uploaded file size and duration; transcode to safe formats.
- Set secure headers; enable HTTPS everywhere; strong CORS.
- Protect against path traversal; never trust user-supplied paths.

---

## 10) Observability
- Structured logging (JSON) with correlation/request IDs. Mask PII.
- Metrics: request rate/latency, job durations, FFmpeg failures, token costs.
- Tracing: OpenTelemetry spans for API handlers and worker tasks.

---

## 11) Error Handling
- Central exception handlers mapping domain errors to HTTP status codes.
- Return stable error codes for the frontend to branch on.
- Include a correlationId in responses; log it in all related spans.

---

## 12) Testing
- Unit tests for services and utilities.
- Integration tests with a real Postgres (Testcontainers) and Redis when queueing.
- E2E happy-path covering upload -> transcript -> repurpose -> clips -> download.
- Contract tests: generate OpenAPI and verify client compatibility.

---

## 13) CI/CD
- Pipelines: lint, type-check, unit/integration tests, build container images.
- Security scans: dependency audit (pip-audit/npm audit), Trivy image scan.
- Environments: dev, staging, prod; config via env vars; no branching logic in code.
- Migrations: auto-apply on deploy, with backup and rollback plan.

---

## 14) Configuration & Env
- Single source of truth config module (config.py/env.ts) with schema validation.
- Required env vars (placeholders):
  - DATABASE_URL={{DATABASE_URL}}
  - SUPABASE_URL={{SUPABASE_URL}}
  - SUPABASE_SERVICE_ROLE_KEY={{SUPABASE_SERVICE_ROLE_KEY}}
  - CLERK_JWT_ISSUER={{CLERK_JWT_ISSUER}}
  - OPENAI_API_KEY={{OPENAI_API_KEY}} (if used)
  - REDIS_URL={{REDIS_URL}}
- Never print secrets; propagate as environment variables only.

---

## 15) Coding Standards
- FastAPI: Pydantic v2 models, SQLAlchemy 2.x, Ruff + Black + MyPy.
- Node: ESLint + Prettier, tsconfig with strict true, path aliases.
- Keep service layer framework-agnostic; API handlers thin and declarative.

---

## 16) Release & Backwards Compatibility
- Version API; never break v1 without deprecation window.
- Database migrations must be backward-compatible during rolling deploys.
- Feature flags for risky features.

---

## 17) Cost Controls
- Cache model results where appropriate; deduplicate repeat runs by content hash.
- Enforce per-plan quotas in API and workers; persist usage counters.
- Monitor CPU/GPU time for transcription and clipping jobs.

---

## 18) PR Checklist
- [ ] Lint, type-check, unit/integration tests pass
- [ ] OpenAPI updated and committed (if applicable)
- [ ] Migrations included and tested
- [ ] Secrets handled via env; no plaintext in code/commits
- [ ] Observability added for new endpoints/jobs
- [ ] Docs updated (README/CHANGELOG)

