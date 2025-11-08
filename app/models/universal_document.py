"""
Universal Knowledge Base Model
Stores ALL types of documents for AI chatbot context
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, JSON
from app.core.database import Base
from datetime import datetime


class UniversalDocument(Base):
    """
    Universal document storage for ANY type of PDF
    This serves as the knowledge base for the AI chatbot
    """

    __tablename__ = "universal_documents"

    id = Column(Integer, primary_key=True, index=True)

    # File information
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Float)  # in bytes

    # Document classification
    document_type = Column(
        String(50), nullable=False, default="OTHER"
    )  # Auto-detected type
    category = Column(String(100))  # Custom category from user
    tags = Column(JSON)  # Array of tags for better search

    # Content
    full_text = Column(Text)  # Complete extracted text
    summary = Column(Text)  # Short summary
    extracted_entities = Column(JSON)  # Dates, emails, phone numbers, etc
    keywords = Column(JSON)  # Top keywords from document
    tables_data = Column(JSON)  # Extracted tables

    # Metadata
    page_count = Column(Integer)
    pdf_metadata = Column(JSON)  # PDF metadata (author, title, etc)

    # AI Processing
    ai_summary = Column(Text)  # Gemini-generated summary
    ai_insights = Column(JSON)  # Gemini-extracted insights
    embedding_vector = Column(Text)  # For future vector search
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)

    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Access control (optional)
    is_public = Column(Boolean, default=True)
    uploaded_by = Column(String(100))  # User who uploaded

    # Search optimization
    search_index = Column(Text)  # Combined text for full-text search

    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "id": self.id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "document_type": self.document_type,
            "category": self.category,
            "tags": self.tags,
            "summary": self.summary,
            "page_count": self.page_count,
            "keywords": self.keywords,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "processed": self.processed,
        }

    def to_dict_full(self):
        """Convert to dictionary with full content"""
        base_dict = self.to_dict()
        base_dict.update(
            {
                "full_text": self.full_text,
                "extracted_entities": self.extracted_entities,
                "tables_data": self.tables_data,
                "pdf_metadata": self.pdf_metadata,
                "ai_summary": self.ai_summary,
                "ai_insights": self.ai_insights,
            }
        )
        return base_dict


class DocumentCollection(Base):
    """
    Group multiple documents into collections
    Example: "HIPMI 2024 Documents", "Project X Contracts", etc
    """

    __tablename__ = "document_collections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    document_ids = Column(JSON)  # Array of document IDs in this collection
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))
    is_active = Column(Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "document_count": len(self.document_ids) if self.document_ids else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active,
        }
