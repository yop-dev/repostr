"""
Quick script to get a test JWT from Clerk for API testing.
You'll need to sign in via Clerk's hosted UI first to have a session.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("To get a test JWT token:")
print("1. Go to your Clerk Dashboard: https://dashboard.clerk.com")
print("2. Navigate to your app → Users")
print("3. Create or select a test user")
print("4. Click the user → View details → Active sessions")
print("5. Copy the session token (JWT)")
print()
print("Your Clerk instance: https://destined-monkey-53.clerk.accounts.dev")
print()
print("Once you have the JWT, set it in PowerShell:")
print('$env:CLERK_JWT = "your-jwt-here"')
print()
print("Then test the API:")
print('curl.exe -H "Authorization: Bearer $env:CLERK_JWT" http://localhost:8000/auth/me')
