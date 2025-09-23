import pandas as pd
import logging
from typing import Any, List, Dict

logger = logging.getLogger(__name__)

def extract_registry_to_df(raw_data: Any) -> pd.DataFrame:
    """
    Transforma dados brutos do registry controller em DataFrame
    """
    try:
        if isinstance(raw_data, dict):
            # Se é dict com 'data' key
            if 'data' in raw_data:
                return pd.DataFrame(raw_data['data'])
            # Se é dict simples
            else:
                return pd.DataFrame([raw_data])
        elif isinstance(raw_data, list):
            # Se é lista de registros
            return pd.DataFrame(raw_data)
        else:
            logger.warning(f"Formato de dados registry desconhecido: {type(raw_data)}")
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f"Erro ao transformar registry em DataFrame: {e}")
        return pd.DataFrame()

def extract_hydro_to_df(raw_data: Any) -> pd.DataFrame:
    """
    Transforma dados brutos do hydro controller em DataFrame
    """
    try:
        if isinstance(raw_data, dict):
            if 'data' in raw_data:
                return pd.DataFrame(raw_data['data'])
            else:
                return pd.DataFrame([raw_data])
        elif isinstance(raw_data, list):
            return pd.DataFrame(raw_data)
        else:
            logger.warning(f"Formato de dados hydro desconhecido: {type(raw_data)}")
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f"Erro ao transformar hydro em DataFrame: {e}")
        return pd.DataFrame()

def extract_ear_to_df(raw_data: Any) -> pd.DataFrame:
    try:
        if isinstance(raw_data, dict):
            if 'data' in raw_data:
                return pd.DataFrame(raw_data['data'])
            else:
                return pd.DataFrame([raw_data])
        elif isinstance(raw_data, list):
            return pd.DataFrame(raw_data)
        else:
            logger.warning(f"Formato de dados EAR desconhecido: {type(raw_data)}")
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f"Erro ao transformar EAR em DataFrame: {e}")
        return pd.DataFrame()