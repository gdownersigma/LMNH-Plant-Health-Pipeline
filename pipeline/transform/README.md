# Transform Script

## Data Output

The transformed data will be returned from a main function as a dictionary holding several DataFrames.
The keys of the dictionary correspond to the table names in the schema.

## Example Output

```python
# Function in transform.py
def main_transform() -> dict[str, pd.DataFrame]:
    return {
        "botanist": pd.DataFrame,
        "country": pd.DataFrame,
        "origin": pd.DataFrame,
        "plant": pd.DataFrame,
        "plant_reading": pd.DataFrame
    }

# Used in main pipeline to get transformed data
if __name__ == "__main__":
    data = main_transform()

    botanist_df = data["botanist"]
    country_df = data["country"]
    origin_df = data["origin"]
    plant_df = data["plant"]
    plant_reading_df = data["plant_reading"]
```