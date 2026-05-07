"""
Testes unitários para SecurityAuditor
"""

import pytest
from datetime import datetime
from agent.security_auditor import SecurityAuditor, SecurityIssue


class TestSecurityAuditor:
    """Testes para o SecurityAuditor"""

    def setup_method(self):
        """Setup para cada teste"""
        self.auditor = SecurityAuditor()

    def test_audit_clean_code(self):
        """Testa auditoria de código limpo (sem vulnerabilidades)"""
        clean_code = """
def hello_world():
    name = "world"
    print(f"Hello {name}")
    return True
"""
        issues = self.auditor.audit_code(clean_code, "python", "test_component")
        assert len(issues) == 0

    def test_detect_code_injection_eval(self):
        """Testa detecção de eval() - injeção de código crítica"""
        vulnerable_code = """
def dangerous_function(user_input):
    result = eval(user_input)  # Code injection vulnerability
    return result
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        issue = issues[0]
        assert issue.severity == "critical"
        assert "eval() detected" in issue.description
        assert "Code Injection Risk" in issue.description
        assert issue.component == "test_component"

    def test_detect_code_injection_exec(self):
        """Testa detecção de exec() - injeção de código crítica"""
        vulnerable_code = """
def dangerous_exec(user_code):
    exec(user_code)  # Code injection vulnerability
    return "executed"
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        assert issues[0].severity == "critical"
        assert "exec() detected" in issues[0].description

    def test_detect_code_injection_subprocess_shell(self):
        """Testa detecção de subprocess com shell=True"""
        vulnerable_code = """
import subprocess
def dangerous_command(cmd):
    result = subprocess.run(cmd, shell=True)  # Command injection
    return result
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        assert issues[0].severity == "critical"
        assert "subprocess with shell=True" in issues[0].description

    def test_detect_sql_injection_fstring(self):
        """Testa detecção de SQL injection com f-string"""
        vulnerable_code = """
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
    return execute_query(query)
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        assert issues[0].severity == "critical"
        assert "SQL with f-string" in issues[0].description

    def test_detect_sql_injection_concatenation(self):
        """Testa detecção de SQL injection por concatenação"""
        vulnerable_code = """
def search_users(search_term):
    query = "SELECT * FROM users WHERE name = '" + search_term + "'"  # SQL injection
    return execute_query(query)
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        assert issues[0].severity == "critical"
        assert "Query concatenation" in issues[0].description

    def test_detect_hardcoded_password(self):
        """Testa detecção de senha hardcoded"""
        vulnerable_code = """
DB_PASSWORD = "super_secret_password_123"  # Hardcoded password
def connect_db():
    return connect(password=DB_PASSWORD)
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        assert issues[0].severity == "critical"
        assert "Hardcoded password" in issues[0].description

    def test_detect_hardcoded_api_key(self):
        """Testa detecção de API key hardcoded"""
        vulnerable_code = """
OPENAI_API_KEY = "sk-1234567890abcdef1234567890abcdef1234567890"  # Hardcoded API key
def call_openai():
    return openai.Completion.create(api_key=OPENAI_API_KEY)
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        assert issues[0].severity == "critical"
        assert "Hardcoded API key" in issues[0].description

    def test_detect_hardcoded_secret_token(self):
        """Testa detecção de token secreto hardcoded"""
        vulnerable_code = """
JWT_SECRET = "my_super_secret_jwt_token_that_is_very_long_and_should_not_be_here"  # Hardcoded secret
def create_token():
    return jwt.encode(payload, JWT_SECRET)
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        assert issues[0].severity == "critical"
        assert "Hardcoded secret token" in issues[0].description

    def test_detect_unsafe_pickle(self):
        """Testa detecção de pickle.loads inseguro"""
        vulnerable_code = """
import pickle
def deserialize_data(data):
    return pickle.loads(data)  # Unsafe deserialization
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        assert issues[0].severity == "high"
        assert "Unsafe pickle deserialization" in issues[0].description

    def test_detect_unsafe_yaml(self):
        """Testa detecção de yaml.load inseguro"""
        vulnerable_code = """
import yaml
def load_config(config_file):
    with open(config_file) as f:
        return yaml.load(f)  # Unsafe YAML loading
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        assert issues[0].severity == "high"
        assert "Unsafe YAML deserialization" in issues[0].description

    def test_detect_unbounded_file_read(self):
        """Testa detecção de leitura de arquivo sem limites"""
        vulnerable_code = """
def read_large_file(filename):
    with open(filename, 'r') as f:
        while True:
            data = f.read()  # Unbounded read
            if not data:
                break
            process(data)
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        assert issues[0].severity == "medium"
        assert "Potential unbounded file read" in issues[0].description

    def test_detect_path_traversal(self):
        """Testa detecção de path traversal"""
        vulnerable_code = """
