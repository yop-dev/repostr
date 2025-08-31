from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from app.core.security import get_current_user, UserPrincipal
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
def auth_me(user: UserPrincipal = Depends(get_current_user)):
    """Return user info from the verified Clerk JWT."""
    return {
        "user_id": user.user_id,
        "email": user.email,
        "name": user.name,
        "claims": user.claims,
    }


@router.post("/webhook")
async def auth_webhook(request: Request):
    """Handle Clerk webhooks (user created/updated/deleted).
    Verifies Svix signature when CLERK_WEBHOOK_SECRET is configured.
    """
    payload = await request.body()
    headers = request.headers

    secret = settings.CLERK_WEBHOOK_SECRET
    if not secret:
        # Accept but note that verification is not configured yet
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={"received": True, "verified": False})

    try:
        from svix import Webhook, WebhookVerificationError

        wh = Webhook(secret)
        event = wh.verify(payload, headers)  # type: ignore[arg-type]
        # TODO: persist event and sync user data in DB as needed
        return {"received": True, "verified": True, "type": event.get("type")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook verification failed: {str(e)}")

