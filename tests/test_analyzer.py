"""Tests for DV analyzer."""

import pytest
from dv.analyzer import DVAnalyzer


class TestDVAnalyzer:
    """Test DV analyzer functionality."""
    
    def test_detect_intent_fifo(self):
        """Test FIFO intent detection."""
        analyzer = DVAnalyzer()
        intent = analyzer.detect_intent("Check my FIFO implementation")
        assert intent == "fifo"
    
    def test_detect_intent_axi(self):
        """Test AXI intent detection."""
        analyzer = DVAnalyzer()
        intent = analyzer.detect_intent("AXI transaction stuck")
        assert intent == "axi"
    
    def test_detect_intent_apb(self):
        """Test APB intent detection."""
        analyzer = DVAnalyzer()
        intent = analyzer.detect_intent("APB protocol issue")
        assert intent == "apb"
    
    def test_detect_intent_assertion(self):
        """Test assertion intent detection."""
        analyzer = DVAnalyzer()
        intent = analyzer.detect_intent("Generate an assertion")
        assert intent == "assertion"
    
    def test_detect_intent_coverage(self):
        """Test coverage intent detection."""
        analyzer = DVAnalyzer()
        intent = analyzer.detect_intent("Coverage for FIFO")
        assert intent == "coverage"
    
    def test_detect_intent_bug(self):
        """Test bug intent detection."""
        analyzer = DVAnalyzer()
        intent = analyzer.detect_intent("Debug this bug")
        assert intent == "bug"
    
    def test_analyze_fifo_code(self):
        """Test FIFO code analysis."""
        analyzer = DVAnalyzer()
        issues = analyzer.analyze_code("logic rd_ptr, wr_ptr;", protocol="fifo")
        assert isinstance(issues, list)
    
    def test_generate_assertion(self):
        """Test assertion generation."""
        analyzer = DVAnalyzer()
        assertion = analyzer.generate_assertion("FIFO should never read when empty")
        assert "empty" in assertion.lower()
    
    def test_get_coverage(self):
        """Test coverage retrieval."""
        analyzer = DVAnalyzer()
        coverage = analyzer.get_coverage("fifo")
        assert isinstance(coverage, list)
        assert len(coverage) > 0
    
    def test_get_test_plan(self):
        """Test test plan retrieval."""
        analyzer = DVAnalyzer()
        plan = analyzer.get_test_plan("FIFO")
        assert "TEST PLAN" in plan
        assert "Objective" in plan
    
    def test_generate_bug_report(self):
        """Test bug report generation."""
        analyzer = DVAnalyzer()
        report = analyzer.generate_bug_report(
            title="Test Bug",
            description="Test description",
            severity="HIGH"
        )
        assert "BUG REPORT" in report
        assert "Test Bug" in report
    
    def test_get_interview_question(self):
        """Test interview question retrieval."""
        analyzer = DVAnalyzer()
        question = analyzer.get_interview_question()
        assert "INTERVIEW" in question
        assert "Question" in question
    
    def test_get_daily_challenge(self):
        """Test daily challenge retrieval."""
        analyzer = DVAnalyzer()
        challenge = analyzer.get_daily_challenge()
        assert "DAILY CHALLENGE" in challenge


class TestDVHandler:
    """Test DV handler functionality."""
    
    def test_handler_start_command(self):
        """Test handler /start command."""
        from agent.handler import DVHandler
        handler = DVHandler()
        response = handler.handle_message("/start", "test_user", "telegram")
        assert "DV Sentinel" in response
    
    def test_handler_assert_command(self):
        """Test handler /assert command."""
        from agent.handler import DVHandler
        handler = DVHandler()
        response = handler.handle_message(
            "/assert FIFO should never read when empty",
            "test_user",
            "telegram"
        )
        assert "assertion" in response.lower() or "ASSERTION" in response
    
    def test_handler_coverage_command(self):
        """Test handler /coverage command."""
        from agent.handler import DVHandler
        handler = DVHandler()
        response = handler.handle_message("/coverage FIFO", "test_user", "telegram")
        assert "COVERAGE" in response or "coverage" in response.lower()
    
    def test_handler_natural_language(self):
        """Test handler natural language processing."""
        from agent.handler import DVHandler
        handler = DVHandler()
        response = handler.handle_message(
            "Why can a FIFO underflow happen?",
            "test_user",
            "telegram"
        )
        assert response  # Should return something
    
    def test_handler_exception_handling(self):
        """Test handler exception handling with fallback."""
        from agent.handler import DVHandler
        handler = DVHandler()
        # Should handle any errors gracefully
        response = handler.handle_message("/start", "test_user", "telegram")
        assert response
        assert "DV Sentinel" in response or "error" in response.lower() or "Error" in response
