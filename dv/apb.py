"""APB analyzer for DV Sentinel."""

from typing import List, Dict, Any


class APBAnalyzer:
    """Analyzes APB protocol issues."""
    
    @staticmethod
    def detect_issues(code: str) -> List[Dict[str, Any]]:
        """Detect common APB issues in SystemVerilog code.
        
        Args:
            code: SystemVerilog code snippet
            
        Returns:
            List of detected issues with severity and description
        """
        issues = []
        code_lower = code.lower()
        
        # Check for PENABLE timing
        if "penable" in code_lower and "psel" in code_lower:
            if "setup" not in code_lower:
                issues.append({
                    "severity": "HIGH",
                    "title": "PENABLE timing violation",
                    "description": "PENABLE must not be asserted in SETUP phase",
                    "suggested_fix": "Ensure PENABLE follows PSEL with one cycle delay",
                    "assertion": APBAnalyzer.assert_enable_timing()
                })
        
        # Check for PREADY handling
        if "penable" in code_lower and "pready" not in code_lower:
            issues.append({
                "severity": "HIGH",
                "title": "Missing PREADY signal",
                "description": "Slave must assert PREADY to complete transfer",
                "suggested_fix": "Add PREADY signal and wait state logic",
                "assertion": APBAnalyzer.assert_ready_completes_transfer()
            })
        
        # Check for PSLVERR
        if "penable" in code_lower and "pslverr" not in code_lower:
            issues.append({
                "severity": "MEDIUM",
                "title": "Missing PSLVERR signal",
                "description": "Error response should be supported",
                "suggested_fix": "Add PSLVERR for error reporting",
                "assertion": None
            })
        
        # Check for address stability
        if "paddr" in code_lower and "penable" in code_lower:
            if "stable" not in code_lower:
                issues.append({
                    "severity": "MEDIUM",
                    "title": "Address stability not checked",
                    "description": "Address must be stable during ACCESS phase",
                    "suggested_fix": "Add stability check on PADDR",
                    "assertion": APBAnalyzer.assert_address_stable()
                })
        
        return issues
    
    @staticmethod
    def assert_enable_timing() -> str:
        """Generate SVA assertion for PENABLE timing."""
        return """assert property (
    @(posedge clk)
    psel && !penable |=> penable
) else $error("PENABLE not asserted after PSEL");

assert property (
    @(posedge clk)
    !psel |-> !penable
) else $error("PENABLE asserted without PSEL");"""
    
    @staticmethod
    def assert_ready_completes_transfer() -> str:
        """Generate SVA assertion for PREADY completing transfer."""
        return """assert property (
    @(posedge clk)
    penable |-> ##[0:$] pready
) else $error("Transfer not completed (PREADY not asserted)");"""
    
    @staticmethod
    def assert_address_stable() -> str:
        """Generate SVA assertion for address stability."""
        return """assert property (
    @(posedge clk)
    penable && !pready |-> $stable(paddr)
) else $error("PADDR changed during ACCESS phase");

assert property (
    @(posedge clk)
    penable && !pready |-> $stable(pwrite)
) else $error("PWRITE changed during ACCESS phase");"""
    
    @staticmethod
    def get_coverage_suggestions() -> List[str]:
        """Get APB coverage suggestions."""
        return [
            "Read transactions",
            "Write transactions",
            "Single cycle transfers (PREADY=1)",
            "Multi-cycle transfers (PREADY=0)",
            "Wait states",
            "Error response (PSLVERR=1)",
            "Back-to-back transfers",
            "Address boundary cases",
            "Data width variations",
            "Setup phase timing",
            "Access phase timing"
        ]
    
    @staticmethod
    def get_test_plan() -> Dict[str, Any]:
        """Get APB test plan."""
        return {
            "objective": "Verify APB protocol compliance and functionality",
            "stimulus": [
                "Random read transactions",
                "Random write transactions",
                "Mixed read/write traffic",
                "Wait state injection",
                "Error response injection"
            ],
            "expected_behavior": [
                "Setup phase precedes enable",
                "Transfers complete on PREADY",
                "Address stable during access",
                "Data stable during access",
                "Error responses handled correctly"
            ],
            "corner_cases": [
                "Maximum wait states",
                "Back-to-back transfers",
                "Error during transfer",
                "Reset during transfer",
                "Minimum gap between transfers"
            ],
            "assertions": [
                "PENABLE timing",
                "PREADY completes transfer",
                "Address stability",
                "Data stability"
            ],
            "functional_coverage": APBAnalyzer.get_coverage_suggestions(),
            "negative_tests": [
                "PENABLE without PSEL",
                "Address change during access",
                "Data change during access",
                "Protocol violation injection"
            ],
            "reset_scenarios": [
                "Reset during SETUP phase",
                "Reset during ACCESS phase",
                "Reset during wait state"
            ],
            "exit_criteria": [
                "All assertions pass",
                "Coverage > 95%",
                "All wait states tested",
                "Error handling verified"
            ]
        }
    
    @staticmethod
    def explain_protocol() -> str:
        """Explain APB protocol states."""
        return """APB Protocol States:

1. IDLE
   - PSEL = 0, PENABLE = 0
   - No transfer in progress

2. SETUP
   - PSEL = 1, PENABLE = 0
   - Address and control signals driven
   - One cycle duration

3. ACCESS
   - PSEL = 1, PENABLE = 1
   - Transfer in progress
   - Stays asserted until PREADY = 1
   - Can have multiple wait states

Transfer Flow:
IDLE -> SETUP -> ACCESS (with wait states) -> IDLE

Key Rules:
- PENABLE must not be asserted in SETUP
- Address must be stable during ACCESS
- PREADY indicates transfer completion
- PSLVERR indicates error response"""
