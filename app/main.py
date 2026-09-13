"""FastAPI application for DV Sentinel."""

import os
from fastapi import FastAPI
from app.config import config
from storage.database import DatabaseManager
from channels.caspian import caspian_manager
from agent.handler import DVHandler
import threading


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
    db_status = "healthy" if db.is_healthy() else "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "app": config.APP_NAME,
        "version": config.APP_VERSION,
        "caspian": caspian_status,
        "database": db_status,
        "mode": "demo" if config.DEMO_MODE else "production"
    }


@app.get("/metrics")
async def metrics():
    """Metrics endpoint (admin-only in production)."""
    metrics_data = db.get_metrics()
    return metrics_data


def run_caspian():
    """Run Caspian event loop in background thread."""
    if caspian_manager.is_available():
        caspian_manager.run()


def start_caspian_thread():
    """Start Caspian in background thread."""
    if not config.DEMO_MODE and caspian_manager.is_available():
        thread = threading.Thread(target=run_caspian, daemon=True)
        thread.start()


def main():
    """Main entry point."""
    import uvicorn
    
    # Initialize Caspian with handler
    def caspian_message_handler(thread, msg, ctx):
        """Bridge Caspian message to DV handler."""
        response = handler.handle_message(
            text=msg.text,
            user_id=str(ctx.user_id) if hasattr(ctx, 'user_id') else "unknown",
            channel=msg.channel if hasattr(msg, 'channel') else "unknown"
        )
        thread.post(response)
    
    caspian_manager.initialize(caspian_message_handler)
    
    # Add channels if configured
    if config.EMAIL_USERNAME:
        email_address = caspian_manager.add_email_channel(config.EMAIL_USERNAME)
        if email_address:
            print(f"Email channel: {email_address}")
    
    if config.TELEGRAM_BOT_TOKEN:
        if caspian_manager.add_telegram_channel(config.TELEGRAM_BOT_TOKEN):
            print("Telegram channel added")
    
    # Start Caspian in background
    start_caspian_thread()
    
    # Run FastAPI
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=config.PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()
