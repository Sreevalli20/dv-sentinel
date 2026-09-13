"""Tests for database manager."""

import pytest
import os
from storage.database import DatabaseManager


class TestDatabaseManager:
    """Test database manager functionality."""
    
    def test_init_db(self):
        """Test database initialization."""
        db = DatabaseManager(":memory:")
        assert db.is_healthy()
    
    def test_log_message(self):
        """Test message logging."""
        db = DatabaseManager(":memory:")
        db.log_message("user1", "telegram", "test message")
    
    def test_log_command(self):
        """Test command logging."""
        db = DatabaseManager(":memory:")
        db.log_command("user1", "telegram", "/start")
    
    def test_store_and_get_context(self):
        """Test context storage and retrieval."""
        db = DatabaseManager(":memory:")
        context_data = {"intent": "fifo", "last_input": "test"}
        db.store_context("user1", context_data)
        
        retrieved = db.get_context("user1")
        assert retrieved == context_data
    
    def test_get_metrics(self):
        """Test metrics retrieval."""
        db = DatabaseManager(":memory:")
        db.log_message("user1", "telegram", "test")
        db.log_message("user2", "email", "test2")
        
        metrics = db.get_metrics()
        assert "total_messages" in metrics
        assert metrics["total_messages"] >= 2
    
    def test_is_healthy(self):
        """Test health check."""
        db = DatabaseManager(":memory:")
        assert db.is_healthy()
