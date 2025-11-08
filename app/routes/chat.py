from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.services.gemini_service import GeminiService
from app.services.universal_document_service import UniversalDocumentService
from app.schemas.chat_schema import ChatQuerySchema, ChatResponseSchema
from app.models.member import Member
from app.models.universal_document import UniversalDocument
import re

router = APIRouter(prefix="/api/chat", tags=["chat"])


# Handler 1: Statistik per Jabatan
def handle_jabatan_query(query_lower: str, db: Session) -> dict | None:
    """Handle query tentang jabatan pengurus"""
    if not ("berapa" in query_lower and ("jabatan" in query_lower or "ketua" in query_lower or "sekum" in query_lower or "bendum" in query_lower)):
        return None
    
    # Extract specific jabatan
    jabatan_match = re.search(r"['\"]([^'\"]+)['\"]", query_lower)
    if jabatan_match:
        jabatan_name = jabatan_match.group(1)
        count = db.query(Member).filter(func.lower(Member.jabatan).like(f"%{jabatan_name.lower()}%")).count()
        return {
            "type": "specific_query",
            "answer": f"Jumlah pengurus dengan jabatan '{jabatan_name}': **{count} orang**",
            "data": {"jabatan": jabatan_name, "count": count},
        }
    
    # Show all jabatan
    if "per jabatan" in query_lower or "jumlah pengurus per jabatan" in query_lower:
        result = db.query(Member.jabatan, func.count(Member.id).label("count")).filter(Member.jabatan.isnot(None)).group_by(Member.jabatan).order_by(func.count(Member.id).desc()).all()
        if result:
            answer = "**Jumlah Pengurus per Jabatan:**\n" + "\n".join([f"- {r.jabatan}: {r.count} orang" for r in result])
            return {"type": "specific_query", "answer": answer, "data": {"jabatan_counts": {r.jabatan: r.count for r in result}}}
    
    return None


# Handler 2: Statistik Bidang Usaha
def handle_bidang_usaha_query(query_lower: str, db: Session) -> dict | None:
    """Handle query tentang bidang usaha"""
    if "bidang usaha" not in query_lower and "kategori bisnis" not in query_lower:
        return None
    
    # Most popular bidang
    if "paling banyak" in query_lower or "terbanyak" in query_lower:
        result = db.query(Member.kategori_bidang_usaha, func.count(Member.id).label("count")).filter(Member.kategori_bidang_usaha.isnot(None)).group_by(Member.kategori_bidang_usaha).order_by(func.count(Member.id).desc()).first()
        if result:
            return {
                "type": "specific_query",
                "answer": f"Bidang usaha terbanyak di kepengurusan: **{result.kategori_bidang_usaha}** ({result.count} pengurus)",
                "data": {"bidang_usaha": result.kategori_bidang_usaha, "count": result.count},
            }
    
    # Specific bidang count
    if "berapa" in query_lower:
        bidang_match = re.search(r"['\"]([^'\"]+)['\"]", query_lower)
        if bidang_match:
            bidang_name = bidang_match.group(1)
            count = db.query(Member).filter(func.lower(Member.kategori_bidang_usaha).like(f"%{bidang_name.lower()}%")).count()
            return {
                "type": "specific_query",
                "answer": f"Jumlah pengurus di bidang '{bidang_name}': **{count} orang**",
                "data": {"bidang_usaha": bidang_name, "count": count},
            }
    
    return None


# Handler 3: Statistik Status KTA
def handle_kta_query(query_lower: str, query: str, db: Session) -> dict | None:
    """Handle query tentang status KTA"""
    if "kta" not in query_lower:
        return None
    
    # Specific status
    status_match = re.search(r"['\"]([^'\"]+)['\"]", query)
    if status_match:
        status_name = status_match.group(1)
        count = db.query(Member).filter(func.lower(Member.status_kta).like(f"%{status_name.lower()}%")).count()
        return {
            "type": "specific_query",
            "answer": f"Jumlah pengurus dengan status KTA '{status_name}': **{count} orang**",
            "data": {"status_kta": status_name, "count": count},
        }
    
    # Show all status
    if "tampilkan status kta" in query_lower:
        result = db.query(Member.status_kta, func.count(Member.id).label("count")).filter(Member.status_kta.isnot(None)).group_by(Member.status_kta).all()
        if result:
            answer = "**Status KTA Semua Pengurus:**\n" + "\n".join([f"- {r.status_kta}: {r.count} orang" for r in result])
            return {"type": "specific_query", "answer": answer, "data": {"status_counts": {r.status_kta: r.count for r in result}}}
    
    return None


