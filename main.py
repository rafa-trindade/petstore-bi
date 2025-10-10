import pandas as pd
from data.extract.extract_to_parquet import extract_to_parquet
from data.transform.transform import atualizar_lat_long, preenche_campos

PARQUET_PATH = "data/lojas.parquet"

def main():

    extract_to_parquet()

    df = pd.read_parquet("data/lojas.parquet")
    df = atualizar_lat_long(df)

    IBGE_CSV = "data/utils/ibge_data_final.csv"
    df = preenche_campos(df, IBGE_CSV)

    df.to_parquet(PARQUET_PATH, index=False)

if __name__ == "__main__":
    main()