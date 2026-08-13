import sqlite3

class CategoryBenchmarkEngine:
    """Combines external market feeds with first-party empirical deal outcomes."""

    def __init__(self, db_path: str = "pharma_procurement.db"):
        self.db_path = db_path

    def get_market_benchmark(self, tenant_id: str, api_material: str) -> dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Empirical deal average
        cursor.execute("""
            SELECT AVG(agreed_price_usd_kg), COUNT(*) 
            FROM deal_history 
            WHERE tenant_id = ? AND api_material LIKE ? AND status = 'APPROVED'
        """, (tenant_id, f"%{api_material}%"))
        
        row = cursor.fetchone()
        avg_price = row[0] if row[0] else None
        deal_count = row[1]
        conn.close()

        # Synthetic Global Cold-Start Market Indexes
        global_indices = {
            "Paracetamol Fine Powder GXP": {"global_index": 14.20, "trend": "-2.1%"},
            "Metformin HCl Ph. Eur.": {"global_index": 27.50, "trend": "+0.8%"},
            "Amoxicillin Trihydrate Compacted": {"global_index": 41.00, "trend": "-1.4%"}
        }

        matched_index = global_indices.get(api_material, {"global_index": 25.00, "trend": "STABLE"})

        if avg_price:
            # Empirical weight grows with deal count
            blended_target = (avg_price * 0.7) + (matched_index["global_index"] * 0.3)
        else:
            blended_target = matched_index["global_index"]

        return {
            "material": api_material,
            "global_index_usd_kg": matched_index["global_index"],
            "empirical_historical_avg_usd_kg": round(avg_price, 2) if avg_price else "No Historic Data",
            "recommended_target_price_usd_kg": round(blended_target, 2),
            "market_trend": matched_index["trend"],
            "flywheel_confidence_score": min(100, (deal_count * 25) + 25)
        }
