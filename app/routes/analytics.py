from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.member import Member
from app.models.universal_document import UniversalDocument
from app.services.gemini_service import GeminiService
from datetime import datetime

router = APIRouter(prefix="/api", tags=["analytics"])


def build_age_range(age: int) -> str:
    """Konversi usia ke rentang untuk histogram"""
    if age < 25:
        return "20-25"
    elif age < 30:
        return "25-30"
    elif age < 35:
        return "30-35"
    elif age < 40:
        return "35-40"
    elif age < 45:
        return "40-45"
    else:
        return "45+"


def process_member_statistics(members: list) -> tuple:
    """Proses statistik dari list members, return tuple (members_data, counts, visualizations)"""
    members_data = []
    jabatan_count = {}
    bidang_usaha_count = {}
    status_kta_count = {}
    gender_count = {"Male": 0, "Female": 0}
    age_distribution = {}
    company_ownership = {"Memiliki Perusahaan": 0, "Tidak Memiliki Perusahaan": 0}
    unique_companies = set()  # Track unique perusahaan

    for m in members:
        # Data untuk AI analysis
        members_data.append(
            {
                "name": m.name,
                "email": m.email,
                "jabatan": m.jabatan,
                "status_kta": m.status_kta,
                "usia": m.usia,
                "jenis_kelamin": m.jenis_kelamin,
                "kategori_bidang_usaha": m.kategori_bidang_usaha,
                "nama_perusahaan": m.nama_perusahaan,
                "jmlh_karyawan": m.jmlh_karyawan,
            }
        )

        # Count statistics
        jabatan = m.jabatan or "Tidak Diketahui"
        jabatan_count[jabatan] = jabatan_count.get(jabatan, 0) + 1

        bidang = m.kategori_bidang_usaha or "Tidak Diketahui"
        bidang_usaha_count[bidang] = bidang_usaha_count.get(bidang, 0) + 1

        status = m.status_kta or "Tidak Diketahui"
        status_kta_count[status] = status_kta_count.get(status, 0) + 1

        if m.jenis_kelamin and m.jenis_kelamin.strip() in ["Male", "Female"]:
            gender_count[m.jenis_kelamin.strip()] += 1

        if m.usia and m.usia > 0:
            age_range = build_age_range(m.usia)
            age_distribution[age_range] = age_distribution.get(age_range, 0) + 1

        # Track unique companies
        if m.nama_perusahaan and m.nama_perusahaan.strip():
            company_ownership["Memiliki Perusahaan"] += 1
            unique_companies.add(m.nama_perusahaan.strip())
        else:
            company_ownership["Tidak Memiliki Perusahaan"] += 1

    stats = {
        "total_pengurus": len(members),
        "by_jabatan": jabatan_count,
        "by_bidang_usaha": bidang_usaha_count,
        "by_status_kta": status_kta_count,
        "total_perusahaan": len(unique_companies),  # Jumlah perusahaan unik
    }

    visualizations = {
        "age_distribution": dict(sorted(age_distribution.items())),
        "gender_proportion": gender_count,
        "by_business_category": dict(
            sorted(bidang_usaha_count.items(), key=lambda x: x[1], reverse=True)
        ),
        "company_ownership": company_ownership,
    }

    return members_data, stats, visualizations


def process_document_statistics(documents: list) -> tuple:
    """Proses statistik dari list documents, return tuple (docs_data, stats)"""
    docs_data = []
    doc_types_count = {}
    categories_count = {}
    total_pages = 0
    total_size = 0

    for doc in documents:
        docs_data.append(
            {
                "filename": doc.filename,
                "document_type": doc.document_type,
                "category": doc.category,
                "page_count": doc.page_count,
                "file_size_mb": doc.file_size_mb,
            }
        )

        dtype = doc.document_type or "Unknown"
        doc_types_count[dtype] = doc_types_count.get(dtype, 0) + 1

        cat = doc.category or "Tidak Dikategorikan"
        categories_count[cat] = categories_count.get(cat, 0) + 1

        if doc.page_count:
            total_pages += doc.page_count
        if doc.file_size_mb:
            total_size += doc.file_size_mb

    stats = {
        "total_documents": len(documents),
        "total_pages": total_pages,
        "total_size_mb": round(total_size, 2),
        "by_type": doc_types_count,
        "by_category": categories_count,
        "avg_pages_per_doc": round(total_pages / len(documents), 1) if documents else 0,
        "avg_size_mb": round(total_size / len(documents), 2) if documents else 0,
    }

    return docs_data, stats


