import requests
import json
import urllib3
from backend.config import ELASTICSEARCH_URL, ELASTICSEARCH_API_KEY, ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD

# Suppress SSL warnings for local development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SIEMConnector:
    def __init__(self):
        self.url = ELASTICSEARCH_URL.rstrip('/')
        self.auth = None
        self.headers = {"Content-Type": "application/json"}
        
        if ELASTICSEARCH_API_KEY:
            self.headers["Authorization"] = f"ApiKey {ELASTICSEARCH_API_KEY}"
        elif ELASTICSEARCH_USER and ELASTICSEARCH_PASSWORD:
            self.auth = (ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD)

    def _request(self, method, endpoint, body=None):
        url = f"{self.url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(
                method, 
                url, 
                auth=self.auth, 
                headers=self.headers, 
                json=body,
                verify=False
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def execute_query(self, index: str, query: dict):
        return self._request("POST", f"{index}/_search", body=query)

    def get_indices(self):
        return self._request("GET", "_cat/indices?format=json")

    def get_mapping(self, index: str):
        return self._request("GET", f"{index}/_mapping")
