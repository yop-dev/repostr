# 📄 Product Requirements Document (PRD)

Product Name: Content Repurposer (working title)

Version: 1.0 (MVP)

Date: [Insert Date]

Owner: [Your Name]

## 1. 🎯 Purpose

The purpose of Content Repurposer is to help creators, agencies, and businesses maximize the value of their long-form content (videos, podcasts, webinars) by automatically repurposing it into multiple platform-ready formats (blogs, social posts, short clips). This saves time, increases reach, and streamlines multi-platform content strategies.

## 2. 🌍 Target Audience

Primary Users:

- Content creators (YouTubers, podcasters, TikTokers)
- Social media managers
- Agencies handling multiple clients

Secondary Users:

- Coaches, educators, solopreneurs, SaaS founders
- Small businesses wanting consistent social media presence

## 3. 🧩 Key Features (MVP Scope)

### A. User & Account Management

- User authentication (Sign up/login via email or Google)
- Dashboard with recent uploads & subscription status
- Subscription management (Stripe integration)

### B. Content Upload & Processing

- File upload: video/audio (MP4, MP3, WAV, etc.)
- File storage in cloud (Supabase/AWS S3)
- Background processing (async job queue)

### C. AI Processing Engine

#### Transcription

- Convert audio to text using Whisper (or similar STT).

#### Content Repurposing (Text)

Generate:

- Blog post
- LinkedIn post
- Twitter/X thread
- Instagram caption
- Facebook caption
- Tiktok caption

#### Video Repurposing (Clips)

- Identify suggested short clips (timestamps)
- Generate subtitles (.srt)
- Export short-form videos (FFmpeg)

### D. Output & Export

- Tabs for each content type (Blog, LinkedIn, Twitter, IG, Clips)
- One-click copy text
- Download options (text, .srt, video clips)

### E. Monetization

- Free tier: 3 uploads/month (basic text only)
- Pro tier ($15–29/month): More uploads, video clipping, subtitles
- Agency tier ($49–99/month): Unlimited uploads, multi-user access, white-label exports

## 4. 📊 Success Metrics

- Activation: % of users who upload at least 1 file in the first week
- Retention: % of users still active after 1 month
- Conversion: Free → Paid upgrade rate
- Engagement: Average number of repurposed outputs used/downloaded per upload

## 5. 🛠 Tech Stack (MVP)

- Frontend: React + Tailwind + Clerk (Auth) + Vercel
- Backend: FastAPI + Celery (for async jobs) + Railway
- DB & Storage: Supabase (Postgres + file storage)
- AI: Whisper (transcription), GPT/LLaMA (text generation), FFmpeg (video clipping)
- Payments: Stripe

## 6. 🗺 Roadmap

### Phase 1 – Foundation (Weeks 1–2)

- Auth & Dashboard
- File upload → transcription (Whisper API/local)

### Phase 2 – Text Repurposing (Weeks 3–4)

- Blog, LinkedIn, Twitter, IG caption generation
- Export (copy/download text)

### Phase 3 – Video Features (Weeks 5–6)

- Subtitle generation
- Auto-clip detection + export with FFmpeg

### Phase 4 – SaaS Layer (Weeks 7–8)

- Stripe integration
- Plan limits (free vs pro vs agency)
- Settings page

### Phase 5 – Beta Launch (Week 9)

- Deploy (Vercel + Railway/Supabase)
- Test with early adopters

## 7. 🚧 Constraints & Risks

- AI Costs: If relying on APIs, costs scale with usage (must optimize or self-host).
- Performance: Long files may take minutes to process (need async jobs + progress tracking).
- Competition: Other repurposing tools exist (e.g., OpusClip) → need differentiation (simplicity, pricing, niche focus).

## 8. 📌 Future Enhancements (Post-MVP)

- Multi-language support
- Direct publishing to social platforms
- Branded video templates (logos, captions style)
- Team collaboration features
- Engagement analytics (track repurposed content performance)

