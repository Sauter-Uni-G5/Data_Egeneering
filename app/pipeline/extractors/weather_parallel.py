import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.weather_service import get_weather_data

def fetch_weather_for_reservoir(reservatorio_id, lat, lon, start_date, end_date):
    print(f"Buscando weather para {reservatorio_id} ({lat}, {lon}) de {start_date} até {end_date}")
    weather = get_weather_data(lat, lon, start_date, end_date)
    daily = weather.get("daily", {})
    dates = daily.get("time", [])
    temp_max = daily.get("temperature_2m_max", [])
    temp_min = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])
    # Monta DataFrame para esse reservatório
    df = pd.DataFrame({
        "id_reservatorio": reservatorio_id,
        "ear_data": pd.to_datetime(dates),
        "temperature_2m_max": temp_max,
        "temperature_2m_min": temp_min,
        "precipitation_sum": precip
    })
    return df

def fetch_weather_batch(df, start_date, end_date, max_workers=5):
    unique_reservoirs = df[["id_reservatorio", "val_latitude", "val_longitude"]].drop_duplicates()
    unique_reservoirs = unique_reservoirs.dropna(subset=["val_latitude", "val_longitude"])
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                fetch_weather_for_reservoir,
                row["id_reservatorio"],
                row["val_latitude"],
                row["val_longitude"],
                start_date,
                end_date
            )
            for _, row in unique_reservoirs.iterrows()
        ]
        for future in as_completed(futures):
            results.append(future.result())

    return pd.concat(results, ignore_index=True)