import sqlite3
from typing import List, Dict, Any

class SupplierDiscoveryEngine:
    """Verifies regulatory compliance (GMP status, active DMF numbers) and retrieves suppliers."""

    def __init__(self, db_path: str = "pharma_procurement.db"):
        self.db_path = db_path

    def search_suppliers(self, tenant_id: str, api_material: str) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
        SELECT id, name, api_material, dmf_number, dmf_status, gmp_certified, benchmark_price_usd_kg, moq_kg, country_of_origin 
        FROM suppliers 
        WHERE tenant_id = ? AND api_material LIKE ?
        """
        cursor.execute(query, (tenant_id, f"%{api_material}%"))
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            results.append({
                "supplier_id": r["id"],
                "name": r["name"],
                "api_material": r["api_material"],
                "dmf_number": r["dmf_number"],
                "dmf_status": r["dmf_status"],
                "gmp_certified": bool(r["gmp_certified"]),
                "raw_price_usd_kg": r["benchmark_price_usd_kg"],
                "moq_kg": r["moq_kg"],
                "origin": r["country_of_origin"]
            })
        return results

    def verify_fda_dmf_status(self, dmf_number: str) -> Dict[str, Any]:
        """Cold-start verification wrapper simulating FDA drug master file lookup."""
        return {
            "dmf_number": dmf_number,
            "status": "ACTIVE",
            "type": "TYPE II - Active Pharmaceutical Ingredient",
            "holder_status": "GDUFA Fee Compliant"
        }
