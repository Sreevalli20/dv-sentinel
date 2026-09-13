"""Configuration for DV Sentinel."""

import os
from typing import Optional


class Config:
    """Application configuration."""
    
    # Caspian
    CASPIAN_API_KEY: str = os.environ.get("CASPIAN_API_KEY", "")
    CASPIAN_BASE_URL: str = os.environ.get(
        "CASPIAN_BASE_URL", 
        "https://api.trycaspianai.com"
    )
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    
    # Email
    EMAIL_USERNAME: str = os.environ.get("EMAIL_USERNAME", "dv-sentinel")
    
    # Database
    DATABASE_PATH: str = os.environ.get("DATABASE_PATH", "dv_sentinel.db")
    
    # Application
    APP_NAME: str = "DV Sentinel"
    APP_VERSION: str = "1.0.0"
    PORT: int = int(os.environ.get("PORT", "8000"))
    
    # Demo mode
    DEMO_MODE: bool = os.environ.get("DEMO_MODE", "false").lower() == "true"
    
    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """Validate required configuration.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not cls.DEMO_MODE:
            if not cls.CASPIAN_API_KEY:
                errors.append("CASPIAN_API_KEY is required in non-demo mode")
        
        return len(errors) == 0, errors


config = Config()
