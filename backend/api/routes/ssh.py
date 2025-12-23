from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from config.database import get_db
from models.ssh_log import SSHLog

router = APIRouter()

@router.get("/logs")
def get_ssh_logs(
    limit: int = Query(100, le=1000),
    offset: int = 0,
    status: Optional[str] = None,
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    suspicious_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get SSH logs dengan filtering"""
    query = db.query(SSHLog)
    
    if status:
        query = query.filter(SSHLog.status == status)
    if username:
        query = query.filter(SSHLog.username.ilike(f"%{username}%"))
    if ip_address:
        query = query.filter(SSHLog.ip_address == ip_address)
    if suspicious_only:
        query = query.filter(SSHLog.is_suspicious == True)
    
    total = query.count()
    logs = query.order_by(desc(SSHLog.timestamp)).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "log_timestamp": log.log_timestamp.isoformat() if log.log_timestamp else None,
                "event_type": log.event_type,
                "username": log.username,
                "ip_address": log.ip_address,
                "port": log.port,
                "status": log.status,
                "auth_method": log.auth_method,
                "is_suspicious": log.is_suspicious,
                "raw_log": log.raw_log
            }
            for log in logs
        ]
    }

@router.get("/stats")
def get_ssh_stats(
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db)
):
    """Get SSH statistics"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    total_attempts = db.query(func.count(SSHLog.id)).filter(
        SSHLog.timestamp >= since
    ).scalar()
    
    successful = db.query(func.count(SSHLog.id)).filter(
        SSHLog.timestamp >= since,
        SSHLog.status == 'success'
    ).scalar()
    
    failed = db.query(func.count(SSHLog.id)).filter(
        SSHLog.timestamp >= since,
        SSHLog.status == 'failed'
    ).scalar()
    
    suspicious = db.query(func.count(SSHLog.id)).filter(
        SSHLog.timestamp >= since,
        SSHLog.is_suspicious == True
    ).scalar()
    
    # Top IPs
    top_ips = db.query(
        SSHLog.ip_address,
        func.count(SSHLog.id).label('count')
    ).filter(
        SSHLog.timestamp >= since
    ).group_by(
        SSHLog.ip_address
    ).order_by(
        desc('count')
    ).limit(10).all()
    
    # Top failed IPs
    top_failed_ips = db.query(
        SSHLog.ip_address,
        func.count(SSHLog.id).label('count')
    ).filter(
        SSHLog.timestamp >= since,
        SSHLog.status == 'failed'
    ).group_by(
        SSHLog.ip_address
    ).order_by(
        desc('count')
    ).limit(10).all()
    
    return {
        "period_hours": hours,
        "total_attempts": total_attempts,
        "successful": successful,
        "failed": failed,
        "suspicious": suspicious,
        "top_ips": [{"ip": ip, "count": count} for ip, count in top_ips],
        "top_failed_ips": [{"ip": ip, "count": count} for ip, count in top_failed_ips]
    }

@router.get("/timeline")
def get_ssh_timeline(
    hours: int = Query(24, le=168),
    interval: str = Query("hour", regex="^(hour|day)$"),
    db: Session = Depends(get_db)
):
    """Get SSH timeline data"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    if interval == "hour":
        time_format = func.date_trunc('hour', SSHLog.timestamp)
    else:
        time_format = func.date_trunc('day', SSHLog.timestamp)
    
    timeline = db.query(
        time_format.label('time'),
        SSHLog.status,
        func.count(SSHLog.id).label('count')
    ).filter(
        SSHLog.timestamp >= since
    ).group_by(
        'time',
        SSHLog.status
    ).order_by('time').all()
    
    return {
        "interval": interval,
        "data": [
            {
                "time": t.isoformat(),
                "status": status,
                "count": count
            }
            for t, status, count in timeline
        ]
    }