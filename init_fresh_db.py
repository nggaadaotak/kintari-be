"""
Fresh Database Initialization
Creates all tables from scratch with updated schema for Pengurus HIPMI
"""

from app.core.database import Base, engine
from app.models.organization import OrganizationInfo, MembershipType, OrgStructure
from app.models.member import Member
from app.models.universal_document import UniversalDocument, DocumentCollection

print("🔄 Creating fresh database for Kintari - HIPMI Knowledge System...")
print("=" * 70)

# Drop all tables (fresh start)
print("\n🗑️  Dropping all existing tables...")
Base.metadata.drop_all(bind=engine)
print("✅ All tables dropped")

# Create all tables
print("\n📦 Creating all tables with updated schema...")
Base.metadata.create_all(bind=engine)
print("✅ All tables created")

# List created tables
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

print("\n📊 Database tables created:")
for table in tables:
    print(f"  ✅ {table}")

    # Show columns for each table
    columns = inspector.get_columns(table)
    print(f"     Columns ({len(columns)}):")
    for col in columns[:10]:  # Show first 10 columns
        col_type = str(col["type"])
        nullable = "NULL" if col["nullable"] else "NOT NULL"
        print(f"       - {col['name']}: {col_type} {nullable}")
    if len(columns) > 10:
        print(f"       ... and {len(columns) - 10} more columns")

print("\n" + "=" * 70)
print("✅ Fresh database initialized successfully!")
print("\n📋 Database Schema Summary:")
print("   - members: Pengurus HIPMI with 30+ fields")
print("     (no, name, jabatan, status_kta, usia, jenis_kelamin,")
print("      kategori_bidang_usaha, nama_perusahaan, jmlh_karyawan, etc)")
print("   - universal_documents: HIPMI documents (PDF, DOCX)")
print("   - document_collections: Document grouping")
print("   - organization_info: HIPMI organization data")
print("   - membership_types: Membership categories")
print("   - org_structure: Organizational structure")
print("\n💾 Database file: kintari.db")
print("✅ Ready to accept data!")
print("=" * 70)
