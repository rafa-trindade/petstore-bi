#%%
import pandas as pd
from utils import eda

df_lojas = pd.read_parquet("../data/lojas.parquet")

df_lojas = df_lojas.dropna(subset=["latitude", "longitude"])

eda(df_lojas)

#%%
df_lojas.to_parquet("../data/lojas_final.parquet", index=False)