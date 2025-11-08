from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.member import Member
from app.models.universal_document import UniversalDocument

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview")
async def get_stats_overview(db: Session = Depends(get_db)):
    """
    📊 STATS OVERVIEW

    Get comprehensive statistics overview:
    - Total documents (universal knowledge base)
    - Total members
    - Storage usage
    - Document types breakdown
    """
    # Count documents from universal knowledge base
    total_documents = db.query(UniversalDocument).count()

    # Count processed documents
    processed_docs = (
        db.query(UniversalDocument).filter(UniversalDocument.processed == True).count()
    )

    # Count members
    total_members = db.query(Member).count()

    # Get latest document
    latest_doc = (
        db.query(UniversalDocument)
        .order_by(UniversalDocument.uploaded_at.desc())
        .first()
    )

    # Calculate total storage
    from sqlalchemy import func

    total_storage = db.query(func.sum(UniversalDocument.file_size)).scalar() or 0

    return {
        "status": "success",
        "data": {
            "total_dokumen": total_documents,
            "processed_documents": processed_docs,
            "total_anggota": total_members,
            "total_storage_mb": round(total_storage / (1024 * 1024), 2),
            "latest_document": latest_doc.filename if latest_doc else None,
            "last_updated": (
                latest_doc.uploaded_at.isoformat() if latest_doc and latest_doc.uploaded_at is not None else None  # type: ignore
            ),
        },
    }
