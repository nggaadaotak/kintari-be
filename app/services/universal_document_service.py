"""
Universal Document Service
Handles ALL document operations for knowledge base
"""

from sqlalchemy.orm import Session
from app.models.universal_document import UniversalDocument, DocumentCollection
from app.services.universal_document_processor import UniversalDocumentProcessor
from app.services.gemini_service import GeminiService
from datetime import datetime
from typing import List, Optional, Dict, Any
import json


class UniversalDocumentService:
    """Service for managing universal documents"""

    @staticmethod
    def process_and_save_document(
        db: Session,
        file_path: str,
        filename: str,
        file_size: float,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        uploaded_by: Optional[str] = None,
        generate_ai_summary: bool = True,
    ) -> UniversalDocument:
        """
        Process PDF and save to universal knowledge base

        This is the MAIN function for handling ANY document upload
        """
        # Extract content from PDF
        extracted_data = UniversalDocumentProcessor.extract_document_content(file_path)

        # Auto-detect document type
        document_type = UniversalDocumentProcessor.detect_document_type(
            filename, extracted_data["full_text"]
        )

        # Create search index (combination of key fields)
        search_index = f"{filename} {extracted_data['full_text'][:5000]}"

        # Create document record
        document = UniversalDocument(
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            document_type=document_type,
            category=category,
            tags=tags if tags else [],
            full_text=extracted_data["full_text"],
            summary=extracted_data["summary"],
            extracted_entities=extracted_data["extracted_entities"],
            keywords=extracted_data["keywords"],
            tables_data=extracted_data["tables"],
            page_count=extracted_data["page_count"],
            pdf_metadata=extracted_data["metadata"],
            search_index=search_index,
            uploaded_by=uploaded_by,
            uploaded_at=datetime.utcnow(),
            processed=True,  # ✅ Set True immediately after PDF extraction
            processed_at=datetime.utcnow(),
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        # Generate AI summary asynchronously (optional, non-blocking)
        # Note: This runs synchronously but won't block the response
        # If it fails, document is already marked as processed
        if generate_ai_summary and extracted_data["full_text"]:
            try:
                print(f"🤖 Generating AI summary for {filename}...")
                gemini = GeminiService()

                # Generate summary (limit to 15000 chars to avoid timeout)
                ai_summary = gemini.summarize_text(extracted_data["full_text"][:15000])

                # Generate insights
                insights_prompt = f"""
Analyze this document briefly and extract key information:
Document Type: {document_type}
Content: {extracted_data['full_text'][:8000]}

Provide a brief analysis covering:
1. Main topics (2-3 points)
2. Key findings (2-3 points)
3. Important entities (people, organizations, dates)
"""

                ai_insights_text = gemini.summarize_text(insights_prompt)

                # Update document with AI data
                document.ai_summary = ai_summary  # type: ignore
                document.ai_insights = {"analysis": ai_insights_text}  # type: ignore

                db.commit()
                db.refresh(document)

                print(f"✅ AI summary generated for {filename}")

            except Exception as e:
                print(f"⚠️ AI processing error (non-critical): {e}")
                # Document is already processed, AI summary is just bonus

        return document

    @staticmethod
    def get_all_documents(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        document_type: Optional[str] = None,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[UniversalDocument]:
        """
        Get all documents with optional filtering
        """
        query = db.query(UniversalDocument)

        if document_type:
            query = query.filter(UniversalDocument.document_type == document_type)

        if category:
            query = query.filter(UniversalDocument.category == category)

        if search_query:
            query = query.filter(UniversalDocument.search_index.contains(search_query))

        return (
            query.order_by(UniversalDocument.uploaded_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_document_by_id(
        db: Session, document_id: int
    ) -> Optional[UniversalDocument]:
        """Get single document by ID"""
        return (
            db.query(UniversalDocument)
            .filter(UniversalDocument.id == document_id)
            .first()
        )

    @staticmethod
    def delete_document(db: Session, document_id: int) -> bool:
        """Delete document from database and optionally from filesystem"""
        document = UniversalDocumentService.get_document_by_id(db, document_id)
        if document:
            db.delete(document)
            db.commit()
            return True
        return False

    @staticmethod
    def update_document_tags(
        db: Session, document_id: int, tags: List[str]
    ) -> Optional[UniversalDocument]:
        """Update document tags"""
        document = UniversalDocumentService.get_document_by_id(db, document_id)
        if document:
            document.tags = tags  # type: ignore
            document.updated_at = datetime.utcnow()  # type: ignore
            db.commit()
            db.refresh(document)
        return document

    @staticmethod
    def update_document_category(
        db: Session, document_id: int, category: str
    ) -> Optional[UniversalDocument]:
        """Update document category"""
        document = UniversalDocumentService.get_document_by_id(db, document_id)
        if document:
            document.category = category  # type: ignore
            document.updated_at = datetime.utcnow()  # type: ignore
            db.commit()
            db.refresh(document)
        return document

    @staticmethod
    def get_documents_by_type(
        db: Session, document_type: str
    ) -> List[UniversalDocument]:
        """Get all documents of specific type"""
        return (
            db.query(UniversalDocument)
            .filter(UniversalDocument.document_type == document_type)
            .order_by(UniversalDocument.uploaded_at.desc())
            .all()
        )

    @staticmethod
    def get_document_stats(db: Session) -> Dict[str, Any]:
        """Get statistics about documents in knowledge base"""
        total_docs = db.query(UniversalDocument).count()
        processed_docs = (
            db.query(UniversalDocument)
            .filter(UniversalDocument.processed == True)
            .count()
        )

        # Count by type
        types_count = {}
        all_docs = db.query(UniversalDocument).all()
        for doc in all_docs:
            doc_type = doc.document_type or "UNKNOWN"
            types_count[doc_type] = types_count.get(doc_type, 0) + 1

        # Total storage used
        from sqlalchemy import func

        total_size = (
            db.query(UniversalDocument)
            .with_entities(func.sum(UniversalDocument.file_size))
            .scalar()
            or 0
        )

        return {
            "total_documents": total_docs,
            "processed_documents": processed_docs,
            "unprocessed_documents": total_docs - processed_docs,
            "documents_by_type": types_count,
            "total_storage_bytes": total_size,
            "total_storage_mb": round(total_size / (1024 * 1024), 2),
        }

    @staticmethod
    def search_documents(
        db: Session, query: str, limit: int = 20
    ) -> List[UniversalDocument]:
        """
        Full-text search across all documents
        """
        from sqlalchemy import or_

        return (
            db.query(UniversalDocument)
            .filter(
                or_(
                    UniversalDocument.filename.contains(query),
                    UniversalDocument.full_text.contains(query),
                    UniversalDocument.summary.contains(query),
                )
            )
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_all_document_types(db: Session) -> List[Dict[str, Any]]:
        """Get list of all document types with counts"""
        docs = db.query(UniversalDocument).all()
        type_counts = {}

        for doc in docs:
            doc_type = doc.document_type or "OTHER"
            if doc_type not in type_counts:
                type_info = UniversalDocumentProcessor.get_document_category_info(
                    str(doc_type)  # type: ignore
                )
                type_counts[doc_type] = {
                    "type": doc_type,
                    "name": type_info["name"],
                    "description": type_info["description"],
                    "icon": type_info["icon"],
                    "count": 0,
                }
            type_counts[doc_type]["count"] += 1

        return list(type_counts.values())

    # ===== COLLECTION MANAGEMENT =====

    @staticmethod
    def create_collection(
        db: Session,
        name: str,
        description: str,
        document_ids: Optional[List[int]] = None,
    ) -> DocumentCollection:
        """Create a new document collection"""
        collection = DocumentCollection(
            name=name,
            description=description,
            document_ids=document_ids if document_ids else [],
        )
        db.add(collection)
        db.commit()
        db.refresh(collection)
        return collection

    @staticmethod
    def add_documents_to_collection(
        db: Session, collection_id: int, document_ids: List[int]
    ) -> Optional[DocumentCollection]:
        """Add documents to existing collection"""
        collection = (
            db.query(DocumentCollection)
            .filter(DocumentCollection.id == collection_id)
            .first()
        )
        if collection:
            current_ids = collection.document_ids or []  # type: ignore
            # Add new IDs without duplicates
            updated_ids = list(set(current_ids + document_ids))  # type: ignore
            collection.document_ids = updated_ids  # type: ignore
            collection.updated_at = datetime.utcnow()  # type: ignore
            db.commit()
            db.refresh(collection)
        return collection

    @staticmethod
    def get_all_collections(db: Session) -> List[DocumentCollection]:
        """Get all document collections"""
        return (
            db.query(DocumentCollection)
            .filter(DocumentCollection.is_active == True)
            .all()
        )

    @staticmethod
    def get_documents_in_collection(
        db: Session, collection_id: int
    ) -> List[UniversalDocument]:
        """Get all documents in a collection"""
        collection = (
            db.query(DocumentCollection)
            .filter(DocumentCollection.id == collection_id)
            .first()
        )

        if not collection:
            return []

        # Safely extract document_ids
        try:
            doc_ids = collection.document_ids  # type: ignore
            if not doc_ids:  # type: ignore
                return []

            # Ensure it's a list
            if not isinstance(doc_ids, list):  # type: ignore
                return []

            if len(doc_ids) == 0:
                return []

            # Query documents by IDs
            return (
                db.query(UniversalDocument)
                .filter(UniversalDocument.id.in_(doc_ids))
                .all()
            )
        except Exception as e:
            print(f"Error getting documents in collection: {e}")
            return []