@router.get("/analytics/members")
async def analyze_members(db: Session = Depends(get_db)):
    """Analisis data pengurus HIPMI dengan AI Gemini"""
    try:
        members = db.query(Member).all()

        if not members:
            return {
                "status": "success",
                "message": "Belum ada data anggota untuk dianalisis",
                "data": {
                    "summary": "Belum ada data anggota HIPMI yang tersimpan di sistem",
                    "total_members": 0,
                    "key_insights": [],
                    "trends": "Tidak ada data untuk analisis tren",
                    "recommendations": [
                        "Upload data anggota untuk mendapatkan analisis"
                    ],
                },
            }

        # Process statistics menggunakan helper
        members_data, stats, visualizations = process_member_statistics(members)

        # AI analysis
        gemini = GeminiService()
        ai_analysis = gemini.analyze_members_data(members_data)

        result = {
            **ai_analysis,
            "statistics": stats,
            "visualizations": visualizations,
            "last_updated": datetime.now().isoformat(),
        }

        return {"status": "success", "data": result}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze members: {str(e)}"
        )


@router.get("/analytics/documents")
async def analyze_documents(db: Session = Depends(get_db)):
    """Analisis data dokumen HIPMI dengan AI Gemini"""
    try:
        documents = db.query(UniversalDocument).all()

        if not documents:
            return {
                "status": "success",
                "message": "Belum ada dokumen untuk dianalisis",
                "data": {
                    "summary": "Belum ada dokumen HIPMI yang tersimpan di sistem",
                    "total_documents": 0,
                    "total_pages": 0,
                    "key_insights": [],
                    "document_health": "Belum ada data",
                    "recommendations": [
                        "Upload dokumen HIPMI untuk mendapatkan analisis"
                    ],
                },
            }

        # Process statistics menggunakan helper
        docs_data, stats = process_document_statistics(documents)

        # AI analysis
        gemini = GeminiService()
        ai_analysis = gemini.analyze_documents_data(docs_data)

        result = {
            **ai_analysis,
            "statistics": stats,
            "last_updated": datetime.now().isoformat(),
        }

        return {"status": "success", "data": result}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze documents: {str(e)}"
        )


@router.get("/analytics/overview")
async def get_overview_analytics(db: Session = Depends(get_db)):
    """Get combined analytics overview untuk dashboard"""
    try:
        members_count = db.query(Member).count()
        documents_count = db.query(UniversalDocument).count()

        overview = {
            "total_members": members_count,
            "total_documents": documents_count,
            "has_data": members_count > 0 or documents_count > 0,
        }

        if overview["has_data"]:
            gemini = GeminiService()
            prompt = f"""Sebagai AI analyst untuk HIPMI, berikan ringkasan singkat kondisi organisasi:

Total Anggota: {members_count}
Total Dokumen: {documents_count}

Berikan 3 poin insight singkat dalam format JSON:
{{
    "health_status": "Excellent/Good/Fair/Needs Improvement",
    "key_points": ["Poin 1", "Poin 2", "Poin 3"],
    "next_actions": "Rekomendasi prioritas"
}}"""

            try:
                response = gemini._call_api(prompt)
                import json

                ai_overview = json.loads(response)
                overview.update(ai_overview)
            except:
                overview["message"] = (
                    "AI analysis tidak tersedia, menampilkan data statistik"
                )

        return {"status": "success", "data": overview}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get overview: {str(e)}")
