import requests
import urllib3
urllib3.disable_warnings()

r = requests.get('https://localhost:9200', auth=('admin', 'admin'), verify=False)
print(f'Status: {r.status_code}')
print(f'Response: {r.text[:500]}')
