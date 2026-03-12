---
description: How to resolve SIEM connection errors and 503 Service Unavailable
---

# Troubleshooting SIEM Connection Errors

If you see a "503 Service Unavailable" or a "Connection Alert" in the UI, follow these steps to resolve it.

## 1. Check if you want Real or Mock Data
The application can run in two modes:
- **Mock Mode**: Uses sample data (no server needed).
- **Live Mode**: Connects to your real Elasticsearch/Wazuh server.

Check your current setting in `backend/.env`:
```env
MOCK_SIEM=true  # Set to true for Mock Mode, false for Live Mode
```

## 2. If using Live Mode (`MOCK_SIEM=false`)
If you want to use real data, ensure your Elasticsearch server is running:

### Windows (Common)
1. Open a new Terminal/PowerShell.
2. Check if Elasticsearch is listening:
   ```powershell
   Test-NetConnection -ComputerName 127.0.0.1 -Port 9200
   ```
3. If it fails, start your Elasticsearch service. Usually, this involves running `elasticsearch.bat` from your Elasticsearch installation folder.

### Check Backend Connectivity
Run the debug script to see exactly why the connection is failing:
```powershell
python debug_siem.py
```

## 3. Persistent Solution (How to prevent repeats)
To prevent the application from ever "breaking" with a 503 error again:

### Keep Mock Mode as Fallback
Always keep `MOCK_SIEM=true` in your `.env` during development. Only set it to `false` when you are actively testing your live SIEM integration.

### Verify Environment Variables
Ensure `backend/.env` has the correct credentials:
- `ELASTICSEARCH_URL` (usually `https://127.0.0.1:9200`)
- `ELASTICSEARCH_USER`
- `ELASTICSEARCH_PASSWORD`

## 4. Common Issues
- **SSL Errors**: The app is configured to ignore SSL warnings for local development (`verify=False`), so this shouldn't be an issue.
- **Wrong Port**: Ensure Elasticsearch isn't running on a different port (e.g., 9201).
