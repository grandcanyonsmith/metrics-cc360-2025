#!/bin/bash

# Start the React app with real data
echo "🚀 Starting React App with Real Data..."

# Check if Python dependencies are installed
if ! python -c "import flask, snowflake.connector, pandas" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Check if Node dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Check if Snowflake key exists
if [ ! -f "snowflake_private_key.pem" ]; then
    echo "🔑 Snowflake private key not found. Please run:"
    echo "   chmod +x generate_keys.sh && ./generate_keys.sh"
    echo "   Then create a .env file with your Snowflake credentials."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating example..."
    cat > .env << EOF
# Snowflake Connection Configuration
SNOWFLAKE_ACCOUNT=TOOOUVG-RHB65714
SNOWFLAKE_USER=COURSECREATOR360
SNOWFLAKE_ROLE=SEGMENT_ROLE
SNOWFLAKE_WAREHOUSE=AUTOMATION_WH
SNOWFLAKE_DATABASE=SEGMENT_DB
SNOWFLAKE_SCHEMA=COURSECREATOR360_WEBSITE_JS_PROD
SNOWFLAKE_PRIVATE_KEY_PATH=snowflake_private_key.pem

# Flask App Configuration
FLASK_ENV=development
FLASK_DEBUG=true
EOF
    echo "📝 Created .env file. Please update with your actual credentials."
fi

echo "🔧 Starting Flask backend on port 60638..."
python app.py &
FLASK_PID=$!

echo "⏳ Waiting for Flask backend to start..."
sleep 3

echo "🌐 Starting React development server on port 3000..."
npm start &
REACT_PID=$!

echo "✅ Both servers are starting..."
echo "   - Flask Backend: http://localhost:60638"
echo "   - React Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
trap "echo '🛑 Stopping servers...'; kill $FLASK_PID $REACT_PID 2>/dev/null; exit" INT
wait 