"""Script to transform and clean plant data."""
import re
import pandas as pd


def load_data(file_path: str):
    """Load data from a CSV file into a DataFrame."""
    return pd.read_csv(file_path)


def save_clean_data(df: pd.DataFrame, file_path: str):
    """Save cleaned data to a CSV file."""
    df.to_csv(file_path, index=False)


def get_botanists(df: pd.DataFrame) -> pd.DataFrame:
    """Extract unique botanist details from the plant data."""
    botanists_df = df[['botanist_name',
                       'botanist_email',
                       'botanist_phone']].dropna().drop_duplicates()

    botanists_df['botanist_phone'] = botanists_df['botanist_phone'].apply(
        clean_phone_number)

    botanists_df = botanists_df.reset_index(drop=True)
    return botanists_df


def clean_phone_number(phone: str) -> str:
    """Clean and standardise phone numbers."""
    if pd.isna(phone) or phone == '':
        return None

    parts = phone.split('x')
    number = parts[0]
    country_code = 0

    number = re.sub(r'[+.\(\)\-]', '', number)

    if len(number[:-10]) > 0:
        country_code = int(number[:-10])

    number = number[-10:-7] + '-' + number[-7:-4] + '-' + number[-4:]

    if country_code > 0:
        number = '+' + str(country_code) + '-' + number

    if len(parts) == 1:
        return number

    return number + 'x' + parts[1]


if __name__ == "__main__":
    df = load_data("out.csv")

    df = get_botanists(df)

    save_clean_data(df, "clean_botanists.csv")
    print("Cleaned botanist data saved to 'clean_botanists.csv'")
