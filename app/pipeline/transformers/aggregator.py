import pandas as pd

def aggregate_ear_hydro_registry(
    df_ear: pd.DataFrame,
    df_hydro: pd.DataFrame,
    df_registry: pd.DataFrame
) -> pd.DataFrame:
    df_ear_sel = df_ear[[
        "nom_reservatorio",
        "tip_reservatorio",
        "nom_bacia",
        "ear_data",
        "ear_reservatorio_percentual",
        "ear_total_mwmes"
    ]].copy()

    df_hydro_sel = df_hydro[[
        "id_reservatorio",
        "nom_bacia", 
        "din_instante",
        "val_volumeutilcon"
    ]].copy()

    df_registry_sel = df_registry[[
        "nom_reservatorio",
        "val_volmax",
        "id_reservatorio",
        "val_latitude",
        "val_longitude"
    ]].copy()

    df = pd.merge(
        df_ear_sel,
        df_registry_sel,
        on="nom_reservatorio",
        how="left"
    )

    # Normaliza datas para .dt.date para garantir merge correto
    df["ear_data"] = pd.to_datetime(df["ear_data"], errors="coerce")
    df_hydro_sel["din_instante"] = pd.to_datetime(df_hydro_sel["din_instante"], errors="coerce")
    df["ear_data"] = df["ear_data"].dt.date
    df_hydro_sel["din_instante"] = df_hydro_sel["din_instante"].dt.date

    # MERGE AJUSTADO: inclui nom_bacia
    df = pd.merge(
        df,
        df_hydro_sel,
        left_on=["id_reservatorio", "ear_data"],
        right_on=["id_reservatorio", "din_instante"],
        how="left"
    )

    final_cols = [
        "nom_reservatorio",
        "tip_reservatorio",
        "ear_data",
        "ear_reservatorio_percentual",
        "ear_total_mwmes",
        "val_volmax",
        "id_reservatorio",
        "val_volumeutilcon"
    ]
    df_final = df[final_cols]
    df_final = df_final.sort_values(["id_reservatorio", "ear_data"]).reset_index(drop=True)
    return df_final