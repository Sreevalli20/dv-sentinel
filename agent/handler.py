"""Shared agent handler for DV Sentinel."""

import time
import traceback
from typing import Optional, Dict, Any
from dv.analyzer import DVAnalyzer
from storage.database import DatabaseManager


class DVHandler:
    """Shared handler for all channels (Telegram, Email)."""
    
    def __init__(self):
        self.analyzer = DVAnalyzer()
        self.db = DatabaseManager()
        # Use persistent connection for faster database operations
        self.db._conn = self.db._conn if self.db._conn else None
    
    def _log_timing(self, channel: str, stage: str, duration_ms: float):
        """Log timing information without secrets."""
        print(f"[Telegram] {stage} completed in {duration_ms:.3f}ms")
    
    def _safe_log_message(self, user_id: str, channel: str, content: str):
        """Safely log message without blocking on errors."""
        try:
            self.db.log_message(user_id, channel, content)
        except Exception as e:
            print(f"[Database] Warning: Failed to log message: {e}")
    
    def _safe_log_command(self, user_id: str, channel: str, command: str):
        """Safely log command without blocking on errors."""
        try:
            self.db.log_command(user_id, channel, command)
        except Exception as e:
            print(f"[Database] Warning: Failed to log command: {e}")
    
    def handle_message(
        self,
        text: str,
        user_id: str,
        channel: str = "unknown"
    ) -> str:
        """Handle incoming message from any channel.
        
        Args:
            text: Message text
            user_id: User identifier
            channel: Channel name (telegram, email)
            
        Returns:
            Response text
        """
        message_received = time.perf_counter()
        print(f"[Telegram] message received from {channel}")
        
        try:
            # Log message asynchronously (non-blocking)
            self._safe_log_message(user_id, channel, text)
            
            # Handle empty input
            if not text or not text.strip():
                handler_finished = time.perf_counter()
                self._log_timing(channel, "handler", (handler_finished - message_received) * 1000)
                return self._get_help_message()
            
            text = text.strip()
            handler_started = time.perf_counter()
            
            # Handle commands
            if text.startswith("/"):
                response = self._handle_command(text, user_id, channel)
            else:
                # Handle natural language
                response = self._handle_natural_language(text, user_id, channel)
            
            handler_finished = time.perf_counter()
            duration_ms = (handler_finished - handler_started) * 1000
            self._log_timing(channel, "DV processing", duration_ms)
            
            return response
            
        except Exception as e:
            # Log exception without secrets
            print(f"[Handler] ERROR: {type(e).__name__}: {str(e)[:100]}")
            traceback.print_exc()
            # Return fallback response
            return self._get_fallback_response()
    
    def _handle_command(self, text: str, user_id: str, channel: str) -> str:
        """Handle slash commands.
        
        Args:
            text: Command text
            user_id: User identifier
            channel: Channel name
            
        Returns:
            Response text
        """
        parts = text.split()
        command = parts[0].lower()
        args = " ".join(parts[1:]) if len(parts) > 1 else ""
        
        # Log command asynchronously (non-blocking)
        self._safe_log_command(user_id, channel, command)
        
        command_map = {
            "/start": self._cmd_start,
            "/help": self._cmd_help,
            "/status": self._cmd_status,
            "/verify": self._cmd_verify,
            "/assert": self._cmd_assert,
            "/debug": self._cmd_debug,
            "/testplan": self._cmd_testplan,
            "/coverage": self._cmd_coverage,
            "/axi": self._cmd_axi,
            "/apb": self._cmd_apb,
            "/fifo": self._cmd_fifo,
            "/bug": self._cmd_bug,
            "/interview": self._cmd_interview,
            "/daily": self._cmd_daily,
            "/reset": self._cmd_reset
        }
        
        handler = command_map.get(command)
        if handler:
            try:
                return handler(args, user_id, channel)
            except Exception as e:
                print(f"[Handler] Command {command} failed: {type(e).__name__}")
                return self._get_command_error_response(command)
        
        return f"Unknown command: {command}. Try /help for available commands."
    
    def _handle_natural_language(self, text: str, user_id: str, channel: str) -> str:
        """Handle natural language input.
        
        Args:
            text: Natural language text
            user_id: User identifier
            channel: Channel name
            
        Returns:
            Response text
        """
        try:
            intent = self.analyzer.detect_intent(text)
            
            # Store context asynchronously (non-blocking)
            try:
                self.db.store_context(user_id, {"intent": intent, "last_input": text})
            except Exception as e:
                print(f"[Database] Warning: Failed to store context: {e}")
            
            if intent == "fifo":
                return self._cmd_fifo(text, user_id, channel)
            elif intent == "axi":
                return self._cmd_axi(text, user_id, channel)
            elif intent == "apb":
                return self._cmd_apb(text, user_id, channel)
            elif intent == "assertion":
                return self._cmd_assert(text, user_id, channel)
            elif intent == "coverage":
                return self._cmd_coverage(text, user_id, channel)
            elif intent == "testplan":
                return self._cmd_testplan(text, user_id, channel)
            elif intent == "bug":
                return self._cmd_debug(text, user_id, channel)
            elif intent == "interview":
                return self._cmd_interview(text, user_id, channel)
            elif intent == "reset":
                return self._cmd_reset(text, user_id, channel)
            elif intent == "review":
                return self._cmd_verify(text, user_id, channel)
            
            # General response
            return self._get_general_response(text)
        except Exception as e:
            print(f"[Handler] Natural language processing failed: {type(e).__name__}")
            return self._get_fallback_response()
    
    def _cmd_start(self, args: str, user_id: str, channel: str) -> str:
        """Handle /start command."""
        return """Hi! I'm DV Sentinel, your Design Verification assistant.

I can help with:
• SystemVerilog review and analysis
• FIFO verification and debugging
• AXI protocol analysis
• APB protocol analysis
• SVA assertion generation
• Coverage planning
• Test plan generation
• Bug report generation
• DV interview questions
• Daily verification challenges

Try:
/assert FIFO should never read when empty
/axi Why is my write transaction stuck?
/coverage Give me FIFO corner cases
/testplan Create a FIFO test plan
/bug My simulation failed
/interview Ask me a DV question
/daily Daily verification challenge

Or just ask me a question in plain English!"""
    
    def _cmd_help(self, args: str, user_id: str, channel: str) -> str:
        """Handle /help command."""
        return """DV SENTINEL COMMANDS
━━━━━━━━━━━━━━━━━━━━

/start - Show welcome message
/help - Show this help
/status - Show system status

/verify <code> - Analyze SystemVerilog code
/assert <request> - Generate SVA assertion
/debug <issue> - Debug a problem
/testplan <component> - Generate test plan
/coverage <topic> - Get coverage suggestions

/axi <question> - AXI protocol help
/apb <question> - APB protocol help
/fifo <question> - FIFO verification help

/bug <description> - Generate bug report
/interview [topic] - DV interview question
/daily - Daily verification challenge
/reset <question> - Reset verification help

You can also just ask questions in plain English:
"Review this SystemVerilog FIFO"
"Why is my AXI transaction hanging?"
"Generate APB verification tests" """
    
    def _cmd_status(self, args: str, user_id: str, channel: str) -> str:
        """Handle /status command."""
        from app.config import config
        from channels.caspian import caspian_manager
        
        caspian_status = "Connected" if caspian_manager.is_available() else "Not connected"
        db_status = "OK" if self.db.is_healthy() else "Error"
        
        return """DV SENTINEL STATUS
━━━━━━━━━━━━━━━━━━

Version: {}
Channel: {}
Caspian: {}
Database: {}
Mode: {}""".format(
            config.APP_VERSION,
            channel,
            caspian_status,
            db_status,
            "Demo" if config.DEMO_MODE else "Production"
        )
    
    def _cmd_verify(self, args: str, user_id: str, channel: str) -> str:
        """Handle /verify command."""
        if not args:
            return "Please provide SystemVerilog code to analyze."
        
        issues = self.analyzer.analyze_code(args)
        
        if not issues:
            return "No issues detected in the provided code. Note: This is static pattern analysis, not formal verification."
        
        response = ["DV SENTINEL ANALYSIS", "=" * 40]
        for i, issue in enumerate(issues, 1):
            response.append(f"\n{i}. {issue.get('title', 'Issue')} [{issue.get('severity', 'MEDIUM')}]")
            response.append(f"   {issue.get('description', 'No description')}")
            if issue.get('suggested_fix'):
                response.append(f"   Fix: {issue['suggested_fix']}")
            if issue.get('assertion'):
                response.append(f"\n   Suggested Assertion:")
                response.append(f"   {issue['assertion']}")
        
        return "\n".join(response)
    
    def _cmd_assert(self, args: str, user_id: str, channel: str) -> str:
        """Handle /assert command."""
        if not args:
            return "Please describe the assertion you need. Example: /assert FIFO should never read when empty"
        
        assertion = self.analyzer.generate_assertion(args)
        
        return f"""DV SENTINEL ASSERTION
━━━━━━━━━━━━━━━━━━━

{assertion}

Note: Validate this assertion against your specific design requirements."""
    
    def _cmd_debug(self, args: str, user_id: str, channel: str) -> str:
        """Handle /debug command."""
        if not args:
            return "Please describe the issue. Example: /debug My AXI write transaction hangs"
        
        intent = self.analyzer.detect_intent(args)
        
        if intent == "axi":
            return self.analyzer.axi.explain_deadlock(args)
        
        # Generate a bug report
        report = self.analyzer.generate_bug_report(
            title="Debug Request",
            description=args,
            severity="MEDIUM",
            component=intent.upper() if intent else "Unknown"
        )
        
        return report
    
    def _cmd_testplan(self, args: str, user_id: str, channel: str) -> str:
        """Handle /testplan command."""
        if not args:
            return "Please specify a component. Example: /testplan FIFO"
        
        return self.analyzer.get_test_plan(args)
    
    def _cmd_coverage(self, args: str, user_id: str, channel: str) -> str:
        """Handle /coverage command."""
        topic = args if args else "fifo"
        coverage = self.analyzer.get_coverage(topic)
        
        response = [f"SUGGESTED COVERAGE: {topic.upper()}", "=" * 40]
        for item in coverage:
            response.append(f"• {item}")
        
        return "\n".join(response)
    
    def _cmd_axi(self, args: str, user_id: str, channel: str) -> str:
        """Handle /axi command."""
        if not args:
            return "Please ask an AXI question. Example: /axi Why is my write transaction stuck?"
        
        intent = self.analyzer.detect_intent(args)
        
        if "deadlock" in args.lower() or "stuck" in args.lower():
            return self.analyzer.axi.explain_deadlock(args)
        
        # Analyze if code is provided
        if "awvalid" in args.lower() or "arvalid" in args.lower():
            issues = self.analyzer.axi.detect_issues(args)
            if issues:
                response = ["AXI ANALYSIS", "=" * 30]
                for issue in issues:
                    response.append(f"\n{issue['title']}: {issue['description']}")
                    if issue.get('assertion'):
                        response.append(f"\n{issue['assertion']}")
                return "\n".join(response)
        
        return f"""AXI ANALYSIS
━━━━━━━━━━━

Common AXI Issues:
• VALID dropped before READY
• Payload unstable while waiting
• READY never asserted
• Response not consumed
• Reset blocking channel

For specific analysis, provide code or describe the issue.

Try: /axi Why is my write transaction stuck?"""
    
    def _cmd_apb(self, args: str, user_id: str, channel: str) -> str:
        """Handle /apb command."""
        if not args:
            return "Please ask an APB question. Example: /apb Explain the protocol states"
        
        # Analyze if code is provided
        if "penable" in args.lower() or "psel" in args.lower():
            issues = self.analyzer.apb.detect_issues(args)
            if issues:
                response = ["APB ANALYSIS", "=" * 30]
                for issue in issues:
                    response.append(f"\n{issue['title']}: {issue['description']}")
                    if issue.get('assertion'):
                        response.append(f"\n{issue['assertion']}")
                return "\n".join(response)
        
        return self.analyzer.apb.explain_protocol()
    
    def _cmd_fifo(self, args: str, user_id: str, channel: str) -> str:
        """Handle /fifo command."""
        if not args:
            return "Please ask a FIFO question. Example: /fifo How do I prevent overflow?"
        
        # Analyze if code is provided
        if "rd_ptr" in args.lower() or "wr_ptr" in args.lower():
            issues = self.analyzer.fifo.detect_issues(args)
            if issues:
                response = ["FIFO ANALYSIS", "=" * 30]
                for issue in issues:
                    response.append(f"\n{issue['title']}: {issue['description']}")
                    if issue.get('assertion'):
                        response.append(f"\n{issue['assertion']}")
                return "\n".join(response)
        
        return """FIFO ANALYSIS
━━━━━━━━━━━

Common FIFO Issues:
• Read while empty
• Write while full
• Pointer synchronization
• Reset initialization
• Overflow/underflow

Key Assertions:
• empty |-> !rd_en
• full |-> !wr_en
• reset clears pointers

For specific analysis, provide your FIFO code."""
    
    def _cmd_bug(self, args: str, user_id: str, channel: str) -> str:
        """Handle /bug command."""
        if not args:
            return "Please describe the bug. Example: /bug Simulation failed with timeout"
        
        return self.analyzer.generate_bug_report(
            title="Bug Report",
            description=args,
            severity="MEDIUM"
        )
    
    def _cmd_interview(self, args: str, user_id: str, channel: str) -> str:
        """Handle /interview command."""
        return self.analyzer.get_interview_question(args if args else None)
    
    def _cmd_daily(self, args: str, user_id: str, channel: str) -> str:
        """Handle /daily command."""
        return self.analyzer.get_daily_challenge()
    
    def _cmd_reset(self, args: str, user_id: str, channel: str) -> str:
        """Handle /reset command."""
        coverage = self.analyzer.get_coverage("reset")
        
        response = ["RESET VERIFICATION", "=" * 40]
        response.append("\nCoverage Points:")
        for item in coverage:
            response.append(f"• {item}")
        
        response.append("\n\nKey Assertion:")
        response.append(self.analyzer.assertions.generate_reset_assertion("signal"))
        
        return "\n".join(response)
    
    def _get_help_message(self) -> str:
        """Get help message for empty input."""
        return """I can help with SystemVerilog, FIFO, AXI, APB, assertions, coverage and DV test planning.

Try /help for available commands."""
    
    def _get_fallback_response(self) -> str:
        """Get fallback response for errors."""
        return """I encountered an error processing your request. Please try again.

If the problem persists, try:
• /start - Restart the conversation
• /help - See available commands
• /status - Check system status"""
    
    def _get_command_error_response(self, command: str) -> str:
        """Get error response for failed command."""
        return f"""Sorry, the /{command} command encountered an error.

Please try again or use /help for alternative commands."""
    
    def _get_general_response(self, text: str) -> str:
        """Get response for general queries."""
        return f"""I understand you're asking about: "{text}"

I can help with:
• SystemVerilog review
• FIFO verification
• AXI/APB protocol analysis
• SVA assertions
• Coverage planning
• Test plans
• Bug reports
• DV interview questions

Try /help for commands, or be more specific about your DV question."""
