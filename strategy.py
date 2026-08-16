from typing import Dict, Any

class NegotiationStrategyEngine:
    """Configures negotiation profiles and concession boundaries."""

    PROFILES = {
        "aggressive": {
            "target_discount_pct": 12.0,
            "max_concession_cap_pct": 15.0,
            "moq_flexibility": "HIGH_VOLUME_LEVERAGE",
            "opening_offer_discount": 18.0
        },
        "balanced": {
            "target_discount_pct": 7.0,
            "max_concession_cap_pct": 10.0,
            "moq_flexibility": "STANDARD",
            "opening_offer_discount": 10.0
        },
        "conservative": {
            "target_discount_pct": 4.0,
            "max_concession_cap_pct": 6.0,
            "moq_flexibility": "STRICT_COMPLIANCE_FIRST",
            "opening_offer_discount": 5.0
        }
    }

    @classmethod
    def calculate_opening_offer(cls, profile: str, baseline_price: float, custom_cap: float = None) -> Dict[str, Any]:
        p = cls.PROFILES.get(profile.lower(), cls.PROFILES["balanced"])
        discount = p["opening_offer_discount"]
        
        opening_price = baseline_price * (1 - (discount / 100.0))
        max_price = baseline_price * (1 - ((custom_cap or p["max_concession_cap_pct"]) / 100.0))

        return {
            "strategy": profile.upper(),
            "baseline_price_usd_kg": baseline_price,
            "recommended_opening_bid_usd_kg": round(opening_price, 2),
            "walkaway_ceiling_usd_kg": round(max_price, 2),
            "moq_policy": p["moq_flexibility"]
        }
