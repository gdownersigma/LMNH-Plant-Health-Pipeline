# Plant Streamlit Dashboard 

A streamlit dashboard to visualise live and summary plant data from the extracted plant data.

## Overview

This dashboard has three main sections including the live data view, summary statistics, and notifications for plant care.

## Project Structure

```
dashboard/
├── dashboard.py                   # Main streamlit dashboard
├── live_data_query.py             # Functions to query live plant data
├── chart.py                       # Functions to create charts
└── pages/
    ├── history.py                 # Page plant history over time
    └── notifications.py           # Page for notifying plant care
```

## Setup

### 1. Install Dependencies

```bash
pip install -r dashboard_requirements.txt
```

### 2. Configure Database Connection

Create a `.env` file in the `dashboard/` directory with your database credentials:

```env
DB_HOST=your_server.database.windows.net
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=plants
DB_PORT=1433
S3_BUCKET=your_bucket_name
AWS_REGION=your_aws_region (default: eu-west-2)
SCHEMA_NAME=c21_curdie_plant_catalog
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

### 3. Running the Pipeline

From the `dashboard/` directory:

```bash
streamlit run dashboard.py
```

### What Happens:

**Dashboard Features:**
- Displays live plant data with real-time moisture and temperature readings
- Shows summary statistics for plant health across the data
- Provides plant care notifications and alerts
- Allows historical data viewing and trend analysis
- Visualises plant data through charts and graphs

## ETL Pipeline Flow

```
Database
   ↓
live_data_query.py (fetch plant data)
   ↓
chart.py (create visualizations)
   ↓
dashboard.py (main dashboard display)
├── Live Data View
├── Summary Statistics
└── Notifications
   ↓
Streamlit Web Interface
```

## Notes

- The dashboard requires active database connectivity to display live data
- Ensure all environment variables are properly configured before running
- The dashboard updates periodically to reflect the latest sensor readings
- Charts and statistics are generated dynamically from the queried data
- Plant care notifications are based on calculated thresholds and plant requirements

## Troubleshooting

**Dashboard Won't Load:**
- Verify the `.env` file is in the `dashboard/` directory with correct credentials
- Check that the Streamlit server is running on the correct port
- Ensure all dependencies from `dashboard_requirements.txt` are installed

**No Data Displaying:**
- Confirm database connection is active and accessible
- Verify database credentials in `.env` are correct
- Check that the database contains plant and sensor data
- Review browser console for any error messages

**Missing Charts or Visualizations:**
- Ensure `chart.py` functions are properly imported in dashboard pages
- Verify that required data fields exist in the database