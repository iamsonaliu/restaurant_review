#!/usr/bin/env python3
"""
Database Connection Test Script
Tests the Oracle database connection and shows detailed error messages
"""

import os
import sys
from dotenv import load_dotenv
import oracledb
import traceback

# Try to initialize thick mode for older Oracle versions
print("\n🔧 Checking Oracle client mode...")
try:
    if oracledb.is_thin_mode():
        print("   Currently in thin mode - attempting to switch to thick mode...")
        try:
            oracledb.init_oracle_client()
            print("   ✅ Initialized Oracle client in thick mode")
        except Exception as e:
            error_msg = str(e)
            print(f"   ⚠️  Could not initialize thick mode: {error_msg}")
            if "DPY-3010" in error_msg or "thick mode" in error_msg.lower():
                print("\n   📝 SOLUTION: You need to install Oracle Instant Client")
                print("   See: backend/ORACLE_CLIENT_SETUP.md for detailed instructions")
                print("\n   Quick steps:")
                print("   1. Download Oracle Instant Client from Oracle website")
                print("   2. Extract to a folder (e.g., C:\\oracle\\instantclient_21_3)")
                print("   3. Add that folder to your system PATH")
                print("   4. Restart your terminal and try again")
    else:
        print("   ✅ Already in thick mode")
except Exception as e:
    print(f"   ⚠️  Error checking mode: {e}")

# Load environment variables
BASE_DIR = os.path.dirname(__file__)
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path)

def test_connection():
    """Test database connection with detailed error reporting"""
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    
    # Get credentials
    user = os.getenv('ORACLE_USER')
    password = os.getenv('ORACLE_PASSWORD')
    dsn = os.getenv('ORACLE_DSN')
    
    print(f"\n📋 Configuration:")
    print(f"   User: {user if user else '❌ NOT SET'}")
    print(f"   Password: {'*' * len(password) if password else '❌ NOT SET'}")
    print(f"   DSN: {dsn if dsn else '❌ NOT SET'}")
    
    # Check if .env file exists
    if not os.path.exists(env_path):
        print(f"\n❌ ERROR: .env file not found at: {env_path}")
        print("\n📝 Please create a .env file in the backend/ directory with:")
        print("   ORACLE_USER=your_username")
        print("   ORACLE_PASSWORD=your_password")
        print("   ORACLE_DSN=your_dsn")
        return False
    
    # Check if all required variables are set
    if not user or not password or not dsn:
        print("\n❌ ERROR: Missing required environment variables!")
        print("\n📝 Please ensure your .env file contains:")
        print("   ORACLE_USER=your_username")
        print("   ORACLE_PASSWORD=your_password")
        print("   ORACLE_DSN=your_dsn")
        print("\n💡 DSN format examples:")
        print("   - localhost:1521/XEPDB1")
        print("   - localhost:1521/ORCL")
        print("   - (DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=XEPDB1)))")
        return False
    
    print("\n🔌 Attempting to connect to database...")
    
    try:
        # Try to create a connection pool
        print("   Creating connection pool...")
        pool = oracledb.create_pool(
            user=user,
            password=password,
            dsn=dsn,
            min=1,
            max=2,
            increment=1
        )
        print("   ✅ Connection pool created successfully!")
        
        # Try to get a connection
        print("   Acquiring connection from pool...")
        conn = pool.acquire()
        print("   ✅ Connection acquired successfully!")
        
        # Try to execute a simple query
        print("   Testing query execution...")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        cursor.close()
        print(f"   ✅ Query executed successfully! Result: {result}")
        
        # Test a more complex query
        print("   Testing table access...")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM RESTAURANTS")
        count = cursor.fetchone()[0]
        cursor.close()
        print(f"   ✅ Found {count} restaurants in database!")
        
        # Return connection to pool
        pool.release(conn)
        print("\n✅ All database tests passed!")
        print("\n💡 Your database connection is working correctly.")
        print("   You can now run the Flask server with: python run.py")
        
        pool.close()
        return True
        
    except oracledb.Error as e:
        error_obj, = e.args
        print(f"\n❌ Oracle Database Error:")
        print(f"   Error Code: {error_obj.code}")
        print(f"   Error Message: {error_obj.message}")
        
        if error_obj.code == 1017:  # Invalid username/password
            print("\n💡 This usually means:")
            print("   - Incorrect username or password")
            print("   - User account is locked")
            print("   - User doesn't have proper permissions")
        elif error_obj.code == 12514:  # TNS:listener does not currently know
            print("\n💡 This usually means:")
            print("   - Database service name is incorrect")
            print("   - Database listener is not running")
            print("   - DSN format is incorrect")
        elif error_obj.code == 12154:  # TNS:could not resolve the connect identifier
            print("\n💡 This usually means:")
            print("   - DSN format is incorrect")
            print("   - Database host/port is wrong")
            print("   - Network connectivity issues")
        elif error_obj.code == 12541:  # TNS:no listener
            print("\n💡 This usually means:")
            print("   - Oracle listener is not running")
            print("   - Wrong port number")
            print("   - Database server is not accessible")
        
        print("\n📝 Troubleshooting steps:")
        print("   1. Verify your .env file has correct credentials")
        print("   2. Check if Oracle database is running")
        print("   3. Verify the DSN format is correct")
        print("   4. Test connection using SQL*Plus or SQL Developer")
        print("   5. Check Oracle listener status: lsnrctl status")
        
        traceback.print_exc()
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        print("\n📝 This might be:")
        print("   - Missing oracledb package: pip install oracledb")
        print("   - Python version incompatibility")
        print("   - System configuration issue")
        
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)

