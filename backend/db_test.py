# db_test.py
import os
import traceback

try:
    import oracledb
except Exception as e:
    print("Failed to import oracledb. Install it with: pip install oracledb")
    print("Import error:", repr(e))
    raise

# Optional: set this to your instant client path if you want thick mode
# e.g. r"C:/Program Files/Oracle/instantclient_19_29"
INSTANT_CLIENT_DIR = os.getenv("INSTANT_CLIENT_DIR", r"C:/Program Files/Oracle/instantclient_19_29")

def try_init_instant_client(lib_dir):
    try:
        if lib_dir and os.path.exists(lib_dir):
            print(f"Attempting to init Oracle Instant Client from: {lib_dir}")
            oracledb.init_oracle_client(lib_dir=lib_dir)
            print("✅ Instant Client initialized (thick mode).")
            return True
        elif lib_dir:
            print(f"Instant Client path does not exist: {lib_dir}")
            return False
        else:
            print("No INSTANT_CLIENT_DIR provided; skipping init_oracle_client (thin mode will be used).")
            return False
    except Exception as ex:
        print("Failed to initialize Instant Client (will try thin mode if available).")
        traceback.print_exc()
        return False

def main():
    # Try to init Instant Client if path is present
    init_ok = try_init_instant_client(INSTANT_CLIENT_DIR)

    # Read env vars (these will pick up values from your .env when load_dotenv is used)
    user = os.getenv('ORACLE_USER', 'system')
    password = os.getenv('ORACLE_PASSWORD', 'oracle')
    dsn = os.getenv('ORACLE_DSN', 'localhost:1521/xe')  # use lowercase 'xe' or 'XE' — both usually work

    print("\nUsing connection parameters:")
    print(" ORACLE_USER:", user)
    print(" ORACLE_DSN :", dsn)
    print(" InstantClientInit:", "yes" if init_ok else "no (thin mode)")

    try:
        # Try a quick connection (thin mode works without instant client in recent oracledb)
        print("\nAttempting to connect to Oracle...")
        conn = oracledb.connect(user=user, password=password, dsn=dsn)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM DUAL")
        row = cur.fetchone()
        print("Connected OK. SELECT 1 ->", row)
        cur.close()
        conn.close()
    except Exception as err:
        print("\n❌ Connection attempt failed. Full traceback follows:")
        traceback.print_exc()
        print("\nCommon issues to check:")
        print(" - Is the Oracle DB (XE) listener running and accessible on the host and port in ORACLE_DSN?")
        print(" - Is ORACLE_USER / ORACLE_PASSWORD correct? (you are using the 'system' user; consider a less-privileged user for app)")
        print(" - If you see DPI or Instant Client related errors, ensure Instant Client files match your Python architecture and you passed the correct INSTANT_CLIENT_DIR.")
        print(" - If you don't need thick mode, ensure you are using a recent python-oracledb that supports thin mode: pip install --upgrade oracledb")

if __name__ == "__main__":
    main()
