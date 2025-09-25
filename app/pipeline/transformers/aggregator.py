import pandas as pd
import logging

logger = logging.getLogger(__name__)

def aggregate_ear_hydro_registry(
    df_ear: pd.DataFrame,
    df_hydro: pd.DataFrame,
    df_registry: pd.DataFrame
) -> pd.DataFrame:
    # Log inicial
    logger.info(f"Iniciando agregação com EAR: {len(df_ear)}, HYDRO: {len(df_hydro)}, REGISTRY: {len(df_registry)} registros")
    
    # 1. Primeiro JOIN: EAR com REGISTRY (por nom_reservatorio)
    df_merged = pd.merge(
        df_ear,
        df_registry,
        on='nom_reservatorio',
        how='left'
    )
    logger.info(f"Após primeiro JOIN (EAR + REGISTRY): {len(df_merged)} registros")
    
    # Verificar quais colunas estão disponíveis após o primeiro merge
    logger.info(f"Colunas após primeiro merge: {sorted(df_merged.columns.tolist())}")
    
    # CORREÇÃO: Ajustar nomes de colunas após o primeiro merge
    # Se nom_bacia_x existe, renomear para nom_bacia
    if 'nom_bacia_x' in df_merged.columns:
        df_merged['nom_bacia'] = df_merged['nom_bacia_x']
    elif 'nom_bacia_y' in df_merged.columns:
        df_merged['nom_bacia'] = df_merged['nom_bacia_y']
        
    # Se tip_reservatorio_x existe, renomear para tip_reservatorio
    if 'tip_reservatorio_x' in df_merged.columns:
        df_merged['tip_reservatorio'] = df_merged['tip_reservatorio_x']
    elif 'tip_reservatorio_y' in df_merged.columns:
        df_merged['tip_reservatorio'] = df_merged['tip_reservatorio_y']
    
    # 2. Segundo JOIN: resultado anterior com HYDRO
    # Garantir que as colunas de junção existam antes de prosseguir
    join_columns_left = ['id_reservatorio', 'nom_bacia', 'ear_data']
    join_columns_right = ['id_reservatorio', 'nom_bacia', 'din_instante']
    
    # Verificar se as colunas existem
    if all(col in df_merged.columns for col in join_columns_left) and all(col in df_hydro.columns for col in join_columns_right[:2]):
        # Converter datas para datetime para comparação adequada
        if 'ear_data' in df_merged.columns:
            df_merged['ear_data'] = pd.to_datetime(df_merged['ear_data'], errors='coerce')
        if 'din_instante' in df_hydro.columns:
            df_hydro['din_instante'] = pd.to_datetime(df_hydro['din_instante'], errors='coerce')
        
        # Executar o segundo JOIN
        df_final = pd.merge(
            df_merged,
            df_hydro,
            left_on=join_columns_left,
            right_on=join_columns_right,
            how='left'
        )
        logger.info(f"Após segundo JOIN (merged + HYDRO): {len(df_final)} registros")
    else:
        logger.warning("Colunas necessárias para o segundo JOIN não encontradas. Mantendo apenas o primeiro merge.")
        df_final = df_merged
    
    # 3. Selecionar as colunas finais (exatamente como no SQL)
    final_cols = [
        'nom_reservatorio',
        'tip_reservatorio',
        'nom_bacia',
        'ear_data',
        'ear_reservatorio_percentual',
        'ear_total_mwmes',
        'val_volmax',
        'id_reservatorio',
        'val_volumeutilcon'
    ]
    
    # Filtrar apenas as colunas que existem (evita KeyError)
    existing_cols = [col for col in final_cols if col in df_final.columns]
    logger.info(f"Colunas que existem no resultado final: {existing_cols}")
    logger.info(f"Colunas que faltam no resultado final: {set(final_cols) - set(existing_cols)}")
    
    # IMPORTANTE: Verificar se val_volumeutilcon está presente
    if 'val_volumeutilcon' not in df_final.columns:
        logger.warning("A coluna val_volumeutilcon não está presente! O feature engineering falhará.")
    
    result = df_final[existing_cols].copy()
    
    # Adicionar logs para depuração
    if 'ear_data' in result.columns:
        try:
            anos = result['ear_data'].dt.year.unique()
            logger.info(f"Anos presentes no resultado final: {sorted(anos)}")
            contagem_por_ano = result['ear_data'].dt.year.value_counts().sort_index()
            logger.info(f"Contagem por ano: {contagem_por_ano.to_dict()}")
        except:
            logger.warning("Não foi possível analisar anos nos resultados")
    
    return result.reset_index(drop=True)