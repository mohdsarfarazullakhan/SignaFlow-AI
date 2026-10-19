from fastapi import APIRouter

from app.api.routes import admin, advisor, analytics, auth, campaigns, copilot, leads, products, quotes, system, vision

api_router = APIRouter(prefix="/api")
api_router.include_router(system.router)
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(products.router)
api_router.include_router(advisor.router)
api_router.include_router(leads.router)
api_router.include_router(quotes.router)
api_router.include_router(copilot.router)
api_router.include_router(campaigns.router)
api_router.include_router(analytics.router)
api_router.include_router(vision.router)
