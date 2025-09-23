import logging
from app.controllers.registry_controller import get_registry_direct
from app.controllers.hydro_controller import get_hydro_data_direct
from app.controllers.ear_controller import get_ear_data_direct
from app.controllers.weather_controller import get_weather_direct

from app.pipeline.extractors.ons_extractor import extract_registry_to_df, extract_hydro_to_df, extract_ear_to_df
from app.pipeline.extractors.weather_extractor import extract_weather_to_dict, extract_multiple_weather_to_df

logging.basicConfig(level=logging.INFO)

def teste_ons_extractors():
    print("🧪 TESTE ONS EXTRACTORS")
    print("-" * 40)
    
    # 1. Registry
    print("1. Registry:")
    try:
        raw_registry = get_registry_direct("61e92787-9847-4731-8b73-e878eb5bc158")  # Função direta
        df_registry = extract_registry_to_df(raw_registry)  # Extractor
        print(f"   Raw type: {type(raw_registry)}")
        print(f"   DataFrame: {len(df_registry)} registros")
        if len(df_registry) > 0:
            print(f"   Colunas: {list(df_registry.columns)[:5]}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # 2. Hydro
    print("2. Hydro:")
    try:
        raw_hydro = get_hydro_data_direct("98a9aa79-06fe-4a9f-ac6b-04aa707bdfca", page_size=100)  # Função direta
        df_hydro = extract_hydro_to_df(raw_hydro)  # Extractor
        print(f"   Raw type: {type(raw_hydro)}")
        print(f"   DataFrame: {len(df_hydro)} registros")
        if len(df_hydro) > 0:
            print(f"   Colunas: {list(df_hydro.columns)[:5]}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # 3. EAR
    print("3. EAR:")
    try:
        raw_ear = get_ear_data_direct("61e92787-9847-4731-8b73-e878eb5bc158", page_size=100)  # Função direta
        df_ear = extract_ear_to_df(raw_ear)  # Extractor
        print(f"   Raw type: {type(raw_ear)}")
        print(f"   DataFrame: {len(df_ear)} registros")
        if len(df_ear) > 0:
            print(f"   Colunas: {list(df_ear.columns)[:5]}")
    except Exception as e:
        print(f"   Erro: {e}")

def teste_weather_extractors():
    print("\n🌤️ TESTE WEATHER EXTRACTORS")
    print("-" * 40)
    
    # 1. Weather único
    print("1. Weather único:")
    try:
        raw_weather = get_weather_direct(-15.7939, -47.8828, "2020-01-01", "2020-01-03")  # Função direta
        weather_dict = extract_weather_to_dict(raw_weather, -15.7939, -47.8828, "BSB")  # Extractor
        print(f"   Raw type: {type(raw_weather)}")
        print(f"   Status: {weather_dict['extraction_status']}")
        print(f"   Dados: {'SIM' if weather_dict['weather_data'] else 'NÃO'}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # 2. Weather múltiplo
    print("2. Weather múltiplo:")
    try:
        # Simular múltiplas chamadas
        weather_results = []
        
        coordinates = [
            (-15.7939, -47.8828, "BSB"),
            (-23.5505, -46.6333, "SP")
        ]
        
        for lat, lng, city_id in coordinates:
            raw_weather = get_weather_direct(lat, lng, "2020-01-01", "2020-01-02")  # Função direta
            weather_dict = extract_weather_to_dict(raw_weather, lat, lng, city_id)  # Extractor
            weather_results.append(weather_dict)
        
        df_weather = extract_multiple_weather_to_df(weather_results)  # Extractor
        print(f"   DataFrame: {len(df_weather)} registros")
        
    except Exception as e:
        print(f"   Erro: {e}")

if __name__ == "__main__":
    teste_ons_extractors()
    teste_weather_extractors()