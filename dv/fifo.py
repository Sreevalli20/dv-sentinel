"""FIFO analyzer for DV Sentinel."""

from typing import List, Dict, Any


class FIFOAnalyzer:
    """Analyzes FIFO-related issues and generates assertions."""
    
    @staticmethod
    def detect_issues(code: str) -> List[Dict[str, Any]]:
        """Detect common FIFO issues in SystemVerilog code.
        
        Args:
            code: SystemVerilog code snippet
            
        Returns:
            List of detected issues with severity and description
        """
        issues = []
        code_lower = code.lower()
        
        # Check for read while empty
        if "rd_en" in code_lower and "empty" in code_lower:
            if "!empty" not in code_lower and "empty == 0" not in code_lower:
                issues.append({
                    "severity": "HIGH",
                    "title": "Potential read while empty",
                    "description": "Read enable may be asserted when FIFO is empty",
                    "suggested_fix": "Add empty check: if (!empty) rd_en <= ...",
                    "assertion": FIFOAnalyzer.assert_no_read_when_empty()
                })
        
        # Check for write while full
        if "wr_en" in code_lower and "full" in code_lower:
            if "!full" not in code_lower and "full == 0" not in code_lower:
                issues.append({
                    "severity": "HIGH",
                    "title": "Potential write while full",
                    "description": "Write enable may be asserted when FIFO is full",
                    "suggested_fix": "Add full check: if (!full) wr_en <= ...",
                    "assertion": FIFOAnalyzer.assert_no_write_when_full()
                })
        
        # Check for pointer synchronization
        if "rd_ptr" in code_lower and "wr_ptr" in code_lower:
            if "gray" not in code_lower:
                issues.append({
                    "severity": "MEDIUM",
                    "title": "Missing Gray code encoding",
                    "description": "Read/write pointers should use Gray code for async FIFOs",
                    "suggested_fix": "Convert pointers to Gray code for clock domain crossing",
                    "assertion": None
                })
        
        # Check for reset initialization
        if "rd_ptr" in code_lower or "wr_ptr" in code_lower:
            if "reset" not in code_lower and "rst" not in code_lower:
                issues.append({
                    "severity": "MEDIUM",
                    "title": "Missing reset initialization",
                    "description": "Pointers should be reset to zero",
                    "suggested_fix": "Add reset logic: if (reset) rd_ptr <= 0;",
                    "assertion": FIFOAnalyzer.assert_reset_clears_pointers()
                })
        
        return issues
    
    @staticmethod
    def assert_no_read_when_empty() -> str:
        """Generate SVA assertion for no read when empty."""
        return """assert property (
    @(posedge clk)
    empty |-> !rd_en
) else $error("FIFO read while empty");"""
    
    @staticmethod
    def assert_no_write_when_full() -> str:
        """Generate SVA assertion for no write when full."""
        return """assert property (
    @(posedge clk)
    full |-> !wr_en
) else $error("FIFO write while full");"""
    
    @staticmethod
    def assert_reset_clears_pointers() -> str:
        """Generate SVA assertion for reset clearing pointers."""
        return """assert property (
    @(posedge clk)
    reset |-> ##1 (rd_ptr == 0 && wr_ptr == 0)
) else $error("FIFO pointers not cleared after reset");"""
    
    @staticmethod
    def assert_data_integrity() -> str:
        """Generate SVA assertion for data integrity."""
        return """assert property (
    @(posedge clk)
    !empty && rd_en |-> ##1 data_out == mem[rd_ptr]
) else $error("FIFO data integrity violation");"""
    
    @staticmethod
    def get_coverage_suggestions() -> List[str]:
        """Get FIFO coverage suggestions."""
        return [
            "FIFO empty state",
            "FIFO full state",
            "FIFO almost empty",
            "FIFO almost full",
            "Simultaneous read and write",
            "Read when empty (negative test)",
            "Write when full (negative test)",
            "Reset during active traffic",
            "Back-to-back reads",
            "Back-to-back writes",
            "Random read/write pattern",
            "Pointer wrap-around",
            "Overflow attempt",
            "Underflow attempt"
        ]
    
    @staticmethod
    def get_test_plan() -> Dict[str, Any]:
        """Get FIFO test plan."""
        return {
            "objective": "Verify FIFO functionality under all operating conditions",
            "stimulus": [
                "Random read/write transactions",
                "Back-to-back operations",
                "Reset during traffic",
                "Corner case sequences"
            ],
            "expected_behavior": [
                "Data written is read in FIFO order",
                "Empty flag correct when FIFO empty",
                "Full flag correct when FIFO full",
                "No data corruption",
                "Reset clears all state"
            ],
            "corner_cases": [
                "Read when empty",
                "Write when full",
                "Simultaneous read/write at boundaries",
                "Reset during full state",
                "Reset during empty state"
            ],
            "assertions": [
                "No read when empty",
                "No write when full",
                "Data integrity",
                "Reset clears pointers"
            ],
            "functional_coverage": FIFOAnalyzer.get_coverage_suggestions(),
            "negative_tests": [
                "Read enable when empty",
                "Write enable when full",
                "Invalid pointer values"
            ],
            "reset_scenarios": [
                "Reset during idle",
                "Reset during active read",
                "Reset during active write",
                "Reset during simultaneous operations"
            ],
            "exit_criteria": [
                "All assertions pass",
                "Coverage > 95%",
                "No data corruption",
                "All corner cases tested"
            ]
        }
