import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kintari.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000"
).split(",")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

# Pastikan direktori upload ada
os.makedirs(UPLOAD_DIR, exist_ok=True)