# Handler 4: Statistik Gender
def handle_gender_query(query_lower: str, db: Session) -> dict | None:
    """Handle query tentang rasio gender"""
    if "rasio" in query_lower and ("pria" in query_lower or "wanita" in query_lower or "gender" in query_lower):
        male_count = db.query(Member).filter(Member.jenis_kelamin == "Male").count()
        female_count = db.query(Member).filter(Member.jenis_kelamin == "Female").count()
        total = male_count + female_count
        if total > 0:
            male_pct = (male_count / total * 100)
            female_pct = (female_count / total * 100)
            return {
                "type": "specific_query",
                "answer": f"**Rasio Gender Pengurus:**\n- Pria: {male_count} orang ({male_pct:.1f}%)\n- Wanita: {female_count} orang ({female_pct:.1f}%)",
                "data": {"male": male_count, "female": female_count, "male_pct": male_pct, "female_pct": female_pct},
            }
    return None


# Handler 5: Detail Pengurus (Natural Language)
def handle_detail_pengurus_query(query_lower: str, db: Session) -> dict | None:
    """Handle query tentang detail pengurus specific"""
    if not ("cari" in query_lower or "info" in query_lower or "siapa" in query_lower or "jabatannya" in query_lower):
        return None
    
    # Extract name dari quotes atau natural language
    name = None
    name_match = re.search(r"['\"]([^'\"]+)['\"]", query_lower)
    if name_match:
        name = name_match.group(1)
    else:
        # Natural language extraction
        for word in ["cari", "info", "lengkap", "siapa", "jabatannya", "apa", "sebagai", "perusahaannya", "umurnya", "kontaknya"]:
            query_lower = query_lower.replace(word, " ")
        potential_name = query_lower.strip()
        if potential_name and len(potential_name) > 2:
            name = potential_name
    
    if name:
        member = db.query(Member).filter(func.lower(Member.name).like(f"%{name.lower()}%")).first()
        if member:
            return {
                "type": "specific_query",
                "answer": f"""**Informasi Lengkap Pengurus:**
- Nama: {member.name}
- Jabatan: {member.jabatan or 'Tidak tersedia'}
- Status KTA: {member.status_kta or 'Tidak tersedia'}
- Usia: {member.usia or 'Tidak tersedia'}
- Jenis Kelamin: {member.jenis_kelamin or 'Tidak tersedia'}
- WhatsApp: {member.phone or 'Tidak tersedia'}
- Email: {member.email or 'Tidak tersedia'}
- Instagram: {member.instagram or 'Tidak tersedia'}
- Perusahaan: {member.nama_perusahaan or 'Tidak tersedia'}
- Jabatan di Perusahaan: {member.jabatan_dlm_akta_perusahaan or 'Tidak tersedia'}
- Bidang Usaha: {member.kategori_bidang_usaha or 'Tidak tersedia'}
- Jumlah Karyawan: {member.jmlh_karyawan or 'Tidak tersedia'}
""",
                "data": {
                    "name": member.name,
                    "jabatan": member.jabatan,
                    "status_kta": member.status_kta,
                    "usia": member.usia,
                    "jenis_kelamin": member.jenis_kelamin,
                    "whatsapp": member.phone,
                    "email": member.email,
                    "instagram": member.instagram,
                    "nama_perusahaan": member.nama_perusahaan,
                    "kategori_bidang_usaha": member.kategori_bidang_usaha,
                    "jmlh_karyawan": member.jmlh_karyawan,
                },
            }
    return None


# Handler 6: Kontak Pengurus
def handle_kontak_query(query_lower: str, db: Session) -> dict | None:
    """Handle query tentang kontak pengurus"""
    if not ("nomor" in query_lower or "wa" in query_lower or "whatsapp" in query_lower or "email" in query_lower or "kontak" in query_lower):
        return None
    
    name_match = re.search(r"['\"]([^'\"]+)['\"]", query_lower)
    if name_match:
        name = name_match.group(1)
        member = db.query(Member).filter(func.lower(Member.name).like(f"%{name.lower()}%")).first()
        if member:
            return {
                "type": "specific_query",
                "answer": f"**Kontak {member.name}:**\n- WhatsApp: {member.phone or 'Tidak tersedia'}\n- Email: {member.email or 'Tidak tersedia'}",
                "data": {"name": member.name, "whatsapp": member.phone, "email": member.email},
            }
    return None


