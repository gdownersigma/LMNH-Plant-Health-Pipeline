# Load Schema and Data into Microsoft SQL Server

This tool loads your schema and botanist data into a Microsoft SQL Server database using Python.

## Prerequisites
- Python 3.x
- `pymssql` package (`pip install pymssql`)
- `python-dotenv` package (`pip install python-dotenv`)

## Usage

1. Ensure your `.env` file in the project root contains:
   - `DB_HOST`
   - `DB_PORT`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_NAME`

2. Run the script:

```sh
python load_schema_and_data.py
```

## Notes
- The script automatically loads credentials from `.env`
- Executes all SQL in `schema.sql`
- Imports all rows from `seed_botanists.csv` into the `botanist` table
