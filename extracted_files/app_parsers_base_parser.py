from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

class BaseParser(ABC):
    """Base class untuk semua log parsers"""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    def parse(self, log_line: str) -> Optional[Dict[str, Any]]:
        """
        Parse single log line
        Returns: Dict dengan parsed data atau None jika gagal
        """
        pass
    
    @abstractmethod
    def save_to_db(self, parsed_data: Dict[str, Any], db_session) -> bool:
        """
        Save parsed data ke database
        Returns: True jika sukses, False jika gagal
        """
        pass
    
    def process_log_line(self, log_line: str, db_session) -> bool:
        """
        Process complete log line: parse dan save
        """
        try:
            parsed = self.parse(log_line.strip())
            if parsed:
                return self.save_to_db(parsed, db_session)
            return False
        except Exception as e:
            print(f"[{self.name}] Error processing log: {e}")
            return False
    
    @staticmethod
    def parse_timestamp(timestamp_str: str, formats: list) -> Optional[datetime]:
        """Helper untuk parse berbagai format timestamp"""
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        return None
    
    def is_suspicious_ip(self, ip: str) -> bool:
        """Basic check untuk suspicious IP (bisa dikembangkan)"""
        # Placeholder - nanti bisa tambah blacklist, rate limiting check, etc
        suspicious_patterns = [
            '0.0.0.0',
            '127.0.0.1' if ip != '127.0.0.1' else None
        ]
        return any(pattern and pattern in ip for pattern in suspicious_patterns)