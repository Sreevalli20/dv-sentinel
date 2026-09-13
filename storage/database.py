"""SQLite database manager for DV Sentinel."""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.config import config


class DatabaseManager:
    """Manages SQLite database for conversation context and metrics."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path if db_path else config.DATABASE_PATH
        self._conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        # For in-memory databases, keep connection alive
        if self.db_path == ":memory:":
            self._conn = sqlite3.connect(self.db_path)
            cursor = self._conn.cursor()
        else:
            self._conn = None
            cursor = sqlite3.connect(self.db_path).cursor()
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Commands table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                command TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Context table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context (
                user_id TEXT PRIMARY KEY,
                context_data TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        if self._conn:
            self._conn.commit()
        else:
            cursor.connection.commit()
            cursor.connection.close()
    
    def log_message(self, user_id: str, channel: str, content: str):
        """Log a message.
        
        Args:
            user_id: User identifier
            channel: Channel name
            content: Message content
        """
        if self._conn:
            cursor = self._conn.cursor()
            cursor.execute(
                "INSERT INTO messages (user_id, channel, content) VALUES (?, ?, ?)",
                (user_id, channel, content[:1000])  # Limit content length
            )
            self._conn.commit()
        else:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO messages (user_id, channel, content) VALUES (?, ?, ?)",
                    (user_id, channel, content[:1000])  # Limit content length
                )
                conn.commit()
    
    def log_command(self, user_id: str, channel: str, command: str):
        """Log a command usage.
        
        Args:
            user_id: User identifier
            channel: Channel name
            command: Command used
        """
        if self._conn:
            cursor = self._conn.cursor()
            cursor.execute(
                "INSERT INTO commands (user_id, channel, command) VALUES (?, ?, ?)",
                (user_id, channel, command)
            )
            self._conn.commit()
        else:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO commands (user_id, channel, command) VALUES (?, ?, ?)",
                    (user_id, channel, command)
                )
                conn.commit()
    
    def store_context(self, user_id: str, context_data: Dict[str, Any]):
        """Store conversation context for a user.
        
        Args:
            user_id: User identifier
            context_data: Context dictionary
        """
        if self._conn:
            cursor = self._conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO context (user_id, context_data, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                (user_id, json.dumps(context_data))
            )
            self._conn.commit()
        else:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO context (user_id, context_data, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    """,
                    (user_id, json.dumps(context_data))
                )
                conn.commit()
    
    def get_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation context for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Context dictionary or None
        """
        if self._conn:
            cursor = self._conn.cursor()
            cursor.execute(
                "SELECT context_data FROM context WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None
        else:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT context_data FROM context WHERE user_id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get usage metrics.
        
        Returns:
            Metrics dictionary
        """
        if self._conn:
            cursor = self._conn.cursor()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
        
        # Total messages
        cursor.execute("SELECT COUNT(*) FROM messages")
        total_messages = cursor.fetchone()[0]
        
        # Messages per channel
        cursor.execute("SELECT channel, COUNT(*) FROM messages GROUP BY channel")
        messages_by_channel = dict(cursor.fetchall())
        
        # Command usage
        cursor.execute("SELECT command, COUNT(*) FROM commands GROUP BY command")
        command_usage = dict(cursor.fetchall())
        
        # Active users
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM messages")
        active_users = cursor.fetchone()[0]
        
        # Active days
        cursor.execute("SELECT COUNT(DISTINCT DATE(timestamp)) FROM messages")
        active_days = cursor.fetchone()[0]
        
        result = {
            "total_messages": total_messages,
            "messages_by_channel": messages_by_channel,
            "command_usage": command_usage,
            "active_users": active_users,
            "active_days": active_days
        }
        
        if not self._conn:
            conn.close()
        
        return result
    
    def is_healthy(self) -> bool:
        """Check if database is healthy.
        
        Returns:
            True if database is accessible
        """
        try:
            if self._conn:
                cursor = self._conn.cursor()
                cursor.execute("SELECT 1")
                return True
            else:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    return True
        except Exception:
            return False
