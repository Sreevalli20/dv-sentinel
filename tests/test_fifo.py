"""Tests for FIFO analyzer."""

import pytest
from dv.fifo import FIFOAnalyzer


class TestFIFOAnalyzer:
    """Test FIFO analyzer functionality."""
    
    def test_detect_read_while_empty(self):
        """Test detection of read while empty issue."""
        code = "always @(posedge clk) if (rd_en) data_out <= mem[rd_ptr]; logic empty;"
        issues = FIFOAnalyzer.detect_issues(code)
        
        # Should detect potential read while empty
        assert any("read while empty" in issue.get("title", "").lower() for issue in issues)
    
    def test_detect_write_while_full(self):
        """Test detection of write while full issue."""
        code = "always @(posedge clk) if (wr_en) mem[wr_ptr] <= data_in; logic full;"
        issues = FIFOAnalyzer.detect_issues(code)
        
        # Should detect potential write while full
        assert any("write while full" in issue.get("title", "").lower() for issue in issues)
    
    def test_detect_missing_gray_code(self):
        """Test detection of missing Gray code encoding."""
        code = "logic [3:0] rd_ptr, wr_ptr;"
        issues = FIFOAnalyzer.detect_issues(code)
        
        # Should detect missing Gray code
        assert any("gray" in issue.get("description", "").lower() for issue in issues)
    
    def test_detect_missing_reset(self):
        """Test detection of missing reset initialization."""
        code = "logic [3:0] rd_ptr, wr_ptr;"
        issues = FIFOAnalyzer.detect_issues(code)
        
        # Should detect missing reset
        assert any("reset" in issue.get("title", "").lower() for issue in issues)
    
    def test_assert_no_read_when_empty(self):
        """Test assertion generation for no read when empty."""
        assertion = FIFOAnalyzer.assert_no_read_when_empty()
        assert "empty" in assertion
        assert "rd_en" in assertion
        assert "assert property" in assertion
    
    def test_assert_no_write_when_full(self):
        """Test assertion generation for no write when full."""
        assertion = FIFOAnalyzer.assert_no_write_when_full()
        assert "full" in assertion
        assert "wr_en" in assertion
        assert "assert property" in assertion
    
    def test_get_coverage_suggestions(self):
        """Test coverage suggestions."""
        coverage = FIFOAnalyzer.get_coverage_suggestions()
        assert isinstance(coverage, list)
        assert len(coverage) > 0
        assert "empty" in str(coverage).lower()
        assert "full" in str(coverage).lower()
    
    def test_get_test_plan(self):
        """Test test plan generation."""
        plan = FIFOAnalyzer.get_test_plan()
        assert "objective" in plan
        assert "stimulus" in plan
        assert "expected_behavior" in plan
        assert "corner_cases" in plan
        assert "assertions" in plan
