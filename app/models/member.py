from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.core.database import Base


class Member(Base):
    """
    Model untuk data pengurus HIPMI (disesuaikan dengan pengurus.csv)
    Kolom: no, nama, jabatan, status_kta, no_kta, tanggal_lahir, usia, jenis_kelamin,
           whatsapp, email, instagram, nama_perusahaan, jabatan_dlm_akta_perusahaan,
           kategori_bidang_usaha, alamat_perusahaan, perusahaan_berdiri_sejak,
           jmlh_karyawan, website, twitter, facebook, youtube
    """

    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)

    # Data Pribadi Pengurus
    no = Column(Integer, nullable=True)  # Nomor urut
    name = Column(String, index=True)  # nama dari CSV
    jabatan = Column(
        String, nullable=True, index=True
    )  # Ketum, WKU, Sekum, Ketua Bidang, dll
    status_kta = Column(
        String, nullable=True
    )  # KTA Fisik, KTA HIPMI NET, Hilang, SK Tum Ibam
    no_kta = Column(String, nullable=True)  # Nomor KTA

    # Demografi
    tanggal_lahir = Column(String, nullable=True)  # DD-MM-YYYY
    usia = Column(Integer, nullable=True, index=True)  # Untuk histogram distribusi usia
    jenis_kelamin = Column(String, nullable=True, index=True)  # Male/Female

    # Kontak
    phone = Column(String, nullable=True)  # whatsapp dari CSV
    email = Column(String, nullable=True, index=True)  # email dari CSV
    instagram = Column(String, nullable=True)  # Username Instagram

    # Data Perusahaan
    nama_perusahaan = Column(String, nullable=True)  # Nama perusahaan
    jabatan_dlm_akta_perusahaan = Column(
        String, nullable=True
    )  # Direktur, CEO, Owner, dll
    kategori_bidang_usaha = Column(
        String, nullable=True, index=True
    )  # IT, Property, F&B, Fashion, dll
    alamat_perusahaan = Column(Text, nullable=True)  # Alamat perusahaan
    perusahaan_berdiri_sejak = Column(String, nullable=True)  # Tahun berdiri
    jmlh_karyawan = Column(Integer, nullable=True)  # Jumlah karyawan

    # Media Sosial Perusahaan
    website = Column(String, nullable=True)
    twitter = Column(String, nullable=True)
    facebook = Column(String, nullable=True)
    youtube = Column(String, nullable=True)

    # Kolom lama (untuk backward compatibility, bisa nullable)
    position = Column(String, nullable=True)  # Alias untuk jabatan
    organization = Column(String, nullable=True)  # Alias untuk kategori_bidang_usaha
    membership_type = Column(String, nullable=True)
    status = Column(String, nullable=True)  # Status lama
    region = Column(String, nullable=True)
    entry_year = Column(Integer, nullable=True)

    # Metadata
    joined_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
