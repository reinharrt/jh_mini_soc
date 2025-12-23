import re
from typing import Dict, Any, Optional
from datetime import datetime
from parsers.base_parser import BaseParser
from models.ssh_log import SSHLog

class SSHParser(BaseParser):
    """Parser untuk SSH logs (auth.log, secure log)"""
    
    def __init__(self):
        super().__init__()
        
        # Regex patterns untuk berbagai event SSH
        self.patterns = {
            'accepted': re.compile(
                r'Accepted (?P<method>\w+) for (?P<user>\S+) from (?P<ip>[\d\.]+) port (?P<port>\d+)'
            ),
            'failed': re.compile(
                r'Failed (?P<method>\w+) for (?P<user>\S+) from (?P<ip>[\d\.]+) port (?P<port>\d+)'
            ),
            'invalid_user': re.compile(
                r'Invalid user (?P<user>\S+) from (?P<ip>[\d\.]+) port (?P<port>\d+)'
            ),
            'disconnected': re.compile(
                r'Disconnected from (?:invalid user )?(?P<user>\S+)?\s*(?P<ip>[\d\.]+) port (?P<port>\d+)'
            ),
            'connection_closed': re.compile(
                r'Connection closed by (?:invalid user )?(?P<user>\S+)?\s*(?P<ip>[\d\.]+) port (?P<port>\d+)'
            ),
            'session_opened': re.compile(
                r'pam_unix\(sshd:session\): session opened for user (?P<user>\S+)'
            ),
            'session_closed': re.compile(
                r'pam_unix\(sshd:session\): session closed for user (?P<user>\S+)'
            ),
        }
        
        # Timestamp formats untuk Linux logs
        self.timestamp_formats = [
            '%b %d %H:%M:%S',  # Dec 23 14:30:45
            '%Y-%m-%d %H:%M:%S',  # 2024-12-23 14:30:45
        ]
    
    def parse(self, log_line: str) -> Optional[Dict[str, Any]]:
        """Parse SSH log line"""
        if not log_line or len(log_line) < 10:
            return None
        
        parsed = {
            'raw_log': log_line,
            'event_type': 'unknown',
            'status': 'unknown',
            'is_suspicious': False
        }
        
        # Extract timestamp, host, process
        parts = log_line.split()
        if len(parts) < 5:
            return None
        
        # Parse timestamp (biasanya 3 bagian pertama)
        timestamp_str = ' '.join(parts[0:3])
        parsed['log_timestamp'] = self.parse_timestamp(
            timestamp_str, 
            self.timestamp_formats
        )
        
        # Parse hostname dan process info
        parsed['host'] = parts[3]
        
        # Extract process name dan PID
        if '[' in parts[4]:
            process_part = parts[4].split('[')
            parsed['process'] = process_part[0].replace(':', '')
            if len(process_part) > 1:
                parsed['pid'] = int(process_part[1].replace(']:', ''))
        
        # Gabungkan message parts
        message = ' '.join(parts[5:])
        
        # Match dengan patterns
        for event_type, pattern in self.patterns.items():
            match = pattern.search(message)
            if match:
                parsed['event_type'] = event_type
                data = match.groupdict()
                
                parsed['username'] = data.get('user')
                parsed['ip_address'] = data.get('ip')
                parsed['auth_method'] = data.get('method')
                
                if data.get('port'):
                    parsed['port'] = int(data['port'])
                
                # Set status
                if event_type == 'accepted':
                    parsed['status'] = 'success'
                elif event_type in ['failed', 'invalid_user']:
                    parsed['status'] = 'failed'
                    parsed['is_suspicious'] = True
                elif event_type in ['session_opened', 'session_closed']:
                    parsed['status'] = 'session'
                else:
                    parsed['status'] = 'closed'
                
                break
        
        # Check suspicious activity
        if parsed.get('ip_address'):
            if self.is_suspicious_ip(parsed['ip_address']):
                parsed['is_suspicious'] = True
        
        return parsed
    
    def save_to_db(self, parsed_data: Dict[str, Any], db_session) -> bool:
        """Save ke database"""
        try:
            log_entry = SSHLog(
                log_timestamp=parsed_data.get('log_timestamp'),
                host=parsed_data.get('host'),
                process=parsed_data.get('process'),
                pid=parsed_data.get('pid'),
                event_type=parsed_data.get('event_type'),
                username=parsed_data.get('username'),
                ip_address=parsed_data.get('ip_address'),
                port=parsed_data.get('port'),
                auth_method=parsed_data.get('auth_method'),
                status=parsed_data.get('status'),
                raw_log=parsed_data.get('raw_log'),
                is_suspicious=parsed_data.get('is_suspicious', False)
            )
            
            db_session.add(log_entry)
            db_session.commit()
            return True
            
        except Exception as e:
            db_session.rollback()
            print(f"[SSHParser] Error saving to DB: {e}")
            return False