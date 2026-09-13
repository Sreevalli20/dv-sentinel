"""Coverage engine for DV Sentinel."""

from typing import List, Dict, Any


class CoverageEngine:
    """Generates functional coverage suggestions for DV."""
    
    @staticmethod
    def generate_fifo_coverage() -> List[str]:
        """Generate FIFO coverage suggestions."""
        return [
            "FIFO depth: empty, almost_empty, normal, almost_full, full",
            "Read operations: single, burst, back-to-back",
            "Write operations: single, burst, back-to-back",
            "Simultaneous read and write",
            "Reset scenarios: idle, active read, active write",
            "Corner cases: overflow attempt, underflow attempt",
            "Pointer wrap-around",
            "Data patterns: all zeros, all ones, walking ones, random"
        ]
    
    @staticmethod
    def generate_axi_coverage() -> List[str]:
        """Generate AXI coverage suggestions."""
        return [
            "Channel handshakes: AW, W, B, AR, R",
            "Burst lengths: 1, 4, 8, 16, INCR",
            "Burst sizes: 8, 16, 32, 64, 128, 256, 512, 1024 bits",
            "Response types: OKAY, EXOKAY, SLVERR, DECERR",
            "Outstanding transactions: 1, 2, 4, 8, 16",
            "Backpressure: READY deasserted on each channel",
            "Reset during active transaction on each channel",
            "Address alignment: aligned, unaligned",
            "Write strobes: all combinations",
            "Interleaved transactions"
        ]
    
    @staticmethod
    def generate_apb_coverage() -> List[str]:
        """Generate APB coverage suggestions."""
        return [
            "Transaction types: read, write",
            "Wait states: 0, 1, 2, 3, 4, 5+",
            "Error responses: no error, error",
            "Address ranges: low, mid, high",
            "Data patterns: zeros, ones, random, walking",
            "Back-to-back transfers",
            "Reset during SETUP phase",
            "Reset during ACCESS phase",
            "PSEL timing variations"
        ]
    
    @staticmethod
    def generate_fsm_coverage(states: List[str]) -> List[str]:
        """Generate FSM coverage suggestions.
        
        Args:
            states: List of FSM state names
        """
        coverage = [
            f"State visited: {state}" for state in states
        ]
        coverage.append("All state transitions covered")
        coverage.append("Reset to initial state")
        coverage.append("Illegal state transitions (negative)")
        return coverage
    
    @staticmethod
    def generate_reset_coverage() -> List[str]:
        """Generate reset coverage suggestions."""
        return [
            "Reset during idle state",
            "Reset during active transaction",
            "Reset during backpressure",
            "Reset assertion timing",
            "Reset deassertion timing",
            "Reset synchronization (if async)",
            "Reset recovery time",
            "Multiple reset cycles"
        ]
    
    @staticmethod
    def generate_handshake_coverage(valid: str, ready: str) -> List[str]:
        """Generate handshake coverage suggestions.
        
        Args:
            valid: Valid signal name
            ready: Ready signal name
        """
        return [
            f"{valid} before {ready}",
            f"{ready} before {valid}",
            f"{valid} and {ready} same cycle",
            f"{valid} asserted multiple cycles before {ready}",
            f"Backpressure: {ready} deasserted",
            f"Continuous transfers: {valid} asserted immediately after completion"
        ]
    
    @staticmethod
    def get_coverage_groups() -> Dict[str, List[str]]:
        """Get all coverage groups."""
        return {
            "fifo": CoverageEngine.generate_fifo_coverage(),
            "axi": CoverageEngine.generate_axi_coverage(),
            "apb": CoverageEngine.generate_apb_coverage(),
            "reset": CoverageEngine.generate_reset_coverage(),
            "handshake": CoverageEngine.generate_handshake_coverage("valid", "ready")
        }
