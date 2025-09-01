# Deploying Repostr to Vercel

This guide covers how to deploy both the Next.js frontend and FastAPI backend to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install globally
   ```bash
   npm i -g vercel
   ```
3. **Environment Variables**: Prepare your environment variables

## Environment Variables Setup

### Backend Environment Variables
Your FastAPI backend likely uses these environment variables. Add them in Vercel Dashboard:

- `ENV` - Set to "production"
- `CORS_ORIGINS` - Your frontend URL (e.g., "https://your-app.vercel.app")
- Database credentials (Supabase)
- API keys (Groq, Clerk, etc.)
- Any other secrets from your backend

### Frontend Environment Variables
Your Next.js frontend needs:
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`
- `NEXT_PUBLIC_API_URL` - Will be your Vercel domain + "/api"
- Any other public/private environment variables

## Deployment Methods

### Method 1: Deploy via Vercel Dashboard (Recommended)

1. **Connect Repository**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "Import Project"
   - Connect your GitHub repository
   - Select your `repostr` repository

2. **Configure Build Settings**:
   - **Root Directory**: Leave empty (uses root)
   - **Framework Preset**: Next.js
   - **Build Command**: `cd frontend && npm run build`
   - **Output Directory**: `frontend/.next`
   - **Install Command**: `cd frontend && npm install`

3. **Add Environment Variables**:
   - In the deployment configuration, add all your environment variables
   - Make sure to add both frontend and backend environment variables

4. **Deploy**: Click "Deploy"

### Method 2: Deploy via CLI

1. **Login to Vercel**:
   ```bash
   vercel login
   ```

2. **Deploy from Root Directory**:
   ```bash
   cd C:\repostr
   vercel
   ```

3. **Follow the prompts**:
   - Link to existing project or create new
   - Set up environment variables when prompted

## Project Structure After Setup

```
repostr/
├── frontend/          # Next.js app
│   ├── src/
│   ├── package.json
│   └── next.config.ts
├── backend/           # FastAPI app (for development)
│   ├── app/
│   └── requirements.txt
├── api/               # Vercel serverless functions
│   ├── index.py
│   └── requirements.txt
└── vercel.json        # Vercel configuration
```

## How It Works

1. **Frontend**: Next.js app is built and served from the `frontend/` directory
2. **Backend**: FastAPI app is wrapped with Mangum and deployed as serverless functions in the `api/` directory
3. **Routing**: Vercel routes `/api/*` to your Python functions, everything else to Next.js

## Testing the Deployment

1. **Frontend**: Your main domain serves the Next.js app
2. **API**: `https://your-app.vercel.app/api/` serves your FastAPI endpoints
3. **Health Check**: Visit `https://your-app.vercel.app/api/` to see the FastAPI root response

## Development vs Production

- **Development**: Next.js rewrites API calls to `localhost:8000` (your local FastAPI server)
- **Production**: API calls go to `/api/*` which Vercel routes to your serverless functions

## Environment Variables You'll Need

### Required for Backend:
```
ENV=production
CORS_ORIGINS=https://your-app.vercel.app
# Add your database, API keys, and other secrets
```

### Required for Frontend:
```
NEXT_PUBLIC_API_URL=https://your-app.vercel.app/api
# Add your Clerk keys and other public variables
```

## Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure all Python dependencies are in `api/requirements.txt`
2. **CORS Issues**: Update `CORS_ORIGINS` in your environment variables
3. **Build Failures**: Check that your Next.js app builds successfully locally
4. **API Routes Not Working**: Verify the `vercel.json` routing configuration

### Debugging:
- Check Vercel function logs in the dashboard
- Use `vercel logs` CLI command
- Test API endpoints directly in browser

## Alternative: Separate Deployments

If you prefer to deploy frontend and backend separately:

### Frontend Only:
```bash
cd frontend
vercel
```

### Backend as Separate Service:
Consider deploying the FastAPI backend to:
- Railway
- Heroku
- Digital Ocean App Platform
- AWS Lambda with API Gateway

Then update your frontend's `NEXT_PUBLIC_API_URL` to point to the backend URL.
