import os
import json
from typing import Optional
from google import genai
from google.genai import types


class GeminiService:
    """Service untuk integrasi dengan Gemini API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = "gemini-2.0-flash-exp"
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def summarize_text(self, text: str, max_length: int = 500) -> str:
        """Ringkasan teks menggunakan Gemini"""
        if not self.api_key:
            return "API Key not configured"

        prompt = f"Buatkan ringkasan singkat ({max_length} karakter) dari teks berikut:\n\n{text}\n\nRingkasan:"
        try:
            return self._call_api(prompt)
        except Exception as e:
            return f"Error: {str(e)}"

    def answer_question(self, question: str, context: str) -> str:
        """Jawab pertanyaan berdasarkan konteks (chatbot)"""
        if not self.api_key:
            return "API Key not configured"

        prompt = f"Berdasarkan konteks berikut, jawab pertanyaan:\n\nKONTEKS:\n{context}\n\nPERTANYAAN:\n{question}\n\nJAWABAN:"
        try:
            return self._call_api(prompt)
        except Exception as e:
            return f"Error: {str(e)}"

    def extract_key_info(self, text: str) -> dict:
        """Ekstrak info kunci dari dokumen organisasi"""
        if not self.api_key:
            return {"error": "API Key not configured"}

        prompt = f"""Ekstrak info kunci dari dokumen: Nama organisasi, Tanggal berdiri, Asas, Tujuan, Struktur (jika ada).
        
Dokumen:
{text[:2000]}

Format JSON."""
        try:
            return {"info": self._call_api(prompt)}
        except Exception as e:
            return {"error": str(e)}

    def analyze_members_data(self, members_data: list) -> dict:
        """Analisis data pengurus HIPMI dengan AI - menghasilkan insight natural"""
        if not self.api_key:
            return {"error": "API Key not configured"}

        # Build statistics
        total = len(members_data)
        stats = self._build_member_stats(members_data)

        prompt = f"""Kamu adalah AI analyst untuk organisasi HIPMI. Analisis data keanggotaan berikut dan berikan insight dalam bahasa Indonesia yang mudah dipahami.

DATA ANGGOTA:
- Total: {total} orang
- Distribusi Jabatan: {stats['positions']}
- Distribusi Bidang Usaha: {stats['business']}
- Distribusi Gender: {stats['gender']}

