import pandas as pd
import plotly.express as px
import streamlit as st
from . import utils as util

@st.cache_data
def load_data():
    df = pd.read_parquet("data/lojas.parquet")
    df = df[df["empresa"].str.lower() == "petland"]
    df = df.dropna(subset=["latitude", "longitude"])
    return df

def petland_analysis():

    df_petland = load_data()

    tab1, tab2, tab3 = st.tabs(["🗺️ Cobertura", "Concorrência", "Expansão"])
    
    with tab1:
        st.write("Em desenvolvimento...")

    with tab2:
        st.write("Em desenvolvimento...")

    with tab3:
        st.write("Em desenvolvimento...")