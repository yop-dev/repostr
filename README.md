# 🚀 Repostr - AI-Powered Content Repurposing Platform

Transform your long-form content into platform-optimized pieces with AI. Deploy intelligent workflows that understand, adapt, and deliver—in minutes, not hours.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Current Features
- 🔐 **Authentication**: Secure user authentication with Clerk
- 👤 **User Profiles**: Customizable user preferences and settings
- 📁 **Project Management**: Create and manage content projects
- 📤 **File Upload**: Support for audio, video, and text files
- 🎯 **Content Generation**: AI-powered content creation for multiple platforms
- 📊 **Dashboard**: User-friendly interface for managing content

### Coming Soon (Phase 2-3)
- 🎙️ **Transcription**: Automatic audio/video transcription with Whisper
- ✂️ **Video Clipping**: Intelligent clip detection and extraction
- 📝 **Subtitles**: Automatic subtitle generation (SRT/VTT)
- 📧 **Email Templates**: Custom email newsletter generation
- 🔄 **Batch Processing**: Process multiple files simultaneously
- 📈 **Analytics**: Track content performance across platforms

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 15.5 with TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Authentication**: Clerk
- **Animations**: Framer Motion

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (Supabase)
- **Storage**: Supabase Storage
- **Authentication**: Clerk JWT verification
- **Task Queue**: Celery (planned)
- **AI**: OpenAI/Anthropic APIs (planned)

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Node.js (v18 or higher)
- Python (v3.9 or higher)
- Git

You'll also need accounts for:
- [Clerk](https://clerk.com) - Authentication
- [Supabase](https://supabase.com) - Database and storage

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/repostr.git
cd repostr
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

### 3. Backend Setup

```bash
cd ../backend
pip install -r requirements.txt
```

### 4. Database Setup

Run the schema SQL in your Supabase SQL editor:

```bash
# The schema file is located at:
# backend/supabase/schema.sql
```

## ⚙️ Configuration

### Frontend Configuration

1. Copy the example environment file:
```bash
cd frontend
cp .env.example .env.local
```

2. Update `.env.local` with your credentials:
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend Configuration

1. Copy the example environment file:
```bash
cd backend
cp .env.example .env
```

2. Update `.env` with your credentials:
```env
CLERK_JWKS_URL=https://your-domain.clerk.accounts.dev/.well-known/jwks.json
CLERK_ISSUER=https://your-domain.clerk.accounts.dev
CLERK_SECRET_KEY=your_clerk_secret_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## 🏃 Running the Application

### Start the Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The API will be available at http://localhost:8000

### Start the Frontend

```bash
cd frontend
npm run dev
```

The application will be available at http://localhost:3000

## 📁 Project Structure

```
repostr/
├── frontend/               # Next.js frontend application
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utility functions
│   │   └── hooks/         # Custom React hooks
│   └── public/            # Static assets
│
├── backend/               # FastAPI backend application
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Core configuration
│   │   ├── schemas/       # Pydantic models
│   │   └── services/      # Business logic
│   └── requirements.txt   # Python dependencies
│
└── docs/                  # Documentation
    ├── API_REFERENCE.md
    ├── DATABASE_SCHEMA.md
    └── PHASE_2_3_IMPLEMENTATION_PLAN.md
```

## 📚 API Documentation

Full API documentation is available in [docs/API_REFERENCE.md](docs/API_REFERENCE.md)

### Key Endpoints

- `POST /projects/` - Create a new project
- `POST /projects/{project_id}/upload` - Upload a file
- `POST /projects/{project_id}/generate/blog` - Generate blog content
- `GET /projects/{project_id}/outputs` - Get generated content

## 🗄️ Database Schema

Complete database schema documentation is available in [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)

### Main Tables

- `profiles` - User profiles and preferences
- `projects` - Content projects
- `files` - Uploaded files
- `outputs` - Generated content
- `templates` - Custom templates

## 🔒 Security

- All environment variables containing sensitive data are excluded from version control
- Row Level Security (RLS) is enabled on all database tables
- JWT authentication is required for all API endpoints
- CORS is configured to allow only specified origins

## 🚦 Development Status

- ✅ Phase 1: Foundation (Complete)
  - Authentication
  - Basic project management
  - File upload infrastructure
  
- 🚧 Phase 2: Text Repurposing (In Progress)
  - Transcription service
  - AI content generation
  - Export functionality
  
- 📅 Phase 3: Video Features (Planned)
  - Video processing
  - Subtitle generation
  - Clip extraction

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Clerk](https://clerk.com) for authentication
- [Supabase](https://supabase.com) for database and storage
- [shadcn/ui](https://ui.shadcn.com) for UI components
- [FastAPI](https://fastapi.tiangolo.com) for the backend framework

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

Built with ❤️ by the Repostr team
