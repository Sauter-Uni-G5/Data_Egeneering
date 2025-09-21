import pandas as pd
import matplotlib.pyplot as plt

# Carregar os dados
df_espera = pd.read_csv('RES_VOLUMEESPERA_2024.csv', sep=';', encoding='utf-8')
df_hidro = pd.read_csv('DADOS_HIDROLOGICOS_RES_2024 (1).csv', sep=';', encoding='utf-8')

# Converter a coluna de data para datetime
df_espera['din_instante'] = pd.to_datetime(df_espera['din_instante'])
df_hidro['din_instante'] = pd.to_datetime(df_hidro['din_instante'])

# Encontrar todos os reservatórios presentes no arquivo de volume esperado
reservatorios = df_espera['id_reservatorio'].unique()

for res_id in reservatorios:
    # Filtrar os dados para o reservatório atual
    espera = df_espera[df_espera['id_reservatorio'] == res_id]
    hidro = df_hidro[df_hidro['id_reservatorio'] == res_id]
    
    # Se não houver dados em ambos, pula
    if espera.empty or hidro.empty:
        continue
    
    # Merge para alinhar as datas (opcional, mas pode ajudar)
    df_plot = pd.merge(
        espera[['din_instante', 'val_volumeespera']],
        hidro[['din_instante', 'val_volumeutilcon']],
        on='din_instante',
        how='outer'
    ).sort_values('din_instante')
    
    # Plot
    plt.figure(figsize=(12,6))
    plt.plot(df_plot['din_instante'], df_plot['val_volumeespera'], label='Volume Espera')
    plt.plot(df_plot['din_instante'], df_plot['val_volumeutilcon'], label='Volume Utilizado')
    plt.title(f'Reservatório {res_id}')
    plt.xlabel('Data')
    plt.ylabel('Volume')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'reservatorio_{res_id}.png')