"""SystemVerilog assertion generator for DV Sentinel."""

from typing import List, Dict, Any


class AssertionGenerator:
    """Generates SVA assertions for common DV scenarios."""
    
    @staticmethod
    def generate_valid_ready_assertion(valid_signal: str, ready_signal: str) -> str:
        """Generate VALID/READY handshake assertion.
        
        Args:
            valid_signal: Name of valid signal
            ready_signal: Name of ready signal
        """
        return f"""assert property (
    @(posedge clk)
    {valid_signal} |-> ##[0:$] {ready_signal}
) else $error("{valid_signal} not followed by {ready_signal}");"""
    
    @staticmethod
    def generate_stability_assertion(signal: str, condition: str) -> str:
        """Generate signal stability assertion.
        
        Args:
            signal: Signal name to check for stability
            condition: Condition when signal should be stable
        """
        return f"""assert property (
    @(posedge clk)
    {condition} |-> $stable({signal})
) else $error("{signal} changed when it should be stable");"""
    
    @staticmethod
    def generate_reset_assertion(signal: str, reset_value: str = "0") -> str:
        """Generate reset assertion.
        
        Args:
            signal: Signal name
            reset_value: Expected value after reset
        """
        return f"""assert property (
    @(posedge clk)
    reset |-> ##1 ({signal} == {reset_value})
) else $error("{signal} not reset to {reset_value}");"""
    
    @staticmethod
    def generate_fsm_assertion(state_signal: str, transitions: Dict[str, List[str]]) -> str:
        """Generate FSM legal transition assertion.
        
        Args:
            state_signal: FSM state signal
            transitions: Dict mapping states to valid next states
        """
        conditions = []
        for from_state, to_states in transitions.items():
            if to_states:
                to_list = " || ".join([f"{state_signal} == {s}" for s in to_states])
                conditions.append(f"({state_signal} == {from_state} |=> {to_list})")
        
        if conditions:
            return f"""assert property (
    @(posedge clk)
    {" or ".join(conditions)}
) else $error("Illegal FSM transition");"""
        return "// No transitions defined"
    
    @staticmethod
    def generate_mutual_exclusion_assertion(signals: List[str]) -> str:
        """Generate mutual exclusion assertion.
        
        Args:
            signals: List of signals that should never be asserted together
        """
        if len(signals) < 2:
            return "// Need at least 2 signals for mutual exclusion"
        
        condition = " && ".join(signals)
        return f"""assert property (
    @(posedge clk)
    !({condition})
) else $error("Mutually exclusive signals asserted together");"""
    
    @staticmethod
    def generate_one_hot_assertion(signal: str) -> str:
        """Generate one-hot assertion.
        
        Args:
            signal: Signal that should be one-hot encoded
        """
        return f"""assert property (
    @(posedge clk)
    $onehot({signal})
) else $error("{signal} is not one-hot");"""
    
    @staticmethod
    def generate_sequence_assertion(sequence: str, name: str = "sequence") -> str:
        """Generate custom sequence assertion.
        
        Args:
            sequence: SVA sequence expression
            name: Name for the assertion
        """
        return f"""assert property (
    @(posedge clk)
    {sequence}
) else $error("{name} violated");"""
    
    @staticmethod
    def get_template_library() -> Dict[str, str]:
        """Get library of assertion templates."""
        return {
            "valid_ready": AssertionGenerator.generate_valid_ready_assertion("valid", "ready"),
            "data_stable": AssertionGenerator.generate_stability_assertion("data", "valid && !ready"),
            "reset_clear": AssertionGenerator.generate_reset_assertion("state"),
            "one_hot": AssertionGenerator.generate_one_hot_assertion("state"),
            "mutual_exclusion": AssertionGenerator.generate_mutual_exclusion_assertion(["req1", "req2"]),
            "eventually": """assert property (
    @(posedge clk)
    req |-> ##[1:10] ack
) else $error("Response not received within 10 cycles");"""
        }
