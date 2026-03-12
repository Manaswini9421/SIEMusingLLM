# Quick Start Guide

## 🚀 One-Click Startup

Simply run this command in PowerShell:

```powershell
cd "c:\Users\Lenovo\Desktop\Manaswinii Mini Project\SIEMusingLLM"
.\start-app.ps1
```

This script automatically:
1. ✅ Starts Docker Desktop (if not running)
2. ✅ Starts Wazuh containers (if not running)
3. ✅ Starts Backend server on port 8000
4. ✅ Starts Frontend server on port 5173
5. ✅ Opens the application in your browser

## 📌 Credentials
- **Username:** `admin`
- **Password:** `admin123`

## 🔧 Manual Startup (if needed)

### 1. Start Wazuh
```powershell
cd "c:\Users\Lenovo\Desktop\Manaswinii Mini Project\SIEMusingLLM\wazuh-deployment\single-node"
docker-compose up -d
```

### 2. Start Backend
```powershell
cd "c:\Users\Lenovo\Desktop\Manaswinii Mini Project\SIEMusingLLM"
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Start Frontend
```powershell
cd "c:\Users\Lenovo\Desktop\Manaswinii Mini Project\SIEMusingLLM\frontend"
npm run dev
```

### 4. Open Browser
Navigate to: **http://localhost:5173**

## ⚠️ Troubleshooting

### Connection Refused Error
**Cause:** Servers are not running  
**Solution:** Run `.\start-app.ps1`

### 503 Service Unavailable
**Cause:** Wazuh authentication issue  
**Solution:** Credentials are already fixed (`admin`/`admin123`). If still failing, see [WAZUH_AUTH_FIX.md](WAZUH_AUTH_FIX.md)

### Port Already in Use
**Cause:** Previous instances still running  
**Solution:**
```powershell
# Kill backend
Get-Process -Name python | Where-Object {$_.Path -like "*Python*"} | Stop-Process -Force

# Kill frontend
Get-Process -Name node | Stop-Process -Force

# Then restart with start-app.ps1
```

## 📱 Application URLs
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **Wazuh Dashboard:** https://localhost:443 (admin/admin123)
- **Wazuh Indexer:** https://localhost:9200

## 🛑 Shutdown

To stop all services:
```powershell
# Stop Wazuh
cd "c:\Users\Lenovo\Desktop\Manaswinii Mini Project\SIEMusingLLM\wazuh-deployment\single-node"
docker-compose down

# Stop servers (close the PowerShell windows or Ctrl+C)
```
