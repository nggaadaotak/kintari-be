from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import ALLOWED_ORIGINS
from app.core.database import Base, engine

# Import all models to ensure they're registered with SQLAlchemy
from app.models import (
    Member,
    OrganizationInfo,
    MembershipType,
    OrgStructure,
    UniversalDocument,
    DocumentCollection,
)

from app.routes import (
    members,
    chat,
    stats,
    universal_documents,
    analytics,
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Kintari Backend API - Universal Knowledge Base",
    description="""
    Backend API untuk Kintari dengan Universal Document Knowledge Base.
    
    🚀 Features:
    - Upload ANY type of PDF document
    - Automatic text extraction and analysis
    - AI-powered chatbot using ALL documents
    - Advanced search and filtering
    - Document collections
    - Gemini AI Integration
    
    Upload documents and the AI chatbot will automatically use them as context!
    """,
    version="2.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dapat diganti dengan ALLOWED_ORIGINS untuk production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(universal_documents.router)  # ⭐ Universal Documents (MAIN)
app.include_router(chat.router)  # 🤖 AI Chatbot with universal knowledge
app.include_router(stats.router)  # 📊 Statistics
app.include_router(members.router)  # 👥 Members management
app.include_router(analytics.router)  # 🧠 AI Analytics for HIPMI data


@app.get("/")
async def root():
    return {
        "message": "Welcome to Kintari Backend API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
