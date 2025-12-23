import uvicorn
import signal
import sys
from threading import Thread
from config.database import init_db
from services.log_watcher import create_log_watcher
from api.main import app

# Global watcher instance
watcher = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n[Main] Shutting down...")
    if watcher:
        watcher.stop()
    sys.exit(0)

def start_log_watcher():
    """Start log watcher in background thread"""
    global watcher
    watcher = create_log_watcher()
    
    # Process existing logs on startup
    print("[Main] Processing existing logs...")
    watcher.process_existing_logs()
    
    # Start watching for new logs
    print("[Main] Starting real-time log monitoring...")
    watcher.start()
    
    # Keep thread alive
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()

if __name__ == "__main__":
    print("=" * 50)
    print("Mini SOC - Log Parser & API")
    print("=" * 50)
    
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize database
    print("[Main] Initializing database...")
    init_db()
    
    # Start log watcher in background thread
    print("[Main] Starting log watcher...")
    watcher_thread = Thread(target=start_log_watcher, daemon=True)
    watcher_thread.start()
    
    # Start FastAPI server
    print("[Main] Starting API server...")
    print("[Main] API available at: http://0.0.0.0:8000")
    print("[Main] Docs available at: http://0.0.0.0:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )