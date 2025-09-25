import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def normalize_and_clean(df: pd.DataFrame, date_col: str = "ear_data"):
    df = df.copy()

    # 1. Criar colunas de dia, mês e ano a partir da data
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df["dia"] = df[date_col].dt.day
        df["mes"] = df[date_col].dt.month
        df["ano"] = df[date_col].dt.year

    # 2. Remover colunas de nomes/texto
    cols_to_drop = ["nom_reservatorio", "tip_reservatorio", "nom_bacia", "ear_data"]
    for col in cols_to_drop:
        if col in df.columns:
            df = df.drop(columns=col)

    # 3. Selecionar apenas colunas numéricas (exceto id_reservatorio, dia, mes, ano)
    cols_to_keep = ["id_reservatorio", "dia", "mes", "ano"]
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cols_final = cols_to_keep + [col for col in numeric_cols if col not in cols_to_keep]
    df = df[cols_final]

    # 4. Normalizar colunas numéricas (exceto id_reservatorio, dia, mes, ano)
    cols_to_normalize = [col for col in df.columns if col not in cols_to_keep]
    if cols_to_normalize:
        scaler = MinMaxScaler()
        df[cols_to_normalize] = scaler.fit_transform(df[cols_to_normalize])

    # 5. Limpeza: remover linhas onde val_volumeutilcon é nulo
    if "val_volumeutilcon" in df.columns:
        df = df[df["val_volumeutilcon"].notnull()]

    df = df.reset_index(drop=True)
    return df