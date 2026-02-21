from fastapi import APIRouter
from app.api.routes import auth, applicants, payments, audit, chatbot, dashboard

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(applicants.router)
api_router.include_router(payments.router)
api_router.include_router(audit.router)
api_router.include_router(chatbot.router)
api_router.include_router(dashboard.router)