from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.core.security import get_current_user, UserPrincipal

router = APIRouter(prefix="/billing", tags=["billing"])  # placeholders


@router.get("/plans")
async def get_plans():
    """Return available plans (static for now)."""
    return [
        {"id": "free", "price": 0, "features": ["3 uploads/month", "basic text only"]},
        {"id": "pro", "price": 29, "features": ["more uploads", "video clipping", "subtitles"]},
        {"id": "agency", "price": 99, "features": ["unlimited", "multi-user", "white-label"]},
    ]


@router.post("/subscribe")
async def subscribe(user: UserPrincipal = Depends(get_current_user)):
    return {"message": "Subscription flow not yet implemented", "status": "todo"}


@router.get("/status")
async def subscription_status(user: UserPrincipal = Depends(get_current_user)):
    # TODO: query billing provider/db
    return {"plan": "free", "status": "active"}


@router.post("/webhook")
async def billing_webhook(request: Request):
    # TODO: verify Stripe/LemonSqueezy signature when configured
    _ = await request.body()
    return {"received": True}

