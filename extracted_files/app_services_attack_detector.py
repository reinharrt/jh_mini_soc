"""
Attack Detection Service
Deteksi berbagai jenis serangan cyber
"""
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class AttackDetector:
    """Detector untuk berbagai jenis serangan"""
    
    def __init__(self):
        # SQL Injection patterns
        self.sql_injection_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bselect\b.*\bfrom\b.*\bwhere\b)",
            r"('+\s*or\s*'1'\s*=\s*'1)",
            r"(--|\#|\/\*)",
            r"(\bexec\b|\bexecute\b)",
            r"(\bdrop\b\s+\btable\b)",
            r"(\binsert\b\s+\binto\b)",
            r"(\bdelete\b\s+\bfrom\b)",
            r"(\bupdate\b.*\bset\b)",
            r"(\bor\b\s+\d+\s*=\s*\d+)",
            r"(';--)",
            r"(\bxp_cmdshell\b)",
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"onerror\s*=",
            r"onload\s*=",
            r"onclick\s*=",
            r"<iframe",
            r"<object",
            r"<embed",
            r"eval\s*\(",
            r"alert\s*\(",
            r"document\.cookie",
            r"document\.write",
        ]
        
        # Path Traversal patterns
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e/",
            r"%252e%252e/",
            r"\.\.%2f",
        ]
        
        # Command Injection patterns
        self.command_injection_patterns = [
            r";\s*(ls|cat|wget|curl|bash|sh|nc|netcat)",
            r"\|\s*(ls|cat|wget|curl|bash|sh|nc)",
            r"`.*`",
            r"\$\(.*\)",
            r"&&\s*(ls|cat|wget|curl)",
        ]
        
        # Web Shell patterns
        self.webshell_patterns = [
            r"c99\.php",
            r"r57\.php",
            r"shell\.php",
            r"cmd\.php",
            r"backdoor\.php",
            r"phpshell",
            r"webshell",
            r"\.php\?cmd=",
        ]
        
        # Suspicious paths
        self.suspicious_paths = [
            r"/admin\.php",
            r"/phpmyadmin",
            r"/wp-admin",
            r"/wp-login\.php",
            r"/wp-config\.php",
            r"/\.env",
            r"/\.git",
            r"/config\.php",
            r"/db\.php",
            r"/database\.php",
            r"/backup",
            r"/xmlrpc\.php",
            r"/\.aws/credentials",
        ]
        
        # Brute force indicators (untuk SSH)
        self.brute_force_threshold = 5  # failed attempts
        self.brute_force_window = 300  # 5 minutes
        
    def detect_sql_injection(self, text: str) -> Dict:
        """Detect SQL Injection attempts"""
        text_lower = text.lower()
        
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return {
                    'detected': True,
                    'attack_type': 'SQL Injection',
                    'severity': 'HIGH',
                    'pattern': pattern,
                    'description': 'Possible SQL injection attempt detected'
                }
        
        return {'detected': False}
    
    def detect_xss(self, text: str) -> Dict:
        """Detect Cross-Site Scripting (XSS) attempts"""
        text_lower = text.lower()
        
        for pattern in self.xss_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return {
                    'detected': True,
                    'attack_type': 'XSS',
                    'severity': 'HIGH',
                    'pattern': pattern,
                    'description': 'Possible XSS attack detected'
                }
        
        return {'detected': False}
    
    def detect_path_traversal(self, text: str) -> Dict:
        """Detect Path Traversal attempts"""
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return {
                    'detected': True,
                    'attack_type': 'Path Traversal',
                    'severity': 'MEDIUM',
                    'pattern': pattern,
                    'description': 'Directory traversal attempt detected'
                }
        
        return {'detected': False}
    
    def detect_command_injection(self, text: str) -> Dict:
        """Detect Command Injection attempts"""
        for pattern in self.command_injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return {
                    'detected': True,
                    'attack_type': 'Command Injection',
                    'severity': 'CRITICAL',
                    'pattern': pattern,
                    'description': 'OS command injection attempt detected'
                }
        
        return {'detected': False}
    
    def detect_webshell(self, text: str) -> Dict:
        """Detect Web Shell access attempts"""
        text_lower = text.lower()
        
        for pattern in self.webshell_patterns:
            if re.search(pattern, text_lower):
                return {
                    'detected': True,
                    'attack_type': 'Web Shell',
                    'severity': 'CRITICAL',
                    'pattern': pattern,
                    'description': 'Web shell access attempt detected'
                }
        
        return {'detected': False}
    
    def detect_suspicious_path(self, path: str) -> Dict:
        """Detect access to suspicious paths"""
        path_lower = path.lower()
        
        for pattern in self.suspicious_paths:
            if re.search(pattern, path_lower):
                return {
                    'detected': True,
                    'attack_type': 'Suspicious Access',
                    'severity': 'MEDIUM',
                    'pattern': pattern,
                    'description': 'Access to sensitive/suspicious path'
                }
        
        return {'detected': False}
    
    def analyze_http_request(self, method: str, path: str, user_agent: str = None) -> List[Dict]:
        """Analyze HTTP request for multiple attack types"""
        threats = []
        
        # Gabungkan semua data untuk analisis
        full_request = f"{method} {path}"
        if user_agent:
            full_request += f" {user_agent}"
        
        # Check SQL Injection
        sql_result = self.detect_sql_injection(full_request)
        if sql_result['detected']:
            threats.append(sql_result)
        
        # Check XSS
        xss_result = self.detect_xss(full_request)
        if xss_result['detected']:
            threats.append(xss_result)
        
        # Check Path Traversal
        traversal_result = self.detect_path_traversal(path)
        if traversal_result['detected']:
            threats.append(traversal_result)
        
        # Check Command Injection
        cmd_result = self.detect_command_injection(full_request)
        if cmd_result['detected']:
            threats.append(cmd_result)
        
        # Check Web Shell
        shell_result = self.detect_webshell(path)
        if shell_result['detected']:
            threats.append(shell_result)
        
        # Check Suspicious Paths
        susp_result = self.detect_suspicious_path(path)
        if susp_result['detected']:
            threats.append(susp_result)
        
        return threats
    
    def detect_brute_force_ssh(self, failed_attempts: List[Dict]) -> Optional[Dict]:
        """
        Detect SSH brute force based on failed login patterns
        failed_attempts: list of {'ip': str, 'timestamp': datetime, 'username': str}
        """
        if len(failed_attempts) >= self.brute_force_threshold:
            return {
                'detected': True,
                'attack_type': 'SSH Brute Force',
                'severity': 'HIGH',
                'description': f'{len(failed_attempts)} failed login attempts detected',
                'failed_count': len(failed_attempts)
            }
        
        return None
    
    def detect_port_scan(self, connections: List[Dict]) -> Optional[Dict]:
        """
        Detect port scanning behavior
        connections: list of connection attempts from same IP
        """
        if len(connections) >= 10:  # Multiple port attempts
            unique_ports = len(set(c.get('port') for c in connections if c.get('port')))
            
            if unique_ports >= 5:  # Scanning multiple ports
                return {
                    'detected': True,
                    'attack_type': 'Port Scan',
                    'severity': 'MEDIUM',
                    'description': f'Port scanning detected: {unique_ports} different ports',
                    'port_count': unique_ports
                }
        
        return None
    
    def get_threat_level(self, severity: str) -> int:
        """Convert severity to numeric threat level"""
        levels = {
            'LOW': 1,
            'MEDIUM': 2,
            'HIGH': 3,
            'CRITICAL': 4
        }
        return levels.get(severity, 0)


# Global detector instance
attack_detector = AttackDetector()