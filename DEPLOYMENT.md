# Deployment Guide

This guide will help you deploy the SaaS Metrics Dashboard to various platforms.

## Prerequisites

1. **Snowflake Account**: You need access to a Snowflake database with the required schemas
2. **Snowflake Private Key**: A private key file for authentication
3. **Environment Variables**: Configuration for your Snowflake connection

## Quick Start

### 1. Prepare Your Environment

First, ensure you have the required files:

```bash
# Check if you have the Snowflake private key
ls snowflake_private_key.p8

# Create .env file with your credentials
cp .env.example .env
# Edit .env with your actual Snowflake credentials
```

### 2. Build the Application

```bash
# Install dependencies and build
npm install
npm run build
```

### 3. Deploy

Choose your deployment platform:

#### Docker (Recommended for local/production)

```bash
# Make the deployment script executable
chmod +x deploy.sh

# Deploy with Docker
./deploy.sh docker
```

The application will be available at `http://localhost:8080`

#### Heroku

```bash
# Install Heroku CLI first
# Then deploy
./deploy.sh heroku
```

#### Railway

```bash
# Install Railway CLI first
# Then deploy
./deploy.sh railway
```

#### Render

```bash
# Generate configuration
./deploy.sh render

# Then deploy manually through Render dashboard
```

## Manual Deployment Options

### Docker

```bash
# Build the image
docker build -t saas-metrics-dashboard .

# Run the container
docker run -d \
  --name saas-metrics-dashboard \
  -p 8080:8080 \
  --env-file .env \
  saas-metrics-dashboard
```

### Heroku

1. Install Heroku CLI
2. Create a new Heroku app
3. Set environment variables:
   ```bash
   heroku config:set SNOWFLAKE_ACCOUNT=your_account
   heroku config:set SNOWFLAKE_USER=your_user
   # ... set all other variables
   ```
4. Deploy:
   ```bash
   git push heroku main
   ```

### Railway

1. Install Railway CLI
2. Login to Railway
3. Deploy:
   ```bash
   railway up
   ```

### Render

1. Connect your GitHub repository
2. Create a new Web Service
3. Use the `render.yaml` configuration
4. Set environment variables in the dashboard

## Environment Variables

Create a `.env` file with the following variables:

```env
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
```

## Health Check

The application includes a health check endpoint at `/api/health` that returns:

```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00.000000"
}
```

## Troubleshooting

### Common Issues

1. **Snowflake Connection Failed**
   - Check your credentials in `.env`
   - Verify the private key file exists
   - Ensure your Snowflake account is accessible

2. **Build Failed**
   - Make sure Node.js is installed
   - Run `npm install` before building
   - Check for any TypeScript/React errors

3. **Port Already in Use**
   - Change the PORT in `.env`
   - Kill any existing processes on the port

4. **Docker Build Failed**
   - Ensure Docker is running
   - Check if all required files are present
   - Verify the Dockerfile syntax

### Logs

Check application logs:

```bash
# Docker
docker logs saas-metrics-dashboard

# Heroku
heroku logs --tail

# Railway
railway logs

# Render
# Check logs in the dashboard
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` files to version control
2. **Private Keys**: Keep your Snowflake private key secure
3. **HTTPS**: Use HTTPS in production
4. **Access Control**: Implement proper authentication if needed

## Monitoring

The application includes:
- Health check endpoint for monitoring
- Error logging
- Performance metrics

## Support

If you encounter issues:
1. Check the logs
2. Verify your Snowflake connection
3. Ensure all environment variables are set correctly
4. Test locally before deploying 