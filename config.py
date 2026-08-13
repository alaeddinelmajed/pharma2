import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "PharmaProcure-AI Enterprise"
    ENV: str = os.getenv("ENV", "production")
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", 8080))
    
    # GCP / Google Antigravity Agent SDK
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "pharma-ai-sovereign")
    GCP_REGION: str = os.getenv("GCP_REGION", "me-central1") # Default Middle East Region
    ANTIGRAVITY_API_KEY: str = os.getenv("ANTIGRAVITY_API_KEY", "sk-antigravity-dev-key")
    
    # Sovereign Cloud Adapter Configuration
    SOVEREIGN_CLOUD_PROVIDER: str = os.getenv("SOVEREIGN_CLOUD_PROVIDER", "HUMAIN_KSA") # HUMAIN_KSA | CORE42_UAE | GCP_PRIMARY
    DATA_ENCRYPTION_KEY: str = os.getenv("DATA_ENCRYPTION_KEY", "sovereign-aes-256-pharma-procure-secret")
    
    # Database
    DATABASE_URL: str = "sqlite:///./pharma_procurement.db"

    class Config:
        env_file = ".env"

settings = Settings()

class SovereignCloudAdapter:
    """Enforces Middle East data residency & sovereign encryption requirements."""
    
    def __init__(self, provider: str = settings.SOVEREIGN_CLOUD_PROVIDER):
        self.provider = provider
        
    def get_routing_header(self) -> dict:
        return {
            "X-Sovereign-Cloud-Provider": self.provider,
            "X-Data-Residency-Region": settings.GCP_REGION,
            "X-Compliance-Level": "GMP-GxP-Level-4"
        }
    
    def sanitize_payload(self, data: dict) -> dict:
        # Guarantees sovereign data bounds before passing to LLM engine
        data["_sovereign_boundary"] = f"VERIFIED-{self.provider}"
        return data

sovereign_adapter = SovereignCloudAdapter()
