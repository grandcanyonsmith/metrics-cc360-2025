"""
Clean SaaS Metrics Dashboard API
Main application using the new service architecture.
"""

import os
import logging
from datetime import datetime, timedelta
from dataclasses import asdict
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from metrics_service import MetricsService
from metrics_registry import registry
from snowflake_service import SnowflakeConnectionError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='build/static', template_folder='build')
CORS(app)

# Initialize services
metrics_service = MetricsService()


def handle_errors(f):
    """Error handling decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except SnowflakeConnectionError as e:
            return jsonify({
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }), 500
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e}")
            return jsonify({
                "error": "Internal server error",
                "details": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }), 500
    return decorated_function


@app.route('/api/health')
@handle_errors
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "cc360-metrics-api",
            "metrics_count": len(registry.get_all_metrics())
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/dashboard_metrics')
@handle_errors
def dashboard_metrics():
    """Get all dashboard metrics for a date range"""
    start_date = request.args.get('start', 
                                 (datetime.now() - timedelta(days=30)).isoformat())
    end_date = request.args.get('end', datetime.now().isoformat())
    
    # Parse dates
    try:
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except Exception:
        start_dt = datetime.now() - timedelta(days=30)
        end_dt = datetime.now()
    
    # Calculate all metrics
    metrics = metrics_service.calculate_all_metrics(start_dt, end_dt)
    
    # Convert to JSON-serializable format
    response = {}
    for key, metric in metrics.items():
        response[key] = asdict(metric)
    
    return jsonify(response)


@app.route('/api/metric_details/<metric_name>')
@handle_errors
def metric_details(metric_name):
    """Get detailed data for a specific metric"""
    start_date = request.args.get('start', 
                                 (datetime.now() - timedelta(days=30)).isoformat())
    end_date = request.args.get('end', datetime.now().isoformat())
    
    # Parse dates
    try:
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except Exception:
        start_dt = datetime.now() - timedelta(days=30)
        end_dt = datetime.now()
    
    # Get additional parameters
    params = {}
    for key, value in request.args.items():
        if key not in ['start', 'end']:
            params[key] = value
    
    try:
        data = metrics_service.get_metric_details(metric_name, start_dt, end_dt, **params)
        return jsonify({"data": data, "status": "ok"})
        
    except Exception as e:
        logger.error(f"Failed to fetch details for {metric_name}: {e}")
        return jsonify({
            "error": f"Failed to fetch details for {metric_name}: {str(e)}"
        }), 500


@app.route('/api/metrics/config')
@handle_errors
def metrics_config():
    """Get metrics configuration for frontend"""
    configs = registry.get_all_metrics()
    response = {}
    
    for key, config in configs.items():
        response[key] = {
            "title": config.title,
            "description": config.description,
            "category": config.category,
            "metric_type": config.metric_type.value,
            "color": config.color,
            "icon": config.icon,
            "trend": config.trend,
            "trend_value": config.trend_value,
            "requires_params": config.requires_params,
            "param_options": config.param_options
        }
    
    return jsonify(response)


@app.route('/api/categories')
@handle_errors
def categories():
    """Get all metric categories"""
    return jsonify({
        "categories": registry.get_categories()
    })


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
    port = int(os.environ.get('PORT', 5002))
    logger.info(f"Starting Flask app on port {port}")
    logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    logger.info(f"Debug mode: {os.environ.get('FLASK_DEBUG', 'False')}")
    app.run(host='0.0.0.0', port=port, debug=False) 