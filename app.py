import os
import traceback
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from functools import wraps
import time

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import pandas as pd
from cachetools import TTLCache, cached

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import query modules
from queries.dunning_recovery_rate import (
    summary_sql as dunning_summary_sql,
    details_sql as dunning_details_sql
)
from queries.dormant_account_rate import (
    summary_sql as dormant_summary_sql,
    details_sql as dormant_details_sql
)
from queries.t24h_activation_rate import (
    summary_sql as t24h_summary_sql,
    details_sql as t24h_details_sql
)
from queries.involuntary_churn_rate import (
    summary_sql as churn_summary_sql,
    details_sql as churn_details_sql
)
from queries.facebook_metrics import (
    facebook_cac_to_ltv_summary_sql,
    facebook_cac_to_ltv_details_sql,
    facebook_lead_ads_summary_sql,
    facebook_lead_ads_details_sql
)
from queries.platform_breakdown import (
    platform_breakdown_summary_sql,
    platform_breakdown_details_sql
)
from queries.root_cause_pareto import (
    root_cause_pareto_summary_sql,
    root_cause_pareto_details_sql
)

# Data classes for structured responses
@dataclass
class MetricResponse:
    value: Optional[float]
    numerator: int
    denominator: int
    status: str
    message: str
    data: Optional[List[Dict]] = None
    cached: bool = False
    execution_time: Optional[float] = None

@dataclass
class ErrorResponse:
    error: str
    status: str = "error"
    details: Optional[str] = None
    timestamp: str = None

class SnowflakeConnectionError(Exception):
    """Custom exception for Snowflake connection issues"""
    pass

