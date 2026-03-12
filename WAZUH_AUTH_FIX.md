# Wazuh Authentication Fix

## Issue
The Wazuh indexer was returning `401 Unauthorized` errors because the admin password in `internal_users.yml` didn't match the credentials in the backend `.env` file.

## Root Cause
The default password hash in `wazuh-deployment/single-node/config/wazuh_indexer/internal_users.yml` was:
```
hash: "$2y$12$K/SpwjtB.wOHJ/Nc6GVRDuc1h0rM1DfvziFRNPtk27P.c4yDr9njO"
```

This hash did NOT correspond to any of the typical default passwords ("admin", "SecretPassword", etc.).

## Solution Applied
1. Generated a new password hash for `admin123`:
   ```bash
   docker exec -u root single-node-wazuh.indexer-1 bash -c "JAVA_HOME=/usr/share/wazuh-indexer/jdk bash /usr/share/wazuh-indexer/plugins/opensearch-security/tools/hash.sh -p admin123"
   ```
   Result: `$2y$12$hOD1kxe1W2g7ubFZDzkpwOvU8PaVSWsEmzTfxA.R9dYA7vZkuTLNi`

2. Updated `wazuh-deployment/single-node/config/wazuh_indexer/internal_users.yml`:
   ```yaml
   admin:
     hash: "$2y$12$hOD1kxe1W2g7ubFZDzkpwOvU8PaVSWsEmzTfxA.R9dYA7vZkuTLNi"
   ```

3. Reloaded security configuration:
   ```bash
   docker exec -u root single-node-wazuh.indexer-1 bash -c "JAVA_HOME=/usr/share/wazuh-indexer/jdk bash /usr/share/wazuh-indexer/plugins/opensearch-security/tools/securityadmin.sh -cd /usr/share/wazuh-indexer/opensearch-security/ -icl -nhnv -cacert /usr/share/wazuh-indexer/certs/root-ca.pem -cert /usr/share/wazuh-indexer/certs/admin.pem -key /usr/share/wazuh-indexer/certs/admin-key.pem"
   ```

4. Updated `backend/.env`:
   ```env
   ELASTICSEARCH_USER=admin
   ELASTICSEARCH_PASSWORD=admin123
   ```

## Current Credentials
- **Username:** `admin`
- **Password:** `admin123`

## To Change Password in Future
1. Generate new hash:
   ```bash
   docker exec -u root single-node-wazuh.indexer-1 bash -c "JAVA_HOME=/usr/share/wazuh-indexer/jdk bash /usr/share/wazuh-indexer/plugins/opensearch-security/tools/hash.sh -p YOUR_NEW_PASSWORD"
   ```

2. Update hash in `wazuh-deployment/single-node/config/wazuh_indexer/internal_users.yml`

3. Reload security:
   ```bash
   docker exec -u root single-node-wazuh.indexer-1 bash -c "JAVA_HOME=/usr/share/wazuh-indexer/jdk bash /usr/share/wazuh-indexer/plugins/opensearch-security/tools/securityadmin.sh -cd /usr/share/wazuh-indexer/opensearch-security/ -icl -nhnv -cacert /usr/share/wazuh-indexer/certs/root-ca.pem -cert /usr/share/wazuh-indexer/certs/admin.pem -key /usr/share/wazuh-indexer/certs/admin-key.pem"
   ```

4. Update `backend/.env` with new password

## Files Modified
- `wazuh-deployment/single-node/config/wazuh_indexer/internal_users.yml`
- `backend/.env`
- `backend/main.py` (improved error handling for dict type checking)
