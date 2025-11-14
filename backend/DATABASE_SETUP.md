# Database Setup Guide

## Overview
The `database.py` file is **automatically used** by the Flask application. You don't need to run it separately. However, you need to configure your database connection first.

## Quick Start

### 1. Create `.env` File
Create a `.env` file in the `backend/` directory with your Oracle database credentials:

```env
ORACLE_USER=your_username
ORACLE_PASSWORD=your_password
ORACLE_DSN=localhost:1521/XEPDB1
SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=jwt-secret-key
CORS_ORIGINS=http://localhost:5173
PORT=5000
FLASK_ENV=development
```

### 2. Test Database Connection
Before running the Flask server, test your database connection:

```bash
cd backend
python test_db_connection.py
```

This script will:
- ✅ Check if `.env` file exists
- ✅ Verify all required variables are set
- ✅ Test database connection
- ✅ Show detailed error messages if connection fails

### 3. Run Flask Server
Once the database connection test passes, start the Flask server:

```bash
python run.py
```

The server will automatically:
- Load the `.env` file
- Create a database connection pool
- Make the connection available to all routes

## DSN Format Examples

### Simple Format (Recommended)
```
localhost:1521/XEPDB1
```
- `localhost` - Database host
- `1521` - Port (default Oracle port)
- `XEPDB1` - Service name or SID

### Full TNS Format
```
(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=XEPDB1)))
```

### Common Service Names
- `XEPDB1` - Oracle Express Edition default
- `ORCL` - Oracle Standard Edition default
- `PDB1` - Pluggable database

## Troubleshooting

### Error: "Database pool not initialized"
**Solution**: 
1. Check if `.env` file exists in `backend/` directory
2. Verify all three variables are set: `ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN`
3. Run `python test_db_connection.py` to diagnose the issue

### Error: "TNS:listener does not currently know"
**Solution**:
- Check if Oracle listener is running: `lsnrctl status`
- Verify the service name in DSN is correct
- Check if database is running

### Error: "Invalid username/password"
**Solution**:
- Verify username and password are correct
- Check if user account is locked
- Ensure user has proper permissions

### Error: "TNS:could not resolve the connect identifier"
**Solution**:
- Check DSN format
- Verify host and port are correct
- Test network connectivity

## How It Works

1. **On Flask App Startup** (`run.py`):
   - Loads `.env` file
   - Calls `db.connect()` to create connection pool
   - Pool is stored in `db.pool`

2. **On Each Request**:
   - Routes call `db.execute_query()` or `db.execute_non_query()`
   - These methods call `db.get_connection()` to get a connection from the pool
   - Connection is automatically returned to pool after use

3. **Connection Pool Benefits**:
   - Reuses connections (faster)
   - Manages connection lifecycle
   - Handles connection errors gracefully

## Testing

### Test Database Connection
```bash
python test_db_connection.py
```

### Test Backend API
```bash
# Make sure Flask server is running first
python test_backend.py
```

## Common Issues

### Issue: Health check shows "disconnected"
**Check**:
1. Is `.env` file in the correct location? (`backend/.env`)
2. Are environment variables loaded? Check server startup logs
3. Is database running and accessible?
4. Run `test_db_connection.py` for detailed diagnostics

### Issue: All queries return "Database query failed"
**Check**:
1. Database connection pool was not created (check startup logs)
2. Database credentials are incorrect
3. Database tables don't exist (run schema setup scripts)

## Next Steps

1. ✅ Create `.env` file with your database credentials
2. ✅ Run `python test_db_connection.py` to verify connection
3. ✅ Start Flask server: `python run.py`
4. ✅ Run `python test_backend.py` to test all endpoints

## Files Reference

- `database.py` - Database connection and query methods (auto-imported)
- `test_db_connection.py` - Standalone connection test script
- `run.py` - Flask server startup (uses database.py automatically)
- `.env` - Environment variables (you need to create this)

