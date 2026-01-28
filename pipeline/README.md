# Plant Sensor Data ETL Pipeline

An ETL (Extract, Transform, Load) pipeline that retrieves plant sensor data from an API, cleans and validates it, and loads it into a Microsoft SQL Server database.

## Overview

This pipeline extracts plant data including sensor readings, botanist information, and geographic origins from the Sigma Labs Plants API, transforms the data to ensure quality and consistency, then loads it into a relational database following proper foreign key relationships.

## Database Schema

The pipeline populates the following tables in order:

1. **country** - Country names
2. **city** - Cities linked to countries
3. **origin** - Geographic coordinates (lat/long) linked to cities
4. **botanist** - Botanist contact information
5. **plant** - Plant records with references to origin and botanist
6. **plant_reading** - Sensor readings (soil moisture, temperature) for each plant

## Project Structure

```
pipeline/
├── pipeline.py              # Main ETL orchestration
├── extract/
│   └── extract.py           # API data extraction functions
├── transform/
│   ├── transform_origin.py     # Clean/validate origin data
│   ├── transform_botanist.py   # Clean botanist data
│   ├── transform_plants.py     # Clean plant data
│   └── transform_readings.py   # Clean sensor readings
└── load/
    ├── load_origin.py          # Load countries, cities, origins
    ├── load_botanist.py        # Load botanists
    ├── load_plant.py           # Load plants
    └── load_plant_readings.py  # Load sensor readings
```

## Setup

### 1. Install Dependencies

```bash
pip install -r pipeline_requirements.txt
```

### 2. Configure Database Connection

Create a `.env` file in the `pipeline/` directory with your database credentials:

```env
DB_HOST=your_server.database.windows.net
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=plants
DB_PORT=1433
```

### 3. Ensure Database Schema Exists

The database tables must be created before running the pipeline. Use the schema definition in the `schema/` folder if needed.

## Running the Pipeline

From the `pipeline/` directory:

```bash
python3 pipeline.py
```

### What Happens:

**Extract Phase:**
- Fetches all plant data from the API
- Handles sensor faults and plants on loan
- Flattens nested JSON into a pandas DataFrame

**Transform Phase:**
- Validates and cleans geographic coordinates
- Standardizes city/country names (title case)
- Cleans botanist phone numbers
- Validates and cleans plant names
- Converts timestamps to proper datetime format
- Rounds sensor readings to appropriate precision

**Load Phase:**
1. Loads unique origins (creates countries/cities as needed)
2. Loads unique botanists (checks for duplicates by email)
3. Loads plants (looks up origin_id and botanist_id)
4. Loads sensor readings

## ETL Pipeline Flow

```
API → Extract → DataFrame
         ↓
    Transform (clean & validate)
    ├── origins
    ├── botanists
    ├── plants
    └── readings
         ↓
    Load (respecting FK constraints)
    ├── countries/cities/origins
    ├── botanists
    ├── plants
    └── readings
         ↓
    Database
```

## Testing

Run tests for individual modules:

```bash
# Test extract functions
pytest extract/test_extract.py

# Test transform functions
pytest transform/test_transform_origin.py
pytest transform/test_transform_botanist.py
pytest transform/test_transform_plants.py
pytest transform/test_readings.py

# Test load functions
pytest load/test_load_origin.py
pytest load/test_load_botanist.py
pytest load/test_load_plant.py
pytest load/test_load_plant_readings.py
```

Run all tests:
```bash
pytest
```

## Notes

- The pipeline handles duplicate data gracefully (get-or-create pattern for botanists and origins)
- Plant data is upserted (update if exists, insert if new)
- Currently, image URLs are truncated to 100 characters to fit database constraints (TODO: increase DB column size)
- Coordinates are cleaned and cast to float for consistent matching

## Troubleshooting

**Connection Issues:**
- Verify `.env` file exists and has correct credentials
- Check database server firewall rules
- Ensure VPN is connected if required

**Foreign Key Errors:**
- Ensure database schema matches expected structure
- Check that all referenced IDs exist before loading dependent tables

**Data Validation Failures:**
- Review validation errors in console output
- Check that API data format hasn't changed
