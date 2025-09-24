import pandas as pd
from app.controllers.registry_controller import get_registry_direct
from app.controllers.ear_controller import get_ear_data_direct
from app.controllers.hydro_controller import get_hydro_data_direct
from app.pipeline.extractors.ons_extractor import (
    extract_registry_to_df, extract_ear_to_df, extract_hydro_to_df
)
from app.pipeline.transformers.data_cleaner import clean_and_normalize
from app.pipeline.transformers.aggregator import aggregate_ear_hydro_registry
from app.pipeline.extractors.weather_parallel import fetch_weather_batch
from app.pipeline.transformers.feature_engineering import create_lags, create_diffs  # <-- NOVO

REGISTRY_PACKAGE = "a849a9c1-09b8-4b9b-84dc-5ac113043f37"
EAR_PACKAGE = "61e92787-9847-4731-8b73-e878eb5bc158"
HYDRO_PACKAGE = "98a9aa79-06fe-4a9f-ac6b-04aa707bdfca"

def main():
    # 1. Registry
    raw_registry = get_registry_direct(REGISTRY_PACKAGE)
    df_registry = extract_registry_to_df(raw_registry)
    df_registry_clean = clean_and_normalize(df_registry)

    # 2. EAR
    raw_ear = get_ear_data_direct(EAR_PACKAGE, start_date="2020-01-01", end_date="2020-12-31", page_size=10000)
    df_ear = extract_ear_to_df(raw_ear)
    df_ear_clean = clean_and_normalize(df_ear, date_col="ear_data" if "ear_data" in df_ear.columns else None)

    # 3. Hydro
    raw_hydro = get_hydro_data_direct(HYDRO_PACKAGE, start_date="2020-01-01", end_date="2020-12-31", page_size=10000)
    df_hydro = extract_hydro_to_df(raw_hydro)
    df_hydro_clean = clean_and_normalize(df_hydro, date_col="din_instante" if "din_instante" in df_hydro.columns else None)

    # 4. Agregação final
    df_final = aggregate_ear_hydro_registry(df_ear_clean, df_hydro_clean, df_registry_clean)

    # 5. Busca meteorologia em paralelo e faz merge
    df_weather = fetch_weather_batch(df_final, start_date="2020-01-01", end_date="2020-12-31", max_workers=5)
    
    print("\nPreview do DataFrame de weather:")
    print(df_weather.head(10))
    print(df_weather.dtypes)
    
    df_final = pd.merge(
        df_final,
        df_weather,
        on=["id_reservatorio", "ear_data"],
        how="left"
    )

    # 6. Testa criação de lags e diffs
    df_final_lag = create_lags(df_final, columns="ear_reservatorio_percentual", lag=1, groupby="id_reservatorio")
    df_final_diff = create_diffs(df_final, columns="ear_reservatorio_percentual", periods=1, groupby="id_reservatorio")

    print("\nColunas após lag:", df_final_lag.columns)
    print(df_final_lag[["id_reservatorio", "ear_data", "ear_reservatorio_percentual", "ear_reservatorio_percentual_lag1"]].head(10).to_string())

    print("\nColunas após diff:", df_final_diff.columns)
    print(df_final_diff[["id_reservatorio", "ear_data", "ear_reservatorio_percentual", "ear_reservatorio_percentual_diff1"]].head(10).to_string())

    df_final = clean_and_normalize(df_final, date_col="ear_data")

    df_final = df_final.drop(columns=["nom_bacia", "ear_data", "tip_reservatorio", "nom_reservatorio"])
    
    # 7. Salva o resultado
    df_final.to_csv("tabela_final.csv", index=False, encoding="utf-8", sep=";")
    print("Tabela final agregada salva como tabela_final.csv")

if __name__ == "__main__":
    main()