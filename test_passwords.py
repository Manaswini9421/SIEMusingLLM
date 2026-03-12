import requests
import urllib3
urllib3.disable_warnings()

passwords = ['admin', 'wazuh', 'changeme', 'Admin123', 'SecurePassword']

for pwd in passwords:
    try:
        r = requests.get('https://localhost:9200', auth=('admin', pwd), verify=False, timeout=2)
        print(f'{pwd}: {r.status_code}')
        if r.status_code == 200:
            print(f'SUCCESS! Password is: {pwd}')
            break
    except Exception as e:
        print(f'{pwd}: Error - {e}')
