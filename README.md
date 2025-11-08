# 🚀 Kintari Backend - HIPMI Knowledge Base API

**FastAPI Backend for HIPMI Knowledge Intelligence Repository & Assistant**

Backend API yang powerful untuk mengelola data pengurus HIPMI, dokumen organisasi, dan menyediakan AI chatbot yang cerdas dengan Gemini AI.

---

## ✨ Fitur Utama

| Fitur                      | Deskripsi                                              |
| -------------------------- | ------------------------------------------------------ |
| � **Pengurus Management**  | Upload CSV, CRUD operations, analytics                 |
| 📄 **Document Processing** | Upload PDF/DOCX, auto-extract, auto-categorize         |
| 🤖 **AI Chatbot**          | Gemini AI dengan context dari data pengurus & dokumen  |
| 📊 **Analytics**           | 4 visualisasi (usia, gender, bidang usaha, perusahaan) |
| 🔍 **Smart Search**        | Full-text search di pengurus & dokumen                 |
| 📈 **Statistics**          | Real-time insights dan trends                          |

---

## 📋 Tech Stack

```
Framework      : FastAPI 0.104.1
Database       : SQLite (dev) / PostgreSQL ready
ORM            : SQLAlchemy 2.x
AI Engine      : Google Gemini (gemini-2.0-flash-exp)
PDF Processing : pdfplumber + PyMuPDF
Python         : 3.11+
CORS           : Enabled untuk frontend (localhost:3000)
```

---

## ⚙️ Instalasi

### 1️⃣ **Prerequisites**