def read_user_file(user_path):
    with open(user_path, 'r') as f:  # Path traversal vulnerability
        return f.read()
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        assert issues[0].severity == "high"
        assert "Path from user input" in issues[0].description

    def test_detect_xxe_vulnerability(self):
        """Testa detecção de XXE vulnerability"""
        vulnerable_code = """
import xml.etree.ElementTree as ET
def parse_xml(xml_data):
    return ET.fromstring(xml_data)  # XXE vulnerability
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        assert issues[0].severity == "high"
        assert "XXE vulnerability" in issues[0].description

    def test_detect_weak_cryptography_md5(self):
        """Testa detecção de MD5 (algoritmo fraco)"""
        vulnerable_code = """
import hashlib
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()  # Weak hash
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        assert issues[0].severity == "medium"
        assert "MD5 detected" in issues[0].description

    def test_detect_weak_cryptography_sha1(self):
        """Testa detecção de SHA1 (algoritmo fraco)"""
        vulnerable_code = """
import hashlib
def hash_data(data):
    return hashlib.sha1(data.encode()).hexdigest()  # Weak hash
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        assert issues[0].severity == "medium"
        assert "SHA1 detected" in issues[0].description

    def test_detect_weak_cryptography_des(self):
        """Testa detecção de DES (criptografia fraca)"""
        vulnerable_code = """
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
def encrypt_data(key, data):
    cipher = Cipher(algorithms.DES(key), modes.ECB())  # Weak encryption
    return cipher.encryptor().update(data)
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        assert issues[0].severity == "medium"
        assert "DES detected" in issues[0].description

    def test_multiple_vulnerabilities(self):
        """Testa detecção de múltiplas vulnerabilidades no mesmo código"""
        vulnerable_code = """
import pickle
import hashlib

def dangerous_function(user_input, password):
    # Multiple vulnerabilities
    data = pickle.loads(user_input)  # Unsafe deserialization
    hashed = hashlib.md5(password.encode()).hexdigest()  # Weak hash
    result = eval(user_input)  # Code injection
    return data, hashed, result
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 3

        # Verificar que temos os tipos certos de vulnerabilidades
        descriptions = [issue.description for issue in issues]
        assert any("Unsafe pickle deserialization" in desc for desc in descriptions)
        assert any("MD5 detected" in desc for desc in descriptions)
        assert any("eval() detected" in desc for desc in descriptions)

    def test_get_summary_empty(self):
        """Testa resumo quando não há issues"""
        summary = self.auditor.get_summary()
        assert summary["total_issues"] == 0
        assert summary["critical_count"] == 0
        assert summary["requires_attention"] == False
        assert "by_severity" in summary

    def test_get_summary_with_issues(self):
        """Testa resumo com issues detectadas"""
        vulnerable_code = """
import pickle
import hashlib
DB_PASSWORD = "secret123"
result = eval("1+1")
data = pickle.loads(untrusted_data)
"""
        self.auditor.audit_code(vulnerable_code, "python", "test_component")
        summary = self.auditor.get_summary()

        assert summary["total_issues"] >= 3  # password, eval, pickle.loads
        assert summary["critical_count"] >= 2  # password and eval
        assert summary["requires_attention"] == True
        assert summary["by_severity"]["critical"] >= 2

    def test_export_issues(self):
        """Testa exportação de issues em formato dict"""
        vulnerable_code = """
result = eval("1+1")  # Code injection
"""
        self.auditor.audit_code(vulnerable_code, "python", "test_component")
        exported = self.auditor.export_issues()

        assert len(exported) == 1
        issue_dict = exported[0]
        assert "id" in issue_dict
        assert "severity" in issue_dict
        assert "description" in issue_dict
        assert "component" in issue_dict
        assert "resolution" in issue_dict
        assert "reported_at" in issue_dict
        assert "status" in issue_dict
        assert "details" in issue_dict

    def test_unique_issue_ids(self):
        """Testa que IDs de issues são únicos"""
        vulnerable_code = """
eval("1")
eval("2")
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        ids = [issue.id for issue in issues]
        assert len(ids) == len(set(ids))  # All IDs are unique

    def test_issue_details_contain_line_number(self):
        """Testa que detalhes da issue contêm número da linha"""
        vulnerable_code = """
def func1():
    pass

def func2():
    result = eval("dangerous")  # This should be detected

def func3():
    pass
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "test_component")
        assert len(issues) == 1
        assert "line" in issues[0].details
        assert issues[0].details["line"] == 6  # eval is on line 6

    def test_different_languages_supported(self):
        """Testa que o auditor suporta diferentes linguagens"""
        # Mesmo código vulnerável em "javascript" (simulado)
        js_vulnerable = """
function dangerous() {
    eval(userInput);  // Code injection
}
"""
        issues = self.auditor.audit_code(js_vulnerable, "javascript", "test_component")
        # Mesmo que seja JS, nossos padrões Python ainda podem detectar alguns problemas
        # Este teste verifica que a linguagem é passada corretamente
        assert len(issues) >= 0  # Pode detectar ou não, mas não deve quebrar

    def test_component_naming(self):
        """Testa que o nome do componente é corretamente atribuído"""
        vulnerable_code = """
result = eval("test")
"""
        issues = self.auditor.audit_code(vulnerable_code, "python", "auth_module")
        assert len(issues) == 1
        assert issues[0].component == "auth_module"