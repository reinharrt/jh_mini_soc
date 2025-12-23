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
    resolved_only: bool = False,
    source_ip: Optional[str] = None,
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
    if source_ip:
        query = query.filter(AttackLog.source_ip == source_ip)
    
    total = query.count()
    attacks = query.order_by(desc(AttackLog.timestamp)).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "attacks": [
            {
                "id": attack.id,
                "timestamp": attack.timestamp.isoformat(),
                "attack_type": attack.attack_type,
                "severity": attack.severity,
                "description": attack.description,
                "source_ip": attack.source_ip,
                "source_country": attack.source_country,
                "target_path": attack.target_path,
                "http_method": attack.http_method,
                "user_agent": attack.user_agent,
                "pattern_matched": attack.pattern_matched,
                "blocked": attack.blocked,
                "resolved": attack.resolved,
                "related_log_type": attack.related_log_type,
                "related_log_id": attack.related_log_id
            }
            for attack in attacks
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
    
    # Severity distribution
    severity_dist = db.query(
        AttackLog.severity,
        func.count(AttackLog.id).label('count')
    ).filter(
        AttackLog.timestamp >= since
    ).group_by(
        AttackLog.severity
    ).all()
    
    # Attack types distribution
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
    
    # Top attackers (by IP)
    top_attackers = db.query(
        AttackLog.source_ip,
        func.count(AttackLog.id).label('count')
    ).filter(
        AttackLog.timestamp >= since,
        AttackLog.source_ip.isnot(None)
    ).group_by(
        AttackLog.source_ip
    ).order_by(
        desc('count')
    ).limit(10).all()
    
    # Attack timeline (per hour)
    if hours <= 24:
        time_format = func.date_trunc('hour', AttackLog.timestamp)
    else:
        time_format = func.date_trunc('day', AttackLog.timestamp)
    
    timeline = db.query(
        time_format.label('time'),
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
            {"type": attack_type, "count": count} 
            for attack_type, count in attack_types
        ],
        "top_attackers": [
            {"ip": ip, "count": count} 
            for ip, count in top_attackers
        ],
        "timeline": [
            {
                "time": t.isoformat() if t else None,
                "count": count
            }
            for t, count in timeline
        ]
    }


@router.get("/summary")
def get_attack_summary(
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db)
):
    """Get quick attack summary for dashboard badge"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    total = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since
    ).scalar()
    
    critical = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since,
        AttackLog.severity == 'CRITICAL'
    ).scalar()
    
    unresolved = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= since,
        AttackLog.resolved == False
    ).scalar()
    
    return {
        "total_attacks": total or 0,
        "critical_attacks": critical or 0,
        "unresolved_attacks": unresolved or 0
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
        "message": f"Attack {attack_id} marked as resolved",
        "attack_id": attack_id
    }


@router.post("/{attack_id}/block")
def block_attack_ip(
    attack_id: int,
    db: Session = Depends(get_db)
):
    """Mark an attack as blocked (for future implementation with firewall)"""
    attack = db.query(AttackLog).filter(AttackLog.id == attack_id).first()
    
    if not attack:
        return {"error": "Attack not found"}, 404
    
    attack.blocked = True
    db.commit()
    
    # TODO: Implement actual IP blocking with iptables or fail2ban
    
    return {
        "success": True,
        "message": f"Attack from {attack.source_ip} marked as blocked",
        "attack_id": attack_id,
        "source_ip": attack.source_ip
    }


@router.get("/types")
def get_attack_types(db: Session = Depends(get_db)):
    """Get list of all attack types detected"""
    types = db.query(AttackLog.attack_type).distinct().all()
    
    return {
        "attack_types": [t[0] for t in types if t[0]]
    }


@router.get("/recent")
def get_recent_attacks(
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Get most recent attacks for real-time monitoring"""
    attacks = db.query(AttackLog).order_by(
        desc(AttackLog.timestamp)
    ).limit(limit).all()
    
    return {
        "attacks": [
            {
                "id": attack.id,
                "timestamp": attack.timestamp.isoformat(),
                "attack_type": attack.attack_type,
                "severity": attack.severity,
                "source_ip": attack.source_ip,
                "target_path": attack.target_path,
                "resolved": attack.resolved
            }
            for attack in attacks
        ]
    }