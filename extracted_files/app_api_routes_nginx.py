from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, timedelta
from config.database import get_db
from models.nginx_log import NginxAccessLog, NginxErrorLog

router = APIRouter()

@router.get("/access/logs")
def get_access_logs(
    limit: int = Query(100, le=1000),
    offset: int = 0,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    ip_address: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get Nginx access logs"""
    query = db.query(NginxAccessLog)
    
    if method:
        query = query.filter(NginxAccessLog.method == method)
    if status_code:
        query = query.filter(NginxAccessLog.status_code == status_code)
    if ip_address:
        query = query.filter(NginxAccessLog.ip_address == ip_address)
    
    total = query.count()
    logs = query.order_by(desc(NginxAccessLog.timestamp)).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "ip_address": log.ip_address,
                "method": log.method,
                "path": log.path,
                "status_code": log.status_code,
                "response_size": log.response_size,
                "request_time": log.request_time,
                "user_agent": log.user_agent
            }
            for log in logs
        ]
    }

@router.get("/error/logs")
def get_error_logs(
    limit: int = Query(100, le=1000),
    offset: int = 0,
    level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get Nginx error logs"""
    query = db.query(NginxErrorLog)
    
    if level:
        query = query.filter(NginxErrorLog.level == level)
    
    total = query.count()
    logs = query.order_by(desc(NginxErrorLog.timestamp)).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "level": log.level,
                "message": log.message,
                "client_ip": log.client_ip,
                "server": log.server
            }
            for log in logs
        ]
    }

@router.get("/stats")
def get_nginx_stats(
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db)
):
    """Get Nginx statistics"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Access stats
    total_requests = db.query(func.count(NginxAccessLog.id)).filter(
        NginxAccessLog.timestamp >= since
    ).scalar()
    
    # Status code distribution
    status_dist = db.query(
        NginxAccessLog.status_code,
        func.count(NginxAccessLog.id).label('count')
    ).filter(
        NginxAccessLog.timestamp >= since
    ).group_by(
        NginxAccessLog.status_code
    ).all()
    
    # Method distribution
    method_dist = db.query(
        NginxAccessLog.method,
        func.count(NginxAccessLog.id).label('count')
    ).filter(
        NginxAccessLog.timestamp >= since
    ).group_by(
        NginxAccessLog.method
    ).all()
    
    # Top IPs
    top_ips = db.query(
        NginxAccessLog.ip_address,
        func.count(NginxAccessLog.id).label('count')
    ).filter(
        NginxAccessLog.timestamp >= since
    ).group_by(
        NginxAccessLog.ip_address
    ).order_by(
        desc('count')
    ).limit(10).all()
    
    # Top paths
    top_paths = db.query(
        NginxAccessLog.path,
        func.count(NginxAccessLog.id).label('count')
    ).filter(
        NginxAccessLog.timestamp >= since
    ).group_by(
        NginxAccessLog.path
    ).order_by(
        desc('count')
    ).limit(10).all()
    
    # Average response time
    avg_response_time = db.query(
        func.avg(NginxAccessLog.request_time)
    ).filter(
        NginxAccessLog.timestamp >= since,
        NginxAccessLog.request_time.isnot(None)
    ).scalar()
    
    # Error stats
    total_errors = db.query(func.count(NginxErrorLog.id)).filter(
        NginxErrorLog.timestamp >= since
    ).scalar()
    
    error_level_dist = db.query(
        NginxErrorLog.level,
        func.count(NginxErrorLog.id).label('count')
    ).filter(
        NginxErrorLog.timestamp >= since
    ).group_by(
        NginxErrorLog.level
    ).all()
    
    return {
        "period_hours": hours,
        "access": {
            "total_requests": total_requests,
            "status_distribution": [
                {"status": status, "count": count} 
                for status, count in status_dist
            ],
            "method_distribution": [
                {"method": method, "count": count} 
                for method, count in method_dist
            ],
            "top_ips": [
                {"ip": ip, "count": count} 
                for ip, count in top_ips
            ],
            "top_paths": [
                {"path": path, "count": count} 
                for path, count in top_paths
            ],
            "avg_response_time": float(avg_response_time) if avg_response_time else 0
        },
        "errors": {
            "total": total_errors,
            "level_distribution": [
                {"level": level, "count": count} 
                for level, count in error_level_dist
            ]
        }
    }