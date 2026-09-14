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
from .intent_engine import IntentEngine
from .response_generator import ResponseGenerator


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
        self.intent_engine = IntentEngine()
        self.response_generator = ResponseGenerator()
    
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
        
        # Simple keyword matching for backward compatibility with legacy tests
        if "fifo" in text_lower:
            return "fifo"
        if "apb" in text_lower:
            return "apb"
        if "axi" in text_lower:
            return "axi"
        
        # Use enhanced intent engine for domain detection
        domain, sub_intent, metadata = self.intent_engine.classify(text)
        
        # Map domain to legacy intent names for backward compatibility
        domain_mapping = {
            "fifo": "fifo",
            "axi": "axi",
            "apb": "apb",
            "sva": "assertion",
            "coverage": "coverage",
            "debugging": "bug",
            "testplan": "testplan",
            "reset": "reset",
            "cdc": "reset",
            "uvm": "review",
            "scoreboard": "bug",
            "constrained_random": "review",
            "regression": "bug"
        }
        
        return domain_mapping.get(domain, "general")
    
    def classify_intent(self, text: str) -> tuple:
        """Classify intent with enhanced engine.
        
        Args:
            text: User input text
            
        Returns:
            Tuple of (domain, sub_intent, metadata)
        """
        return self.intent_engine.classify(text)
    
    def generate_intelligent_response(self, text: str) -> str:
        """Generate intelligent response based on intent classification.
        
        Args:
            text: User input text
            
        Returns:
            Formatted response
        """
        domain, sub_intent, metadata = self.intent_engine.classify(text)
        return self.response_generator.generate_response(domain, sub_intent, metadata, text)
    
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
            {
                "challenge": "Debug an AXI write transaction that occasionally hangs. AWVALID is asserted but AWREADY stays low for extended periods.",
                "domain": "axi",
                "hint": "Check which handshake is stuck. Verify AWREADY assertion logic. Inspect outstanding transaction state.",
                "solution": "The slave may have backpressure or the AWREADY logic has a bug. Add assertions for AWVALID persistence and check that AWREADY is eventually asserted. Verify no deadlock in outstanding transaction tracking."
            },
            {
                "challenge": "Write an SVA property that prevents reading an empty FIFO.",
                "domain": "sva",
                "hint": "Use implication operator. Check empty flag and read enable.",
                "solution": "assert property (@(posedge clk) empty |-> !rd_en) else $error(\"FIFO read while empty\");"
            },
            {
                "challenge": "A synchronous FIFO has depth 16. Write and read pointers are 4 bits. What happens when pointers wrap around, and how should full and empty be distinguished?",
                "domain": "fifo",
                "hint": "4 bits address 0-15. Equal pointers are ambiguous. Need additional state.",
                "solution": "Use a phase/wrap bit. With 5-bit pointers: lower 4 bits = address, upper bit = phase. Equal full pointers = empty. Same address + opposite phase = full."
            },
            {
                "challenge": "My scoreboard reports a mismatch only after reset. Give me a systematic debug plan.",
                "domain": "scoreboard",
                "hint": "Check reset timing. Verify scoreboard reset. Check reference model reset.",
                "solution": "Verify reset clears all state in DUT, reference model, and scoreboard. Check that reset timing is aligned. Add assertions for post-reset state. Inspect waveform at reset release."
            },
            {
                "challenge": "How would you verify an AXI slave supporting eight outstanding transactions?",
                "domain": "axi",
                "hint": "Track outstanding count. Verify ID matching. Check ordering rules.",
                "solution": "Track outstanding transaction count per ID. Verify response ID matches request ID. Check ordering rules for same ID. Cover maximum outstanding transactions. Verify no ID exhaustion."
            },
            {
                "challenge": "Explain the difference between |-> and |=> in SVA with examples.",
                "domain": "sva",
                "hint": "Overlapping vs non-overlapping. Same cycle vs next cycle.",
                "solution": "|-> is overlapping implication (same cycle): req |-> ack. |=> is non-overlapping (next cycle): req |=> ack. Use |-> when consequent should be true immediately, |=> when there's a known cycle delay."
            },
            {
                "challenge": "My code coverage is 98% but functional coverage is only 72%. What should I do?",
                "domain": "coverage",
                "hint": "Code executed != intent verified. Identify missing functional scenarios.",
                "solution": "Identify uncovered functional bins. Determine if bins are unreachable or missing tests. Add targeted stimulus for uncovered scenarios. Use coverage closure rather than blind randomization."
            },
            {
                "challenge": "Create a functional coverage plan for FIFO empty, full, overflow, underflow, simultaneous read/write and pointer wraparound.",
                "domain": "coverage",
                "hint": "Define coverpoints for each condition. Use cross for combinations.",
                "solution": "covergroup fifo_cg; coverpoint empty; coverpoint full; coverpoint overflow; coverpoint underflow; cross empty, full, rd_en, wr_en; coverpoint wr_ptr[3:0] { bins wrap = (15 => 0); } endgroup"
            },
            {
                "challenge": "Explain the APB setup and access phases and give assertions for the transition.",
                "domain": "apb",
                "hint": "SETUP: PSEL=1, PENABLE=0. ACCESS: PSEL=1, PENABLE=1. PENABLE timing is critical.",
                "solution": "assert property (@(posedge clk) psel && !penable |=> penable); assert property (@(posedge clk) penable |-> ##[0:$] pready);"
            },
            {
                "challenge": "How would you verify an asynchronous FIFO crossing two unrelated clocks?",
                "domain": "cdc",
                "hint": "Gray code for pointers. Synchronizer stages. Metastability.",
                "solution": "Use Gray code for write and read pointers. Add 2-3 stage synchronizers for pointer crossing. Verify Gray encoding/decoding. Cover all Gray code transitions. Check CDC violations with tools."
            }
        ]
        
        import random
        challenge = random.choice(challenges)
        
        return f"""DV SENTINEL DAILY CHALLENGE
━━━━━━━━━━━━━━━━━━━━━━━━

{challenge['challenge']}

**Domain:** {challenge['domain'].upper()}

**Hint:** {challenge['hint']}

Think about it, then ask me for the solution!
Use /interview for more DV questions."""
