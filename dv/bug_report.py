"""Bug report generator for DV Sentinel."""

from typing import Dict, Any


class BugReportGenerator:
    """Generates structured bug reports from DV issues."""
    
    @staticmethod
    def generate_bug_report(
        title: str,
        description: str,
        severity: str = "MEDIUM",
        component: str = "Unknown",
        evidence: str = "",
        suggested_fix: str = ""
    ) -> Dict[str, Any]:
        """Generate a structured bug report.
        
        Args:
            title: Bug title
            description: Bug description
            severity: LOW, MEDIUM, HIGH, CRITICAL
            component: Component name
            evidence: Evidence of the bug
            suggested_fix: Suggested fix
        """
        return {
            "title": title,
            "severity": severity.upper(),
            "component": component,
            "environment": "Simulation",
            "steps_to_reproduce": [
                "1. Describe the test scenario",
                "2. Provide stimulus",
                "3. Observe failure"
            ],
            "observed_result": description,
            "expected_result": "Expected behavior not specified",
            "likely_root_cause": BugReportGenerator._analyze_cause(description),
            "evidence_needed": evidence or "Waveforms, log files, test case",
            "suggested_regression_test": BugReportGenerator._suggest_test(component),
            "suggested_assertion": BugReportGenerator._suggest_assertion(component)
        }
    
    @staticmethod
    def _analyze_cause(description: str) -> str:
        """Analyze likely cause from description."""
        desc_lower = description.lower()
        
        if "fifo" in desc_lower:
            if "empty" in desc_lower and "read" in desc_lower:
                return "Read enable asserted when FIFO empty"
            if "full" in desc_lower and "write" in desc_lower:
                return "Write enable asserted when FIFO full"
            return "FIFO pointer or flag logic error"
        
        if "axi" in desc_lower:
            if "valid" in desc_lower and "ready" in desc_lower:
                return "Handshake protocol violation"
            if "deadlock" in desc_lower:
                return "Channel deadlock - check READY/VALID timing"
            return "AXI protocol violation"
        
        if "apb" in desc_lower:
            if "enable" in desc_lower:
                return "PENABLE timing violation"
            return "APB protocol violation"
        
        if "reset" in desc_lower:
            return "Reset logic or synchronization issue"
        
        if "assertion" in desc_lower:
            return "Assertion logic error"
        
        return "Logic error - requires further analysis"
    
    @staticmethod
    def _suggest_test(component: str) -> str:
        """Suggest regression test."""
        if "fifo" in component.lower():
            return "Directed test targeting the specific FIFO condition"
        if "axi" in component.lower():
            return "AXI protocol compliance test with specific scenario"
        if "apb" in component.lower():
            return "APB transfer test with specific timing"
        return "Directed test targeting the specific condition"
    
    @staticmethod
    def _suggest_assertion(component: str) -> str:
        """Suggest assertion."""
        if "fifo" in component.lower():
            return "Add SVA to check FIFO empty/full flags"
        if "axi" in component.lower():
            return "Add SVA to check AXI handshake protocol"
        if "apb" in component.lower():
            return "Add SVA to check APB timing"
        return "Add SVA to check the specific condition"
    
    @staticmethod
    def format_bug_report(report: Dict[str, Any]) -> str:
        """Format bug report for display.
        
        Args:
            report: Bug report dictionary
        """
        output = []
        output.append("DV SENTINEL BUG REPORT")
        output.append("=" * 50)
        output.append(f"\nTitle: {report.get('title', 'N/A')}")
        output.append(f"Severity: {report.get('severity', 'N/A')}")
        output.append(f"Component: {report.get('component', 'N/A')}")
        output.append(f"Environment: {report.get('environment', 'N/A')}")
        
        output.append("\nSteps to Reproduce:")
        for step in report.get("steps_to_reproduce", []):
            output.append(f"  {step}")
        
        output.append(f"\nObserved Result:\n  {report.get('observed_result', 'N/A')}")
        output.append(f"\nExpected Result:\n  {report.get('expected_result', 'N/A')}")
        
        output.append(f"\nLikely Root Cause:\n  {report.get('likely_root_cause', 'N/A')}")
        
        output.append(f"\nEvidence Needed:\n  {report.get('evidence_needed', 'N/A')}")
        
        output.append(f"\nSuggested Regression Test:\n  {report.get('suggested_regression_test', 'N/A')}")
        
        output.append(f"\nSuggested Assertion:\n  {report.get('suggested_assertion', 'N/A')}")
        
        return "\n".join(output)
