# File: backend/services/__init__.py
from .log_watcher import LogWatcherService, create_log_watcher

__all__ = ['LogWatcherService', 'create_log_watcher']