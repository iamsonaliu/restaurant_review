import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.user = os.getenv('ORACLE_USER')
        self.password = os.getenv('ORACLE_PASSWORD')
        self.dsn = os.getenv('ORACLE_DSN')
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=self.dsn
            )
            return self.connection
        except oracledb.Error as error:
            print(f"Database connection error: {error}")
            return None
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query, params=None, fetch_one=False):
        """Execute a query and return results"""
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
            
            return result
        except oracledb.Error as error:
            print(f"Query execution error: {error}")
            return None
        finally:
            cursor.close()
    
    def execute_update(self, query, params=None):
        """Execute an INSERT/UPDATE/DELETE query"""
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return True
        except oracledb.Error as error:
            print(f"Update execution error: {error}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

# Global database instance
db = Database()