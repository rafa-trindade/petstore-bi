import pandas as pd
from data.extract.extract_to_parquet import extract_to_parquet
from data.transform.transform import atualizar_lat_long

PARQUET_PATH = "data/lojas.parquet"

def main():

    extract_to_parquet()

    df = pd.read_parquet("data/lojas.parquet")
    df = atualizar_lat_long(df)
    df.to_parquet(PARQUET_PATH, index=False)

if __name__ == "__main__":
    main()