# SaaS Metrics Dashboard

A comprehensive dashboard for tracking key SaaS metrics including churn rates, activation rates, Facebook metrics, and more.

## Features

- **Dormant Account Rate**: Track inactive user accounts
- **24-Hour Activation Rate**: Monitor user engagement after signup
- **Involuntary Churn Rate**: Track payment failures and cancellations
- **Dunning Recovery Rate**: Monitor payment recovery success
- **Facebook Metrics**: CAC to LTV ratio and lead ads tracking
- **Platform Breakdown**: User activity by platform
- **Root Cause Analysis**: Payment failure reasons

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+ (for frontend development)
- Snowflake account with proper credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd metrics-cc360-2025
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**
   ```bash
   npm install
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your Snowflake credentials
   ```

5. **Build the frontend**
   ```bash
   npm run build
   ```

### Running the Application

#### Option 1: Using the startup script
```bash
./start.sh
```

#### Option 2: Direct Python execution
```bash
python app.py
```

The application will be available at: **http://localhost:5002**

## Environment Variables

Create a `.env` file with the following variables:

```env
# Snowflake Connection Configuration
SNOWFLAKE_ACCOUNT=your_account_here
SNOWFLAKE_USER=your_username_here
SNOWFLAKE_ROLE=your_role_here
SNOWFLAKE_WAREHOUSE=your_warehouse_here
SNOWFLAKE_DATABASE=your_database_here
SNOWFLAKE_SCHEMA=your_schema_here
SNOWFLAKE_PRIVATE_KEY_PATH=snowflake_private_key.p8

# Flask App Configuration
FLASK_ENV=production
FLASK_DEBUG=false
PORT=8080
```

## API Endpoints

### Health Check
```
GET /api/health
```

### Dashboard Metrics
```
GET /api/dashboard_metrics?start=2025-05-26T00:00:00Z&end=2025-06-26T23:59:59Z
```

### Metric Details
```
GET /api/metric_details/{metric_name}
```

Available metrics:
- `dormant_account_rate`
- `t24h_activation_rate`
- `involuntary_churn_rate`
- `dunning_recovery_rate`
- `facebook_lead_ads_total`
- `facebook_cac_to_ltv_ratio`
- `platform_breakdown`
- `root_cause_pareto`

## Development

### Frontend Development
```bash
npm start
```

### Backend Development
```bash
python app.py
```

### Building for Production
```bash
npm run build
```

## Troubleshooting

### Common Issues

1. **Snowflake Connection Error**
   - Verify your credentials in `.env`
   - Ensure the private key file exists
   - Check network connectivity

2. **Facebook Metrics Error**
   - Verify Facebook data sources are accessible
   - Check date range parameters

3. **Port Already in Use**
   - Change the port in `.env` or app.py
   - Kill existing processes on port 5002

### Logs

The application logs to stdout. Check for:
- Connection errors
- Query execution times
- Data processing issues

## Deployment

### Docker
```bash
docker build -t saas-metrics-dashboard .
docker run -p 5002:5002 saas-metrics-dashboard
```

### Railway
```bash
railway up
```

### Render
```bash
# Deploy via Render dashboard or CLI
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is proprietary and confidential. 