"""Tests for APB analyzer."""

import pytest
from dv.apb import APBAnalyzer


class TestAPBAnalyzer:
    """Test APB analyzer functionality."""
    
    def test_detect_enable_timing(self):
        """Test detection of PENABLE timing violation."""
        code = "logic psel, penable;"
        issues = APBAnalyzer.detect_issues(code)
        
        # Should detect timing issue
        assert any("timing" in issue.get("title", "").lower() for issue in issues)
    
    def test_detect_missing_pready(self):
        """Test detection of missing PREADY."""
        code = "logic psel, penable;"
        issues = APBAnalyzer.detect_issues(code)
        
        # Should detect missing PREADY
        assert any("ready" in issue.get("title", "").lower() for issue in issues)
    
    def test_assert_enable_timing(self):
        """Test assertion generation for PENABLE timing."""
        assertion = APBAnalyzer.assert_enable_timing()
        assert "penable" in assertion
        assert "psel" in assertion
        assert "assert property" in assertion
    
    def test_get_coverage_suggestions(self):
        """Test coverage suggestions."""
        coverage = APBAnalyzer.get_coverage_suggestions()
        assert isinstance(coverage, list)
        assert len(coverage) > 0
        assert "read" in str(coverage).lower()
        assert "write" in str(coverage).lower()
    
    def test_explain_protocol(self):
        """Test protocol explanation."""
        explanation = APBAnalyzer.explain_protocol()
        assert "setup" in explanation.lower()
        assert "access" in explanation.lower()
        assert "idle" in explanation.lower()