# Handler 7: Perusahaan Pengurus
def handle_perusahaan_query(query_lower: str, db: Session) -> dict | None:
    """Handle query tentang perusahaan pengurus"""
    if not ("perusahaan" in query_lower and "nama" in query_lower):
        return None
    
    name_match = re.search(r"['\"]([^'\"]+)['\"]", query_lower)
    if name_match:
        name = name_match.group(1)
        member = db.query(Member).filter(func.lower(Member.name).like(f"%{name.lower()}%")).first()
        if member:
            return {
                "type": "specific_query",
                "answer": f"**Perusahaan {member.name}:**\n- Nama Perusahaan: {member.nama_perusahaan or 'Tidak tersedia'}\n- Jabatan: {member.jabatan_dlm_akta_perusahaan or 'Tidak tersedia'}\n- Bidang Usaha: {member.kategori_bidang_usaha or 'Tidak tersedia'}",
                "data": {
                    "name": member.name,
                    "nama_perusahaan": member.nama_perusahaan,
                    "jabatan_perusahaan": member.jabatan_dlm_akta_perusahaan,
                    "bidang_usaha": member.kategori_bidang_usaha,
                },
            }
    return None


# Handler 8: Total Karyawan
def handle_total_karyawan_query(query_lower: str, db: Session) -> dict | None:
    """Handle query tentang total karyawan"""
    if "total" in query_lower and "karyawan" in query_lower:
        total_karyawan = db.query(func.sum(Member.jmlh_karyawan)).scalar() or 0
        pengurus_count = db.query(Member).filter(Member.jmlh_karyawan.isnot(None)).count()
        return {
            "type": "specific_query",
            "answer": f"**Total Jumlah Karyawan:**\n- Total karyawan dari semua perusahaan pengurus: **{total_karyawan:,} karyawan**\n- Dari {pengurus_count} pengurus yang memiliki data karyawan",
            "data": {"total_karyawan": total_karyawan, "pengurus_with_data": pengurus_count},
        }
    return None


def detect_specific_query(query: str, db: Session) -> dict | None:
    """Deteksi dan jawab query spesifik dengan 8 handlers"""
    query_lower = query.lower()
    
    handlers = [
        handle_jabatan_query,
        lambda q, db: handle_bidang_usaha_query(q, db),
        lambda q, db: handle_kta_query(q, query, db),
        handle_gender_query,
        handle_detail_pengurus_query,
        handle_kontak_query,
        handle_perusahaan_query,
        handle_total_karyawan_query,
    ]
    
    for handler in handlers:
        result = handler(query_lower, db)
        if result:
            return result
    
    return None


def build_ai_context(db: Session) -> tuple:
    """Build context untuk AI dari database, return (context_string, members_count, docs_count)"""
    # Get data
    members = db.query(Member).all()
    documents = db.query(UniversalDocument).all()
    
    # Stats pengurus
    members_stats = {
        "total": len(members),
        "jabatan": {},
        "bidang_usaha": {},
        "status_kta": {},
        "gender": {"Male": 0, "Female": 0},
        "total_karyawan": 0,
    }
    
    members_list = []
    for m in members:
        # Count stats
        jabatan = m.jabatan or "Tidak Diketahui"
        members_stats["jabatan"][jabatan] = members_stats["jabatan"].get(jabatan, 0) + 1
        
        bidang = m.kategori_bidang_usaha or "Tidak Diketahui"
        members_stats["bidang_usaha"][bidang] = members_stats["bidang_usaha"].get(bidang, 0) + 1
        
        status = m.status_kta or "Tidak Diketahui"
        members_stats["status_kta"][status] = members_stats["status_kta"].get(status, 0) + 1
        
        if m.jenis_kelamin:
            members_stats["gender"][m.jenis_kelamin] = members_stats["gender"].get(m.jenis_kelamin, 0) + 1
        
        if m.jmlh_karyawan:
            members_stats["total_karyawan"] += m.jmlh_karyawan
        
        # Build member list untuk AI
        if m.name:
            member_info = f"- {m.name}"
            if m.jabatan:
                member_info += f" (Jabatan: {m.jabatan})"
            if m.nama_perusahaan:
                member_info += f", Perusahaan: {m.nama_perusahaan}"
            if m.kategori_bidang_usaha:
                member_info += f", Bidang: {m.kategori_bidang_usaha}"
            members_list.append(member_info)
    
    # Stats dokumen
    docs_stats = {"total": len(documents), "types": {}, "categories": {}}
    for doc in documents:
        dtype = doc.document_type or "Unknown"
        docs_stats["types"][dtype] = docs_stats["types"].get(dtype, 0) + 1
        
        cat = doc.category or "Tidak Dikategorikan"
        docs_stats["categories"][cat] = docs_stats["categories"].get(cat, 0) + 1
    
    # Build context string
    analytics_context = f"""=== DATA PENGURUS HIPMI ===

STATISTIK PENGURUS:
- Total Pengurus: {members_stats['total']}
- Total Karyawan (semua perusahaan): {members_stats['total_karyawan']:,}
- Gender: {members_stats['gender']['Male']} Pria, {members_stats['gender']['Female']} Wanita
- Distribusi Jabatan: {members_stats['jabatan']}
- Distribusi Bidang Usaha: {members_stats['bidang_usaha']}
- Status KTA: {members_stats['status_kta']}

DAFTAR PENGURUS:
{chr(10).join(members_list[:50])}  
{"... (dan " + str(len(members_list) - 50) + " pengurus lainnya)" if len(members_list) > 50 else ""}

DOKUMEN HIPMI:
- Total Dokumen: {docs_stats['total']}
- Tipe Dokumen: {docs_stats['types']}
- Kategori: {docs_stats['categories']}

===========================
"""
    
    # Add document contents
    context_parts = [analytics_context]
    all_docs = UniversalDocumentService.get_all_documents(db=db, limit=10)
    
    if all_docs:
        for doc in all_docs:
            if doc.full_text:
                # Classify document
                filename_lower = doc.filename.lower()
                doc_category = ""
                
                if "sejarah" in filename_lower:
                    doc_category = "Sejarah HIPMI"
                elif "visimisi" in filename_lower or "visi" in filename_lower:
                    doc_category = "Visi & Misi"
                elif "motto" in filename_lower:
                    doc_category = "Motto HIPMI"
                elif filename_lower == "ad.pdf" or "anggaran dasar" in filename_lower:
                    doc_category = "Anggaran Dasar (AD)"
                elif filename_lower == "art.pdf" or "anggaran rumah tangga" in filename_lower:
                    doc_category = "Anggaran Rumah Tangga (ART)"
                elif "po" in filename_lower:
                    po_num = re.search(r"po[_\-\s]?(\d+)", filename_lower)
                    doc_category = f"Peraturan Organisasi (PO{po_num.group(1)})" if po_num else "Peraturan Organisasi (PO)"
                else:
                    doc_category = doc.document_type or "Dokumen"
                
                context_parts.append(f"[{doc_category}: {doc.filename}]\n{doc.full_text[:3000]}\n")
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Limit context size
    if len(context) > 25000:
        context = context[:25000] + "\n\n[Context truncated...]"
    
    return context, len(members), len(documents)


