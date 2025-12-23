from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, timedelta
from config.database import get_db
from models.attack_log import AttackLog

router = APIRouter()

@router.get("/summary")
def get_attack_summary(
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db)
):
    """Get attack summary statistics"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Total attacks
    total_attacks = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since
    ).scalar()
    
    # Critical attacks
    critical_attacks = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since,
        AttackLog.severity == 'CRITICAL'
    ).scalar()
    
    # Unresolved attacks
    unresolved_attacks = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since,
        AttackLog.resolved == False
    ).scalar()
    
    # Blocked attacks
    blocked_attacks = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since,
        AttackLog.blocked == True
    ).scalar()
    
    return {
        "period_hours": hours,
        "total_attacks": total_attacks or 0,
        "critical_attacks": critical_attacks or 0,
        "unresolved_attacks": unresolved_attacks or 0,
        "blocked_attacks": blocked_attacks or 0
    }

@router.get("/stats")
def get_attack_stats(
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db)
):
    """Get detailed attack statistics"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Total attacks
    total_attacks = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since
    ).scalar()
    
    # Critical attacks
    critical_attacks = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since,
        AttackLog.severity == 'CRITICAL'
    ).scalar()
    
    # Unresolved
    unresolved_attacks = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since,
        AttackLog.resolved == False
    ).scalar()
    
    # Blocked
    blocked_attacks = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since,
        AttackLog.blocked == True
    ).scalar()
    
    # Severity distribution
    severity_dist = db.query(
        AttackLog.severity,
        func.count(AttackLog.id).label('count')
    ).filter(
        AttackLog.timestamp >= since
    ).group_by(
        AttackLog.severity
    ).all()
    
    # Attack types
    attack_types = db.query(
        AttackLog.attack_type,
        func.count(AttackLog.id).label('count')
    ).filter(
        AttackLog.timestamp >= since
    ).group_by(
        AttackLog.attack_type
    ).order_by(
        desc('count')
    ).all()
    
    # Top attackers
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
    
    # Timeline (hourly)
    timeline = db.query(
        func.date_trunc('hour', AttackLog.timestamp).label('time'),
        func.count(AttackLog.id).label('count')
    ).filter(
        AttackLog.timestamp >= since
    ).group_by(
        'time'
    ).order_by('time').all()
    
    return {
        "period_hours": hours,
        "total_attacks": total_attacks or 0,
        "critical_attacks": critical_attacks or 0,
        "unresolved_attacks": unresolved_attacks or 0,
        "blocked_attacks": blocked_attacks or 0,
        "severity_distribution": [
            {"severity": severity, "count": count}
            for severity, count in severity_dist
        ],
        "attack_types": [
            {"type": atype, "count": count}
            for atype, count in attack_types
        ],
        "top_attackers": [
            {"ip": ip, "count": count}
            for ip, count in top_attackers
        ],
        "timeline": [
            {"time": t.isoformat(), "count": count}
            for t, count in timeline
        ]
    }

@router.get("/logs")
def get_attack_logs(
    limit: int = Query(100, le=1000),
    offset: int = 0,
    attack_type: Optional[str] = None,
    severity: Optional[str] = None,
    resolved_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get attack logs with filtering"""
    query = db.query(AttackLog)
    
    if attack_type:
        query = query.filter(AttackLog.attack_type == attack_type)
    if severity:
        query = query.filter(AttackLog.severity == severity)
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
                "source_country": log.source_country,
                "target_path": log.target_path,
                "http_method": log.http_method,
                "user_agent": log.user_agent,
                "pattern_matched": log.pattern_matched,
                "blocked": log.blocked,
                "resolved": log.resolved
            }
            for log in logs
        ]
    }

@router.post("/{attack_id}/resolve")
def resolve_attack(
    attack_id: int,
    db: Session = Depends(get_db)
):
    """Mark an attack as resolved"""
    attack = db.query(AttackLog).filter(AttackLog.id == attack_id).first()
    
    if not attack:
        return {"error": "Attack not found"}, 404
    
    attack.resolved = True
    db.commit()
    
    return {
        "success": True,
        "attack_id": attack_id,
        "message": "Attack marked as resolved"
    }

@router.post("/{attack_id}/block")
def block_attack(
    attack_id: int,
    db: Session = Depends(get_db)
):
    """Mark an attack as blocked"""
    attack = db.query(AttackLog).filter(AttackLog.id == attack_id).first()
    
    if not attack:
        return {"error": "Attack not found"}, 404
    
    attack.blocked = True
    db.commit()
    
    return {
        "success": True,
        "attack_id": attack_id,
        "message": "Attack marked as blocked"
    }