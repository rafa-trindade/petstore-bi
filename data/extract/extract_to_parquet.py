import pandas as pd
from config.db_config import engine

CSV_PATH = "data/lojas.parquet"


def extract_to_parquet():
    
    query = "SELECT * FROM lojas_gold;"
    df_lojas = pd.read_sql(query, engine)

    df_lojas.to_parquet(CSV_PATH, index=False)

    print(f"{len(df_lojas)} registros salvos em {CSV_PATH}")
    
    return df_lojas