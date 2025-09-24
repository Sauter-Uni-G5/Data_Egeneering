import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.weather_service import get_weather_data
import pandas as pd
from datetime import datetime, timedelta

def fetch_weather_for_reservoir(reservatorio_id, lat, lon, start_date, end_date):
    print(f"Buscando weather para {reservatorio_id} ({lat}, {lon}) de {start_date} até {end_date}")
    weather = get_weather_data(lat, lon, start_date, end_date)
    daily = weather.get("daily", {})
    dates = daily.get("time", [])
    temp_max = daily.get("temperature_2m_max", [])
    temp_min = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])

    df = pd.DataFrame({
        "id_reservatorio": reservatorio_id,
        "ear_data": pd.to_datetime(dates),
        "temperature_2m_max": temp_max,
        "temperature_2m_min": temp_min,
        "precipitation_sum": precip
    })
    return df

def fetch_weather_batch(df, start_date, end_date, max_workers=10, delta_days=60):
    unique_reservoirs = df[["id_reservatorio", "val_latitude", "val_longitude"]].drop_duplicates()
    unique_reservoirs = unique_reservoirs.dropna(subset=["val_latitude", "val_longitude"])
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                fetch_weather_for_reservoir_paged,
                row["id_reservatorio"],
                row["val_latitude"],
                row["val_longitude"],
                start_date,
                end_date,
                delta_days
            )
            for _, row in unique_reservoirs.iterrows()
        ]
        for future in as_completed(futures):
            results.append(future.result())
    return pd.concat(results, ignore_index=True)

def split_date_range(start_date: str, end_date: str, delta_days: int = 30):
    """Divide o intervalo em subintervalos de delta_days."""
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    ranges = []
    current = start
    while current < end:
        next_date = min(current + timedelta(days=delta_days-1), end)
        ranges.append((current.strftime("%Y-%m-%d"), next_date.strftime("%Y-%m-%d")))
        current = next_date + timedelta(days=1)
    return ranges

def fetch_weather_for_reservoir_paged(reservatorio_id, lat, lon, start_date, end_date, delta_days=30):
    dfs = []
    for sd, ed in split_date_range(start_date, end_date, delta_days):
        df = fetch_weather_for_reservoir(reservatorio_id, lat, lon, sd, ed)
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)