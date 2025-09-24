import requests

def get_weather_data(latitude: float, longitude: float, start_date: str, end_date: str):
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={latitude}&longitude={longitude}"
        f"&start_date={start_date}&end_date={end_date}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=America/Sao_Paulo"
    )
    try:
        response = requests.get(url, timeout=30)  # timeout aumentado para 30 segundos
        if response.status_code == 200:
            return response.json()
        return {"error": "Não foi possível obter os dados meteorológicos", "status_code": response.status_code}
    except Exception as e:
        print(f"Erro na requisição weather: {e}")
        return {"error": str(e), "status_code": None}