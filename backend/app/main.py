from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.v1.routes import auth as auth_routes
from .api.v1.routes import users as users_routes
from .api.v1.routes import projects as projects_routes
from .api.v1.routes import files as files_routes
from .api.v1.routes import generate as generate_routes
from .api.v1.routes import outputs as outputs_routes
from .api.v1.routes import templates as templates_routes
from .api.v1.routes import billing as billing_routes
from .api.v1.routes import admin as admin_routes
from .api.v1.routes import anonymous as anonymous_routes
# from .api.v1.routes import transcription_projects as transcription_routes

app = FastAPI(title="Repostr API", version="1.0")

# CORS
origins = []
if settings.CORS_ORIGINS:
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (no API version prefix to match your request)
app.include_router(auth_routes.router)
app.include_router(users_routes.router)
app.include_router(projects_routes.router)
app.include_router(files_routes.router)
app.include_router(generate_routes.router)
app.include_router(outputs_routes.router)
app.include_router(templates_routes.router)
app.include_router(billing_routes.router)
app.include_router(admin_routes.router)
app.include_router(anonymous_routes.router)
# app.include_router(transcription_routes.router)


@app.get("/")
def root():
    return {"status": "ok", "env": settings.ENV}

