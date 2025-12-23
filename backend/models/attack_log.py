from sqlalchemy import Column, Integer, String, DateTime, Text, Index, Boolean
from datetime import datetime
from config.database import Base

class AttackLog(Base):
    """Log untuk detected attacks"""
    __tablename__ = "attack_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Attack Info
    attack_type = Column(String(50), index=True)  # SQL Injection, XSS, etc
    severity = Column(String(20), index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    description = Column(Text)
    
    # Source Info
    source_ip = Column(String(45), index=True)
    source_country = Column(String(100), nullable=True)
    
    # Target Info
    target_path = Column(Text, nullable=True)
    http_method = Column(String(10), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Additional Context
    pattern_matched = Column(Text, nullable=True)
    raw_request = Column(Text, nullable=True)
    
    # Status
    blocked = Column(Boolean, default=False)
    resolved = Column(Boolean, default=False, index=True)
    
    # Related log references
    related_log_type = Column(String(20), nullable=True)  # nginx, ssh
    related_log_id = Column(Integer, nullable=True)
    
    __table_args__ = (
        Index('idx_attack_timestamp_severity', 'timestamp', 'severity'),
        Index('idx_attack_ip_type', 'source_ip', 'attack_type'),
    )
    
    def __repr__(self):
        return f"<AttackLog {self.attack_type} from {self.source_ip} - {self.severity}>"