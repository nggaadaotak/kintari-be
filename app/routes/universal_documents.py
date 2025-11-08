"""
Universal Documents API Routes
Handles ALL types of documents for knowledge base
"""

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.universal_document_service import UniversalDocumentService
from app.services.universal_document_processor import UniversalDocumentProcessor
from pathlib import Path
from typing import List, Optional
import os

router = APIRouter(prefix="/api/documents", tags=["universal-documents"])


@router.post("/upload")
async def upload_any_document(
    file: UploadFile = File(...),
    category: Optional[str] = None,
    tags: Optional[str] = None,  # Comma-separated tags
    generate_ai_summary: bool = False,  # ✅ Changed default to False for faster uploads
    db: Session = Depends(get_db),
):
    """
    🚀 UNIVERSAL DOCUMENT UPLOAD

    Upload ANY type of PDF document to the knowledge base.
    The system will automatically:
    - Extract all text content
    - Detect document type
    - Extract tables
    - Find emails, dates, phone numbers
    - Generate AI summary (optional, set generate_ai_summary=true)
    - Create searchable index

    Examples of supported documents:
    - HIPMI documents (PO, AD, ART, SK)
    - Contracts and agreements
    - Reports and proposals
    - Presentations
    - Manuals and guides
    - ANY PDF file!

    The AI chatbot will use ALL uploaded documents as context!

    Performance:
    - generate_ai_summary=false (default): Fast upload, ~2-5 seconds for 1MB
    - generate_ai_summary=true: Slower, adds 10-30 seconds for AI processing
    """
    if file.filename is None or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Create uploads directory
        upload_dir = Path("./uploads")
        upload_dir.mkdir(exist_ok=True)

        # Save file
        file_path = upload_dir / file.filename
        contents = await file.read()

        # Validate file size (minimum 1KB to avoid fake PDFs)
        if len(contents) < 1024:
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file. File is too small (minimum 1KB required). Please upload a valid PDF document.",
            )

        # Validate PDF header
        if not contents.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file. File does not have valid PDF header. Please upload a valid PDF document.",
            )

        with open(file_path, "wb") as f:
            f.write(contents)

        file_size = os.path.getsize(file_path)

        # Parse tags
        tags_list = [tag.strip() for tag in tags.split(",")] if tags else []

        # Process and save to knowledge base
        # OPTIMIZATION: If generate_ai_summary=True, we still do it synchronously
        # but you can change this to background task using FastAPI BackgroundTasks
        document = UniversalDocumentService.process_and_save_document(
            db=db,
            file_path=str(file_path),
            filename=file.filename,
            file_size=file_size,
            category=category,
            tags=tags_list,
            generate_ai_summary=generate_ai_summary,
        )

        # Get document type info
        type_info = UniversalDocumentProcessor.get_document_category_info(
            document.document_type
        )

        return {
            "status": "success",
            "message": "Document uploaded and processed successfully",
            "document": {
                "id": document.id,
                "filename": document.filename,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "document_type": document.document_type,
                "type_info": type_info,
                "category": document.category,
                "tags": document.tags,
                "page_count": document.page_count,
                "keywords_count": len(document.keywords) if document.keywords else 0,
                "has_tables": (
                    len(document.tables_data) > 0 if document.tables_data else False
                ),
                "processed": document.processed,
                "uploaded_at": (
                    document.uploaded_at.isoformat() if document.uploaded_at else None
                ),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing document: {str(e)}"
        )


@router.get("/")
async def get_all_documents(
    skip: int = 0,
    limit: int = 100,
    document_type: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    📚 GET ALL DOCUMENTS

    Retrieve all documents from knowledge base with optional filters.

    Filters:
    - document_type: Filter by auto-detected type (HIPMI_PO, CONTRACT, REPORT, etc)
    - category: Filter by custom category
    - search: Full-text search in filename and content
    """
    documents = UniversalDocumentService.get_all_documents(
        db=db,
        skip=skip,
        limit=limit,
        document_type=document_type,
        category=category,
        search_query=search,
    )

    return {
        "total": len(documents),
        "skip": skip,
        "limit": limit,
        "filters": {
            "document_type": document_type,
            "category": category,
            "search": search,
        },
        "documents": [doc.to_dict() for doc in documents],
    }


@router.get("/{document_id}")
async def get_document_detail(document_id: int, db: Session = Depends(get_db)):
    """
    📄 GET DOCUMENT DETAILS

    Get complete information about a specific document including full text.
    """
    document = UniversalDocumentService.get_document_by_id(db, document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    type_info = UniversalDocumentProcessor.get_document_category_info(
        document.document_type
    )

    return {
        "document": document.to_dict_full(),
        "type_info": type_info,
        "content_stats": {
            "text_length": len(document.full_text) if document.full_text else 0,
            "keyword_count": len(document.keywords) if document.keywords else 0,
            "table_count": len(document.tables_data) if document.tables_data else 0,
            "entity_counts": (
                {
                    key: len(val) if isinstance(val, list) else 0
                    for key, val in (document.extracted_entities or {}).items()
                }
                if document.extracted_entities
                else {}
            ),
        },
    }


@router.delete("/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """
    🗑️ DELETE DOCUMENT

    Remove a document from the knowledge base.
    """
    success = UniversalDocumentService.delete_document(db, document_id)

    if not success:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"status": "success", "message": "Document deleted successfully"}


@router.put("/{document_id}/tags")
async def update_document_tags(
    document_id: int, tags: List[str], db: Session = Depends(get_db)
):
    """
    🏷️ UPDATE DOCUMENT TAGS

    Add or update tags for better organization and search.
    """
    document = UniversalDocumentService.update_document_tags(db, document_id, tags)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "status": "success",
        "message": "Tags updated successfully",
        "document": document.to_dict(),
    }


@router.put("/{document_id}/category")
async def update_document_category(
    document_id: int, category: str, db: Session = Depends(get_db)
):
    """
    📂 UPDATE DOCUMENT CATEGORY

    Set or change the document category.
    """
    document = UniversalDocumentService.update_document_category(
        db, document_id, category
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "status": "success",
        "message": "Category updated successfully",
        "document": document.to_dict(),
    }


@router.get("/stats/overview")
async def get_documents_stats(db: Session = Depends(get_db)):
    """
    📊 KNOWLEDGE BASE STATISTICS

    Get overview statistics about all documents in the knowledge base.
    """
    stats = UniversalDocumentService.get_document_stats(db)

    return {"status": "success", "stats": stats}


@router.get("/types/list")
async def get_document_types(db: Session = Depends(get_db)):
    """
    📋 LIST ALL DOCUMENT TYPES

    Get all document types currently in the knowledge base with counts.
    """
    types = UniversalDocumentService.get_all_document_types(db)

    return {"status": "success", "total_types": len(types), "types": types}


@router.get("/search/")
async def search_documents(
    q: str = Query(..., description="Search query"), db: Session = Depends(get_db)
):
    """
    🔍 SEARCH DOCUMENTS

    Full-text search across all documents in the knowledge base.
    Searches in: filename, content, summary
    """
    documents = UniversalDocumentService.search_documents(db, q)

    return {
        "status": "success",
        "query": q,
        "results_count": len(documents),
        "documents": [doc.to_dict() for doc in documents],
    }


@router.get("/type/{document_type}")
async def get_documents_by_type(document_type: str, db: Session = Depends(get_db)):
    """
    📑 GET DOCUMENTS BY TYPE

    Get all documents of a specific type.

    Available types:
    - HIPMI_PO, HIPMI_AD, HIPMI_ART, HIPMI_SK
    - CONTRACT, REPORT, PROPOSAL
    - PRESENTATION, REGULATION, MANUAL
    - OTHER
    """
    documents = UniversalDocumentService.get_documents_by_type(db, document_type)

    type_info = UniversalDocumentProcessor.get_document_category_info(document_type)

    return {
        "status": "success",
        "document_type": document_type,
        "type_info": type_info,
        "count": len(documents),
        "documents": [doc.to_dict() for doc in documents],
    }


# ===== COLLECTIONS API =====


@router.post("/collections/")
async def create_collection(
    name: str,
    description: str,
    document_ids: List[int] = [],
    db: Session = Depends(get_db),
):
    """
    📁 CREATE DOCUMENT COLLECTION

    Group multiple documents into a collection for better organization.
    Example: "HIPMI 2024 Documents", "Project Contracts", etc.
    """
    collection = UniversalDocumentService.create_collection(
        db, name, description, document_ids
    )

    return {
        "status": "success",
        "message": "Collection created successfully",
        "collection": collection.to_dict(),
    }


@router.get("/collections/")
async def get_all_collections(db: Session = Depends(get_db)):
    """
    📚 GET ALL COLLECTIONS

    List all document collections.
    """
    collections = UniversalDocumentService.get_all_collections(db)

    return {
        "status": "success",
        "total": len(collections),
        "collections": [c.to_dict() for c in collections],
    }


@router.get("/collections/{collection_id}/documents")
async def get_collection_documents(collection_id: int, db: Session = Depends(get_db)):
    """
    📂 GET DOCUMENTS IN COLLECTION

    Get all documents that belong to a specific collection.
    """
    documents = UniversalDocumentService.get_documents_in_collection(db, collection_id)

    return {
        "status": "success",
        "collection_id": collection_id,
        "document_count": len(documents),
        "documents": [doc.to_dict() for doc in documents],
    }


@router.put("/collections/{collection_id}/add")
async def add_documents_to_collection(
    collection_id: int, document_ids: List[int], db: Session = Depends(get_db)
):
    """
    ➕ ADD DOCUMENTS TO COLLECTION

    Add one or more documents to an existing collection.
    """
    collection = UniversalDocumentService.add_documents_to_collection(
        db, collection_id, document_ids
    )

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    return {
        "status": "success",
        "message": f"Added {len(document_ids)} document(s) to collection",
        "collection": collection.to_dict(),
    }
