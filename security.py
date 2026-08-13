import re
import hashlib
from typing import Dict, Any

class MultiTenantSecurityManager:
    """Manages multi-tenant workspace separation and automatic PII/PHI masking."""
    
    # PII / Sensitive Commercial Terms Regex Patterns
    PATTERNS = {
        "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "phone": r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}",
        "bank_account": r"\b\d{8,17}\b",
        "tax_id": r"\b\d{2}-\d{7}\b"
    }

    @staticmethod
    def get_tenant_hash(tenant_id: str) -> str:
        return hashlib.sha256(tenant_id.encode()).hexdigest()[:12]

    @classmethod
    def mask_pii(cls, text: str) -> str:
        masked_text = text
        for key, pattern in cls.PATTERNS.items():
            masked_text = re.sub(pattern, f"[MASKED_{key.upper()}]", masked_text)
        return masked_text

    @classmethod
    def enforce_tenant_context(cls, tenant_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Injects tenant security token into database query context."""
        payload["tenant_id"] = tenant_id
        payload["tenant_hash"] = cls.get_tenant_hash(tenant_id)
        return payload
