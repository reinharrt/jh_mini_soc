import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Dict
from config.database import SessionLocal
from parsers.ssh_parser import SSHParser
from parsers.nginx_parser import NginxAccessParser, NginxErrorParser

class LogFileHandler(FileSystemEventHandler):
    """Handler untuk monitoring perubahan file log"""
    
    def __init__(self, parser, file_path):
        self.parser = parser
        self.file_path = file_path
        self.file_position = 0
        
        # Set posisi ke akhir file untuk hanya baca log baru
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                f.seek(0, 2)  # Seek ke end
                self.file_position = f.tell()
    
    def on_modified(self, event):
        """Trigger saat file dimodifikasi"""
        if event.src_path == self.file_path:
            self.process_new_lines()
    
    def process_new_lines(self):
        """Process baris baru di file"""
        try:
            with open(self.file_path, 'r') as f:
                f.seek(self.file_position)
                new_lines = f.readlines()
                self.file_position = f.tell()
                
                if new_lines:
                    db = SessionLocal()
                    try:
                        for line in new_lines:
                            self.parser.process_log_line(line, db)
                    finally:
                        db.close()
                        
        except Exception as e:
            print(f"[LogWatcher] Error processing {self.file_path}: {e}")


class LogWatcherService:
    """Service untuk watch multiple log files"""
    
    def __init__(self, log_configs: Dict[str, Dict]):
        """
        log_configs format:
        {
            'ssh': {'path': '/logs/ssh/auth.log', 'parser': SSHParser()},
            'nginx_access': {'path': '/logs/nginx/access.log', 'parser': NginxAccessParser()},
        }
        """
        self.log_configs = log_configs
        self.observers = []
        self.handlers = []
    
    def start(self):
        """Start watching semua log files"""
        print("[LogWatcher] Starting log monitoring...")
        
        for name, config in self.log_configs.items():
            log_path = config['path']
            parser = config['parser']
            
            if not os.path.exists(log_path):
                print(f"[LogWatcher] Warning: {log_path} tidak ditemukan, skip...")
                continue
            
            # Create handler
            handler = LogFileHandler(parser, log_path)
            self.handlers.append(handler)
            
            # Create observer
            observer = Observer()
            observer.schedule(handler, path=os.path.dirname(log_path), recursive=False)
            observer.start()
            self.observers.append(observer)
            
            print(f"[LogWatcher] ✓ Monitoring {name}: {log_path}")
        
        print(f"[LogWatcher] Monitoring {len(self.observers)} log files")
    
    def stop(self):
        """Stop semua observers"""
        print("[LogWatcher] Stopping log monitoring...")
        for observer in self.observers:
            observer.stop()
            observer.join()
        print("[LogWatcher] Stopped")
    
    def process_existing_logs(self):
        """Process existing logs saat startup (opsional)"""
        print("[LogWatcher] Processing existing logs...")
        
        for name, config in self.log_configs.items():
            log_path = config['path']
            parser = config['parser']
            
            if not os.path.exists(log_path):
                continue
            
            print(f"[LogWatcher] Processing existing: {name}")
            
            db = SessionLocal()
            try:
                with open(log_path, 'r') as f:
                    # Ambil 100 baris terakhir untuk initial data
                    lines = f.readlines()[-100:]
                    
                    for line in lines:
                        parser.process_log_line(line, db)
                        
                print(f"[LogWatcher] ✓ Processed {len(lines)} lines from {name}")
                
            except Exception as e:
                print(f"[LogWatcher] Error processing existing logs: {e}")
            finally:
                db.close()


def create_log_watcher():
    """Factory function untuk create log watcher"""
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
        'nginx_error': {
            'path': os.path.join(log_base, 'nginx', 'error.log'),
            'parser': NginxErrorParser()
        }
    }
    
    return LogWatcherService(log_configs)