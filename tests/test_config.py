"""Tests for configuration."""

import pytest
import os
from app.config import Config


class TestConfig:
    """Test configuration functionality."""
    
    def test_default_values(self):
        """Test default configuration values."""
        assert Config.APP_NAME == "DV Sentinel"
        assert Config.APP_VERSION == "1.0.0"
        assert Config.PORT == 8000
    
    def test_demo_mode(self):
        """Test demo mode configuration."""
        original_demo = Config.DEMO_MODE
        os.environ["DEMO_MODE"] = "true"
        Config.DEMO_MODE = os.environ.get("DEMO_MODE", "false").lower() == "true"
        assert Config.DEMO_MODE is True
        
        os.environ["DEMO_MODE"] = "false"
        Config.DEMO_MODE = os.environ.get("DEMO_MODE", "false").lower() == "true"
        assert Config.DEMO_MODE is False
        
        Config.DEMO_MODE = original_demo
    
    def test_validate_with_demo_mode(self):
        """Test validation in demo mode."""
        original_demo = Config.DEMO_MODE
        original_api_key = Config.CASPIAN_API_KEY
        
        Config.DEMO_MODE = True
        Config.CASPIAN_API_KEY = ""
        
        is_valid, errors = Config.validate()
        assert is_valid is True
        assert len(errors) == 0
        
        Config.DEMO_MODE = original_demo
        Config.CASPIAN_API_KEY = original_api_key
    
    def test_validate_without_api_key(self):
        """Test validation without API key in production mode."""
        original_demo = Config.DEMO_MODE
        original_api_key = Config.CASPIAN_API_KEY
        
        Config.DEMO_MODE = False
        Config.CASPIAN_API_KEY = ""
        
        is_valid, errors = Config.validate()
        assert is_valid is False
        assert len(errors) > 0
        
        Config.DEMO_MODE = original_demo
        Config.CASPIAN_API_KEY = original_api_key
