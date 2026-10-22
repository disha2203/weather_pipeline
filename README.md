
# Weather and Demographics Data Pipeline

## Overview

This project collects current weather data from the Open-Meteo API and combines it with a demographic dataset using Python and Pandas. The cleaned dataset is uploaded to Google BigQuery for SQL-based analysis.

## Technologies

- Python
- Requests
- Pandas
- Open-Meteo API
- Google BigQuery
- SQL
- Git and GitHub

## Project Structure

- `data/` — Local demographic dataset (excluded from Git)
- `scripts/main.py` — Data ingestion, cleaning, and BigQuery upload
- `.gitignore` — Excludes local datasets, virtual environments, and credentials

## Pipeline Steps

1. Read the demographic CSV dataset.
2. Retrieve current temperature and wind speed for selected locations.
3. Merge weather data with demographic data by city and country.
4. Clean missing values and enforce data types.
5. Calculate temperature in Fahrenheit.
6. Upload the cleaned dataset to BigQuery.
7. Query the uploaded data using SQL.

## Setup

1. Create and activate a Python virtual environment.
2. Install the required Python packages: `requests`, `pandas`, `google-cloud-bigquery`, and `pyarrow`.
3. Place the supplied demographic dataset at `data/population.csv`.
4. Configure Google Cloud credentials locally at `scripts/gcp-key.json`.
5. Update the project ID in `scripts/main.py` if using a different Google Cloud project.

## Run

From the project root, execute:

```bash
python scripts/main.py
```

## Security

Never commit service-account JSON keys, credentials, or other secrets to GitHub. The credential file is excluded using `.gitignore`.

## Notes

The script uses the first 50 locations from the supplied demographic dataset. Population values reflect the dataset's recorded city populations, not necessarily national populations.
