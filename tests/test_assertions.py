"""Tests for assertion generator."""

import pytest
from dv.assertions import AssertionGenerator


class TestAssertionGenerator:
    """Test assertion generator functionality."""
    
    def test_generate_valid_ready_assertion(self):
        """Test VALID/READY assertion generation."""
        assertion = AssertionGenerator.generate_valid_ready_assertion("valid", "ready")
        assert "valid" in assertion
        assert "ready" in assertion
        assert "assert property" in assertion
    
    def test_generate_stability_assertion(self):
        """Test stability assertion generation."""
        assertion = AssertionGenerator.generate_stability_assertion("data", "valid && !ready")
        assert "data" in assertion
        assert "$stable" in assertion
    
    def test_generate_reset_assertion(self):
        """Test reset assertion generation."""
        assertion = AssertionGenerator.generate_reset_assertion("signal", "0")
        assert "signal" in assertion
        assert "reset" in assertion
    
    def test_generate_fsm_assertion(self):
        """Test FSM assertion generation."""
        transitions = {"IDLE": ["ACTIVE"], "ACTIVE": ["DONE", "IDLE"]}
        assertion = AssertionGenerator.generate_fsm_assertion("state", transitions)
        assert "assert property" in assertion
    
    def test_generate_mutual_exclusion_assertion(self):
        """Test mutual exclusion assertion generation."""
        assertion = AssertionGenerator.generate_mutual_exclusion_assertion(["req1", "req2"])
        assert "req1" in assertion
        assert "req2" in assertion
    
    def test_get_template_library(self):
        """Test template library."""
        templates = AssertionGenerator.get_template_library()
        assert isinstance(templates, dict)
        assert "valid_ready" in templates
        assert "data_stable" in templates
