"""Caspian channel integration for DV Sentinel."""

import os
from typing import Optional, Callable
from app.config import config


class CaspianManager:
    """Manages Caspian SDK integration."""
    
    def __init__(self):
        self.cx = None
        self._initialized = False
    
    def initialize(self, message_handler: Callable) -> bool:
        """Initialize Caspian SDK.
        
        Args:
            message_handler: Function to handle incoming messages
            
        Returns:
            True if initialized successfully
        """
        if config.DEMO_MODE:
            # Demo mode doesn't need Caspian
            self._initialized = True
            return True
        
        if not config.CASPIAN_API_KEY:
            return False
        
        try:
            from caspian import Caspian, HandlerContext, Message, Thread
            
            self.cx = Caspian(
                api_key=config.CASPIAN_API_KEY,
                base_url=config.CASPIAN_BASE_URL,
            )
            
            # Register message handler for all channels
            @self.cx.on_message({"channel": "*"})
            def handle_caspian_message(thread: Thread, msg: Message, ctx: HandlerContext) -> None:
                message_handler(thread, msg, ctx)
            
            self._initialized = True
            return True
            
        except ImportError:
            return False
        except Exception as e:
            print(f"Caspian initialization error: {e}")
            return False
    
    def add_email_channel(self, username: str) -> Optional[str]:
        """Add email channel.
        
        Args:
            username: Email username (part before @)
            
        Returns:
            Email address if successful, None otherwise
        """
        if not self._initialized or not self.cx:
            return None
        
        try:
            result = self.cx.channels.add("email", username=username)
            # Result may be a dict with 'address' or the address string directly
            if isinstance(result, dict):
                return result.get("address")
            return str(result) if result else None
        except Exception as e:
            print(f"Email channel addition error: {e}")
            return None
    
    def add_telegram_channel(self, bot_token: str) -> bool:
        """Add Telegram channel.
        
        Args:
            bot_token: Telegram bot token from BotFather
            
        Returns:
            True if successful
        """
        if not self._initialized or not self.cx:
            return False
        
        try:
            self.cx.channels.add("telegram", bot_token=bot_token)
            return True
        except Exception as e:
            print(f"Telegram channel addition error: {e}")
            return False
    
    def run(self):
        """Start the Caspian event loop (blocking)."""
        if self._initialized and self.cx:
            self.cx.run()
    
    def is_available(self) -> bool:
        """Check if Caspian is available."""
        return self._initialized and self.cx is not None


# Global instance
caspian_manager = CaspianManager()
