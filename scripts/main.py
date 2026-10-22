import requests
import pandas as pd
import time
from pathlib import Path
from google.cloud import bigquery
from google.oauth2 import service_account

# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
POPULATION_FILE = PROJECT_DIR / "data" / "population.csv"

# Open-Meteo API endpoint
API_URL = "https://api.open-meteo.com/v1/forecast"
def upload_to_bigquery(dataframe):
    """Upload cleaned weather data to BigQuery."""

    project_id = "noted-amphora-512320-t4"
    dataset_id = "global_weather_data"
    table_id = "current_weather_stats"

    key_path = PROJECT_DIR / "scripts" / "gcp-key.json"

    credentials = service_account.Credentials.from_service_account_file(
        str(key_path)
    )

    client = bigquery.Client(
        project=project_id,
        credentials=credentials,
    )

    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    job = client.load_table_from_dataframe(
        dataframe,
        table_ref,
        job_config=job_config,
    )

    job.result()

    print(f"Successfully uploaded {len(dataframe)} rows to {table_ref}")



def fetch_weather(location):
    """Fetch current temperature and wind speed, retrying temporary failures."""

    params = {
        "latitude": location["Latitude"],
        "longitude": location["Longitude"],
        "current": "temperature_2m,wind_speed_10m",
        "timezone": "auto",
    }

    for attempt in range(1, 4):
        try:
            response = requests.get(API_URL, params=params, timeout=30)
            response.raise_for_status()
            payload = response.json()

            current = payload.get("current")

            if not current:
                raise ValueError(
                    "Current weather data is missing from the API response."
                )

            return {
                "City": location["City"],
                "Country": location["Country"],
                "Temperature": current["temperature_2m"],
                "Wind_Speed": current["wind_speed_10m"],
            }

        except requests.RequestException:
            if attempt == 3:
                raise

            print(
                f"Request failed for {location['City']}. "
                f"Retrying ({attempt}/3)..."
            )
            time.sleep(2)



def main():
    # Load the original dataset supplied for the assignment.
    population_df = pd.read_csv(POPULATION_FILE)

    required_columns = {
        "City", "Country", "Population", "Latitude", "Longitude"
    }

    missing_columns = required_columns - set(population_df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Use the first 50 locations from the supplied dataset.
    locations = population_df.head(50).copy()

    print(f"Locations selected: {len(locations)}")
    print("Fetching weather data from Open-Meteo...\n")

    weather_records = []

    for _, location in locations.iterrows():
        try:
            record = fetch_weather(location)
            weather_records.append(record)

            print(
                f"{record['City']}, {record['Country']}: "
                f"{record['Temperature']} °C, "
                f"wind speed {record['Wind_Speed']}"
            )

        except (requests.RequestException, ValueError, KeyError) as error:
            print(f"Could not fetch weather for {location['City']}: {error}")

    if not weather_records:
        raise RuntimeError(
            "No weather records were retrieved. Check your internet connection."
        )

    weather_df = pd.DataFrame(weather_records)

    # Merge on city and country to match records accurately.
    merged_df = population_df.merge(
        weather_df,
        on=["City", "Country"],
        how="inner",
        validate="one_to_one",
    )

    print(f"\nRows after merging: {len(merged_df)}")

    # Remove rows missing required values, as permitted by the assignment.
    merged_df = merged_df.dropna(
        subset=[
            "City",
            "Country",
            "Population",
            "Latitude",
            "Longitude",
            "Temperature",
            "Wind_Speed",
        ]
    ).copy()

    # Enforce the required data types.
    merged_df["Population"] = pd.to_numeric(
        merged_df["Population"], errors="raise"
    ).astype("int64")

    merged_df["Temperature"] = pd.to_numeric(
        merged_df["Temperature"], errors="raise"
    ).astype("float64")

    merged_df["Wind_Speed"] = pd.to_numeric(
        merged_df["Wind_Speed"], errors="raise"
    ).astype("float64")

    # Convert Celsius to Fahrenheit.
    merged_df["Temperature_Fahrenheit"] = (
        merged_df["Temperature"] * 9 / 5 + 32
    ).astype("float64")

    print(f"Rows after cleaning: {len(merged_df)}")

    print("\nData types:")
    print(merged_df.dtypes)

    print("\nMissing values:")
    print(merged_df.isna().sum())

    print("\nFirst 10 rows of the cleaned dataset:")
    print(merged_df.head(10).to_string(index=False))

    print("\nLocal data pipeline completed successfully.")

    upload_to_bigquery(merged_df)

    return merged_df

if __name__ == "__main__":
    cleaned_df = main()