- Python 3.11+ ([Download](https://www.python.org/downloads/))
- pip (package manager)
- Git
- Gemini API Key ([Get Free Key](https://makersuite.google.com/app/apikey))

### 2️⃣ **Clone & Setup Virtual Environment**

```bash
# Clone repository
git clone https://github.com/Sastraaaa/kintari-be.git
cd kintari-be

# Buat virtual environment
python -m venv venv

# Aktivasi virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows CMD:
venv\Scripts\activate.bat

# Linux/Mac:
source venv/bin/activate
```

### 3️⃣ **Install Dependencies**

```bash
pip install -r requirements.txt
```

**Dependencies utama:**

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM
- `google-generativeai` - Gemini AI
- `pdfplumber` - PDF extraction
- `python-multipart` - File upload
- `python-dotenv` - Environment variables

### 4️⃣ **Configure Environment**

Buat file `.env` di root folder:

```env
# Database
DATABASE_URL=sqlite:///./kintari.db

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Upload Directory
UPLOAD_DIR=./uploads

# Optional: Production Settings
# DATABASE_URL=postgresql://user:password@localhost/kintari
# ENVIRONMENT=production
```

**⚠️ IMPORTANT:** Dapatkan Gemini API Key gratis di [Google AI Studio](https://makersuite.google.com/app/apikey)

### 5️⃣ **Initialize Database**

```bash
python init_fresh_db.py
```

**Output:**

```
🔄 Creating fresh database for Kintari - HIPMI Knowledge System...
✅ All tables dropped
✅ All tables created
📊 Database tables created:
  ✅ members (31 columns)
  ✅ universal_documents (24 columns)
  ✅ organization_info
  ...
💾 Database file: kintari.db
✅ Ready to accept data!
```

### 6️⃣ **Run Development Server**

```bash
uvicorn app.main:app --reload --port 8000
```

**Output:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Server berjalan di: **http://localhost:8000**

---

## 📚 API Documentation

Setelah server running, akses dokumentasi interaktif:

- **Swagger UI** (Recommended): http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔌 API Endpoints

### � **Pengurus Management**

| Method   | Endpoint                  | Deskripsi                |
| -------- | ------------------------- | ------------------------ |
| `POST`   | `/api/members/upload-csv` | Upload CSV data pengurus |
| `GET`    | `/api/members`            | List semua pengurus      |
| `GET`    | `/api/members/{id}`       | Get pengurus by ID       |
| `PUT`    | `/api/members/{id}`       | Update data pengurus     |
| `DELETE` | `/api/members/{id}`       | Hapus pengurus           |

**CSV Format:**

```csv
no,nama,jabatan,status_kta,usia,jenis_kelamin,whatsapp,email,kategori_bidang_usaha,nama_perusahaan,jmlh_karyawan
1,Ibrahim,Ketum,KTA Fisik,35,Male,08xxx,email,IT,PT ABC,100
```

### 📄 **Document Management**

| Method   | Endpoint                         | Deskripsi          |
| -------- | -------------------------------- | ------------------ |
| `POST`   | `/api/documents/upload`          | Upload PDF/DOCX    |
| `GET`    | `/api/documents`                 | List semua dokumen |
| `GET`    | `/api/documents/{id}`            | Get detail dokumen |
| `DELETE` | `/api/documents/{id}`            | Hapus dokumen      |
| `GET`    | `/api/documents/search/?q=query` | Search dokumen     |

### 📊 **Analytics**

| Method | Endpoint                 | Deskripsi                          |
| ------ | ------------------------ | ---------------------------------- |
| `GET`  | `/api/analytics/members` | Analytics pengurus (4 visualisasi) |
| `GET`  | `/api/stats/overview`    | Statistics overview                |

**Response Analytics:**

```json
{
  "status": "success",
  "statistics": {
    "total_pengurus": 134,
    "by_jabatan": {"Ketum": 1, "WKU": 1, ...},
    "by_bidang_usaha": {"IT": 15, "Property": 20, ...},
    "by_status_kta": {"KTA Fisik": 50, "HIPMI NET": 30, ...},
    "total_karyawan": 2500
  },
  "visualizations": {
    "age_distribution": [...],
    "gender_proportion": [...],
    "by_business_category": [...],
    "company_ownership": [...]
  }
}
```

### 🤖 **AI Chatbot**

| Method | Endpoint            | Deskripsi              |
| ------ | ------------------- | ---------------------- |
| `POST` | `/api/chat/query`   | Kirim query ke AI      |
| `GET`  | `/api/chat/context` | Get current AI context |

**Request:**

```json
{
  "query": "Ibrahim jabatannya apa?"
}
```

**Response:**

```json
{
  "status": "success",
  "query": "Ibrahim jabatannya apa?",
  "response": "Ibrahim Imaduddin Islam menjabat sebagai Ketua Umum (Ketum) di HIPMI.",
  "source": "HIPMI Knowledge Base + AI Analytics",
  "query_type": "specific_query"
}
```

---

## 🚀 Penggunaan

### **1. Upload Data Pengurus (CSV)**

```bash
curl -X POST "http://localhost:8000/api/members/upload-csv" \
  -F "file=@pengurus.csv"
```

### **2. Upload Dokumen HIPMI (PDF)**

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@AD_HIPMI.pdf" \
  -F "category=Anggaran Dasar"
```

### **3. Get Analytics Data**

```bash
curl "http://localhost:8000/api/analytics/members"
```

### **4. Ask AI Chatbot**

```bash
curl -X POST "http://localhost:8000/api/chat/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Siapa ketua bidang 1?"}'
```

### **5. Search Pengurus**

```bash
curl "http://localhost:8000/api/members?search=ibrahim"
```

---

## 🗂️ Project Structure

```
kintari-be/
├── app/
│   ├── main.py                     # FastAPI application
│   ├── core/
│   │   ├── config.py              # Configuration
│   │   ├── database.py            # Database setup
│   │   └── utils.py               # Utility functions
│   ├── models/
│   │   ├── member.py              # Member/Pengurus model (31 fields)
│   │   ├── universal_document.py  # Document model
│   │   └── organization.py        # Organization model
│   ├── routes/
│   │   ├── members.py             # Pengurus endpoints
│   │   ├── documents.py           # Document endpoints
│   │   ├── chat.py                # AI Chatbot endpoints
│   │   ├── analytics.py           # Analytics endpoints
│   │   └── stats.py               # Statistics endpoints
│   ├── schemas/
│   │   ├── member_schema.py       # Pydantic schemas
│   │   ├── chat_schema.py
│   │   └── organization_schema.py
│   └── services/
│       ├── gemini_service.py      # Gemini AI integration
│       ├── pdf_extractor.py       # PDF processing
│       └── universal_document_service.py
├── uploads/                        # Uploaded files storage
├── tests/                          # Unit tests
├── init_fresh_db.py               # Database initialization
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables
└── README.md                      # This file
```

│ ├── main.py # FastAPI app entry point
│ ├── core/
│ │ ├── config.py # Environment & configuration
│ │ ├── database.py # SQLAlchemy setup
│ │ └── utils.py # Utility functions
│ ├── models/
│ │ ├── universal_document.py # ⭐ NEW: Universal document models
│ │ ├── organization.py # Organization models (legacy HIPMI)
│ │ └── member.py # Member model
│ ├── schemas/ # Pydantic validation schemas
│ ├── routes/
│ │ ├── universal_documents.py # ⭐ NEW: 16 endpoints for universal KB
│ │ ├── chat.py # ⭐ UPDATED: Multi-doc AI chatbot
│ │ ├── members.py # Members endpoints
│ │ ├── stats.py # Statistics endpoints
│ │ └── organization.py # Legacy HIPMI endpoints
│ └── services/
│ ├── universal_document_processor.py # ⭐ NEW: Extract ANY PDF
│ ├── universal_document_service.py # ⭐ NEW: Business logic
│ ├── pdf_extractor.py # Legacy HIPMI extractor
│ └── gemini_service.py # Gemini AI integration
├── init_fresh_db.py # Database initialization script
├── requirements.txt # Python dependencies
├── .env # Environment variables (gitignored)
├── .env.example # Template .env
├── kintari.db # SQLite database (auto-created)
└── README.md # This file

````

## �️ Database Schema

### Main Tables (7 total):

| Table                    | Description                                  |
| ------------------------ | -------------------------------------------- |
| `universal_documents`    | ⭐ Stores ANY uploaded PDF with full content |
| `document_collections`   | ⭐ Groups related documents together         |
| `organization_info`      | HIPMI organization data (legacy)             |
| `organization_structure` | Organizational hierarchy                     |
| `membership_types`       | Membership categories                        |
| `members`                | Member information                           |
| `documents`              | Legacy document tracking                     |

### Universal Document Model (25+ fields):

```python
{
  "id": 1,
  "filename": "contract.pdf",
  "file_path": "uploads/contract.pdf",
  "file_size": 1024000,
  "page_count": 50,
  "full_text": "Extracted full text content...",
  "summary": "Auto-generated summary...",
  "extracted_entities": {
    "emails": [...],
    "dates": [...],
    "phones": [...]
  },
  "keywords": ["keyword1", "keyword2"],
  "tables_data": [...],
  "document_type": "CONTRACT",
  "category": "Legal",
  "tags": ["important", "2024"],
  "ai_summary": "AI-generated insights...",
  "processed": true,
  "uploaded_at": "2024-01-01T00:00:00"
}
````

---

## 📊 Database Schema

### **Main Tables:**

| Table                    | Description            | Columns                                                                                                                    |
| ------------------------ | ---------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `members`                | Data pengurus HIPMI    | 31 fields (no, name, jabatan, status_kta, usia, jenis_kelamin, kategori_bidang_usaha, nama_perusahaan, jmlh_karyawan, dll) |
| `universal_documents`    | Dokumen PDF/DOCX HIPMI | 24 fields (filename, full_text, summary, keywords, document_type, dll)                                                     |
| `document_collections`   | Grouping dokumen       | 8 fields                                                                                                                   |
| `organization_info`      | Info organisasi HIPMI  | 10 fields                                                                                                                  |
| `membership_types`       | Tipe keanggotaan       | 7 fields                                                                                                                   |
| `organization_structure` | Struktur organisasi    | 8 fields                                                                                                                   |

### **Member Model (31 Fields):**

```python
{
  "id": 1,
  "no": 1,
  "name": "Ibrahim Imaduddin Islam",
  "jabatan": "Ketum",
  "status_kta": "KTA Fisik",
  "no_kta": "1319-1890-0002-4190",
  "tanggal_lahir": "16-03-1990",
  "usia": 35,
  "jenis_kelamin": "Male",
  "phone": "082127712571",
  "email": "ibrahim@email.com",
  "instagram": "ibrahim_ig",
  "nama_perusahaan": "PT. Mavens Studio Indonesia",
  "jabatan_dlm_akta_perusahaan": "Direktur Utama",
  "kategori_bidang_usaha": "Industri Kreatif",
  "alamat_perusahaan": "Jl. Guntur Sari Kulon No.19",
  "perusahaan_berdiri_sejak": "2015",
  "jmlh_karyawan": 100,
  "website": "mavens.co.id",
  "twitter": "@mavens",
  "facebook": "mavens",
  "youtube": "mavensstudio"
}
```

---

## 🤖 AI Chatbot Features

### **Query Types yang Didukung:**

**1. Statistik Jabatan:**

```
"Ada berapa orang Ketua Bidang?"
"Jumlah pengurus per jabatan?"
```

**2. Statistik Bidang Usaha:**

```
"Bidang usaha apa yang paling banyak?"
"Ada berapa pengurus di bidang Property?"
```

**3. Statistik Status KTA:**

```
"Berapa pengurus yang KTA-nya Hilang?"
"Tampilkan status KTA semua pengurus"
```

**4. Statistik Gender:**

```
"Berapa rasio pengurus pria dan wanita?"
```

**5. Pencarian Detail Pengurus:**

```
"Cari info lengkap Ibrahim"
"Ibrahim jabatannya apa?"  // Natural query!
"Siapa Ibrahim?"
```

**6. Pencarian Kontak:**

```
"Minta nomor WA Ibrahim"
"Email Rangga berapa?"
```

**7. Pencarian Perusahaan:**

```
"Apa nama perusahaan Archy?"
```

**8. Total Karyawan:**

```
"Berapa total jumlah karyawan dari semua pengurus?"
```

**9. Tentang Dokumen HIPMI:**

```
"Kapan HIPMI didirikan?"
"Apa visi dan misi HIPMI?"
"Berapa batas usia anggota biasa?"
```

### **AI Context:**

- **Daftar Pengurus** - 50 pengurus pertama dengan nama, jabatan, perusahaan
- **Statistik** - Total pengurus, gender ratio, distribusi jabatan/bidang usaha
- **Dokumen** - Full text dari semua dokumen yang diupload (AD, ART, PO, dll)

---

## 🎨 Supported Document Types

Backend otomatis mendeteksi 12 tipe dokumen:

| Type             | Description           | Example                   |
| ---------------- | --------------------- | ------------------------- |
| `HIPMI_AD`       | Anggaran Dasar        | AD.pdf                    |
| `HIPMI_ART`      | Anggaran Rumah Tangga | ART.pdf                   |
| `HIPMI_PO`       | Peraturan Organisasi  | PO1.pdf - PO18.pdf        |
| `HIPMI_SK`       | Surat Keputusan       | SK_001.pdf                |
| `HIPMI_DOCUMENT` | Dokumen HIPMI lainnya | Sejarah.pdf, VisiMisi.pdf |
| `CONTRACT`       | Kontrak               | kontrak_vendor.pdf        |
| `REPORT`         | Laporan               | laporan_keuangan.pdf      |
| `PROPOSAL`       | Proposal              | proposal_project.pdf      |
| `PRESENTATION`   | Presentasi            | slide_meeting.pdf         |
| `REGULATION`     | Peraturan             | peraturan_pemerintah.pdf  |
| `MANUAL`         | Manual                | user_manual.pdf           |
| `OTHER`          | Lainnya               | document.pdf              |

---

## 🐛 Troubleshooting

### ❌ **Error: ModuleNotFoundError**

**Solusi:**

```bash
# Pastikan virtual environment aktif
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### ❌ **Error: GEMINI_API_KEY not set**

**Solusi:**

1. Buat file `.env` di root folder
2. Tambahkan: `GEMINI_API_KEY=your_api_key_here`
3. Get free API key: https://makersuite.google.com/app/apikey

### ❌ **Error: Database locked**

**Solusi:**

```bash
# Stop all backend processes
taskkill /F /IM python.exe

# Delete database dan recreate
del kintari.db
python init_fresh_db.py
```

### ❌ **Error: Port 8000 already in use**

**Solusi:**

```bash
# Windows: Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID [PID_NUMBER] /F

# Run on different port
uvicorn app.main:app --reload --port 8001
```

### ❌ **CSV Upload failed: Header mismatch**

**Solusi:**

- Pastikan header CSV exact match: `no,nama,jabatan,status_kta,...`
- Hapus spasi di header (contoh: `nama ` → `nama`)
- Encoding harus UTF-8
- Gunakan koma sebagai delimiter

---

## 🧪 Testing

### **Manual Testing:**

```bash
# Health check
curl http://localhost:8000/

# Test members endpoint
curl http://localhost:8000/api/members

# Test analytics
curl http://localhost:8000/api/analytics/members

# Test chatbot
curl -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Test query"}'
```

### **Run Unit Tests:**

```bash
# Install pytest
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

---

## 🚢 Production Deployment

### **1. Update Environment**

```env
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@host:5432/kintari
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### **2. Use Production Database**

```bash
# Migrate to PostgreSQL
pip install psycopg2-binary

# Update DATABASE_URL in .env
# Run migrations
python init_fresh_db.py
```

### **3. Run with Gunicorn**

```bash
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### **4. Deploy Options:**

- **Docker** - Containerize dengan Dockerfile
- **AWS** - Deploy ke EC2 / ECS / Lambda
- **Heroku** - One-click deploy
- **Railway** - Modern deployment platform
- **VPS** - DigitalOcean, Linode, Vultr

---

## 📝 Development Tips

1. **Use Swagger UI** - Test endpoints interaktif di `/docs`
2. **Database Browser** - Install DB Browser for SQLite
3. **Hot Reload** - `--reload` flag untuk auto-restart
4. **Logging** - Check console untuk debug info
5. **CORS** - Update `ALLOWED_ORIGINS` untuk frontend URL baru

---

## 🔒 Security Notes

- ✅ CORS configured untuk localhost:3000
- ✅ File upload validation (PDF/DOCX only, max 10MB)
- ✅ SQL injection protected (SQLAlchemy ORM)
- ⚠️ **TODO**: Add authentication (JWT tokens)
- ⚠️ **TODO**: Add rate limiting
- ⚠️ **TODO**: Add file encryption for sensitive documents

---

## 📄 License

MIT License - Free to use for HIPMI projects

---

## 🤝 Support & Contributing

- **Issues**: [GitHub Issues](https://github.com/Sastraaaa/kintari-be/issues)
- **Frontend**: Lihat README di `kintari-ai/` folder
- **API Docs**: http://localhost:8000/docs (when server running)
- **Contact**: Hubungi maintainer untuk support

---

## 🎯 Roadmap

- [x] Member/Pengurus management with 31 fields
- [x] CSV upload with auto-trim headers
- [x] Analytics dengan 4 visualisasi (usia, gender, bidang usaha, perusahaan)
- [x] AI Chatbot dengan Gemini (8+ query types)
- [x] Natural language query (tanpa kutip)
- [x] Document upload & processing
- [x] Full-text search
- [ ] Authentication & Authorization (JWT)
- [ ] Real-time notifications (WebSocket)
- [ ] Export to Excel/PDF
- [ ] Email notifications
- [ ] Advanced analytics & ML predictions

---

**Built with ❤️ for HIPMI Bandung**

**Tech Stack:** FastAPI + SQLAlchemy + Gemini AI + Python 3.11+

## 🤖 How It Works

```
1️⃣ Upload ANY PDF document
       ↓
2️⃣ Auto Extract Content:
   • Full text (all pages)
   • Tables with structure
   • Emails, dates, phones, URLs
   • Keywords (top 20)
       ↓
3️⃣ Auto Detect Type (12 types)
       ↓
4️⃣ Save to Database (with rich metadata)
       ↓
5️⃣ AI Chatbot uses ALL documents as knowledge base
       ↓
6️⃣ Ask questions → Get intelligent answers!
```

**Example Extraction Result:**

- **Input**: 8.62 MB PDF (323 pages)
- **Extracted**: 497,634 characters
- **Found**: 160 dates, 35 emails, 62 phone numbers, 50 tables
- **Keywords**: 20 auto-generated
- **Processing Time**: ~15 seconds

## 🐛 Troubleshooting

| Issue                      | Solution                                           |
| -------------------------- | -------------------------------------------------- |
| `ModuleNotFoundError`      | Pastikan venv aktif: `.\venv\Scripts\Activate.ps1` |
| `Database locked`          | Hapus `kintari.db`, run `python init_fresh_db.py`  |
| `GEMINI_API_KEY not found` | Set di `.env`: `GEMINI_API_KEY=your_key`           |
| Port 8000 sudah terpakai   | Gunakan: `uvicorn app.main:app --port 8001`        |
| Upload gagal               | Cek folder `uploads/` exists & permissions         |

## � Production Deployment

```bash
# Install production server
pip install gunicorn

# Run with gunicorn (4 workers)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Production Checklist:**

- ✅ Migrate to PostgreSQL
- ✅ Setup HTTPS/SSL
- ✅ Configure CORS properly
- ✅ Setup monitoring (logs, metrics)
- ✅ Backup database regularly
- ✅ Rate limiting for API endpoints

## 🤝 Integration dengan Frontend

Frontend Next.js dapat mengakses backend di:

- **Development**: `http://localhost:8000`
- **Production**: Configure `ALLOWED_ORIGINS` di `.env`

**Example Frontend Integration:**

```typescript
// Upload document
const formData = new FormData();
formData.append("file", file);
formData.append("category", "Contracts");

const response = await fetch("http://localhost:8000/api/documents/upload", {
  method: "POST",
  body: formData,
});

// AI Chatbot query
const chatResponse = await fetch("http://localhost:8000/api/chat/query", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ query: "What is HIPMI vision?" }),
});
```

## � Features Comparison

| Feature                 | Old System (HIPMI-only) | New System (Universal KB)      |
| ----------------------- | ----------------------- | ------------------------------ |
| Supported Documents     | HIPMI only              | **ANY PDF** ✅                 |
| Auto Content Extraction | Basic                   | **Rich (25+ fields)** ✅       |
| Entity Detection        | ❌                      | **✅ (emails, dates, phones)** |
| Document Type Detection | Manual                  | **Auto (12 types)** ✅         |
| AI Chatbot Context      | Single document         | **Multi-document** ✅          |
| Full-text Search        | ❌                      | **✅**                         |
| Document Collections    | ❌                      | **✅**                         |
| Analytics & Statistics  | Basic                   | **Advanced** ✅                |

---

**🎉 Ready to use! Upload any document and start asking AI questions!**

**Last Updated**: January 2025 | **Version**: 2.0.0 (Universal KB)
#
