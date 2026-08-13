import sqlite3
import json
import os

DB_FILE = "pharma_procurement.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Tenants Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tenants (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        sovereign_region TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Active Suppliers Table (GMP / DMF Verified)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id TEXT PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        name TEXT NOT NULL,
        api_material TEXT NOT NULL,
        dmf_number TEXT UNIQUE NOT NULL,
        dmf_status TEXT NOT NULL,
        gmp_certified INTEGER NOT NULL,
        benchmark_price_usd_kg REAL NOT NULL,
        moq_kg INTEGER NOT NULL,
        country_of_origin TEXT NOT NULL,
        FOREIGN KEY(tenant_id) REFERENCES tenants(id)
    )
    """)

    # Negotiation History & Flywheel
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deal_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_id TEXT NOT NULL,
        supplier_id TEXT NOT NULL,
        api_material TEXT NOT NULL,
        agreed_price_usd_kg REAL NOT NULL,
        volume_kg REAL NOT NULL,
        concession_rate_pct REAL NOT NULL,
        status TEXT NOT NULL,
        closed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def seed_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if seeded
    cursor.execute("SELECT COUNT(*) FROM tenants")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # 1. Seed Tenants
    cursor.executemany("INSERT INTO tenants VALUES (?, ?, ?)", [
        ("tenant-alpha", "PharmaCorp Alpha (Riyadh Hub)", "HUMAIN_KSA"),
        ("tenant-beta", "BioMed Beta (Dubai Hub)", "CORE42_UAE")
    ])

    # 2. Seed High-Value Raw APIs
    suppliers_data = [
        ("sup-101", "tenant-alpha", "Apex Bio-Pharma Ltd", "Paracetamol Fine Powder GXP", "DMF-034821", "ACTIVE", 1, 14.50, 5000, "India"),
        ("sup-102", "tenant-alpha", "SinoActive Chemical Corp", "Paracetamol Fine Powder GXP", "DMF-021944", "ACTIVE", 1, 12.80, 10000, "China"),
        ("sup-103", "tenant-alpha", "Heidelberg Fine APIs GmbH", "Metformin HCl Ph. Eur.", "DMF-019233", "ACTIVE", 1, 28.00, 2000, "Germany"),
        ("sup-104", "tenant-beta", "Emirates Bio-Tech Labs", "Amoxicillin Trihydrate Compacted", "DMF-044102", "ACTIVE", 1, 42.50, 1000, "UAE"),
        ("sup-105", "tenant-beta", "Gujarat Organics Ltd", "Amoxicillin Trihydrate Compacted", "DMF-038190", "ACTIVE", 0, 36.00, 3000, "India")
    ]
    cursor.executemany("INSERT INTO suppliers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", suppliers_data)

    # 3. Seed Historic Deal Flywheel Data
    deals_data = [
        ("tenant-alpha", "sup-101", "Paracetamol Fine Powder GXP", 13.90, 10000, 4.1, "APPROVED"),
        ("tenant-alpha", "sup-103", "Metformin HCl Ph. Eur.", 26.50, 5000, 5.3, "APPROVED"),
        ("tenant-beta", "sup-104", "Amoxicillin Trihydrate Compacted", 40.00, 2000, 5.8, "APPROVED")
    ]
    cursor.executemany("INSERT INTO deal_history (tenant_id, supplier_id, api_material, agreed_price_usd_kg, volume_kg, concession_rate_pct, status) VALUES (?, ?, ?, ?, ?, ?, ?)", deals_data)

    conn.commit()
    conn.close()
    print("✅ Database successfully created and seeded with pharmaceutical baseline records.")

if __name__ == "__main__":
    init_db()
    seed_db()
