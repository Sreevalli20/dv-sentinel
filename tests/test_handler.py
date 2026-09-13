"""Tests for DV handler."""

import pytest
from agent.handler import DVHandler


class TestDVHandler:
    """Test DV handler functionality."""
    
    def test_handle_empty_input(self):
        """Test handling of empty input."""
        handler = DVHandler()
        response = handler.handle_message("", "user1", "telegram")
        assert "help" in response.lower()
    
    def test_handle_start_command(self):
        """Test /start command."""
        handler = DVHandler()
        response = handler.handle_message("/start", "user1", "telegram")
        assert "DV Sentinel" in response
        assert "Design Verification" in response
    
    def test_handle_help_command(self):
        """Test /help command."""
        handler = DVHandler()
        response = handler.handle_message("/help", "user1", "telegram")
        assert "COMMANDS" in response
        assert "/start" in response
    
    def test_handle_assert_command(self):
        """Test /assert command."""
        handler = DVHandler()
        response = handler.handle_message("/assert FIFO should never read when empty", "user1", "telegram")
        assert "ASSERTION" in response
        assert "empty" in response.lower()
    
    def test_handle_coverage_command(self):
        """Test /coverage command."""
        handler = DVHandler()
        response = handler.handle_message("/coverage FIFO", "user1", "telegram")
        assert "COVERAGE" in response
        assert "empty" in response.lower() or "full" in response.lower()
    
    def test_handle_testplan_command(self):
        """Test /testplan command."""
        handler = DVHandler()
        response = handler.handle_message("/testplan FIFO", "user1", "telegram")
        assert "TEST PLAN" in response
        assert "Objective" in response
    
    def test_handle_interview_command(self):
        """Test /interview command."""
        handler = DVHandler()
        response = handler.handle_message("/interview", "user1", "telegram")
        assert "INTERVIEW" in response
        assert "Question" in response
    
    def test_handle_daily_command(self):
        """Test /daily command."""
        handler = DVHandler()
        response = handler.handle_message("/daily", "user1", "telegram")
        assert "DAILY CHALLENGE" in response
    
    def test_handle_natural_language_fifo(self):
        """Test natural language FIFO query."""
        handler = DVHandler()
        response = handler.handle_message("My FIFO has overflow issue", "user1", "telegram")
        assert "FIFO" in response.upper()
    
    def test_handle_natural_language_axi(self):
        """Test natural language AXI query."""
        handler = DVHandler()
        response = handler.handle_message("Why is my AXI transaction hanging?", "user1", "telegram")
        assert "AXI" in response.upper()
    
    def test_handle_unknown_command(self):
        """Test unknown command."""
        handler = DVHandler()
        response = handler.handle_message("/unknown", "user1", "telegram")
        assert "Unknown command" in response
