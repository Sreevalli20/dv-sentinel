"""Main DV analyzer for DV Sentinel."""

from typing import List, Dict, Any
from .fifo import FIFOAnalyzer
from .axi import AXIAnalyzer
from .apb import APBAnalyzer
from .assertions import AssertionGenerator
from .coverage import CoverageEngine
from .testplan import TestPlanGenerator
from .bug_report import BugReportGenerator
from .interview import InterviewGenerator


class DVAnalyzer:
    """Main analyzer that coordinates all DV analysis modules."""
    
    def __init__(self):
        self.fifo = FIFOAnalyzer()
        self.axi = AXIAnalyzer()
        self.apb = APBAnalyzer()
        self.assertions = AssertionGenerator()
        self.coverage = CoverageEngine()
        self.testplan = TestPlanGenerator()
        self.bug_report = BugReportGenerator()
        self.interview = InterviewGenerator()
    
    def detect_intent(self, text: str) -> str:
        """Detect user intent from natural language.
        
        Args:
            text: User input text
            
        Returns:
            Detected intent category
        """
        text_lower = text.lower()
        
        # Check for actions first (higher priority)
        if "assert" in text_lower or "assertion" in text_lower or "sva" in text_lower:
            return "assertion"
        if "coverage" in text_lower:
            return "coverage"
        if "testplan" in text_lower or "test plan" in text_lower:
            return "testplan"
        if "bug" in text_lower or "debug" in text_lower:
            return "bug"
        if "interview" in text_lower or "question" in text_lower:
            return "interview"
        if "reset" in text_lower:
            return "reset"
        if "fsm" in text_lower or "state machine" in text_lower:
            return "fsm"
        if "review" in text_lower or "analyze" in text_lower:
            return "review"
        
        # Check for specific protocols (lower priority)
        if "fifo" in text_lower:
            return "fifo"
        if "axi" in text_lower:
            return "axi"
        if "apb" in text_lower:
            return "apb"
        
        return "general"
    
    def analyze_code(self, code: str, protocol: str = None) -> List[Dict[str, Any]]:
        """Analyze SystemVerilog code based on protocol.
        
        Args:
            code: SystemVerilog code
            protocol: Optional protocol hint (fifo, axi, apb)
            
        Returns:
            List of detected issues
        """
        if protocol == "fifo" or "fifo" in code.lower():
            return self.fifo.detect_issues(code)
        elif protocol == "axi" or "axi" in code.lower():
            return self.axi.detect_issues(code)
        elif protocol == "apb" or "apb" in code.lower():
            return self.apb.detect_issues(code)
        
        # Try to auto-detect
        issues = []
        code_lower = code.lower()
        
        if "fifo" in code_lower or ("rd_ptr" in code_lower and "wr_ptr" in code_lower):
            issues.extend(self.fifo.detect_issues(code))
        if "axi" in code_lower or ("awvalid" in code_lower or "arvalid" in code_lower):
            issues.extend(self.axi.detect_issues(code))
        if "apb" in code_lower or ("psel" in code_lower and "penable" in code_lower):
            issues.extend(self.apb.detect_issues(code))
        
        return issues
    
    def generate_assertion(self, request: str) -> str:
        """Generate assertion based on request.
        
        Args:
            request: User request for assertion
            
        Returns:
            Generated assertion
        """
        request_lower = request.lower()
        
        if "fifo" in request_lower:
            if "empty" in request_lower and "read" in request_lower:
                return self.fifo.assert_no_read_when_empty()
            if "full" in request_lower and "write" in request_lower:
                return self.fifo.assert_no_write_when_full()
            if "reset" in request_lower:
                return self.fifo.assert_reset_clears_pointers()
            return self.fifo.assert_data_integrity()
        
        if "axi" in request_lower:
            if "valid" in request_lower and "ready" in request_lower:
                return self.axi.assert_valid_wait_ready()
            if "stable" in request_lower:
                return self.axi.assert_payload_stable()
            if "reset" in request_lower:
                return self.axi.assert_reset_clears_channels()
            return self.axi.assert_response_consumed()
        
        if "apb" in request_lower:
            if "enable" in request_lower:
                return self.apb.assert_enable_timing()
            if "ready" in request_lower:
                return self.apb.assert_ready_completes_transfer()
            return self.apb.assert_address_stable()
        
        # Generic assertion
        return self.assertions.generate_valid_ready_assertion("valid", "ready")
    
    def get_coverage(self, topic: str) -> List[str]:
        """Get coverage suggestions for topic.
        
        Args:
            topic: Topic (fifo, axi, apb, reset, fsm)
            
        Returns:
            List of coverage suggestions
        """
        topic_lower = topic.lower()
        
        if topic_lower == "fifo":
            return self.fifo.get_coverage_suggestions()
        elif topic_lower == "axi":
            return self.axi.get_coverage_suggestions()
        elif topic_lower == "apb":
            return self.apb.get_coverage_suggestions()
        elif topic_lower == "reset":
            return self.coverage.generate_reset_coverage()
        elif topic_lower == "fsm":
            return self.coverage.generate_fsm_coverage(["IDLE", "ACTIVE", "DONE"])
        else:
            return self.coverage.generate_fifo_coverage()
    
    def get_test_plan(self, component: str) -> str:
        """Get test plan for component.
        
        Args:
            component: Component name
            
        Returns:
            Formatted test plan
        """
        component_lower = component.lower()
        
        if component_lower == "fifo":
            plan = self.fifo.get_test_plan()
        elif component_lower == "axi":
            plan = self.axi.get_test_plan()
        elif component_lower == "apb":
            plan = self.apb.get_test_plan()
        else:
            plan = self.testplan.generate_test_plan(
                component=component,
                objective=f"Verify {component} functionality",
                features=["basic operation", "corner cases"],
                corner_cases=["boundary conditions"]
            )
        
        return self.testplan.format_testplan(plan)
    
    def generate_bug_report(
        self,
        title: str,
        description: str,
        severity: str = "MEDIUM",
        component: str = "Unknown"
    ) -> str:
        """Generate bug report.
        
        Args:
            title: Bug title
            description: Bug description
            severity: Severity level
            component: Component name
            
        Returns:
            Formatted bug report
        """
        report = self.bug_report.generate_bug_report(
            title=title,
            description=description,
            severity=severity,
            component=component
        )
        return self.bug_report.format_bug_report(report)
    
    def get_interview_question(self, topic: str = None) -> str:
        """Get interview question.
        
        Args:
            topic: Optional topic filter
            
        Returns:
            Formatted question and answer
        """
        qa = self.interview.get_random_question(topic)
        return self.interview.format_question(qa)
    
    def get_daily_challenge(self) -> str:
        """Get daily DV challenge.
        
        Returns:
            Challenge description
        """
        challenges = [
            "Write an SVA assertion to prevent FIFO overflow.",
            "Identify the AXI handshake protocol violation in this scenario: AWVALID is asserted but never deasserted even without AWREADY.",
            "Generate functional coverage points for an APB slave with wait states.",
            "Explain why Gray code is used for async FIFO pointers.",
            "Write a test plan for a simple FSM with IDLE, ACTIVE, DONE states.",
            "What's the difference between blocking and non-blocking assignments?",
            "Generate a bug report for: 'My AXI write transaction hangs - BVALID never asserted'.",
            "Write an SVA assertion for APB PENABLE timing.",
            "What coverage points would you add for a reset sequence?",
            "Explain the UVM build vs connect phase."
        ]
        
        import random
        challenge = random.choice(challenges)
        
        return f"""DV SENTINEL DAILY CHALLENGE
━━━━━━━━━━━━━━━━━━━━━━━━

{challenge}

Think about it, then ask me for hints or solutions!
Use /interview for more DV questions."""
