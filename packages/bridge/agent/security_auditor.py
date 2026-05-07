"""
Security Auditor - Detecta vulnerabilidades e riscos de segurança
"""

import re
import hashlib
from typing import Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class SecurityIssue:
    """Representa um problema de segurança detectado"""
    id: str
    severity: str  # "critical", "high", "medium", "low"
    description: str
    component: str
    resolution: str
    reported_at: datetime
    status: str  # "open", "resolved", "ignored"
    details: dict[str, Any]

    def to_dict(self):
        return {
            **asdict(self),
            "reported_at": self.reported_at.isoformat()
        }


class SecurityAuditor:
    """Serviço de auditoria de segurança"""
    
    def __init__(self):
        self.issues: list[SecurityIssue] = []
        self.checks = [
            self._check_code_injection,
            self._check_sql_injection,
            self._check_hardcoded_secrets,
            self._check_unsafe_deserialization,
            self._check_resource_limits,
            self._check_path_traversal,
            self._check_xxe_vulnerabilities,
            self._check_weak_cryptography,
        ]
    
    def audit_code(self, code: str, language: str = "python", component: str = "unknown") -> list[SecurityIssue]:
        """Executa auditoria de segurança de código"""
        self.issues = []
        
        for check in self.checks:
            check(code, language, component)
        
        return self.issues
    
    def _check_code_injection(self, code: str, language: str, component: str):
        """Detecta possíveis injeções de código"""
        patterns = [
            (r'\beval\s*\(', "eval() detected - Code Injection Risk"),
            (r'\bexec\s*\(', "exec() detected - Code Injection Risk"),
            (r'\b__import__\s*\(', "__import__() detected - Import Risk"),
            (r'os\.system\s*\(\s*f[\"\'].*[\"\']', "f-string with os.system - Command Injection Risk"),
            (r'subprocess\..*\(\s*cmd.*shell\s*=\s*True', "subprocess with shell=True - Command Injection Risk"),
        ]
        
        for pattern, description in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                self.issues.append(SecurityIssue(
                    id=self._generate_id(),
                    severity="critical" if "injection" in description.lower() else "high",
                    description=description,
                    component=component,
                    resolution="Avoid dynamic code execution. Use safer alternatives or validate inputs strictly.",
                    reported_at=datetime.now(),
                    status="open",
                    details={
                        "line": code[:match.start()].count('\n') + 1,
                        "matched_text": match.group(0)
                    }
                ))
    
    def _check_sql_injection(self, code: str, language: str, component: str):
        """Detecta possíveis vulnerabilidades de SQL Injection"""
        patterns = [
            (r'f["\'].*SELECT.*\{.*\}', "SQL with f-string - SQL Injection Risk"),
            (r'query\s*=.*\+.*', "Query concatenation with user input - SQL Injection Risk"),
            (r'\.format\s*\(.*\).*query', "SQL query with .format() - SQL Injection Risk"),
        ]
        
        for pattern, description in patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                self.issues.append(SecurityIssue(
                    id=self._generate_id(),
                    severity="critical",
                    description=description,
                    component=component,
                    resolution="Use parameterized queries or prepared statements. Never concatenate user input directly.",
                    reported_at=datetime.now(),
                    status="open",
                    details={
                        "line": code[:match.start()].count('\n') + 1,
                        "matched_text": match.group(0)
                    }
                ))
    
    def _check_hardcoded_secrets(self, code: str, language: str, component: str):
        """Detecta segredos hardcoded (chaves, senhas, tokens)"""
        patterns = [
            (r'(password|passwd|pwd)\b.*?=\s*["\']([^"\']+)["\']', "Hardcoded password"),
            (r'(api_key|apikey|api-key|api_token)\b.*?=\s*["\']([^"\']{20,})["\']', "Hardcoded API key"),
            (r'(secret|token)\b.*?=\s*["\']([^"\']{20,})["\']', "Hardcoded secret token"),
            (r'(private_key|privatekey)\b.*?=\s*["\']', "Hardcoded private key"),
        ]
        
        for pattern, description in patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                self.issues.append(SecurityIssue(
                    id=self._generate_id(),
                    severity="critical",
                    description=description,
                    component=component,
                    resolution="Move all secrets to environment variables or secure vaults. Never commit secrets to version control.",
                    reported_at=datetime.now(),
                    status="open",
                    details={
                        "line": code[:match.start()].count('\n') + 1,
                        "secret_type": description
                    }
                ))
    
    def _check_unsafe_deserialization(self, code: str, language: str, component: str):
        """Detecta desserialização insegura"""
        patterns = [
            (r'pickle\.loads\s*\(', "Unsafe pickle deserialization"),
            (r'yaml\.load\s*\(', "Unsafe YAML deserialization"),
            (r'json\.loads\s*\(.*untrusted', "JSON deserialization of untrusted data"),
        ]
        
        for pattern, description in patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                self.issues.append(SecurityIssue(
                    id=self._generate_id(),
                    severity="high",
                    description=description,
                    component=component,
                    resolution="Use safe deserialization methods. For pickle, use json instead. For YAML, use safe_load with specific Loader.",
                    reported_at=datetime.now(),
                    status="open",
                    details={
                        "line": code[:match.start()].count('\n') + 1,
                        "matched_text": match.group(0)
                    }
                ))
    
    def _check_resource_limits(self, code: str, language: str, component: str):
        """Detecta falta de limites de recursos"""
        patterns = [
            (r'open\s*\([^)]*\)\s*as\s+f.*?while\s+True.*?f\.read', "Potential unbounded file read"),
            (r'requests\.get\s*\([^)]*stream\s*=\s*True', "Unbounded HTTP response stream"),
            (r'while\s+True.*?\.recv', "Unbounded network recv loop"),
        ]
        
        for pattern, description in patterns:
            matches = re.finditer(pattern, code, re.DOTALL)
            for match in matches:
                self.issues.append(SecurityIssue(
                    id=self._generate_id(),
                    severity="medium",
                    description=description,
                    component=component,
                    resolution="Add size limits, timeouts, and max iterations to prevent resource exhaustion.",
                    reported_at=datetime.now(),
                    status="open",
                    details={
                        "line": code[:match.start()].count('\n') + 1,
                        "recommendation": "Set MAX_BYTES, timeout, or max iterations"
                    }
                ))
    
    def _check_path_traversal(self, code: str, language: str, component: str):
        """Detecta vulnerabilidades de Path Traversal"""
        patterns = [
            (r'open\s*\(\s*user.*path', "Path from user input without sanitization"),
            (r'os\.path\.join\s*\(.*user', "Path joining with untrusted input"),
            (r'read.*file\s*\(\s*[\"\'].*\.\./', "Hardcoded path traversal pattern"),
        ]
        
        for pattern, description in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                self.issues.append(SecurityIssue(
                    id=self._generate_id(),
                    severity="high",
                    description=description,
                    component=component,
                    resolution="Validate and sanitize file paths. Use pathlib.Path.resolve() to ensure paths stay within allowed directory.",
                    reported_at=datetime.now(),
                    status="open",
                    details={
                        "line": code[:match.start()].count('\n') + 1,
                    }
                ))
    
    def _check_xxe_vulnerabilities(self, code: str, language: str, component: str):
        """Detecta vulnerabilidades XXE (XML External Entity)"""
        patterns = [
            (r'ET\.parse\s*\(', "XXE vulnerability in ElementTree"),
            (r'ElementTree\.parse\s*\(', "XXE vulnerability in ElementTree"),
            (r'ET\.fromstring\s*\(', "XXE vulnerability in fromstring"),
            (r'ElementTree\.fromstring\s*\(', "XXE vulnerability in fromstring"),
            (r'lxml\.etree\.parse\s*\(', "XXE vulnerability in lxml"),
        ]
        
        for pattern, description in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                self.issues.append(SecurityIssue(
                    id=self._generate_id(),
                    severity="high",
                    description=description,
                    component=component,
                    resolution="Disable external entity processing. Use defusedxml library for safer XML parsing.",
                    reported_at=datetime.now(),
                    status="open",
                    details={
                        "line": code[:match.start()].count('\n') + 1,
                    }
                ))
    
    def _check_weak_cryptography(self, code: str, language: str, component: str):
        """Detecta uso de criptografia fraca"""
        patterns = [
            (r'md5\s*\(', "MD5 detected - Weak hash algorithm"),
            (r'sha1\s*\(', "SHA1 detected - Weak hash algorithm"),
            (r'DES\s*\(', "DES detected - Weak encryption"),
            (r'random\.Random\s*\(.*key', "random.Random() for cryptography - Not secure"),
        ]
        
        for pattern, description in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                self.issues.append(SecurityIssue(
                    id=self._generate_id(),
                    severity="high" if "random" in description else "medium",
                    description=description,
                    component=component,
                    resolution="Use strong algorithms: SHA-256 for hashing, AES-256 for encryption, secrets module for randomness.",
                    reported_at=datetime.now(),
                    status="open",
                    details={
                        "line": code[:match.start()].count('\n') + 1,
                    }
                ))
    
    def _generate_id(self) -> str:
        """Gera ID único para o problema"""
        timestamp = datetime.now().isoformat()
        hash_obj = hashlib.sha256(timestamp.encode())
        return f"sec-{hash_obj.hexdigest()[:12]}"
    
    def get_summary(self) -> dict[str, Any]:
        """Retorna um resumo da auditoria"""
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for issue in self.issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        return {
            "total_issues": len(self.issues),
            "by_severity": severity_counts,
            "critical_count": severity_counts.get("critical", 0),
            "requires_attention": severity_counts.get("critical", 0) > 0 or severity_counts.get("high", 0) > 0,
            "timestamp": datetime.now().isoformat()
        }
    
    def export_issues(self) -> list[dict[str, Any]]:
        """Exporta todas as issues em formato dict"""
        return [issue.to_dict() for issue in self.issues]