@router.post("/query")
async def chat_query(request: ChatQuerySchema, db: Session = Depends(get_db)):
    """Endpoint chatbot AI dengan deteksi query spesifik + knowledge base"""
    try:
        # Step 1: Check specific queries (fast path)
        specific_result = detect_specific_query(request.query, db)
        if specific_result:
            return {
                "status": "success",
                "query": request.query,
                "response": specific_result["answer"],
                "source": "Direct Database Query",
                "query_type": "specific",
                "data": specific_result.get("data", {}),
            }
        
        # Step 2: Build context untuk AI
        context = request.context or ""
        members_count = 0
        docs_count = 0
        
        if not context:
            context, members_count, docs_count = build_ai_context(db)
        
        # Step 3: Call Gemini AI
        gemini = GeminiService()
        enhanced_query = f"""Berdasarkan data HIPMI (pengurus, dokumen organisasi, dan peraturan) yang tersedia, jawab pertanyaan berikut:

Pertanyaan: {request.query}

Instruksi:
- Gunakan DAFTAR PENGURUS untuk pertanyaan tentang nama, jabatan, perusahaan pengurus tertentu
- Contoh: "Ibrahim jabatannya apa?" → cari di daftar pengurus nama "Ibrahim"
- Gunakan data statistik untuk pertanyaan tentang angka/jumlah
- Gunakan isi dokumen untuk pertanyaan tentang peraturan, sejarah, visi/misi, dll
- Jika informasi tidak tersedia, katakan "Saya tidak memiliki informasi tersebut dalam database"
- Sebutkan sumber data jika memungkinkan (nama pengurus/file/dokumen)
- Jawab dalam Bahasa Indonesia yang profesional dan jelas
- Untuk pertanyaan tentang PO (Peraturan Organisasi), sebutkan nomor PO-nya
- Untuk nama pengurus, gunakan nama lengkap yang ada di daftar
"""
        
        response = gemini.answer_question(enhanced_query, context)
        
        return {
            "status": "success",
            "query": request.query,
            "response": response,
            "source": "HIPMI Knowledge Base + AI Analytics",
            "query_type": "general",
            "members_count": members_count,
            "documents_count": docs_count,
            "context_size": len(context),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat query failed: {str(e)}")


@router.get("/context")
async def get_chat_context(db: Session = Depends(get_db)):
    """Get AI context summary untuk debugging"""
    try:
        context, members_count, docs_count = build_ai_context(db)
        return {
            "status": "success",
            "members_count": members_count,
            "documents_count": docs_count,
            "context_length": len(context),
            "context_preview": context[:500] + "..." if len(context) > 500 else context,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get context: {str(e)}")
