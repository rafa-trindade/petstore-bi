import streamlit as st
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


empresa_source = {
    "Geral": geral_analysis,
    "Cobasi": cobasi_analysis,
    "Petlove": petlove_analysis,
    "Petz": petz_analysis
}

empresa = st.sidebar.selectbox(
    "Selecione Empresa para Análise:",
    list(empresa_source.keys())
)

empresa_source[empresa]()

col1_side, col2_side = st.sidebar.columns([2,1])
col1_side.markdown('<h5 style="margin-bottom: -25px;">Quantidade Lojas:', unsafe_allow_html=True)
col2_side.markdown('<h5 style="text-align: end; margin-bottom: -25px;"> 533</h5>', unsafe_allow_html=True)
col1_side.markdown('<h5 style="margin-bottom: -25px;">Última Extração:', unsafe_allow_html=True)
col2_side.markdown('<h5 style="text-align: end; margin-bottom: -25px;"> 05/10/25</h5>', unsafe_allow_html=True)

st.sidebar.markdown("---")

util.aplicar_estilo()


