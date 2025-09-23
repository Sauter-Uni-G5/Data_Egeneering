import pandas as pd
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def extract_weather_to_dict(raw_weather_data: Any, lat: float, lng: float, location_id: str = None) -> Dict:
    try:
        result = {
            'location_id': location_id or f"lat_{lat}_lng_{lng}",
            'latitude': lat,
            'longitude': lng,
            'weather_data': raw_weather_data,
            'extraction_status': 'success' if raw_weather_data else 'empty',
            'error_message': None
        }
        
        logger.debug(f"Weather transformado para {lat}, {lng}")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao transformar weather: {e}")
        return {
            'location_id': location_id or f"lat_{lat}_lng_{lng}",
            'latitude': lat,
            'longitude': lng,
            'weather_data': None,
            'extraction_status': 'error',
            'error_message': str(e)
        }

def extract_multiple_weather_to_df(weather_results: list) -> pd.DataFrame:
    try:
        if not weather_results:
            return pd.DataFrame()
        
        df = pd.DataFrame(weather_results)
        
        logger.info(f"Weather DataFrame criado: {len(df)} registros")
        return df
        
    except Exception as e:
        logger.error(f"Erro ao criar DataFrame weather: {e}")
        return pd.DataFrame()