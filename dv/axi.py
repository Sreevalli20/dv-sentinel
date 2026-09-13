"""AXI analyzer for DV Sentinel."""

from typing import List, Dict, Any


class AXIAnalyzer:
    """Analyzes AXI4/AXI-Lite protocol issues."""
    
    @staticmethod
    def detect_issues(code: str) -> List[Dict[str, Any]]:
        """Detect common AXI issues in SystemVerilog code.
        
        Args:
            code: SystemVerilog code snippet
            
        Returns:
            List of detected issues with severity and description
        """
        issues = []
        code_lower = code.lower()
        
        # Check for VALID/READY handshake
        if "awvalid" in code_lower or "wvalid" in code_lower or "arvalid" in code_lower:
            if "ready" not in code_lower:
                issues.append({
                    "severity": "HIGH",
                    "title": "Missing READY signal",
                    "description": "VALID signal must wait for corresponding READY",
                    "suggested_fix": "Add READY signal and proper handshake logic",
                    "assertion": AXIAnalyzer.assert_valid_wait_ready()
                })
        
        # Check for payload stability
        if ("awvalid" in code_lower and "awaddr" in code_lower) or \
           ("wvalid" in code_lower and "wdata" in code_lower) or \
           ("arvalid" in code_lower and "araddr" in code_lower):
            if "stable" not in code_lower and "$stable" not in code_lower:
                issues.append({
                    "severity": "MEDIUM",
                    "title": "Payload stability not checked",
                    "description": "Address must remain stable while VALID is asserted",
                    "suggested_fix": "Add stability check on address signals",
                    "assertion": AXIAnalyzer.assert_payload_stable()
                })
        
        # Check for response consumption
        if "bvalid" in code_lower:
            if "bready" not in code_lower:
                issues.append({
                    "severity": "HIGH",
                    "title": "Response not consumed",
                    "description": "Write response must be consumed with BREADY",
                    "suggested_fix": "Add BREADY signal to consume response",
                    "assertion": AXIAnalyzer.assert_response_consumed()
                })
        
        # Check for reset blocking
        if "aresetn" in code_lower or "reset" in code_lower:
            if "reset" in code_lower and "valid" in code_lower:
                issues.append({
                    "severity": "MEDIUM",
                    "title": "Reset may block channel",
                    "description": "Reset should clear all pending transactions",
                    "suggested_fix": "Ensure reset clears VALID signals and state",
                    "assertion": AXIAnalyzer.assert_reset_clears_channels()
                })
        
        return issues
    
    @staticmethod
    def assert_valid_wait_ready() -> str:
        """Generate SVA assertion for VALID waiting for READY."""
        return """// Write Address Channel
assert property (
    @(posedge clk)
    awvalid |-> ##[0:$] awready
) else $error("AWVALID not followed by AWREADY");

// Write Data Channel
assert property (
    @(posedge clk)
    wvalid |-> ##[0:$] wready
) else $error("WVALID not followed by WREADY");

// Read Address Channel
assert property (
    @(posedge clk)
    arvalid |-> ##[0:$] arready
) else $error("ARVALID not followed by ARREADY");"""
    
    @staticmethod
    def assert_payload_stable() -> str:
        """Generate SVA assertion for payload stability."""
        return """assert property (
    @(posedge clk)
    awvalid && !awready |-> $stable(awaddr)
) else $error("AWADDR changed while AWVALID asserted");

assert property (
    @(posedge clk)
    wvalid && !wready |-> $stable(wdata)
) else $error("WDATA changed while WVALID asserted");"""
    
    @staticmethod
    def assert_response_consumed() -> str:
        """Generate SVA assertion for response consumption."""
        return """assert property (
    @(posedge clk)
    bvalid |-> ##[0:$] bready
) else $error("BVALID not followed by BREADY");

assert property (
    @(posedge clk)
    rvalid |-> ##[0:$] rready
) else $error("RVALID not followed by RREADY");"""
    
    @staticmethod
    def assert_reset_clears_channels() -> str:
        """Generate SVA assertion for reset clearing channels."""
        return """assert property (
    @(posedge clk)
    !aresetn |-> ##1 (!awvalid && !wvalid && !arvalid && !bvalid && !rvalid)
) else $error("Channels not cleared after reset");"""
    
    @staticmethod
    def get_coverage_suggestions() -> List[str]:
        """Get AXI coverage suggestions."""
        return [
            "Write address channel handshake",
            "Write data channel handshake",
            "Write response channel handshake",
            "Read address channel handshake",
            "Read data channel handshake",
            "Backpressure (READY deasserted)",
            "Burst lengths (1, 4, 8, 16)",
            "Response types (OKAY, EXOKAY, SLVERR, DECERR)",
            "Outstanding transactions",
            "Reset during transaction",
            "Interleaved transactions",
            "Single beat transfers",
            "Aligned vs unaligned addresses",
            "Write data strobes (WSTRB)"
        ]
    
    @staticmethod
    def get_test_plan() -> Dict[str, Any]:
        """Get AXI test plan."""
        return {
            "objective": "Verify AXI protocol compliance and functionality",
            "stimulus": [
                "Random write transactions",
                "Random read transactions",
                "Mixed read/write traffic",
                "Backpressure scenarios",
                "Burst transfers"
            ],
            "expected_behavior": [
                "All handshakes complete correctly",
                "Data integrity maintained",
                "Responses match transactions",
                "No protocol violations",
                "Reset clears all state"
            ],
            "corner_cases": [
                "Backpressure on each channel",
                "Reset during active transaction",
                "Maximum outstanding transactions",
                "Minimum burst length",
                "Maximum burst length",
                "Error response handling"
            ],
            "assertions": [
                "VALID waits for READY",
                "Payload stable during handshake",
                "Response consumed",
                "Reset clears channels"
            ],
            "functional_coverage": AXIAnalyzer.get_coverage_suggestions(),
            "negative_tests": [
                "VALID dropped before READY",
                "Payload changes during handshake",
                "Response not consumed",
                "Protocol violation injection"
            ],
            "reset_scenarios": [
                "Reset during write address",
                "Reset during write data",
                "Reset during read address",
                "Reset during read data",
                "Reset during response"
            ],
            "exit_criteria": [
                "All assertions pass",
                "Coverage > 95%",
                "No protocol violations",
                "All response types tested"
            ]
        }
    
    @staticmethod
    def explain_deadlock(code: str) -> str:
        """Explain potential AXI deadlock scenarios."""
        return """Common AXI Deadlock Causes:

1. VALID dropped before READY
   - Master deasserts VALID before slave asserts READY
   - Fix: Keep VALID asserted until handshake completes

2. READY never asserted
   - Slave never ready to accept transaction
   - Fix: Check slave flow control and backpressure

3. Response not consumed
   - Master doesn't assert BREADY/RREADY
   - Fix: Ensure master consumes all responses

4. Reset blocking channel
   - Reset stuck active or not properly synchronized
   - Fix: Verify reset assertion/deassertion timing

5. Outstanding transaction limit
   - Too many transactions pending without responses
   - Fix: Implement transaction counting and throttling"""
