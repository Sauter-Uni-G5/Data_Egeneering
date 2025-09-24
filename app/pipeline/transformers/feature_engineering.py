import pandas as pd
from typing import List, Union

def create_lags(df: pd.DataFrame, columns: Union[str, List[str]], lag: int = 1, groupby: Union[str, List[str], None] = None) -> pd.DataFrame:
    """
    Adiciona colunas de lag para as colunas especificadas.
    - df: DataFrame de entrada
    - columns: coluna(s) para aplicar o lag
    - lag: valor do lag (ex: 1 para lag de 1 período)
    - groupby: coluna(s) para agrupar antes de aplicar o lag (ex: id_reservatorio)
    Retorna o DataFrame com novas colunas: {col}_lag{lag}
    """
    df_copy = df.copy()
    if isinstance(columns, str):
        columns = [columns]
    if groupby is not None:
        for col in columns:
            df_copy[f"{col}_lag{lag}"] = df_copy.groupby(groupby)[col].shift(lag)
    else:
        for col in columns:
            df_copy[f"{col}_lag{lag}"] = df_copy[col].shift(lag)
    return df_copy

def create_diffs(df: pd.DataFrame, columns: Union[str, List[str]], periods: int = 1, groupby: Union[str, List[str], None] = None) -> pd.DataFrame:
    """
    Adiciona colunas de diferença (diff) para as colunas especificadas.
    - df: DataFrame de entrada
    - columns: coluna(s) para aplicar o diff
    - periods: número de casas atrás para calcular a diferença
    - groupby: coluna(s) para agrupar antes de aplicar o diff (ex: id_reservatorio)
    Retorna o DataFrame com novas colunas: {col}_diff{periods}
    """
    df_copy = df.copy()
    if isinstance(columns, str):
        columns = [columns]
    if groupby is not None:
        for col in columns:
            df_copy[f"{col}_diff{periods}"] = df_copy.groupby(groupby)[col].diff(periods)
    else:
        for col in columns:
            df_copy[f"{col}_diff{periods}"] = df_copy[col].diff(periods)
    return df_copy