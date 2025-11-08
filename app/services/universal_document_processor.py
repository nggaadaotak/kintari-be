"""
Universal Document Processor
Handles ANY type of PDF documents for knowledge base
"""

import pdfplumber
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import re


class UniversalDocumentProcessor:
    """
    Process any PDF document and extract text + metadata
    This serves as the universal knowledge base for the AI chatbot
    """

    @staticmethod
    def extract_document_content(file_path: str) -> Dict[str, Any]:
        """
        Extract complete content from any PDF document

        Args:
            file_path: Path to PDF file

        Returns:
            Dictionary containing:
            - full_text: Complete extracted text
            - page_count: Number of pages
            - metadata: PDF metadata
            - summary: Auto-generated summary
            - extracted_entities: Key information extracted
        """
        result = {
            "full_text": "",
            "page_count": 0,
            "metadata": {},
            "summary": "",
            "extracted_entities": {},
            "tables": [],
            "keywords": [],
        }

        try:
            # Validate PDF file before processing
            with open(file_path, "rb") as f:
                header = f.read(5)
                if header != b"%PDF-":
                    raise Exception(
                        "Invalid PDF file. File does not have PDF header. Please upload a valid PDF document."
                    )

            with pdfplumber.open(file_path) as pdf:
                # Extract metadata
                result["metadata"] = {
                    "title": pdf.metadata.get("Title", ""),
                    "author": pdf.metadata.get("Author", ""),
                    "subject": pdf.metadata.get("Subject", ""),
                    "creator": pdf.metadata.get("Creator", ""),
                    "producer": pdf.metadata.get("Producer", ""),
                    "creation_date": pdf.metadata.get("CreationDate", ""),
                }

                result["page_count"] = len(pdf.pages)

                # Extract text from all pages
                full_text = []
                tables = []

                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    text = page.extract_text()
                    if text:
                        full_text.append(text)

                    # Extract tables
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table in page_tables:
                            tables.append(
                                {
                                    "page": page_num,
                                    "data": table,
                                    "rows": len(table),
                                    "cols": len(table[0]) if table else 0,
                                }
                            )

                result["full_text"] = "\n\n".join(full_text)
                result["tables"] = tables

                # Extract key entities automatically
                result["extracted_entities"] = (
                    UniversalDocumentProcessor._extract_entities(result["full_text"])
                )

                # Extract keywords
                result["keywords"] = UniversalDocumentProcessor._extract_keywords(
                    result["full_text"]
                )

                # Generate summary (first 500 characters)
                result["summary"] = (
                    result["full_text"][:500] + "..."
                    if len(result["full_text"]) > 500
                    else result["full_text"]
                )

        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")

        return result

    @staticmethod
    def _extract_entities(text: str) -> Dict[str, Any]:
        """
        Extract key entities from text using pattern matching
        This is language-agnostic and works for any document type
        """
        entities = {
            "dates": [],
            "numbers": [],
            "organizations": [],
            "emails": [],
            "urls": [],
            "phone_numbers": [],
        }

        # Extract dates (various formats)
        date_patterns = [
            r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}",  # DD-MM-YYYY, DD/MM/YYYY
            r"\d{4}[-/]\d{1,2}[-/]\d{1,2}",  # YYYY-MM-DD
            r"\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4}",
            r"\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}",
        ]
        for pattern in date_patterns:
            entities["dates"].extend(re.findall(pattern, text))

        # Extract emails
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        entities["emails"] = re.findall(email_pattern, text)

        # Extract URLs
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        entities["urls"] = re.findall(url_pattern, text)

        # Extract phone numbers (Indonesian format)
        phone_patterns = [
            r"\+62\s?\d{2,3}[-\s]?\d{3,4}[-\s]?\d{3,4}",  # +62 format
            r"0\d{2,3}[-\s]?\d{3,4}[-\s]?\d{3,4}",  # 0xxx format
            r"\(\d{2,3}\)\s?\d{3,4}[-\s]?\d{3,4}",  # (0xx) format
        ]
        for pattern in phone_patterns:
            entities["phone_numbers"].extend(re.findall(pattern, text))

        # Extract numbers (amounts, percentages)
        number_pattern = r"\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?\s*%?\b"
        entities["numbers"] = re.findall(number_pattern, text)[:50]  # Limit to 50

        return entities

    @staticmethod
    def _extract_keywords(text: str, top_n: int = 20) -> List[str]:
        """
        Extract top keywords from text using simple frequency analysis
        """
        # Remove special characters and split into words
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())

        # Common stopwords (Indonesian + English)
        stopwords = set(
            [
                "yang",
                "dan",
                "untuk",
                "pada",
                "dalam",
                "dengan",
                "adalah",
                "dari",
                "ini",
                "itu",
                "akan",
                "dapat",
                "telah",
                "atau",
                "oleh",
                "sebagai",
                "the",
                "and",
                "for",
                "that",
                "this",
                "with",
                "from",
                "have",
                "been",
                "will",
                "their",
                "which",
            ]
        )

        # Count word frequency
        word_freq = {}
        for word in words:
            if word not in stopwords and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency and get top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_n]]

    @staticmethod
    def detect_document_type(filename: str, text: str) -> str:
        """
        Auto-detect document type based on filename and content

        Returns one of:
        - HIPMI_PO (Peraturan Organisasi)
        - HIPMI_AD (Anggaran Dasar)
        - HIPMI_ART (Anggaran Rumah Tangga)
        - HIPMI_SK (Surat Keputusan)
        - CONTRACT (Kontrak/Perjanjian)
        - REPORT (Laporan)
        - PROPOSAL (Proposal)
        - PRESENTATION (Presentasi)
        - REGULATION (Peraturan)
        - MANUAL (Manual/Panduan)
        - OTHER (Lainnya)
        """
        filename_lower = filename.lower()
        text_lower = text.lower()

        # Check filename patterns
        if "po" in filename_lower or "peraturan organisasi" in text_lower[:1000]:
            return "HIPMI_PO"
        elif "ad" in filename_lower or "anggaran dasar" in text_lower[:1000]:
            return "HIPMI_AD"
        elif "art" in filename_lower or "anggaran rumah tangga" in text_lower[:1000]:
            return "HIPMI_ART"
        elif "sk" in filename_lower or "surat keputusan" in text_lower[:1000]:
            return "HIPMI_SK"
        elif any(
            word in filename_lower for word in ["kontrak", "perjanjian", "contract"]
        ):
            return "CONTRACT"
        elif any(word in filename_lower for word in ["laporan", "report"]):
            return "REPORT"
        elif "proposal" in filename_lower:
            return "PROPOSAL"
        elif any(
            word in filename_lower for word in ["presentasi", "presentation", "slide"]
        ):
            return "PRESENTATION"
        elif any(
            word in filename_lower for word in ["peraturan", "regulation", "kebijakan"]
        ):
            return "REGULATION"
        elif any(word in filename_lower for word in ["manual", "panduan", "guide"]):
            return "MANUAL"

        # Check content patterns (first 2000 chars)
        content_check = text_lower[:2000]
        if "hipmi" in content_check:
            return "HIPMI_DOCUMENT"
        elif "kontrak" in content_check or "perjanjian" in content_check:
            return "CONTRACT"
        elif "laporan" in content_check:
            return "REPORT"

        return "OTHER"

    @staticmethod
    def get_document_category_info(doc_type: str) -> Dict[str, str]:
        """
        Get human-readable information about document type
        """
        categories = {
            "HIPMI_PO": {
                "name": "Peraturan Organisasi HIPMI",
                "description": "Dokumen peraturan organisasi internal",
                "icon": "📋",
            },
            "HIPMI_AD": {
                "name": "Anggaran Dasar HIPMI",
                "description": "Dokumen anggaran dasar organisasi",
                "icon": "📜",
            },
            "HIPMI_ART": {
                "name": "Anggaran Rumah Tangga HIPMI",
                "description": "Dokumen anggaran rumah tangga organisasi",
                "icon": "🏛️",
            },
            "HIPMI_SK": {
                "name": "Surat Keputusan HIPMI",
                "description": "Dokumen surat keputusan organisasi",
                "icon": "✅",
            },
            "HIPMI_DOCUMENT": {
                "name": "Dokumen HIPMI",
                "description": "Dokumen umum HIPMI",
                "icon": "📄",
            },
            "CONTRACT": {
                "name": "Kontrak/Perjanjian",
                "description": "Dokumen kontrak atau perjanjian",
                "icon": "📝",
            },
            "REPORT": {
                "name": "Laporan",
                "description": "Dokumen laporan",
                "icon": "📊",
            },
            "PROPOSAL": {
                "name": "Proposal",
                "description": "Dokumen proposal",
                "icon": "💼",
            },
            "PRESENTATION": {
                "name": "Presentasi",
                "description": "Slide presentasi",
                "icon": "📽️",
            },
            "REGULATION": {
                "name": "Peraturan",
                "description": "Dokumen peraturan",
                "icon": "⚖️",
            },
            "MANUAL": {
                "name": "Manual/Panduan",
                "description": "Dokumen manual atau panduan",
                "icon": "📖",
            },
            "OTHER": {
                "name": "Dokumen Lainnya",
                "description": "Dokumen umum lainnya",
                "icon": "📑",
            },
        }

        return categories.get(
            doc_type,
            {"name": "Unknown", "description": "Unknown document type", "icon": "❓"},
        )
