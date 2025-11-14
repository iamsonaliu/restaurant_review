# Oracle Instant Client Setup Guide

## Problem
You're seeing this error:
```
DPY-3010: connections to this database server version are not supported by python-oracledb in thin mode
```

This happens because you're using an older Oracle Database version (Oracle XE 11g or earlier) that requires "thick mode" connections, which need Oracle Instant Client.

## Solution: Install Oracle Instant Client

### Option 1: Automatic Installation (Recommended)

The code will automatically try to use thick mode. If it fails, you need to install Oracle Instant Client manually.

### Option 2: Manual Installation

#### For Windows:

1. **Download Oracle Instant Client**
   - Go to: https://www.oracle.com/database/technologies/instant-client/downloads.html
   - Download "Basic Package" for your system (Windows x64)
   - Extract to a folder (e.g., `C:\oracle\instantclient_21_3`)

2. **Set Environment Variables**
   - Add the Instant Client path to your system PATH:
     - Right-click "This PC" → Properties → Advanced System Settings
     - Click "Environment Variables"
     - Under "System Variables", find "Path" and click "Edit"
     - Click "New" and add: `C:\oracle\instantclient_21_3` (or your path)
     - Click OK on all dialogs

3. **Restart Your Terminal/IDE**
   - Close and reopen your terminal/PowerShell
   - Or restart your IDE (VS Code, etc.)

4. **Verify Installation**
   ```bash
   python test_db_connection.py
   ```

#### For Linux:

1. **Download Oracle Instant Client**
   ```bash
   cd /tmp
   wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basic-linux.x64-21.1.0.0.0.zip
   ```

2. **Extract and Install**
   ```bash
   sudo mkdir -p /opt/oracle
   sudo unzip instantclient-basic-linux.x64-21.1.0.0.0.zip -d /opt/oracle
   cd /opt/oracle/instantclient_21_1
   sudo ln -sf libclntsh.so.21.1 libclntsh.so
   ```

3. **Set Environment Variables**
   ```bash
   export LD_LIBRARY_PATH=/opt/oracle/instantclient_21_1:$LD_LIBRARY_PATH
   ```
   
   Add to `~/.bashrc` or `~/.zshrc`:
   ```bash
   echo 'export LD_LIBRARY_PATH=/opt/oracle/instantclient_21_1:$LD_LIBRARY_PATH' >> ~/.bashrc
   source ~/.bashrc
   ```

#### For macOS:

1. **Using Homebrew (Easiest)**
   ```bash
   brew install instantclient-basic
   ```

2. **Or Manual Installation**
   - Download from Oracle website
   - Extract to `/opt/oracle/instantclient_21_1`
   - Set environment variable:
     ```bash
     export DYLD_LIBRARY_PATH=/opt/oracle/instantclient_21_1:$DYLD_LIBRARY_PATH
     ```

## Alternative: Use Thin Mode (If Possible)

If you can upgrade to Oracle Database 12c or later, you can use thin mode (no Instant Client needed). However, for Oracle XE 11g, you must use thick mode.

## Verify Installation

After installing Instant Client, test the connection:

```bash
cd backend
python test_db_connection.py
```

You should see:
```
✅ Connection pool created successfully!
✅ Connection acquired successfully!
✅ Query executed successfully!
```

## Troubleshooting

### Error: "Could not initialize thick mode"
- Make sure Instant Client is installed
- Check that PATH (Windows) or LD_LIBRARY_PATH (Linux) is set correctly
- Restart your terminal/IDE after setting environment variables

### Error: "libclntsh.so: cannot open shared object file" (Linux)
- Check LD_LIBRARY_PATH is set
- Verify the library file exists in the Instant Client directory

### Error: Still getting DPY-3010
- Make sure you restarted your terminal after installing
- Try setting the path explicitly in your code (see below)

## Explicit Path Configuration

If automatic detection doesn't work, you can set the path explicitly in `database.py`:

```python
# At the top of database.py, before other imports
import oracledb

# Set the path to your Instant Client
oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_21_3")
# Or for Linux:
# oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_21_1")
```

## Quick Test

After installation, run:
```bash
python test_db_connection.py
```

If successful, you'll see all green checkmarks! ✅

