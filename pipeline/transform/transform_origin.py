"""Script to transform origin data."""

import pandas as pd

def get_raw_origin(data: pd.DataFrame) -> pd.DataFrame:
    """Extract unique origin details from the plant data."""
    origin_data = data[['origin_city', 'origin_country',
                      'origin_latitude', 'origin_longitude']]

    origin_data = origin_data.reset_index(drop=True)
    return origin_data


def validate_latitude(latitude) -> bool:
    """Validate latitude values."""
    if pd.isna(latitude):
        print("Validation failed: latitude is NaN")
        return False
    max_lat = 90.0
    min_lat = -90.0

    if not isinstance(latitude, (float, int)):
        print(
            f"Validation failed: latitude {latitude} is not a number (type: {type(latitude)})")
        return False

    if not min_lat <= latitude <= max_lat:
        print(f"Validation failed: latitude {latitude} out of range [{min_lat}, {max_lat}]")
        return False

    return True


def validate_longitude(longitude) -> bool:
    """Validate longitude values."""
    if pd.isna(longitude):
        print("Validation failed: longitude is NaN")
        return False
    max_long = 180.0
    min_long = -180.0

    if not isinstance(longitude, (float, int)):
        print(
            f"Validation failed: longitude {longitude} is not a number (type: {type(longitude)})")
        return False

    if not min_long <= longitude <= max_long:
        print(f"Validation failed: longitude {longitude} out of range [{min_long}, {max_long}]")
        return False

    return True


def validate_city_country(data: pd.DataFrame) -> bool:
    """Validate city and country data for the origin data."""

    if pd.isna(data):
        print("Validation failed: city/country is NaN")
        return False
    if not isinstance(data, str):
        print(f"Validation failed: city/country {data} is not a string (type: {type(data)})")
        return False
    if data.strip() == "":
        print("Validation failed: city/country is empty or whitespace only")
        return False
    return True


def validate_origin_data(origin_data: pd.DataFrame) -> bool:
    """Validate origin location data columns."""
    if not origin_data['origin_latitude'].apply(validate_latitude).all():
        print("Validation failed: lat/long contains invalid latitude values")
        return False

    if not origin_data['origin_longitude'].apply(validate_longitude).all():
        print("Validation failed: lat/long contains invalid longitude values")
        return False

    for col in ['origin_city', 'origin_country']:
        if not origin_data[col].apply(validate_city_country).all():
            print(f"Validation failed: column '{col}' contains invalid city/country values")
            return False
    return True


def clean_city_country(df: pd.DataFrame) -> pd.DataFrame:
    """Clean city and country data for the origin data."""

    df['origin_city'] = df['origin_city'].apply(lambda x: x.strip().title() if isinstance(x, str) else x)
    df['origin_country'] = df['origin_country'].apply(lambda x: x.strip().title() if isinstance(x, str) else x)
    return df


def clean_lat_long(df: pd.DataFrame) -> pd.DataFrame:
    """Clean latitudes and longitudes for the origin data."""

    df['origin_latitude'] = df['origin_latitude'].astype(float)
    df['origin_longitude'] = df['origin_longitude'].astype(float)
    return df


def transform_origin_data(origin_data: pd.DataFrame) -> pd.DataFrame:
    """Transform and clean origin location data."""
    origin_data = clean_city_country(origin_data)
    origin_data = clean_lat_long(origin_data)
    if validate_origin_data(origin_data):
        print("Origin data validation passed")
        return origin_data
    print("ERROR: Origin data validation failed")
    raise ValueError("Origin data validation failed.")


def get_country_ids(origin_data: pd.DataFrame) -> None:
    """Generate country IDs and save to countries.csv."""

    countries_df = origin_data[['origin_country']].drop_duplicates().reset_index(drop=True)
    countries_df.insert(0, 'country_id', range(1, len(countries_df) + 1))
    countries_df.to_csv('countries.csv', index=False)


def get_city_ids(origin_data: pd.DataFrame) -> None:
    """Generate city IDs and save to cities.csv."""

    cities_df = origin_data[['origin_city', 'country_id']].drop_duplicates().reset_index(drop=True)
    cities_df.insert(0, 'city_id', range(1, len(cities_df) + 1))
    cities_df.to_csv('cities.csv', index=False)


def assign_country_ids(origin_data: pd.DataFrame) -> pd.DataFrame:
    """Assign country IDs to origin data based on countries.csv."""

    countries_df = pd.read_csv('countries.csv')
    new_countries = [c for c in origin_data['origin_country'].unique()
                     if c not in countries_df['origin_country'].values]

    if new_countries:
        next_id = countries_df['country_id'].max() + 1
        new_countries_df = pd.DataFrame({
            'country_id': range(next_id, next_id + len(new_countries)),
            'origin_country': new_countries
        })
        countries_df = pd.concat([countries_df, new_countries_df], ignore_index=True)
        countries_df.to_csv('countries.csv', index=False)

    merged_df = origin_data.merge(countries_df, on='origin_country', how='left').drop(columns=['origin_country'])
    return merged_df


def assign_city_ids(origin_data: pd.DataFrame) -> pd.DataFrame:
    """Assign city IDs to origin data based on cities.csv."""
    cities_df = pd.read_csv('cities.csv')
    new_cities = [c for c in origin_data['origin_city'].unique()
                  if c not in cities_df['origin_city'].values]
    if new_cities:
        next_id = cities_df['city_id'].max() + 1
        new_cities_df = pd.DataFrame({
            'city_id': range(next_id, next_id + len(new_cities)),
            'origin_city': new_cities
        })
        cities_df = pd.concat([cities_df, new_cities_df], ignore_index=True)
        cities_df.to_csv('cities.csv', index=False)

    merged_df = origin_data.merge(cities_df, on='origin_city', how='left').drop(columns=['origin_city'])

    return merged_df


def process_origin_data(all_data: pd.DataFrame) -> None:
    """Main function to process origin data."""
    origin_df = get_raw_origin(all_data).dropna()
    transformed_origin_df = transform_origin_data(origin_df)
    get_country_ids(transformed_origin_df['origin_country'].to_frame())
    assigned_origin_df = assign_country_ids(transformed_origin_df)
    get_city_ids(assigned_origin_df[['origin_city', 'country_id']])
    assigned_origin_df = assign_city_ids(assigned_origin_df)
    return assigned_origin_df


if __name__ == "__main__":
    # Takes input from extract.py
    # all_plants = fetch_all_plants()
    # plants_df = to_dataframe(all_plants)

    #From transform_origin.py
    # origin_df = process_origin_data(plants_df)
    # cities_df = pd.read_csv('cities.csv')
    # countries_df = pd.read_csv('countries.csv')
    pass
