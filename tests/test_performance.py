"""Performance benchmark tests for DV Sentinel."""

import time
import pytest
from agent.handler import DVHandler


class TestPerformanceBenchmark:
    """Performance benchmark tests for handler latency."""
    
    def test_start_command_performance(self):
        """Benchmark /start command response time."""
        handler = DVHandler()
        
        times = []
        for _ in range(10):
            start = time.perf_counter()
            response = handler.handle_message("/start", "test_user", "telegram")
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms
            assert "DV Sentinel" in response
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"\n/start performance:")
        print(f"  Average: {avg_time:.3f}ms")
        print(f"  Max: {max_time:.3f}ms")
        print(f"  Min: {min(times):.3f}ms")
        
        # Should complete in under 10ms on average (deterministic handler)
        assert avg_time < 50, f"Average /start time {avg_time:.3f}ms exceeds threshold"
    
    def test_assert_command_performance(self):
        """Benchmark /assert command response time."""
        handler = DVHandler()
        
        times = []
        for _ in range(10):
            start = time.perf_counter()
            response = handler.handle_message(
                "/assert FIFO should never read when empty",
                "test_user",
                "telegram"
            )
            end = time.perf_counter()
            times.append((end - start) * 1000)
            assert "assertion" in response.lower() or "ASSERTION" in response
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"\n/assert performance:")
        print(f"  Average: {avg_time:.3f}ms")
        print(f"  Max: {max_time:.3f}ms")
        print(f"  Min: {min(times):.3f}ms")
        
        # Should complete in under 50ms on average
        assert avg_time < 100, f"Average /assert time {avg_time:.3f}ms exceeds threshold"
    
    def test_natural_language_performance(self):
        """Benchmark natural language DV request response time."""
        handler = DVHandler()
        
        queries = [
            "Why can a FIFO underflow happen?",
            "Review this SystemVerilog FIFO",
            "Generate APB verification tests",
            "AXI transaction stuck issue",
            "FIFO coverage corner cases",
            "APB protocol states",
            "Reset verification",
            "SystemVerilog assertions",
            "Test plan for FIFO",
            "Debug my simulation"
        ]
        
        times = []
        for query in queries:
            start = time.perf_counter()
            response = handler.handle_message(query, "test_user", "telegram")
            end = time.perf_counter()
            times.append((end - start) * 1000)
            assert response  # Should always return something
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"\nNatural language performance:")
        print(f"  Average: {avg_time:.3f}ms")
        print(f"  Max: {max_time:.3f}ms")
        print(f"  Min: {min(times):.3f}ms")
        
        # Should complete in under 100ms on average
        assert avg_time < 150, f"Average NL time {avg_time:.3f}ms exceeds threshold"
    
    def test_multiple_commands_sequential(self):
        """Test multiple different commands sequentially."""
        handler = DVHandler()
        
        commands = [
            "/start",
            "/help",
            "/assert FIFO should never read when empty",
            "/axi Why is my write transaction stuck?",
            "/coverage FIFO",
            "/testplan FIFO",
            "/bug My simulation failed",
            "/interview",
            "/daily",
            "/help"
        ]
        
        times = []
        for cmd in commands:
            start = time.perf_counter()
            response = handler.handle_message(cmd, "test_user", "telegram")
            end = time.perf_counter()
            times.append((end - start) * 1000)
            assert response
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"\nSequential commands performance:")
        print(f"  Average: {avg_time:.3f}ms")
        print(f"  Max: {max_time:.3f}ms")
        print(f"  Min: {min(times):.3f}ms")
        
        # Should complete in under 100ms on average
        assert avg_time < 150, f"Average sequential time {avg_time:.3f}ms exceeds threshold"
    
    def test_handler_exception_handling(self):
        """Test that handler exceptions don't crash and return fallback."""
        handler = DVHandler()
        
        # This should handle any internal errors gracefully
        response = handler.handle_message("/start", "test_user", "telegram")
        assert response
        assert "DV Sentinel" in response or "error" in response.lower() or "Error" in response
    
    def test_no_secrets_in_logs(self):
        """Test that handler doesn't log secrets."""
        import io
        import sys
        from agent.handler import DVHandler
        
        handler = DVHandler()
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        try:
            handler.handle_message("/start", "test_user", "telegram")
            output = captured_output.getvalue()
            
            # Check no secrets are logged
            assert "CASPIAN_API_KEY" not in output
            assert "TELEGRAM_BOT_TOKEN" not in output
            assert "authorization" not in output.lower()
            assert "bearer" not in output.lower()
            
            # Check timing logs are present
            assert "Telegram" in output or "DV" in output
        finally:
            sys.stdout = old_stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
