import re
from typing import Dict, Any, Optional
from datetime import datetime
from parsers.base_parser import BaseParser
from models.nginx_log import NginxAccessLog, NginxErrorLog
from models.attack_log import AttackLog
from services.attack_detector import attack_detector

class NginxAccessParser(BaseParser):
    """Parser untuk Nginx access logs dengan attack detection"""
    
    def __init__(self):
        super().__init__()
        
        # Nginx combined log format
        self.pattern = re.compile(
            r'(?P<ip>[\d\.]+) - (?P<remote_user>\S+) \[(?P<timestamp>[^\]]+)\] '
            r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>\S+)" '
            r'(?P<status>\d+) (?P<size>\d+|-) '
            r'"(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
            r'(?: "(?P<forwarded>[^"]*)")?\s*'
            r'(?P<request_time>[\d\.]+)?\s*(?P<upstream_time>[\d\.]+)?'
        )
        
        self.timestamp_format = '%d/%b/%Y:%H:%M:%S %z'
    
    def parse(self, log_line: str) -> Optional[Dict[str, Any]]:
        """Parse Nginx access log line"""
        match = self.pattern.search(log_line)
        if not match:
            return None
        
        data = match.groupdict()
        
        parsed = {
            'raw_log': log_line,
            'ip_address': data['ip'],
            'method': data['method'],
            'path': data['path'],
            'protocol': data['protocol'],
            'status_code': int(data['status']),
            'referer': data['referer'] if data['referer'] != '-' else None,
            'user_agent': data['user_agent'] if data['user_agent'] != '-' else None,
        }
        
        # Parse timestamp
        try:
            parsed['log_timestamp'] = datetime.strptime(
                data['timestamp'], 
                self.timestamp_format
            )
        except ValueError:
            pass
        
        # Parse response size
        if data['size'] != '-':
            parsed['response_size'] = int(data['size'])
        
        # Parse request time
        if data.get('request_time'):
            parsed['request_time'] = float(data['request_time'])
        
        if data.get('upstream_time') and data['upstream_time'] != '-':
            parsed['upstream_time'] = float(data['upstream_time'])
        
        # Attack Detection
        threats = attack_detector.analyze_http_request(
            method=data['method'],
            path=data['path'],
            user_agent=data.get('user_agent')
        )
        
        parsed['threats_detected'] = threats
        
        return parsed
    
    def save_to_db(self, parsed_data: Dict[str, Any], db_session) -> bool:
        """Save ke database termasuk attack logs"""
        try:
            # Save nginx access log
            log_entry = NginxAccessLog(
                log_timestamp=parsed_data.get('log_timestamp'),
                ip_address=parsed_data.get('ip_address'),
                method=parsed_data.get('method'),
                path=parsed_data.get('path'),
                protocol=parsed_data.get('protocol'),
                status_code=parsed_data.get('status_code'),
                response_size=parsed_data.get('response_size'),
                referer=parsed_data.get('referer'),
                user_agent=parsed_data.get('user_agent'),
                request_time=parsed_data.get('request_time'),
                upstream_time=parsed_data.get('upstream_time'),
                raw_log=parsed_data.get('raw_log')
            )
            
            db_session.add(log_entry)
            db_session.flush()  # Get log_entry.id
            
            # Save attack logs if threats detected
            threats = parsed_data.get('threats_detected', [])
            for threat in threats:
                attack_log = AttackLog(
                    attack_type=threat['attack_type'],
                    severity=threat['severity'],
                    description=threat['description'],
                    source_ip=parsed_data.get('ip_address'),
                    target_path=parsed_data.get('path'),
                    http_method=parsed_data.get('method'),
                    user_agent=parsed_data.get('user_agent'),
                    pattern_matched=threat.get('pattern'),
                    raw_request=parsed_data.get('raw_log'),
                    related_log_type='nginx',
                    related_log_id=log_entry.id
                )
                db_session.add(attack_log)
            
            db_session.commit()
            
            # Log if threats detected
            if threats:
                print(f"[NginxParser] ⚠️  {len(threats)} threat(s) detected from {parsed_data.get('ip_address')}")
                for threat in threats:
                    print(f"  - {threat['attack_type']}: {threat['description']}")
            
            return True
            
        except Exception as e:
            db_session.rollback()
            print(f"[NginxAccessParser] Error saving to DB: {e}")
            return False


class NginxErrorParser(BaseParser):
    """Parser untuk Nginx error logs"""
    
    def __init__(self):
        super().__init__()
        
        self.pattern = re.compile(
            r'(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) '
            r'\[(?P<level>\w+)\] '
            r'(?P<pid>\d+)#(?P<tid>\d+): '
            r'(?:\*(?P<connection>\d+) )?'
            r'(?P<message>.*?)'
            r'(?:, client: (?P<client>[\d\.]+))?'
            r'(?:, server: (?P<server>\S+))?'
            r'(?:, request: "(?P<request>[^"]+)")?'
        )
        
        self.timestamp_format = '%Y/%m/%d %H:%M:%S'
    
    def parse(self, log_line: str) -> Optional[Dict[str, Any]]:
        """Parse Nginx error log line"""
        match = self.pattern.search(log_line)
        if not match:
            return None
        
        data = match.groupdict()
        
        parsed = {
            'raw_log': log_line,
            'level': data['level'],
            'pid': int(data['pid']) if data['pid'] else None,
            'tid': int(data['tid']) if data['tid'] else None,
            'message': data['message'],
            'client_ip': data.get('client'),
            'server': data.get('server'),
            'request': data.get('request')
        }
        
        # Parse timestamp
        try:
            parsed['log_timestamp'] = datetime.strptime(
                data['timestamp'], 
                self.timestamp_format
            )
        except ValueError:
            pass
        
        return parsed
    
    def save_to_db(self, parsed_data: Dict[str, Any], db_session) -> bool:
        """Save ke database"""
        try:
            log_entry = NginxErrorLog(
                log_timestamp=parsed_data.get('log_timestamp'),
                level=parsed_data.get('level'),
                pid=parsed_data.get('pid'),
                tid=parsed_data.get('tid'),
                client_ip=parsed_data.get('client_ip'),
                server=parsed_data.get('server'),
                request=parsed_data.get('request'),
                message=parsed_data.get('message'),
                raw_log=parsed_data.get('raw_log')
            )
            
            db_session.add(log_entry)
            db_session.commit()
            return True
            
        except Exception as e:
            db_session.rollback()
            print(f"[NginxErrorParser] Error saving to DB: {e}")
            return False