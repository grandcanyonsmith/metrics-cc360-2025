"""
Snowflake Service
Clean service for handling all Snowflake database operations.
"""

import os
import time
import traceback
import logging
from datetime import datetime
from typing import List, Dict
import pandas as pd
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key

logger = logging.getLogger(__name__)


class SnowflakeConnectionError(Exception):
    """Custom exception for Snowflake connection issues"""
    pass


class SnowflakeService:
    """Service for handling Snowflake database operations"""
    
    def __init__(self):
        self.conn = None
        self.last_connection_time = None
        self.connection_timeout = 300  # 5 minutes
    
    def get_connection(self):
        """Get or create Snowflake connection with connection pooling"""
        current_time = time.time()
        
        # Check if connection is stale or doesn't exist
        if (self.conn is None or 
            self.last_connection_time is None or 
            current_time - self.last_connection_time > self.connection_timeout):
            
            if self.conn:
                try:
                    self.conn.close()
                except:
                    pass
            
            self.conn = self._create_connection()
            self.last_connection_time = current_time
            logger.info("Created new Snowflake connection")
        
        return self.conn
    
    def _create_connection(self):
        """Create a Snowflake connection using PEM key authentication"""
        try:
            account = os.getenv('SNOWFLAKE_ACCOUNT', 'TOOOUVG-RHB65714')
            user = os.getenv('SNOWFLAKE_USER', 'COURSECREATOR360')
            role = os.getenv('SNOWFLAKE_ROLE', 'SEGMENT_ROLE')
            warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'AUTOMATION_WH')
            database = os.getenv('SNOWFLAKE_DATABASE', 'SEGMENT_DB')
            schema = os.getenv('SNOWFLAKE_SCHEMA', 'COURSECREATOR360_WEBSITE_JS_PROD')
            
            pem_path = os.getenv('SNOWFLAKE_PRIVATE_KEY_PATH', 
                               'snowflake_private_key.p8')
            
            if not os.path.exists(pem_path):
                # Try .pem extension as fallback
                pem_path = pem_path.replace('.p8', '.pem')
                if not os.path.exists(pem_path):
                    raise FileNotFoundError(f"Private key file not found: {pem_path}")
            
            with open(pem_path, 'rb') as key_file:
                private_key_pem = key_file.read()
            
            private_key = load_pem_private_key(private_key_pem, password=None)
            private_key_der = private_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            conn = snowflake.connector.connect(
                account=account,
                user=user,
                role=role,
                warehouse=warehouse,
                database=database,
                schema=schema,
                private_key=private_key_der,
                insecure_mode=True,
                autocommit=True,
                session_parameters={
                    'QUERY_TAG': 'saas_metrics_dashboard'
                }
            )
            
            return conn
            
        except Exception as e:
            logger.error(f"Snowflake connection error: {e}")
            traceback.print_exc()
            raise SnowflakeConnectionError(f"Failed to connect to Snowflake: {str(e)}")
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return DataFrame with error handling"""
        conn = self.get_connection()
        start_time = time.time()
        
        try:
            logger.info(f"Executing query: {query[:100]}...")
            df = pd.read_sql(query, conn)
            execution_time = time.time() - start_time
            logger.info(f"Query executed successfully in {execution_time:.2f}s, "
                       f"returned {len(df)} rows")
            return df
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Query execution failed after {execution_time:.2f}s: {e}")
            raise Exception(f"Query execution failed: {str(e)}")
    
    def clean_dataframe_for_json(self, df: pd.DataFrame) -> List[Dict]:
        """Clean DataFrame to handle NaT, NaN, and other non-serializable values"""
        if df.empty:
            return []
        
        df_clean = df.where(pd.notnull(df), None)
        records = []
        
        for _, row in df_clean.iterrows():
            record = {}
            for col, value in row.items():
                if pd.isna(value) or value is None:
                    record[col] = None
                elif isinstance(value, (pd.Timestamp, datetime)):
                    record[col] = value.isoformat() if pd.notna(value) else None
                else:
                    record[col] = value
            records.append(record)
        
        return records 