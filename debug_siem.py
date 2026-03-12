import os
from dotenv import load_dotenv
from pathlib import Path
import urllib3

# Force load .env
env_path = Path("backend/.env")
load_dotenv(dotenv_path=env_path)

print(f"URL: {os.getenv('ELASTICSEARCH_URL')}")
print(f"User: {os.getenv('ELASTICSEARCH_USER')}")

from backend.services.siem_connector import SIEMConnector

try:
    connector = SIEMConnector()
    print("Attempting to get indices...")
    indices = connector.get_indices()
    print(f"Indices Result Type: {type(indices)}")
    print(f"Indices Result: {indices}")
    
    if isinstance(indices, dict) and "error" in indices:
        print("ERROR DETECTED IN RESPONSE")
except Exception as e:
    print(f"EXCEPTION: {e}")
