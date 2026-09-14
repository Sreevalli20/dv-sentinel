"""Enhanced intent engine for DV Sentinel - Natural language intent classification."""

from typing import Dict, List, Tuple, Optional
import re


class IntentEngine:
    """Sophisticated intent classifier for DV technical questions."""
    
    # Domain-specific keyword patterns
    FIFO_KEYWORDS = [
        "depth", "pointer", "width", "address", "wrap", "wraparound", "full", "empty",
        "almost full", "almost empty", "overflow", "underflow", "simultaneous", "reset",
        "synchronization", "occupancy", "phase", "gray code", "asynchronous", "synchronous",
        "boundary", "rd_ptr", "wr_ptr", "read pointer", "write pointer"
    ]
    
    AXI_KEYWORDS = [
        "awvalid", "arvalid", "wvalid", "bvalid", "rvalid",
        "awready", "arready", "wready", "bready", "rready",
        "awid", "arid", "wid", "rid", "bid",
        "awaddr", "araddr", "wdata", "rdata",
        "awlen", "arlen", "awsize", "arsize",
        "awburst", "arburst", "awlock", "arlock",
        "awcache", "arcache", "awprot", "arprot",
        "awqos", "arqos", "awregion", "arregion",
        "wstrb", "rlast", "wlast",
        "bresp", "rresp", "rid",
        "outstanding", "ordering", "backpressure", "interleaving",
        "axi", "handshake", "protocol", "valid", "ready", "burst", "len", "size"
    ]
    
    APB_KEYWORDS = [
        "psel", "penable", "pready", "paddr", "pwrite", "pwdata", "prdata", "pslverr",
        "setup", "access", "wait state", "phase"
    ]
    
    SVA_KEYWORDS = [
        "assert", "assertion", "sva", "property", "|->", "|=>", "##", "$past", "$rose",
        "$fell", "$stable", "throughout", "until", "disable iff", "implication", "sequence"
    ]
    
    COVERAGE_KEYWORDS = [
        "coverage", "functional coverage", "code coverage", "assertion coverage",
        "toggle coverage", "bins", "illegal_bins", "ignore_bins", "cross coverage",
        "coverage closure", "coverage hole"
    ]
    
    DEBUGGING_KEYWORDS = [
        "timeout", "hang", "mismatch", "scoreboard", "intermittent", "failure",
        "random seed", "regression", "waveform", "assertion failure", "race", "reset",
        "x propagation", "deadlock", "debug", "bug"
    ]
    
    TESTPLAN_KEYWORDS = [
        "test plan", "testplan", "verification plan", "test scenario", "test case",
        "directed test", "constrained random", "negative test"
    ]
    
    RESET_KEYWORDS = [
        "reset", "synchronous reset", "asynchronous reset", "reset during", "reset release",
        "initialization", "pointer reset", "state reset"
    ]
    
    CDC_KEYWORDS = [
        "cdc", "clock domain crossing", "metastability", "synchronizer", "gray code",
        "async fifo", "pulse synchronization", "handshake synchronization"
    ]
    
    UVM_KEYWORDS = [
        "uvm", "driver", "monitor", "sequencer", "sequence", "agent", "env", "scoreboard",
        "factory", "config_db", "objection", "build phase", "connect phase", "run phase"
    ]
    
    SCOREBOARD_KEYWORDS = [
        "scoreboard", "reference model", "mismatch", "expected", "actual", "comparison"
    ]
    
    CONSTRAINED_RANDOM_KEYWORDS = [
        "constrained random", "rand", "randc", "constraint", "randomization", "solve",
        "pre_randomize", "post_randomize"
    ]
    
    REGRESSION_KEYWORDS = [
        "regression", "test suite", "test run", "seed", "randomization", "coverage goal"
    ]
    
    @staticmethod
    def classify(text: str) -> Tuple[str, str, Dict[str, any]]:
        """Classify user intent with domain and sub-intent.
        
        Args:
            text: User input text
            
        Returns:
            Tuple of (domain, sub_intent, metadata)
        """
        text_lower = text.lower()
        
        # Check for reset first (high priority) - but only if it's the main topic
        # Don't trigger if reset is just mentioned in passing (e.g., "after reset", "corner cases")
        reset_keywords = ["reset verification", "reset timing", "reset assertion", "reset behavior", 
                         "asynchronous reset", "synchronous reset", "reset deassertion", "reset synchronization"]
        if any(kw in text_lower for kw in reset_keywords):
            return "reset", IntentEngine._extract_sub_intent(text_lower, "reset")[0], {}
        
        # Check for UVM
        if "uvm" in text_lower or "factory" in text_lower or "sequencer" in text_lower or "driver" in text_lower or "monitor" in text_lower:
            return "uvm", IntentEngine._extract_sub_intent(text_lower, "uvm")[0], {}
        
        # Score each domain for protocol-specific questions
        scores = {
            "fifo": IntentEngine._score_domain(text_lower, IntentEngine.FIFO_KEYWORDS),
            "axi": IntentEngine._score_domain(text_lower, IntentEngine.AXI_KEYWORDS),
            "apb": IntentEngine._score_domain(text_lower, IntentEngine.APB_KEYWORDS),
            "sva": IntentEngine._score_domain(text_lower, IntentEngine.SVA_KEYWORDS),
            "coverage": IntentEngine._score_domain(text_lower, IntentEngine.COVERAGE_KEYWORDS),
            "debugging": IntentEngine._score_domain(text_lower, IntentEngine.DEBUGGING_KEYWORDS),
            "testplan": IntentEngine._score_domain(text_lower, IntentEngine.TESTPLAN_KEYWORDS),
            "reset": IntentEngine._score_domain(text_lower, IntentEngine.RESET_KEYWORDS),
            "cdc": IntentEngine._score_domain(text_lower, IntentEngine.CDC_KEYWORDS),
            "uvm": IntentEngine._score_domain(text_lower, IntentEngine.UVM_KEYWORDS),
            "scoreboard": IntentEngine._score_domain(text_lower, IntentEngine.SCOREBOARD_KEYWORDS),
            "constrained_random": IntentEngine._score_domain(text_lower, IntentEngine.CONSTRAINED_RANDOM_KEYWORDS),
            "regression": IntentEngine._score_domain(text_lower, IntentEngine.REGRESSION_KEYWORDS),
        }
        
        # Find highest scoring domain
        max_score = max(scores.values())
        if max_score == 0:
            return "general", "unknown", {}
        
        domain = max(scores, key=scores.get)
        
        # Extract sub-intent based on domain
        sub_intent, metadata = IntentEngine._extract_sub_intent(text_lower, domain)
        
        return domain, sub_intent, metadata
    
    @staticmethod
    def _score_domain(text: str, keywords: List[str]) -> int:
        """Score domain relevance based on keyword matches."""
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 1
        return score
    
    @staticmethod
    def _extract_sub_intent(text: str, domain: str) -> Tuple[str, Dict[str, any]]:
        """Extract sub-intent and metadata for a domain."""
        metadata = {}
        
        if domain == "fifo":
            return IntentEngine._extract_fifo_intent(text, metadata)
        elif domain == "axi":
            return IntentEngine._extract_axi_intent(text, metadata)
        elif domain == "apb":
            return IntentEngine._extract_apb_intent(text, metadata)
        elif domain == "sva":
            return IntentEngine._extract_sva_intent(text, metadata)
        elif domain == "coverage":
            return IntentEngine._extract_coverage_intent(text, metadata)
        elif domain == "debugging":
            return IntentEngine._extract_debugging_intent(text, metadata)
        elif domain == "testplan":
            return IntentEngine._extract_testplan_intent(text, metadata)
        elif domain == "reset":
            return IntentEngine._extract_reset_intent(text, metadata)
        elif domain == "cdc":
            return IntentEngine._extract_cdc_intent(text, metadata)
        elif domain == "uvm":
            return IntentEngine._extract_uvm_intent(text, metadata)
        elif domain == "scoreboard":
            return IntentEngine._extract_scoreboard_intent(text, metadata)
        elif domain == "constrained_random":
            return IntentEngine._extract_constrained_random_intent(text, metadata)
        elif domain == "regression":
            return IntentEngine._extract_regression_intent(text, metadata)
        
        return "general", metadata
    
    @staticmethod
    def _extract_fifo_intent(text: str, metadata: Dict) -> Tuple[str, Dict]:
        """Extract FIFO-specific intent."""
        # Check for pointer wraparound questions
        if "wrap" in text or "wraparound" in text:
            if "pointer" in text:
                metadata["concept"] = "pointer_wraparound"
                return "pointer_wraparound", metadata
        
        # Check for depth/width questions
        if "depth" in text or "width" in text or "address" in text:
            metadata["concept"] = "depth_width"
            return "depth_width", metadata
        
        # Check for full/empty distinction
        if "full" in text and "empty" in text:
            metadata["concept"] = "full_empty_distinction"
            return "full_empty_distinction", metadata
        
        # Check for overflow/underflow
        if "overflow" in text or "underflow" in text:
            metadata["concept"] = "overflow_underflow"
            return "overflow_underflow", metadata
        
        # Check for async FIFO
        if "async" in text or "asynchronous" in text:
            metadata["concept"] = "async_fifo"
            return "async_fifo", metadata
        
        # Check for Gray code
        if "gray" in text or "grey" in text:
            metadata["concept"] = "gray_code"
            return "gray_code", metadata
        
        return "general_fifo", metadata
    
    @staticmethod
    def _extract_axi_intent(text: str, metadata: Dict) -> Tuple[str, Dict]:
        """Extract AXI-specific intent."""
        # Check for deadlock/hang questions
        if "deadlock" in text or "hang" in text or "stuck" in text:
            metadata["concept"] = "deadlock"
            return "deadlock", metadata
        
        # Check for backpressure
        if "backpressure" in text or "ready" in text:
            metadata["concept"] = "backpressure"
            return "backpressure", metadata
        
        # Check for outstanding transactions
        if "outstanding" in text:
            metadata["concept"] = "outstanding"
            return "outstanding", metadata
        
        # Check for burst questions
        if "burst" in text:
            metadata["concept"] = "burst"
            return "burst", metadata
        
        # Check for VALID/READY protocol
        if "valid" in text and "ready" in text:
            metadata["concept"] = "valid_ready"
            return "valid_ready", metadata
        
        return "general_axi", metadata
    
    @staticmethod
    def _extract_apb_intent(text: str, metadata: Dict) -> Tuple[str, Dict]:
        """Extract APB-specific intent."""
        # Check for protocol phases
        if "setup" in text or "access" in text or "phase" in text:
            metadata["concept"] = "protocol_phases"
            return "protocol_phases", metadata
        
        # Check for PENABLE timing
        if "penable" in text:
            metadata["concept"] = "penable_timing"
            return "penable_timing", metadata
        
        # Check for wait states
        if "wait" in text or "pready" in text:
            metadata["concept"] = "wait_states"
            return "wait_states", metadata
        
        return "general_apb", metadata
    
    @staticmethod
    def _extract_sva_intent(text: str, metadata: Dict) -> Tuple[str, Dict]:
        """Extract SVA-specific intent."""
        # Check for specific operators
        if "|->" in text or "|=>" in text:
            metadata["concept"] = "implication"
            return "implication", metadata
        
        if "##" in text:
            metadata["concept"] = "delay"
            return "delay", metadata
        
        if "$stable" in text:
            metadata["concept"] = "stability"
            return "stability", metadata
        
        # Check for assertion request
        if "write" in text and "assertion" in text:
            metadata["concept"] = "write_assertion"
            return "write_assertion", metadata
        
        return "general_sva", metadata
    
    @staticmethod
    def _extract_coverage_intent(text: str, metadata: Dict) -> Tuple[str, Dict]:
        """Extract coverage-specific intent."""
        # Check for code vs functional coverage
        if "code" in text and "functional" in text:
            metadata["concept"] = "code_vs_functional"
            return "code_vs_functional", metadata
        
        # Check for coverage holes
        if "hole" in text or "gap" in text or "missing" in text:
            metadata["concept"] = "coverage_holes"
            return "coverage_holes", metadata
        
        # Check for coverage closure
        if "closure" in text or "target" in text:
            metadata["concept"] = "coverage_closure"
            return "coverage_closure", metadata
        
        return "general_coverage", metadata
    
    @staticmethod
    def _extract_debugging_intent(text: str, metadata: Dict) -> Tuple[str, Dict]:
        """Extract debugging-specific intent."""
        # Check for specific failure types
        if "timeout" in text:
            metadata["concept"] = "timeout"
            return "timeout", metadata
        
        if "hang" in text or "stuck" in text:
            metadata["concept"] = "hang"
            return "hang", metadata
        
        if "mismatch" in text:
            metadata["concept"] = "mismatch"
            return "mismatch", metadata
        
        if "intermittent" in text or "random" in text:
            metadata["concept"] = "intermittent"
            return "intermittent", metadata
        
        if "reset" in text:
            metadata["concept"] = "reset_issue"
            return "reset_issue", metadata
        
        return "general_debugging", metadata
    
    @staticmethod
    def _extract_testplan_intent(text: str, metadata: Dict) -> Tuple[str, Dict]:
        """Extract testplan-specific intent."""
        # Extract component if mentioned
        for component in ["fifo", "axi", "apb", "uvm"]:
            if component in text:
                metadata["component"] = component
                return f"{component}_testplan", metadata
        
        return "general_testplan", metadata
    
    @staticmethod
    def _extract_reset_intent(text: str, metadata: Dict) -> Tuple[str, Dict]:
        """Extract reset-specific intent."""
        if "async" in text or "asynchronous" in text:
            metadata["concept"] = "async_reset"
            return "async_reset", metadata
        
        if "synchronous" in text:
            metadata["concept"] = "sync_reset"
            return "sync_reset", metadata
        
        return "general_reset", metadata
    
    @staticmethod
    def _extract_cdc_intent(text: str, metadata: Dict) -> Tuple[str, Dict]:
        """Extract CDC-specific intent."""
        if "gray" in text or "grey" in text:
            metadata["concept"] = "gray_code"
            return "gray_code", metadata
        
        if "synchronizer" in text:
            metadata["concept"] = "synchronizer"
            return "synchronizer", metadata
        
        if "metastability" in text:
            metadata["concept"] = "metastability"
            return "metastability", metadata
        
        return "general_cdc", metadata
    
    @staticmethod
    def _extract_uvm_intent(text: str, metadata: Dict) -> Tuple[str, Dict]:
        """Extract UVM-specific intent."""
        if "phase" in text:
            metadata["concept"] = "phases"
            return "phases", metadata
        
        if "factory" in text:
            metadata["concept"] = "factory"
            return "factory", metadata
        
        if "driver" in text or "monitor" in text or "sequencer" in text:
            metadata["concept"] = "components"
            return "components", metadata
        
        return "general_uvm", metadata
    
    @staticmethod
    def _extract_scoreboard_intent(text: str, metadata: Dict) -> Tuple[str, Dict]:
        """Extract scoreboard-specific intent."""
        if "mismatch" in text:
            metadata["concept"] = "mismatch"
            return "mismatch", metadata
        
        if "reference" in text:
            metadata["concept"] = "reference_model"
            return "reference_model", metadata
        
        return "general_scoreboard", metadata
    
    @staticmethod
    def _extract_constrained_random_intent(text: str, metadata: Dict) -> Tuple[str, Dict]:
        """Extract constrained random-specific intent."""
        if "constraint" in text:
            metadata["concept"] = "constraints"
            return "constraints", metadata
        
        if "rand" in text or "randc" in text:
            metadata["concept"] = "randomization"
            return "randomization", metadata
        
        return "general_constrained_random", metadata
    
    @staticmethod
    def _extract_regression_intent(text: str, metadata: Dict) -> Tuple[str, Dict]:
        """Extract regression-specific intent."""
        if "seed" in text:
            metadata["concept"] = "seed"
            return "seed", metadata
        
        if "failure" in text:
            metadata["concept"] = "failure"
            return "failure", metadata
        
        return "general_regression", metadata
