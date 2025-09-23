import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def clean_and_normalize(df: pd.DataFrame, cols_to_normalize=None, date_col: str = None):
    df = df.copy()

    # Converter todas as colunas que parecem numéricas para float
    for col in df.columns:
        # Tenta converter para float se a coluna não for de texto/data
        if df[col].dtype == object:
            try:
                df[col] = pd.to_numeric(df[col], errors="ignore")
            except Exception:
                pass

    # Separar dia, mes, ano se date_col for informado
    if date_col and date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df["dia"] = df[date_col].dt.day
        df["mes"] = df[date_col].dt.month
        df["ano"] = df[date_col].dt.year

    if cols_to_normalize is None:
        cols_to_normalize = [
            "ear_reservatorio_percentual",
            "ear_total_mwmes",
            "val_volmax",
            "val_volumeutilcon",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
        ]

    cols_existentes = [col for col in cols_to_normalize if col in df.columns]

    # Converter para float ANTES de tratar nulos e normalizar
    for col in cols_existentes:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Tratar valores nulos (preencher com zero)
    if cols_existentes:
        df[cols_existentes] = df[cols_existentes].fillna(0)
        scaler = MinMaxScaler()
        df[cols_existentes] = scaler.fit_transform(df[cols_existentes])

    return df