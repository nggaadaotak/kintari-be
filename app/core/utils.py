import os
from pathlib import Path


def ensure_upload_dir():
    """Memastikan direktori upload ada"""
    upload_dir = Path("./uploads")
    upload_dir.mkdir(exist_ok=True)
    return upload_dir


def get_file_extension(filename: str) -> str:
    """Mengambil ekstensi file"""
    return Path(filename).suffix.lower()


def is_allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Cek apakah file extension diizinkan"""
    return get_file_extension(filename) in allowed_extensions