class MetricsService:
    """Service class for handling metrics calculations with caching and connection pooling"""
    
    def __init__(self):
        self.conn = None
        self.last_connection_time = None
        self.connection_timeout = 300  # 5 minutes
        self._cache = TTLCache(maxsize=100, ttl=300)  # 5 minute cache
    
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
            
            pem_path = os.getenv('SNOWFLAKE_PRIVATE_KEY_PATH', 'snowflake_private_key.p8')
            
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
            logger.info(f"Query executed successfully in {execution_time:.2f}s, returned {len(df)} rows")
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
    
    @cached(cache=TTLCache(maxsize=50, ttl=300))
    def calculate_dormant_account_rate(self, start_dt: datetime, end_dt: datetime) -> MetricResponse:
        """Calculate dormant account rate with caching"""
        start_time = time.time()
        
        try:
            query = dormant_summary_sql(start_dt, end_dt)
            df = self.execute_query(query)
            
            if df.empty:
                return MetricResponse(
                    value=0.0,
                    numerator=0,
                    denominator=0,
                    status="ok",
                    message="No data available for dormant account rate",
                    cached=True,
                    execution_time=time.time() - start_time
                )
            
            row = df.iloc[0]
            dormant_rate = row.get('DORMANT_RATE') or row.get('dormant_rate') or 0
            dormant_users = row.get('DORMANT_USERS') or row.get('dormant_users') or 0
            total_users = row.get('TOTAL_USERS') or row.get('total_users') or 0
            
            return MetricResponse(
                value=float(dormant_rate),
                numerator=int(dormant_users),
                denominator=int(total_users),
                status="ok",
                message=f"{dormant_users} out of {total_users} users became dormant after first purchase",
                cached=True,
                execution_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Error calculating dormant account rate: {e}")
            return MetricResponse(
                value=None,
                numerator=0,
                denominator=0,
                status="error",
                message=f"Error calculating dormant account rate: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    @cached(cache=TTLCache(maxsize=50, ttl=300))
    def calculate_activation_rate(self, start_dt: datetime, end_dt: datetime) -> MetricResponse:
        """Calculate 24h activation rate with caching"""
        start_time = time.time()
        
        try:
            query = t24h_summary_sql(start_dt, end_dt)
            df = self.execute_query(query)
            
            if df.empty:
                return MetricResponse(
                    value=0.0,
                    numerator=0,
                    denominator=0,
                    status="ok",
                    message="No data available for activation rate",
                    cached=True,
                    execution_time=time.time() - start_time
                )
            
            row = df.iloc[0]
            activation_rate = row.get('ACTIVATION_RATE') or row.get('activation_rate') or 0
            activated_users = row.get('ACTIVATED_USERS') or row.get('activated_users') or 0
            total_users = row.get('TOTAL_USERS') or row.get('total_users') or 0
            
            return MetricResponse(
                value=float(activation_rate),
                numerator=int(activated_users),
                denominator=int(total_users),
                status="ok",
                message=f"{activated_users} out of {total_users} users activated within 24 hours",
                cached=True,
                execution_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Error calculating activation rate: {e}")
            return MetricResponse(
                value=None,
                numerator=0,
                denominator=0,
                status="error",
                message=f"Error calculating activation rate: {str(e)}",
                execution_time=time.time() - start_time
            )

    def calculate_involuntary_churn_rate(self, start_dt: datetime, end_dt: datetime) -> MetricResponse:
        """Calculate involuntary churn rate"""
        start_time = time.time()
        
        try:
            query = churn_summary_sql(start_dt, end_dt)
            df = self.execute_query(query)
            
            if df.empty:
                return MetricResponse(
                    value=0.0,
                    numerator=0,
                    denominator=0,
                    status="ok",
                    message="No data available for involuntary churn rate",
                    execution_time=time.time() - start_time
                )
            
            row = df.iloc[0]
            churn_rate = row.get('CHURN_RATE') or row.get('churn_rate') or 0
            churned_users = row.get('CHURNED_USERS') or row.get('churned_users') or 0
            total_users = row.get('TOTAL_USERS') or row.get('total_users') or 0
            
            return MetricResponse(
                value=float(churn_rate),
                numerator=int(churned_users),
                denominator=int(total_users),
                status="ok",
                message=f"{churned_users} out of {total_users} users churned due to payment failures",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Error calculating involuntary churn rate: {e}")
            return MetricResponse(
                value=None,
                numerator=0,
                denominator=0,
                status="error",
                message=f"Error calculating involuntary churn rate: {str(e)}",
                execution_time=time.time() - start_time
            )

    def calculate_dunning_recovery_rate(self, start_dt: datetime, end_dt: datetime) -> MetricResponse:
        """Calculate dunning recovery rate"""
        start_time = time.time()
        
        try:
            query = dunning_summary_sql(start_dt, end_dt)
            df = self.execute_query(query)
            
            if df.empty:
                return MetricResponse(
                    value=0.0,
                    numerator=0,
                    denominator=0,
                    status="ok",
                    message="No data available for dunning recovery rate",
                    execution_time=time.time() - start_time
                )
            
            row = df.iloc[0]
            recovery_rate = row.get('RECOVERY_RATE') or row.get('recovery_rate') or 0
            recovered_payments = row.get('RECOVERED_PAYMENTS') or row.get('recovered_payments') or 0
            total_failures = row.get('TOTAL_FAILURES') or row.get('total_failures') or 0
            
            return MetricResponse(
                value=float(recovery_rate),
                numerator=int(recovered_payments),
                denominator=int(total_failures),
                status="ok",
                message=f"{recovered_payments} out of {total_failures} failed payments were recovered",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Error calculating dunning recovery rate: {e}")
            return MetricResponse(
                value=None,
                numerator=0,
                denominator=0,
                status="error",
                message=f"Error calculating dunning recovery rate: {str(e)}",
                execution_time=time.time() - start_time
            )

    def calculate_facebook_metrics(self, start_dt: datetime, end_dt: datetime) -> Dict[str, MetricResponse]:
        """Calculate Facebook-related metrics"""
        try:
            # Facebook Lead Ads Total
            lead_ads_query = facebook_lead_ads_summary_sql(start_dt, end_dt)
            df_leads = self.execute_query(lead_ads_query)
            
            # Safely extract total_leads with better error handling
            total_leads = 0
            if not df_leads.empty and 'total_leads' in df_leads.columns:
                total_leads = df_leads.iloc[0]['total_leads']
            elif not df_leads.empty:
                # If column name is different, try to get the first numeric column
                numeric_columns = df_leads.select_dtypes(include=['number']).columns
                if len(numeric_columns) > 0:
                    total_leads = df_leads.iloc[0][numeric_columns[0]]
            
            return {
                'facebook_lead_ads_total': MetricResponse(
                    value=float(total_leads),
                    numerator=int(total_leads),
                    denominator=1,
                    status="ok",
                    message="Total Facebook lead ads in selected date range"
                )
            }
        except Exception as e:
            logger.error(f"Error calculating Facebook metrics: {e}")
            return {
                'facebook_lead_ads_total': MetricResponse(
                    value=None,
                    numerator=0,
                    denominator=0,
                    status="error",
                    message=f"Error calculating Facebook metrics: {str(e)}"
                )
            }

    def calculate_platform_breakdown(self, start_dt: datetime, end_dt: datetime) -> MetricResponse:
        """Calculate platform breakdown"""
        start_time = time.time()
        
        try:
            query = platform_breakdown_summary_sql(start_dt, end_dt)
            df = self.execute_query(query)
            data = self.clean_dataframe_for_json(df)
            
            return MetricResponse(
                value=None,
                numerator=0,
                denominator=0,
                status="ok",
                message="Top 5 platforms by event count",
                data=data,
                execution_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Error calculating platform breakdown: {e}")
            return MetricResponse(
                value=None,
                numerator=0,
                denominator=0,
                status="error",
                message=f"Error calculating platform breakdown: {str(e)}",
                execution_time=time.time() - start_time
            )

    def calculate_root_cause_pareto(self, start_dt: datetime, end_dt: datetime) -> MetricResponse:
        """Calculate root cause Pareto analysis"""
        start_time = time.time()
        
        try:
            query = root_cause_pareto_summary_sql(start_dt, end_dt)
            df = self.execute_query(query)
            data = self.clean_dataframe_for_json(df)
            
            return MetricResponse(
                value=None,
                numerator=0,
                denominator=0,
                status="ok",
                message="Top payment failure reasons",
                data=data,
                execution_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Error calculating root cause Pareto: {e}")
            return MetricResponse(
                value=None,
                numerator=0,
                denominator=0,
                status="error",
                message=f"Error calculating root cause Pareto: {str(e)}",
                execution_time=time.time() - start_time
            )

# Initialize Flask app and services
app = Flask(__name__, static_folder='build/static', template_folder='build')
CORS(app)
metrics_service = MetricsService()

# Error handling decorator
def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except SnowflakeConnectionError as e:
            return jsonify(asdict(ErrorResponse(str(e)))), 500
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e}")
            traceback.print_exc()
            return jsonify(asdict(ErrorResponse("Internal server error", details=str(e)))), 500
    return decorated_function

# API Routes
@app.route('/api/health')
@handle_errors
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/dashboard_metrics')
@handle_errors
def dashboard_metrics():
    """Get all dashboard metrics for a date range"""
    start_date = request.args.get('start', (datetime.now() - timedelta(days=30)).isoformat())
    end_date = request.args.get('end', datetime.now().isoformat())
    
    # Parse dates
    try:
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except Exception:
        start_dt = datetime.now() - timedelta(days=30)
        end_dt = datetime.now()
    
    # Calculate all metrics
    metrics = {}
    
    # Core metrics
    metrics['dormant_account_rate'] = metrics_service.calculate_dormant_account_rate(start_dt, end_dt)
    metrics['t24h_activation_rate'] = metrics_service.calculate_activation_rate(start_dt, end_dt)
    metrics['involuntary_churn_rate'] = metrics_service.calculate_involuntary_churn_rate(start_dt, end_dt)
    metrics['dunning_recovery_rate'] = metrics_service.calculate_dunning_recovery_rate(start_dt, end_dt)
    
    # Facebook metrics
    facebook_metrics = metrics_service.calculate_facebook_metrics(start_dt, end_dt)
    metrics.update(facebook_metrics)
    
    # Additional metrics
    metrics['platform_breakdown'] = metrics_service.calculate_platform_breakdown(start_dt, end_dt)
    metrics['root_cause_pareto'] = metrics_service.calculate_root_cause_pareto(start_dt, end_dt)
    
    # Convert to JSON-serializable format
    response = {}
    for key, metric in metrics.items():
        response[key] = asdict(metric)
    
    return jsonify(response)

@app.route('/api/metric_details/<metric_name>')
@handle_errors
def metric_details(metric_name):
    """Get detailed data for a specific metric"""
    start_date = request.args.get('start', (datetime.now() - timedelta(days=30)).isoformat())
    end_date = request.args.get('end', datetime.now().isoformat())
    
    # Parse dates
    try:
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except Exception:
        start_dt = datetime.now() - timedelta(days=30)
        end_dt = datetime.now()
    
    # Get additional parameters
    activated = request.args.get('activated')
    dormant = request.args.get('dormant')
    
    try:
        if metric_name == 'dormant_account_rate':
            query = dormant_details_sql(start_dt, end_dt, dormant=dormant == 'true')
        elif metric_name == 't24h_activation_rate':
            query = t24h_details_sql(start_dt, end_dt, activated=activated == 'false')
        elif metric_name == 'involuntary_churn_rate':
            query = churn_details_sql(start_dt, end_dt)
        elif metric_name == 'dunning_recovery_rate':
            query = dunning_details_sql(start_dt, end_dt)
        elif metric_name == 'facebook_cac_to_ltv_ratio':
            query = facebook_cac_to_ltv_details_sql(start_dt, end_dt)
        elif metric_name == 'facebook_lead_ads_total':
            query = facebook_lead_ads_details_sql(start_dt, end_dt)
        elif metric_name == 'platform_breakdown':
            query = platform_breakdown_details_sql(start_dt, end_dt)
        elif metric_name == 'root_cause_pareto':
            query = root_cause_pareto_details_sql(start_dt, end_dt)
        else:
            return jsonify({"error": f"Unknown metric: {metric_name}"}), 400
        
        df = metrics_service.execute_query(query)
        data = metrics_service.clean_dataframe_for_json(df)
        
        return jsonify({"data": data, "status": "ok"})
        
    except Exception as e:
        logger.error(f"Failed to fetch details for {metric_name}: {e}")
        return jsonify({"error": f"Failed to fetch details for {metric_name}: {str(e)}"}), 500

# Static file serving
@app.route('/')
def root():
    return send_from_directory('build', 'index.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory('build', 'index.html')

@app.route('/<path:path>')
def serve_react(path):
    if path.startswith('api/'):
        return jsonify({"error": "API endpoint not found"}), 404
    return send_from_directory('build', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True) 