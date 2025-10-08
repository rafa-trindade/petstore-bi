#%%
import pandas as pd
from utils import eda

df_lojas = pd.read_parquet("../data/lojas.parquet")

eda(df_lojas)