import streamlit as st
import pandas as pd
import source.utils as util

from source.cobasi import cobasi_analysis
from source.petlove import petlove_analysis
from source.petz import petz_analysis
from source.geral import geral_analysis

st.set_page_config(
    layout="wide",
    page_title="petStore BI | Rafael ", 
    initial_sidebar_state="expanded", 
    page_icon="📊")

sidebar_logo = "https://i.postimg.cc/fWBrwgQt/logo-pettore.png"
main_body_logo = "https://i.postimg.cc/3xkGPmC6/streamlit02.png"
st.logo(sidebar_logo, icon_image=main_body_logo)

df_lojas = pd.read_parquet("data/lojas.parquet")

empresas_unicas = df_lojas['empresa'].str.capitalize().sort_values().unique().tolist()
opcoes = ["Geral"] + empresas_unicas

empresa = st.sidebar.selectbox("Selecione Empresa para Análise:", opcoes)

empresa_source = {
    "Geral": geral_analysis,
    "Cobasi": cobasi_analysis,
    "Petlove": petlove_analysis,
    "Petz": petz_analysis
}

func = empresa_source.get(empresa, geral_analysis)
func()

registros = str(len(df_lojas))
ultima_atualizacao = df_lojas.loc[0, 'ultima_atualizacao']

col1_side, col2_side = st.sidebar.columns([2,1])
col1_side.markdown('<h5 style="margin-bottom: -25px;">Registros:', unsafe_allow_html=True)
col2_side.markdown('<h5 style="text-align: end; margin-bottom: -25px;">' + registros + '</h5>', unsafe_allow_html=True)
col1_side.markdown('<h5 style="margin-bottom: -25px;">Última Extração:', unsafe_allow_html=True)
col2_side.markdown('<h5 style="text-align: end; margin-bottom: -25px;">' + ultima_atualizacao + '</h5>', unsafe_allow_html=True)

st.sidebar.markdown("---")

util.aplicar_estilo()


