from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.member import Member
import csv
import io

router = APIRouter(prefix="/api/members", tags=["members"])


def parse_int_field(value: str) -> int | None:
    """Parse string ke integer, return None jika gagal"""
    if not value:
        return None
    try:
        val = value.strip()
        return int(val) if val.isdigit() else None
    except:
        return None


def get_str_field(row: dict, key: str) -> str | None:
    """Ambil field string dari row, return None jika kosong"""
    val = row.get(key, "").strip()
    return val if val else None


@router.post("/upload-csv")
async def upload_members_csv(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Upload CSV data pengurus HIPMI"""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        contents = await file.read()
        stream = io.StringIO(contents.decode("utf-8"))
        reader = csv.DictReader(stream)

        # Bersihkan header (trim spasi)
        reader.fieldnames = [f.strip() if f else f for f in reader.fieldnames]

        imported_count = 0
        errors = []

        for row_num, row in enumerate(reader, 1):
            try:
                member = Member(
                    no=parse_int_field(row.get("no", "")),
                    name=get_str_field(row, "nama"),
                    jabatan=get_str_field(row, "jabatan"),
                    status_kta=get_str_field(row, "status_kta"),
                    no_kta=get_str_field(row, "no_kta"),
                    tanggal_lahir=get_str_field(row, "tanggal_lahir"),
                    usia=parse_int_field(row.get("usia", "")),
                    jenis_kelamin=get_str_field(row, "jenis_kelamin"),
                    phone=get_str_field(row, "whatsapp"),
                    email=get_str_field(row, "email"),
                    instagram=get_str_field(row, "instagram"),
                    nama_perusahaan=get_str_field(row, "nama_perusahaan"),
                    jabatan_dlm_akta_perusahaan=get_str_field(
                        row, "jabatan_dlm_akta_perusahaan"
                    ),
                    kategori_bidang_usaha=get_str_field(row, "kategori_bidang_usaha"),
                    alamat_perusahaan=get_str_field(row, "alamat_perusahaan"),
                    perusahaan_berdiri_sejak=get_str_field(
                        row, "perusahaan_berdiri_sejak"
                    ),
                    jmlh_karyawan=parse_int_field(row.get("jmlh_karyawan", "")),
                    website=get_str_field(row, "website"),
                    twitter=get_str_field(row, "twitter"),
                    facebook=get_str_field(row, "facebook"),
                    youtube=get_str_field(row, "youtube"),
                    # Backward compatibility
                    position=get_str_field(row, "jabatan"),
                    organization=get_str_field(row, "kategori_bidang_usaha"),
                )
                db.add(member)
                imported_count += 1
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")

        db.commit()

        return {
            "status": "success",
            "imported": imported_count,
            "errors": errors if errors else None,
            "message": f"Successfully imported {imported_count} pengurus from CSV",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/")
async def list_members(db: Session = Depends(get_db)):
    """Ambil semua data pengurus"""
    members = db.query(Member).all()

    return {
        "status": "success",
        "total": len(members),
        "data": [
            {
                "id": m.id,
                "no": m.no,
                "name": m.name,
                "email": m.email,
                "phone": m.phone,
                "jabatan": m.jabatan,
                "status_kta": m.status_kta,
                "no_kta": m.no_kta,
                "tanggal_lahir": m.tanggal_lahir,
                "usia": m.usia,
                "jenis_kelamin": m.jenis_kelamin,
                "instagram": m.instagram,
                "nama_perusahaan": m.nama_perusahaan,
                "jabatan_dlm_akta_perusahaan": m.jabatan_dlm_akta_perusahaan,
                "kategori_bidang_usaha": m.kategori_bidang_usaha,
                "alamat_perusahaan": m.alamat_perusahaan,
                "perusahaan_berdiri_sejak": m.perusahaan_berdiri_sejak,
                "jmlh_karyawan": m.jmlh_karyawan,
                "website": m.website,
                "twitter": m.twitter,
                "facebook": m.facebook,
                "youtube": m.youtube,
                "position": m.position,
                "organization": m.organization,
                "status": m.status,
                "region": m.region,
                "entry_year": m.entry_year,
            }
            for m in members
        ],
    }
