# Backend (FastAPI) for Content Repurposer

This service exposes the MVP API endpoints and integrates with Clerk (JWT verification) and Supabase (Postgres + Storage). Many handlers include safe placeholders so you can run locally and iterate.

## Endpoints (MVP)
- Auth
  - GET /auth/me
  - POST /auth/webhook
- Users
  - GET /users/me
  - PATCH /users/me
- Projects
  - POST /projects
  - GET /projects
  - GET /projects/{project_id}
  - PATCH /projects/{project_id}
  - DELETE /projects/{project_id}
- Files
  - POST /projects/{project_id}/upload
  - GET /projects/{project_id}/files
  - DELETE /projects/{project_id}/files/{file_id}
- Generate (queue stubs)
  - POST /projects/{project_id}/generate/blog
  - POST /projects/{project_id}/generate/social
  - POST /projects/{project_id}/generate/email
- Outputs
  - GET /projects/{project_id}/outputs
  - GET /projects/{project_id}/outputs/{output_id}
  - PATCH /projects/{project_id}/outputs/{output_id}
  - DELETE /projects/{project_id}/outputs/{output_id}
- Templates
  - GET /templates
  - POST /templates/custom
  - DELETE /templates/{template_id}
- Billing (placeholders)
  - GET /billing/plans
  - POST /billing/subscribe
  - GET /billing/status
  - POST /billing/webhook
- Admin (optional)
  - GET /admin/users
  - GET /admin/projects

## Setup
1) Create your env file
Copy .env.example to .env and fill in values. At minimum, set CLERK_JWKS_URL so JWTs can be verified.

2) Install dependencies
pip install -r requirements.txt

3) Run the server
uvicorn app.main:app --reload --port 8000

Server runs at http://localhost:8000. Open http://localhost:8000/docs for Swagger UI.

## Notes
- Clerk JWT verification uses JWKS via PyJWT. Set CLERK_ISSUER and CLERK_AUDIENCE if you want issuer/audience checks.
- Supabase is optional at boot; routes check for configuration and fail gracefully if not set. For full functionality (uploads, persistence), set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.
- Webhooks: Clerk webhooks verified via Svix when CLERK_WEBHOOK_SECRET is provided.
- CORS is open by default unless you set CORS_ORIGINS.

