"""FastAPI application for DV Sentinel."""

import os
from fastapi import FastAPI
from app.config import config
from storage.database import DatabaseManager
from channels.caspian import caspian_manager
from agent.handler import DVHandler


# Initialize FastAPI
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="Design Verification Engineer Assistant"
)

# Initialize components
db = DatabaseManager()
handler = DVHandler()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": config.APP_NAME,
        "version": config.APP_VERSION,
        "status": "running",
        "description": "Design Verification Engineer Assistant"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    caspian_status = "connected" if caspian_manager.is_available() else "disconnected"
    caspian_running = "running" if caspian_manager.is_running() else "not_running"
    db_status = "healthy" if db.is_healthy() else "unhealthy"
    telegram_status = "registered" if caspian_manager.is_telegram_registered() else "not_registered"
    email_status = "registered" if caspian_manager.is_email_registered() else "not_registered"
    
    # Get detailed poll status
    poll_status = caspian_manager.get_poll_status()
    
    # Determine overall health
    overall_status = "healthy"
    if db_status != "healthy":
        overall_status = "degraded"
    if not config.DEMO_MODE and caspian_status == "disconnected":
        overall_status = "degraded"
    if not config.DEMO_MODE and caspian_running != "running":
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "app": config.APP_NAME,
        "version": config.APP_VERSION,
        "caspian": caspian_status,
        "caspian_event_loop": caspian_running,
        "caspian_poll_status": poll_status,
        "telegram": telegram_status,
        "email": email_status,
        "database": db_status,
        "mode": "demo" if config.DEMO_MODE else "production"
    }


@app.get("/metrics")
async def metrics():
    """Metrics endpoint (admin-only in production)."""
    metrics_data = db.get_metrics()
    return metrics_data


def start_caspian():
    """Start Caspian event loop in background."""
    if not config.DEMO_MODE and caspian_manager.is_available():
        caspian_manager.start_in_background()


def main():
    """Main entry point."""
    import uvicorn
    import atexit
    import signal
    import sys
    
    print("=" * 60)
    print(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    print("=" * 60)
    
    # Initialize Caspian with handler
    def caspian_message_handler(thread, msg, ctx):
        """Bridge Caspian message to DV handler."""
        # Extract channel from thread_id (format: "channel:conversation_id" in hosted mode)
        thread_id_str = str(thread.thread_id) if hasattr(thread, 'thread_id') else "unknown"
        channel = thread_id_str.split(":")[0] if ":" in thread_id_str else "unknown"
        
        response = handler.handle_message(
            text=msg.text if hasattr(msg, 'text') else "",
            user_id=msg.sender if hasattr(msg, 'sender') else "unknown",
            channel=channel
        )
        thread.post(response)
    
    if not caspian_manager.initialize(caspian_message_handler):
        print("[Startup] ERROR: Caspian initialization failed")
        if not config.DEMO_MODE:
            print("[Startup] ERROR: Cannot run in production mode without Caspian")
            return
    
    # Add channels if configured
    if config.EMAIL_USERNAME:
        email_address = caspian_manager.add_email_channel(config.EMAIL_USERNAME)
        if email_address:
            print(f"[Caspian] Email channel registered: {email_address}")
        else:
            print("[Startup] WARNING: Email channel registration failed")
    
    if config.TELEGRAM_BOT_TOKEN:
        if caspian_manager.add_telegram_channel(config.TELEGRAM_BOT_TOKEN):
            print("[Caspian] Telegram channel registered successfully")
        else:
            print("[Startup] WARNING: Telegram channel registration failed")
    
    # Start Caspian in background
    if not config.DEMO_MODE:
        start_caspian()
    
    print("[Startup] DV Sentinel handler registered")
    print("[Startup] Starting FastAPI server...")
    print("=" * 60)
    
    # Register cleanup on exit
    def cleanup():
        print("[Shutdown] Cleaning up...")
        caspian_manager.stop()
    
    atexit.register(cleanup)
    
    # Handle signals for graceful shutdown
    def signal_handler(sig, frame):
        print(f"[Shutdown] Received signal {sig}")
        cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run FastAPI
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=config.PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()
