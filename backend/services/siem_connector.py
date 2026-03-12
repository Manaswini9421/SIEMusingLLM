import requests
import json
import urllib3
from backend.config import ELASTICSEARCH_URL, ELASTICSEARCH_API_KEY, ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD, MOCK_SIEM

# Suppress SSL warnings for local development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

    def _get_mock_response(self, endpoint, body):
        """Returns sample data for demonstration when live SIEM is unavailable."""
        if "_cat/indices" in endpoint:
            return [
                {"health": "green", "status": "open", "index": "wazuh-alerts-4.x-sample", "pri": "1", "rep": "0", "docs.count": "1500"},
                {"health": "green", "status": "open", "index": "filebeat-sample-logs", "pri": "1", "rep": "0", "docs.count": "342"}
            ]
        elif "_mapping" in endpoint:
            return {
                "wazuh-alerts-sample": {
                    "mappings": {
                        "properties": {
                            "timestamp": {"type": "date"},
                            "rule": {"properties": {"description": {"type": "text"}, "level": {"type": "integer"}}},
                            "agent": {"properties": {"id": {"type": "keyword"}, "name": {"type": "keyword"}}},
                            "data": {"properties": {"srcip": {"type": "ip"}, "destip": {"type": "ip"}}}
                        }
                    }
                }
            }
        elif "_search" in endpoint:
            # Return some sample hits
            return {
                "hits": {
                    "total": {"value": 2, "relation": "eq"},
                    "hits": [
                        {
                            "_source": {
                                "timestamp": "2024-02-02T10:00:00Z",
                                "rule": {"description": "Suspicious login attempt", "level": 10},
                                "agent": {"name": "web-server-01"},
                                "data": {"srcip": "192.168.1.100"}
                            }
                        },
                        {
                            "_source": {
                                "timestamp": "2024-02-02T10:05:00Z",
                                "rule": {"description": "Multiple authentication failures", "level": 12},
                                "agent": {"name": "db-server-01"},
                                "data": {"srcip": "10.0.0.5"}
                            }
                        }
                    ]
                }
            }
        return {}

    def execute_query(self, index: str, query: dict):
        return self._request("POST", f"{index}/_search", body=query)

    def get_indices(self):
        return self._request("GET", "_cat/indices?format=json")

    def get_mapping(self, index: str):
        return self._request("GET", f"{index}/_mapping")
