import pandas as pd
import plotly.express as px
import streamlit as st


def petz_analysis():

    df = pd.read_parquet("data/lojas.parquet")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"])

    tab1, tab2 = st.tabs(["🗺️ Visão Geral", "-"])
    
    with tab1:
        st.write("Em desenvolvimento...")
