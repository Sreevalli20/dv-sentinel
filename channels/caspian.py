"""Caspian channel integration for DV Sentinel."""

import os
import threading
from typing import Optional, Callable
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
            from caspian import Caspian, Message, Thread
            
            print("[Caspian] Initializing SDK...")
            self.cx = Caspian(
                api_key=config.CASPIAN_API_KEY,
                base_url=config.CASPIAN_BASE_URL,
            )
            
            # Register message handler for all channels
            @self.cx.on_message({"channel": "*"})
            def handle_caspian_message(thread: Thread, msg: Message, ctx) -> None:
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
            print("[Caspian] Adding Telegram channel...")
            self.cx.channels.add("telegram", bot_token=bot_token)
            self._telegram_registered = True
            print("[Caspian] Telegram channel registered successfully")
            return True
        except Exception as e:
            print(f"[Caspian] ERROR: Telegram channel addition failed: {e}")
            return False
    
    def run(self):
        """Start the Caspian event loop (blocking)."""
        if self._initialized and self.cx:
            print("[Caspian] Starting event loop...")
            self._running = True
            try:
                self.cx.run()
            except Exception as e:
                print(f"[Caspian] ERROR: Event loop failed: {e}")
                self._running = False
    
    def start_in_background(self):
        """Start Caspian event loop in a background thread."""
        if not self._initialized or not self.cx:
            print("[Caspian] ERROR: Cannot start - not initialized")
            return False
        
        if self._running:
            print("[Caspian] Already running")
            return True
        
        print("[Caspian] Starting event loop in background thread...")
        self._run_thread = threading.Thread(target=self.run, daemon=False)
        self._run_thread.start()
        return True
    
    def is_available(self) -> bool:
        """Check if Caspian is available."""
        return self._initialized and self.cx is not None
    
    def is_running(self) -> bool:
        """Check if Caspian event loop is running."""
        return self._running
    
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
