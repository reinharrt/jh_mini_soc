from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, timedelta
from config.database import get_db
from models.attack_log import AttackLog

router = APIRouter()

@router.get("/logs")
def get_attack_logs(
    limit: int = Query(100, le=1000),
    offset: int = 0,
    attack_type: Optional[str] = None,
    severity: Optional[str] = None,
    source_ip: Optional[str] = None,
    resolved_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get attack logs dengan filtering"""
    query = db.query(AttackLog)
    
    if attack_type:
        query = query.filter(AttackLog.attack_type == attack_type)
    if severity:
        query = query.filter(AttackLog.severity == severity)
    if source_ip:
        query = query.filter(AttackLog.source_ip == source_ip)
    if resolved_only:
        query = query.filter(AttackLog.resolved == False)
    
    total = query.count()
    logs = query.order_by(desc(AttackLog.timestamp)).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "attacks": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "attack_type": log.attack_type,
                "severity": log.severity,
                "description": log.description,
                "source_ip": log.source_ip,
                "target_path": log.target_path,
                "http_method": log.http_method,
                "blocked": log.blocked,
                "resolved": log.resolved
            }
            for log in logs
        ]
    }

@router.get("/stats")
def get_attack_stats(
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db)
):
    """Get attack statistics"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Total attacks
    total_attacks = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since
    ).scalar()
    
    # Attacks by type
    attack_types = db.query(
        AttackLog.attack_type,
        func.count(AttackLog.id).label('count')
    ).filter(
        AttackLog.timestamp >= since
    ).group_by(
        AttackLog.attack_type
    ).all()
    
    # Attacks by severity
    severity_dist = db.query(
        AttackLog.severity,
        func.count(AttackLog.id).label('count')
    ).filter(
        AttackLog.timestamp >= since
    ).group_by(
        AttackLog.severity
    ).all()
    
    # Top attacking IPs
    top_attackers = db.query(
        AttackLog.source_ip,
        func.count(AttackLog.id).label('count')
    ).filter(
        AttackLog.timestamp >= since
    ).group_by(
        AttackLog.source_ip
    ).order_by(
        desc('count')
    ).limit(10).all()
    
    # Top targeted paths
    top_targets = db.query(
        AttackLog.target_path,
        func.count(AttackLog.id).label('count')
    ).filter(
        AttackLog.timestamp >= since,
        AttackLog.target_path.isnot(None)
    ).group_by(
        AttackLog.target_path
    ).order_by(
        desc('count')
    ).limit(10).all()
    
    # Critical attacks (CRITICAL and HIGH severity)
    critical_attacks = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since,
        AttackLog.severity.in_(['CRITICAL', 'HIGH'])
    ).scalar()
    
    # Unresolved attacks
    unresolved = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since,
        AttackLog.resolved == False
    ).scalar()
    
    return {
        "period_hours": hours,
        "total_attacks": total_attacks,
        "critical_attacks": critical_attacks,
        "unresolved_attacks": unresolved,
        "attack_types": [
            {"type": type, "count": count} 
            for type, count in attack_types
        ],
        "severity_distribution": [
            {"severity": severity, "count": count} 
            for severity, count in severity_dist
        ],
        "top_attackers": [
            {"ip": ip, "count": count} 
            for ip, count in top_attackers
        ],
        "top_targets": [
            {"path": path, "count": count} 
            for path, count in top_targets
        ]
    }

@router.get("/timeline")
def get_attack_timeline(
    hours: int = Query(24, le=168),
    interval: str = Query("hour", regex="^(hour|day)$"),
    db: Session = Depends(get_db)
):
    """Get attack timeline data"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    if interval == "hour":
        time_format = func.date_trunc('hour', AttackLog.timestamp)
    else:
        time_format = func.date_trunc('day', AttackLog.timestamp)
    
    timeline = db.query(
        time_format.label('time'),
        AttackLog.severity,
        func.count(AttackLog.id).label('count')
    ).filter(
        AttackLog.timestamp >= since
    ).group_by(
        'time',
        AttackLog.severity
    ).order_by('time').all()
    
    return {
        "interval": interval,
        "data": [
            {
                "time": t.isoformat(),
                "severity": severity,
                "count": count
            }
            for t, severity, count in timeline
        ]
    }

@router.post("/{attack_id}/resolve")
def resolve_attack(
    attack_id: int,
    db: Session = Depends(get_db)
):
    """Mark attack as resolved"""
    attack = db.query(AttackLog).filter(AttackLog.id == attack_id).first()
    
    if not attack:
        return {"error": "Attack not found"}, 404
    
    attack.resolved = True
    db.commit()
    
    return {
        "success": True,
        "message": f"Attack {attack_id} marked as resolved"
    }

@router.get("/summary")
def get_attack_summary(
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db)
):
    """Get quick attack summary for dashboard"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    total = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since
    ).scalar()
    
    critical = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since,
        AttackLog.severity == 'CRITICAL'
    ).scalar()
    
    high = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since,
        AttackLog.severity == 'HIGH'
    ).scalar()
    
    # Most common attack type
    most_common = db.query(
        AttackLog.attack_type,
        func.count(AttackLog.id).label('count')
    ).filter(
        AttackLog.timestamp >= since
    ).group_by(
        AttackLog.attack_type
    ).order_by(
        desc('count')
    ).first()
    
    return {
        "period_hours": hours,
        "total_attacks": total,
        "critical_count": critical,
        "high_count": high,
        "most_common_attack": {
            "type": most_common[0] if most_common else None,
            "count": most_common[1] if most_common else 0
        }
    }