import pandas as pd
from app.controllers.registry_controller import get_registry_direct
from app.controllers.ear_controller import get_ear_data_direct
from app.controllers.hydro_controller import get_hydro_data_direct
from app.pipeline.extractors.ons_extractor import (
    extract_registry_to_df, extract_ear_to_df, extract_hydro_to_df
)
from app.pipeline.transformers.data_cleaner import clean_and_normalize
from app.pipeline.transformers.aggregator import aggregate_ear_hydro_registry

REGISTRY_PACKAGE = "a849a9c1-09b8-4b9b-84dc-5ac113043f37"
EAR_PACKAGE = "61e92787-9847-4731-8b73-e878eb5bc158"
HYDRO_PACKAGE = "98a9aa79-06fe-4a9f-ac6b-04aa707bdfca"

def main():
    # 1. Registry
    raw_registry = get_registry_direct(REGISTRY_PACKAGE)
    df_registry = extract_registry_to_df(raw_registry)
    print("Colunas do registry após extractor:", df_registry.columns.tolist())
    df_registry_clean = clean_and_normalize(df_registry)
    print("Colunas do registry após limpeza:", df_registry_clean.columns.tolist())

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

    # 5. Salva o resultado
    df_final.to_csv("tabela_final.csv", index=False, encoding="utf-8", sep=";")
    print("Tabela final agregada salva como tabela_final.csv")
    print(df_final.head(10).to_string())

if __name__ == "__main__":
    main()