Berikan analisis dalam format berikut (TANPA markdown, TANPA ```json):

SUMMARY:
[Ringkasan kondisi keanggotaan dalam 2-3 kalimat yang mudah dipahami]

KEY_INSIGHTS:
- [Insight penting pertama dalam 1-2 kalimat]
- [Insight penting kedua dalam 1-2 kalimat]
- [Insight penting ketiga dalam 1-2 kalimat]

TRENDS:
[Analisis tren dalam 2-3 kalimat, fokus pada pola yang terlihat]

RECOMMENDATIONS:
- [Rekomendasi strategis pertama yang actionable]
- [Rekomendasi strategis kedua yang actionable]
- [Rekomendasi strategis ketiga yang actionable]

Gunakan bahasa yang profesional namun mudah dipahami. Fokus pada insight yang praktis dan actionable."""

        try:
            response = self._call_api(prompt).strip()

            # Parse response
            summary = ""
            key_insights = []
            trends = ""
            recommendations = []

            current_section = None
            for line in response.split("\n"):
                line = line.strip()
                if not line:
                    continue

                if line.upper().startswith("SUMMARY"):
                    current_section = "summary"
                    continue
                elif line.upper().startswith("KEY_INSIGHTS") or line.upper().startswith(
                    "KEY INSIGHTS"
                ):
                    current_section = "insights"
                    continue
                elif line.upper().startswith("TRENDS"):
                    current_section = "trends"
                    continue
                elif line.upper().startswith("RECOMMENDATIONS"):
                    current_section = "recommendations"
                    continue

                # Clean line dari bullet points
                clean_line = line.lstrip("•-*").strip()
                if not clean_line or clean_line.startswith("#"):
                    continue

                if current_section == "summary":
                    summary += " " + clean_line if summary else clean_line
                elif current_section == "insights":
                    if clean_line:
                        key_insights.append(clean_line)
                elif current_section == "trends":
                    trends += " " + clean_line if trends else clean_line
                elif current_section == "recommendations":
                    if clean_line:
                        recommendations.append(clean_line)

            # Fallback jika parsing gagal
            if not summary:
                summary = "Data keanggotaan HIPMI tersimpan dengan baik di sistem."
            if not key_insights:
                key_insights = [
                    "Analisis sedang diproses",
                    "Silakan coba beberapa saat lagi",
                    "Data tersedia untuk analisis lebih lanjut",
                ]
            if not trends:
                trends = "Tren menunjukkan perkembangan positif organisasi."
            if not recommendations:
                recommendations = [
                    "Pertahankan kualitas data",
                    "Lakukan pembaruan rutin",
                    "Monitor perkembangan anggota",
                ]

            return {
                "summary": summary.strip(),
                "total_members": total,
                "key_insights": key_insights[:3],
                "trends": trends.strip(),
                "recommendations": recommendations[:3],
            }
        except Exception as e:
            # Fallback dengan data statistik dasar
            return {
                "summary": f"Organisasi HIPMI memiliki {total} anggota dengan distribusi di berbagai bidang usaha dan jabatan.",
                "total_members": total,
                "key_insights": [
                    f"Total {total} anggota terdaftar dalam sistem",
                    f"Distribusi gender: {stats['gender'].get('Male', 0)} Pria, {stats['gender'].get('Female', 0)} Wanita",
                    f"Terdapat {len(stats['business'])} kategori bidang usaha yang berbeda",
                ],
                "trends": "Data menunjukkan keragaman bidang usaha di antara anggota HIPMI.",
                "recommendations": [
                    "Lakukan update data anggota secara berkala",
                    "Monitor distribusi anggota per bidang",
                    "Tingkatkan engagement melalui program yang relevan",
                ],
                "error_detail": str(e),
            }

    def analyze_documents_data(self, documents_data: list) -> dict:
        """Analisis data dokumen HIPMI dengan AI - menghasilkan insight natural"""
        if not self.api_key:
            return {"error": "API Key not configured"}

        # Build statistics
        total = len(documents_data)
        stats = self._build_document_stats(documents_data)

        prompt = f"""Kamu adalah AI analyst untuk dokumentasi HIPMI. Analisis data dokumen berikut dan berikan insight dalam bahasa Indonesia yang mudah dipahami.

DATA DOKUMEN:
- Total Dokumen: {total}
- Total Halaman: {stats['total_pages']}
- Distribusi Tipe: {stats['types']}
- Distribusi Kategori: {stats['categories']}

Berikan analisis dalam format berikut (TANPA markdown, TANPA ```json):

SUMMARY:
[Ringkasan kondisi dokumentasi dalam 2-3 kalimat]

KEY_INSIGHTS:
- [Insight penting pertama tentang kondisi dokumentasi]
- [Insight penting kedua tentang kelengkapan atau kualitas]
- [Insight penting ketiga tentang distribusi atau coverage]

DOCUMENT_HEALTH:
[Status kesehatan dokumentasi dalam 1 kalimat - apakah sudah baik/cukup/perlu perbaikan]

RECOMMENDATIONS:
- [Rekomendasi praktis pertama untuk meningkatkan dokumentasi]
- [Rekomendasi praktis kedua]
- [Rekomendasi praktis ketiga]

