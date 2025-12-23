import os
import time
from typing import Dict
from threading import Thread
from config.database import SessionLocal
from parsers.ssh_parser import SSHParser
from parsers.nginx_parser import NginxAccessParser, NginxErrorParser

class LogFilePoller:
    """Poller for log files - works with Docker mounted files"""
    
    def __init__(self, parser, file_path, name):
        self.parser = parser
        self.file_path = file_path
        self.name = name
        self.file_position = 0
        self.running = False
        
        # Initialize position to end of file
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(0, 2)
                    self.file_position = f.tell()
                    print(f"[LogPoller] Initialized {name}: {file_path} at position {self.file_position}")
            except Exception as e:
                print(f"[LogPoller] Error initializing {name}: {e}")
        else:
            print(f"[LogPoller] File not found: {file_path}")
    
    def check_and_process(self):
        """Check file for new content and process"""
        if not os.path.exists(self.file_path):
            return
        
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Get current size
                f.seek(0, 2)
                current_size = f.tell()
                
                # Check if file grew
                if current_size > self.file_position:
                    # Read new content
                    f.seek(self.file_position)
                    new_lines = f.readlines()
                    
                    if new_lines:
                        print(f"[LogPoller] {self.name}: Found {len(new_lines)} new lines")
                        
                        db = SessionLocal()
                        try:
                            success_count = 0
                            for line in new_lines:
                                if line.strip():
                                    if self.parser.process_log_line(line, db):
                                        success_count += 1
                            
                            if success_count > 0:
                                print(f"[LogPoller] {self.name}: Processed {success_count}/{len(new_lines)} lines")
                        finally:
                            db.close()
                    
                    # Update position
                    self.file_position = current_size
                
                elif current_size < self.file_position:
                    # File was truncated/rotated
                    print(f"[LogPoller] {self.name}: File truncated, resetting position")
                    self.file_position = 0
                    
        except Exception as e:
            print(f"[LogPoller] Error processing {self.file_path}: {e}")
    
    def poll_loop(self, interval=2):
        """Main polling loop"""
        print(f"[LogPoller] Starting poll loop for {self.name} (interval: {interval}s)")
        self.running = True
        
        while self.running:
            self.check_and_process()
            time.sleep(interval)
    
    def stop(self):
        """Stop polling"""
        self.running = False


class LogWatcherService:
    """Service to poll multiple log files"""
    
    def __init__(self, log_configs: Dict[str, Dict], poll_interval=2):
        """
        log_configs format:
        {
            'ssh': {'path': '/logs/ssh/auth.log', 'parser': SSHParser()},
            'nginx_access': {'path': '/logs/nginx/access.log', 'parser': NginxAccessParser()},
        }
        poll_interval: seconds between checks (default 2)
        """
        self.log_configs = log_configs
        self.poll_interval = poll_interval
        self.pollers = []
        self.threads = []
    
    def start(self):
        """Start polling all log files"""
        print("[LogWatcher] Starting log monitoring (POLLING MODE)...")
        print(f"[LogWatcher] Poll interval: {self.poll_interval}s")
        
        for name, config in self.log_configs.items():
            log_path = config['path']
            parser = config['parser']
            
            if not os.path.exists(log_path):
                print(f"[LogWatcher] Warning: {log_path} not found, will retry...")
            
            # Create poller
            poller = LogFilePoller(parser, log_path, name)
            self.pollers.append(poller)
            
            # Start polling thread
            thread = Thread(
                target=poller.poll_loop,
                args=(self.poll_interval,),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
            
            print(f"[LogWatcher] ✓ Polling {name}: {log_path}")
        
        print(f"[LogWatcher] Monitoring {len(self.pollers)} log files")
    
    def stop(self):
        """Stop all pollers"""
        print("[LogWatcher] Stopping log monitoring...")
        for poller in self.pollers:
            poller.stop()
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=5)
        
        print("[LogWatcher] Stopped")
    
    def process_existing_logs(self):
        """Process existing logs on startup"""
        print("[LogWatcher] Processing existing logs...")
        
        for name, config in self.log_configs.items():
            log_path = config['path']
            parser = config['parser']
            
            if not os.path.exists(log_path):
                continue
            
            print(f"[LogWatcher] Processing existing: {name}")
            
            db = SessionLocal()
            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Read last 100 lines for initial data
                    lines = f.readlines()
                    recent_lines = lines[-100:] if len(lines) > 100 else lines
                    
                    success_count = 0
                    for line in recent_lines:
                        if line.strip():
                            if parser.process_log_line(line, db):
                                success_count += 1
                    
                    print(f"[LogWatcher] ✓ Processed {success_count} existing lines from {name}")
                
            except Exception as e:
                print(f"[LogWatcher] Error processing existing logs: {e}")
            finally:
                db.close()


def create_log_watcher():
    """Factory function to create log watcher with polling"""
    log_base = os.getenv('LOG_PATH', '/logs')
    
    log_configs = {
        'ssh': {
            'path': os.path.join(log_base, 'ssh', 'auth.log'),
            'parser': SSHParser()
        },
        'nginx_access': {
            'path': os.path.join(log_base, 'nginx', 'access.log'),
            'parser': NginxAccessParser()
        },
        'nginx_test_access': {
            'path': os.path.join(log_base, 'nginx', 'test-access.log'),
            'parser': NginxAccessParser()
        },
        'nginx_error': {
            'path': os.path.join(log_base, 'nginx', 'error.log'),
            'parser': NginxErrorParser()
        },
        'nginx_test_error': {
            'path': os.path.join(log_base, 'nginx', 'test-error.log'),
            'parser': NginxErrorParser()
        }
    }
    
    # Use 2 second polling interval (good balance between latency and CPU usage)
    return LogWatcherService(log_configs, poll_interval=2)