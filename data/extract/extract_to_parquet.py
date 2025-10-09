import pandas as pd
from config.db_config import engine
from datetime import datetime

PARQUET_PATH = "data/lojas.parquet"

def extract_to_parquet():

    query = "SELECT * FROM lojas_gold;"
    df_lojas = pd.read_sql(query, engine)

    if 'data_extracao' in df_lojas.columns:
        df_lojas['data_extracao'] = pd.to_datetime(df_lojas['data_extracao'], errors='coerce').dt.strftime('%d/%m/%Y')

    df_lojas['ultima_atualizacao'] = datetime.today().strftime('%d/%m/%Y')

    df_lojas.to_parquet(PARQUET_PATH, index=False)

    print(f"{len(df_lojas)} registros salvos em {PARQUET_PATH}")

