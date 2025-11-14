# inside app/database.py (Database.connect)
import traceback
import os
import oracledb
import sys
from dotenv import load_dotenv

# safe to load again - no-op if already loaded
load_dotenv()

# Try to initialize thick mode for older Oracle versions
# This is required for Oracle XE 11g and earlier versions
# The error DPY-3010 means we need thick mode
try:
    # Check if we're in thin mode
    if oracledb.is_thin_mode():
        # Try to switch to thick mode
        # This will use Oracle Instant Client if installed
        try:
            oracledb.init_oracle_client()
            print("✅ Initialized Oracle client in thick mode")
        except Exception as e:
            # If init_oracle_client fails, Instant Client might not be installed
            # or might not be in PATH
            error_msg = str(e)
            if "DPY-3010" in error_msg or "thick mode" in error_msg.lower():
                print("⚠️  Oracle Instant Client not found or not in PATH")
                print("   Please install Oracle Instant Client for Oracle XE 11g")
                print("   See: backend/ORACLE_CLIENT_SETUP.md for instructions")
            else:
                print(f"⚠️  Could not initialize thick mode: {e}")
except Exception:
    # If already in thick mode or other issue, continue
    pass

class Database:
    def __init__(self):
        self.user = os.getenv('ORACLE_USER')
        self.password = os.getenv('ORACLE_PASSWORD')
        self.dsn = os.getenv('ORACLE_DSN')
        self.pool = None

    def connect(self):
        if self.pool:
            return True
        try:
            print(f"Attempting to create DB pool with user={self.user}, dsn={self.dsn}")
            self.pool = oracledb.create_pool(
                user=self.user,
                password=self.password,
                dsn=self.dsn,
                min=1,
                max=4,
                increment=1,
                getmode=oracledb.SPOOL_ATTRVAL_WAIT
            )
            print("✅ Database pool created successfully.")
            return True
        except Exception as err:
            print("❌ Database connection error:", repr(err))
            traceback.print_exc()
            print("Ensure ORACLE_USER/ORACLE_PASSWORD/ORACLE_DSN are correct and DB listener is running.")
            self.pool = None
            return False

    def disconnect(self):
        try:
            if self.pool:
                self.pool.close()
                print("Database pool closed.")
                self.pool = None
        except Exception as err:
            print("Error closing pool:", repr(err))

    def get_connection(self):
        if not self.pool:
            # Try to connect if pool doesn't exist
            if not self.connect():
                raise RuntimeError(
                    "Database pool not initialized. "
                    "Please check your .env file and ensure the database is running. "
                    f"User: {self.user}, DSN: {self.dsn}"
                )
        return self.pool.acquire()
    def _dict_from_cursor(self, cursor):
        """Convert cursor.description + rows -> list[dict]"""
        cols = []
        if cursor.description:
            cols = [d[0].lower() for d in cursor.description]
        rows = cursor.fetchall()
        if not cols:
            # no column metadata (e.g., DDL or no rows)
            return rows
        result = [dict(zip(cols, row)) for row in rows]
        return result

    def execute_query(self, sql, params=None, fetch_one=False):
        """
        Run a SELECT or other query that returns rows.
        Returns: list of dicts (column names lowercased) or empty list.
        If fetch_one=True, returns single dict or None.
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # oracledb supports binding via dict or tuple
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            data = self._dict_from_cursor(cursor)
            cursor.close()
            conn.close()  # returns connection to pool
            
            if fetch_one:
                return data[0] if data else None
            return data
        except Exception as e:
            # print traceback for server logs (helps debugging)
            print("DB execute_query error:", repr(e), file=sys.stderr)
            traceback.print_exc()
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
            return None  # calling code should handle None -> raise/500

    def execute_non_query(self, sql, params=None, returning=False):
        """
        Run INSERT/UPDATE/DELETE.
        If returning is a tuple of (return_column, bind_var_name), attempts to fetch RETURNING into Python var.
        Returns: dict with keys: rowcount, returning (if any)
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if returning and isinstance(returning, tuple) and len(returning) == 2:
                # Example use: returning = ('id', 'rid')
                return_col, bind_name = returning
                # create a variable placeholder and bind it
                out_var = cursor.var(oracledb.DB_TYPE_VARCHAR)  # adjust type as needed
                bind_params = params or {}
                bind_params[bind_name] = out_var
                cursor.execute(sql, bind_params)
                # commit and return value
                conn.commit()
                val = out_var.getvalue()
                cursor.close()
                conn.close()
                return {'rowcount': cursor.rowcount, 'returning': val}
            else:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                conn.commit()
                rc = cursor.rowcount
                cursor.close()
                conn.close()
                return {'rowcount': rc}
        except Exception as e:
            print("DB execute_non_query error:", repr(e), file=sys.stderr)
            traceback.print_exc()
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
            return None

db = Database()