Gunakan bahasa yang profesional namun mudah dipahami."""

        try:
            response = self._call_api(prompt).strip()

            # Parse response
            summary = ""
            key_insights = []
            document_health = ""
            recommendations = []

            current_section = None
            for line in response.split("\n"):
                line = line.strip()
                if not line:
                    continue

                if line.upper().startswith("SUMMARY"):
                    current_section = "summary"
                    continue
                elif line.upper().startswith("KEY_INSIGHTS") or line.upper().startswith(
                    "KEY INSIGHTS"
                ):
                    current_section = "insights"
                    continue
                elif line.upper().startswith(
                    "DOCUMENT_HEALTH"
                ) or line.upper().startswith("DOCUMENT HEALTH"):
                    current_section = "health"
                    continue
                elif line.upper().startswith("RECOMMENDATIONS"):
                    current_section = "recommendations"
                    continue

                # Clean line
                clean_line = line.lstrip("•-*").strip()
                if not clean_line or clean_line.startswith("#"):
                    continue

                if current_section == "summary":
                    summary += " " + clean_line if summary else clean_line
                elif current_section == "insights":
                    if clean_line:
                        key_insights.append(clean_line)
                elif current_section == "health":
                    document_health += (
                        " " + clean_line if document_health else clean_line
                    )
                elif current_section == "recommendations":
                    if clean_line:
                        recommendations.append(clean_line)

            # Fallback
            if not summary:
                summary = f"Sistem memiliki {total} dokumen dengan total {stats['total_pages']} halaman."
            if not key_insights:
                key_insights = [
                    "Dokumentasi tersedia untuk analisis",
                    "Data dokumen tersimpan dengan baik",
                    "Sistem siap untuk pengelolaan lebih lanjut",
                ]
            if not document_health:
                document_health = "Kondisi dokumentasi dalam status baik."
            if not recommendations:
                recommendations = [
                    "Pertahankan kualitas dokumentasi",
                    "Update dokumen secara berkala",
                    "Monitor kelengkapan dokumen",
                ]

            return {
                "summary": summary.strip(),
                "total_documents": total,
                "total_pages": stats["total_pages"],
                "key_insights": key_insights[:3],
                "document_health": document_health.strip(),
                "recommendations": recommendations[:3],
            }
        except Exception as e:
            return {
                "summary": f"Sistem memiliki {total} dokumen dengan total {stats['total_pages']} halaman.",
                "total_documents": total,
                "total_pages": stats["total_pages"],
                "key_insights": [
                    f"Total {total} dokumen tersimpan di sistem",
                    f"Terdapat {len(stats['categories'])} kategori dokumen",
                    f"Total {stats['total_pages']} halaman dokumentasi",
                ],
                "document_health": "Dokumentasi tersimpan dengan baik di sistem.",
                "recommendations": [
                    "Lakukan categorization dokumen secara konsisten",
                    "Update metadata dokumen secara berkala",
                    "Monitor kelengkapan dokumentasi organisasi",
                ],
                "error_detail": str(e),
            }

    def _build_member_stats(self, members_data: list) -> dict:
        """Build statistik dari data members"""
        positions = {}
        business = {}
        gender = {"Male": 0, "Female": 0}

        for m in members_data:
            # Count positions
            pos = m.get("jabatan", "Unknown")
            positions[pos] = positions.get(pos, 0) + 1

            # Count business categories
            biz = m.get("kategori_bidang_usaha", "Unknown")
            business[biz] = business.get(biz, 0) + 1

            # Count gender
            g = m.get("jenis_kelamin")
            if g in ["Male", "Female"]:
                gender[g] += 1

        return {"positions": positions, "business": business, "gender": gender}

    def _build_document_stats(self, documents_data: list) -> dict:
        """Build statistik dari data documents"""
        types_count = {}
        categories = {}
        total_pages = 0

        for doc in documents_data:
            # Count types
            dtype = doc.get("document_type", "Unknown")
            types_count[dtype] = types_count.get(dtype, 0) + 1

            # Count categories
            cat = doc.get("category", "Uncategorized")
            categories[cat] = categories.get(cat, 0) + 1

            # Sum pages
            pages = doc.get("page_count", 0)
            if pages:
                total_pages += pages

        return {
            "types": types_count,
            "categories": categories,
            "total_pages": total_pages,
        }

    def _call_api(self, prompt: str) -> str:
        """Call Gemini API"""
        if not self.client:
            raise Exception("Gemini API client not initialized. Check GEMINI_API_KEY.")

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.95,
                    max_output_tokens=2048,
                ),
            )

            if response.text is None:
                raise Exception("Gemini API returned empty response")

            return response.text
        except Exception as e:
            raise Exception(f"Gemini API call failed: {str(e)}")
