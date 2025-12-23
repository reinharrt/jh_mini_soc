from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Index
from datetime import datetime
from config.database import Base

class NginxAccessLog(Base):
    __tablename__ = "nginx_access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    log_timestamp = Column(DateTime, nullable=True)
    ip_address = Column(String(45), index=True)
    method = Column(String(10), index=True)
    path = Column(Text)
    protocol = Column(String(20))
    status_code = Column(Integer, index=True)
    response_size = Column(Integer, nullable=True)
    referer = Column(Text, nullable=True)
    user_agent = Column(Text, nullable=True)
    request_time = Column(Float, nullable=True)
    upstream_time = Column(Float, nullable=True)
    raw_log = Column(Text)
    country = Column(String(100), nullable=True)
    
    __table_args__ = (
        Index('idx_nginx_timestamp_status', 'timestamp', 'status_code'),
        Index('idx_nginx_ip_method', 'ip_address', 'method'),
    )
    
    def __repr__(self):
        return f"<NginxLog {self.method} {self.path} - {self.status_code}>"


class NginxErrorLog(Base):
    __tablename__ = "nginx_error_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    log_timestamp = Column(DateTime, nullable=True)
    level = Column(String(20), index=True)  # error, warn, crit, alert
    pid = Column(Integer, nullable=True)
    tid = Column(Integer, nullable=True)
    client_ip = Column(String(45), index=True, nullable=True)
    server = Column(String(255), nullable=True)
    request = Column(Text, nullable=True)
    message = Column(Text)
    raw_log = Column(Text)
    
    __table_args__ = (
        Index('idx_nginx_error_timestamp_level', 'timestamp', 'level'),
    )
    
    def __repr__(self):
        return f"<NginxError {self.level} - {self.message[:50]}>"