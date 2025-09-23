import logging
import pandas as pd

from app.controllers.registry_controller import get_registry_direct
from app.controllers.hydro_controller import get_hydro_data_direct  
from app.controllers.ear_controller import get_ear_data_direct
from app.controllers.weather_controller import get_weather_direct

from app.pipeline.extractors.ons_extractor import extract_registry_to_df, extract_hydro_to_df, extract_ear_to_df
from app.pipeline.extractors.weather_extractor import extract_weather_to_dict, extract_multiple_weather_to_df

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def teste_completo():
    """Teste simples: Controller → Extractor → DataFrame"""
    print("🧪 TESTE EXTRACTORS COMPLETO")
    print("=" * 50)
    
    REGISTRY_PACKAGE = "61e92787-9847-4731-8b73-e878eb5bc158"
    HYDRO_PACKAGE = "98a9aa79-06fe-4a9f-ac6b-04aa707bdfca"
    EAR_PACKAGE = "61e92787-9847-4731-8b73-e878eb5bc158"
    
    # 1. TESTE REGISTRY
    print("\n1️⃣ REGISTRY:")
    print("-" * 20)
    try:
        raw_registry = get_registry_direct(REGISTRY_PACKAGE)
        print(f"Controller retornou: {type(raw_registry)}")
        print(f"Tamanho: {len(raw_registry) if isinstance(raw_registry, (list, dict)) else 'N/A'}")
        df_registry = extract_registry_to_df(raw_registry)
        print(f"Extractor criou: DataFrame com {len(df_registry)} registros")
        if not df_registry.empty:
            print("Colunas:", list(df_registry.columns)[:5], "...")
            print("Preview:")
            print(df_registry.head(2).to_string())
    except Exception as e:
        print(f"❌ Erro no Registry: {e}")

    # 2. TESTE HYDRO
    print("\n2️⃣ HYDRO:")
    print("-" * 20)
    try:
        raw_hydro = get_hydro_data_direct(HYDRO_PACKAGE, start_date="2020-01-01", end_date="2020-12-31", page_size=50)
        print(f"Controller retornou: {type(raw_hydro)}")
        print(f"Tamanho: {len(raw_hydro) if isinstance(raw_hydro, (list, dict)) else 'N/A'}")
        df_hydro = extract_hydro_to_df(raw_hydro)
        print(f"Extractor criou: DataFrame com {len(df_hydro)} registros")
        if not df_hydro.empty:
            print("Colunas:", list(df_hydro.columns)[:5], "...")
            print("Preview:")
            print(df_hydro.head(2).to_string())
    except Exception as e:
        print(f"❌ Erro no Hydro: {e}")

    # 3. TESTE EAR
    print("\n3️⃣ EAR:")
    print("-" * 20)
    try:
        raw_ear = get_ear_data_direct(EAR_PACKAGE, start_date="2020-01-01", end_date="2020-12-31", page_size=50)
        print(f"Controller retornou: {type(raw_ear)}")
        print(f"Tamanho: {len(raw_ear) if isinstance(raw_ear, (list, dict)) else 'N/A'}")
        df_ear = extract_ear_to_df(raw_ear)
        print(f"Extractor criou: DataFrame com {len(df_ear)} registros")
        if not df_ear.empty:
            print("Colunas:", list(df_ear.columns)[:5], "...")
            print("Preview:")
            print(df_ear.head(2).to_string())
    except Exception as e:
        print(f"❌ Erro no EAR: {e}")

    # 4. TESTE WEATHER
    print("\n4️⃣ WEATHER:")
    print("-" * 20)
    try:
        raw_weather = get_weather_direct(-15.7939, -47.8828, "2020-01-01", "2020-01-03")
        print(f"Controller retornou: {type(raw_weather)}")
        weather_dict = extract_weather_to_dict(raw_weather, -15.7939, -47.8828, "BSB")
        print(f"Extractor criou: Dict com status '{weather_dict['extraction_status']}'")
        weather_list = [weather_dict]
        df_weather = extract_multiple_weather_to_df(weather_list)
        print(f"DataFrame weather: {len(df_weather)} registros")
        if not df_weather.empty:
            print("Colunas:", list(df_weather.columns))
            print("Preview:")
            print(df_weather.head(1).to_string())
    except Exception as e:
        print(f"❌ Erro no Weather: {e}")

    print("\n✅ TESTE CONCLUÍDO!")

if __name__ == "__main__":
    teste_completo()