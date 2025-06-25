#!/bin/bash

# Deployment script for SaaS Metrics Dashboard
set -e

echo "🚀 Starting deployment process..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "app.py" ] || [ ! -f "package.json" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Build React app
print_status "Building React application..."
if [ ! -d "node_modules" ]; then
    print_status "Installing Node.js dependencies..."
    npm install
fi

npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    print_error "React build failed - build directory not found"
    exit 1
fi

print_status "React build completed successfully"

# Check for environment variables
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating example..."
    cat > .env << EOF
# Snowflake Connection Configuration
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
SNOWFLAKE_PRIVATE_KEY_PATH=snowflake_private_key.p8

# Flask App Configuration
FLASK_ENV=production
FLASK_DEBUG=false
PORT=8080
EOF
    print_warning "Please update .env with your actual Snowflake credentials"
fi

# Check for Snowflake private key
if [ ! -f "snowflake_private_key.p8" ]; then
    print_error "Snowflake private key (snowflake_private_key.p8) not found"
    print_error "Please ensure your Snowflake private key is in the project root"
    exit 1
fi

# Determine deployment target
DEPLOY_TARGET=${1:-docker}

case $DEPLOY_TARGET in
    "docker")
        print_status "Deploying with Docker..."
        
        # Build Docker image
        docker build -t saas-metrics-dashboard .
        
        # Run container
        docker run -d \
            --name saas-metrics-dashboard \
            -p 8080:8080 \
            --env-file .env \
            saas-metrics-dashboard
        
        print_status "Docker deployment completed!"
        print_status "Application available at: http://localhost:8080"
        ;;
        
    "heroku")
        print_status "Deploying to Heroku..."
        
        # Check if Heroku CLI is installed
        if ! command -v heroku &> /dev/null; then
            print_error "Heroku CLI not found. Please install it first."
            exit 1
        fi
        
        # Create Procfile for Heroku
        echo "web: python app.py" > Procfile
        
        # Deploy to Heroku
        heroku create saas-metrics-dashboard-$(date +%s) || true
        heroku config:set FLASK_ENV=production
        heroku config:set FLASK_DEBUG=false
        heroku config:set PORT=8080
        
        # Set Snowflake environment variables
        source .env
        heroku config:set SNOWFLAKE_ACCOUNT="$SNOWFLAKE_ACCOUNT"
        heroku config:set SNOWFLAKE_USER="$SNOWFLAKE_USER"
        heroku config:set SNOWFLAKE_ROLE="$SNOWFLAKE_ROLE"
        heroku config:set SNOWFLAKE_WAREHOUSE="$SNOWFLAKE_WAREHOUSE"
        heroku config:set SNOWFLAKE_DATABASE="$SNOWFLAKE_DATABASE"
        heroku config:set SNOWFLAKE_SCHEMA="$SNOWFLAKE_SCHEMA"
        heroku config:set SNOWFLAKE_PRIVATE_KEY_PATH="$SNOWFLAKE_PRIVATE_KEY_PATH"
        
        git add .
        git commit -m "Deploy to Heroku" || true
        git push heroku main
        
        print_status "Heroku deployment completed!"
        print_status "Application available at: $(heroku info -s | grep web_url | cut -d= -f2)"
        ;;
        
    "railway")
        print_status "Deploying to Railway..."
        
        # Check if Railway CLI is installed
        if ! command -v railway &> /dev/null; then
            print_error "Railway CLI not found. Please install it first."
            exit 1
        fi
        
        # Create railway.json for Railway
        cat > railway.json << EOF
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "python app.py",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF
        
        # Deploy to Railway
        railway up
        
        print_status "Railway deployment completed!"
        ;;
        
    "render")
        print_status "Deploying to Render..."
        
        # Create render.yaml for Render
        cat > render.yaml << EOF
services:
  - type: web
    name: saas-metrics-dashboard
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: FLASK_ENV
        value: production
      - key: FLASK_DEBUG
        value: false
      - key: PORT
        value: 8080
      - key: SNOWFLAKE_ACCOUNT
        sync: false
      - key: SNOWFLAKE_USER
        sync: false
      - key: SNOWFLAKE_ROLE
        sync: false
      - key: SNOWFLAKE_WAREHOUSE
        sync: false
      - key: SNOWFLAKE_DATABASE
        sync: false
      - key: SNOWFLAKE_SCHEMA
        sync: false
      - key: SNOWFLAKE_PRIVATE_KEY_PATH
        sync: false
EOF
        
        print_status "Render configuration created!"
        print_status "Please deploy manually to Render using the render.yaml file"
        ;;
        
    *)
        print_error "Unknown deployment target: $DEPLOY_TARGET"
        print_status "Available targets: docker, heroku, railway, render"
        exit 1
        ;;
esac

print_status "Deployment completed successfully! 🎉" 