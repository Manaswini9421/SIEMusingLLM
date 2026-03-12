import requests
import json

# Test the backend endpoint
url = "http://localhost:8000/chat"
payload = {
    "session_id": "test123",
    "message": "Show me recent alerts",
    "index_name": "wazuh-alerts-*"
}

print("Sending request to:", url)
print("Payload:", json.dumps(payload, indent=2))

try:
    response = requests.post(url, json=payload)
    print("\nStatus Code:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))
except Exception as e:
    print("\nError:", str(e))
    if hasattr(e, 'response') and e.response:
        print("Response text:", e.response.text)
