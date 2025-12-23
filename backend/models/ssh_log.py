from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index
from datetime import datetime
from config.database import Base

class SSHLog(Base):
    __tablename__ = "ssh_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    log_timestamp = Column(DateTime, nullable=True)
    host = Column(String(255))
    process = Column(String(100))
    pid = Column(Integer, nullable=True)
    event_type = Column(String(50), index=True)  # accepted, failed, invalid, session
    username = Column(String(100), index=True, nullable=True)
    ip_address = Column(String(45), index=True, nullable=True)  # IPv6 support
    port = Column(Integer, nullable=True)
    auth_method = Column(String(50), nullable=True)  # password, publickey
    status = Column(String(20), index=True)  # success, failed, invalid
    session_id = Column(String(100), nullable=True)
    raw_log = Column(Text)
    is_suspicious = Column(Boolean, default=False, index=True)
    country = Column(String(100), nullable=True)
    
    # Indexes untuk query performance
    __table_args__ = (
        Index('idx_ssh_timestamp_status', 'timestamp', 'status'),
        Index('idx_ssh_ip_status', 'ip_address', 'status'),
        Index('idx_ssh_user_ip', 'username', 'ip_address'),
    )
    
    def __repr__(self):
        return f"<SSHLog {self.event_type} - {self.username}@{self.ip_address}>"