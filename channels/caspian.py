"""Caspian channel integration for DV Sentinel."""

import os
import threading
import time
from typing import Optional, Callable, Any
from app.config import config


class CaspianManager:
    """Manages Caspian SDK integration."""
    
    def __init__(self):
        self.cx = None
        self._initialized = False
        self._email_registered = False
        self._telegram_registered = False
        self._email_address = None
        self._running = False
        self._run_thread = None
        self._stop_event = threading.Event()
        self._last_poll_time = None
        self._poll_error_count = 0
        self._telegram_connection_id = None
    
    def initialize(self, message_handler: Callable) -> bool:
        """Initialize Caspian SDK.
        
        Args:
            message_handler: Function to handle incoming messages
            
        Returns:
            True if initialized successfully
        """
        if config.DEMO_MODE:
            print("[Caspian] Demo mode - skipping initialization")
            self._initialized = True
            return True
        
        if not config.CASPIAN_API_KEY:
            print("[Caspian] ERROR: CASPIAN_API_KEY not set")
            return False
        
        try:
            from caspian.facade.caspian import Caspian
            from caspian.facade.host import HandlerContext
            from caspian.facade.thread import Thread
            from caspian.core.types import Message
            
            print("[Caspian] Initializing SDK...")
            self.cx = Caspian(
                api_key=config.CASPIAN_API_KEY,
                base_url=config.CASPIAN_BASE_URL,
            )
            
            # Register message handler for all channels
            @self.cx.on_message()
            def handle_caspian_message(thread: Thread, msg: Message, ctx: HandlerContext) -> None:
                message_handler(thread, msg, ctx)
            
            self._initialized = True
            print("[Caspian] SDK initialized successfully")
            return True
            
        except ImportError as e:
            print(f"[Caspian] ERROR: Failed to import caspian SDK: {e}")
            return False
        except Exception as e:
            print(f"[Caspian] ERROR: Initialization failed: {e}")
            return False
    
    def add_email_channel(self, username: str) -> Optional[str]:
        """Add email channel.
        
        Args:
            username: Email username (part before @)
            
        Returns:
            Email address if successful, None otherwise
        """
        if not self._initialized or not self.cx:
            print("[Caspian] ERROR: Cannot add email channel - not initialized")
            return None
        
        try:
            print(f"[Caspian] Adding email channel for username: {username}")
            result = self.cx.channels.add("email", username=username)
            # Result may be a dict with 'address' or the address string directly
            if isinstance(result, dict):
                address = result.get("address")
            else:
                address = str(result) if result else None
            
            if address:
                self._email_registered = True
                self._email_address = address
                print(f"[Caspian] Email channel registered: {address}")
            else:
                print("[Caspian] ERROR: Email channel registration returned no address")
            return address
        except Exception as e:
            print(f"[Caspian] ERROR: Email channel addition failed: {e}")
            return None
    
    def add_telegram_channel(self, bot_token: str) -> bool:
        """Add Telegram channel.
        
        Args:
            bot_token: Telegram bot token from BotFather
            
        Returns:
            True if successful
        """
        if not self._initialized or not self.cx:
            print("[Caspian] ERROR: Cannot add Telegram channel - not initialized")
            return False
        
        try:
            print("[Caspian] Telegram registration started")
            result = self.cx.channels.add("telegram", bot_token=bot_token)
            # Result may be a dict with connection info or just success
            if isinstance(result, dict):
                conn_id = result.get("id") or result.get("connection_id")
                if conn_id:
                    self._telegram_connection_id = conn_id
                    print(f"[Caspian] Telegram connection ID: {conn_id[:8]}...")
            self._telegram_registered = True
            print("[Caspian] Telegram registration successful")
            return True
        except Exception as e:
            print(f"[Caspian] ERROR: Telegram channel addition failed: {e}")
            return False
    
    def run(self):
        """Start the Caspian event loop (blocking)."""
        if self._initialized and self.cx:
            print("[Caspian] Event loop starting")
            self._running = True
            self._stop_event.clear()
            try:
                while not self._stop_event.is_set():
                    self._last_poll_time = time.time()
                    # Run one iteration with short interval
                    results = self.cx.run(max_iterations=1, interval=1.0)
                    # Check for errors in results
                    for result in results:
                        if not result.is_ok:
                            self._poll_error_count += 1
                            if self._poll_error_count <= 5:  # Limit error spam
                                print(f"[Caspian] Poll error: {result.error}")
                        else:
                            self._poll_error_count = 0  # Reset on success
            except Exception as e:
                print(f"[Caspian] Event loop stopped unexpectedly: {e}")
                self._running = False
                raise
            finally:
                self._running = False
                print("[Caspian] Event loop stopped")
    
    def start_in_background(self):
        """Start Caspian event loop in a background thread."""
        if not self._initialized or not self.cx:
            print("[Caspian] ERROR: Cannot start - not initialized")
            return False
        
        if self._running:
            print("[Caspian] Already running")
            return True
        
        print("[Caspian] Starting event loop in background thread...")
        self._stop_event.clear()
        self._run_thread = threading.Thread(target=self.run, daemon=False)
        self._run_thread.start()
        return True
    
    def stop(self):
        """Stop the Caspian event loop."""
        if self._running:
            print("[Caspian] Stopping event loop...")
            self._stop_event.set()
            if self._run_thread and self._run_thread.is_alive():
                self._run_thread.join(timeout=5.0)
            self._running = False
            print("[Caspian] Event loop stopped")
    
    def get_poll_status(self) -> dict[str, Any]:
        """Get current polling status for health checks."""
        return {
            "running": self._running,
            "last_poll_time": self._last_poll_time,
            "error_count": self._poll_error_count,
            "telegram_connection_id": self._telegram_connection_id[:8] + "..." if self._telegram_connection_id else None,
        }
    
    def is_available(self) -> bool:
        """Check if Caspian is available."""
        return self._initialized and self.cx is not None
    
    def is_running(self) -> bool:
        """Check if Caspian event loop is running."""
        if not self._running:
            return False
        # Check if thread is actually alive
        if self._run_thread and not self._run_thread.is_alive():
            self._running = False
            return False
        return True
    
    def get_email_address(self) -> Optional[str]:
        """Get registered email address."""
        return self._email_address
    
    def is_email_registered(self) -> bool:
        """Check if email channel is registered."""
        return self._email_registered
    
    def is_telegram_registered(self) -> bool:
        """Check if Telegram channel is registered."""
        return self._telegram_registered


# Global instance
caspian_manager = CaspianManager()
