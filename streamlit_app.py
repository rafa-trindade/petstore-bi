import streamlit as st
import pandas as pd
import source.utils.utils as util

from source.cobasi import cobasi_analysis
from source.petcamp import petcamp_analysis
from source.petland import petland_analysis
from source.petlove import petlove_analysis
from source.petz import petz_analysis
from source.poppet import pop_pet_analysis



from source.geral import geral_analysis

st.set_page_config(
    layout="wide",
    page_title="petstore-bi | Rafael Trindade ", 
    initial_sidebar_state="expanded", 
    page_icon="🗺️")


st.sidebar.markdown(
    """
    <style>
    /* Logo customizado */
    .custom-sidebar-logo {
        position: relative;   /* permite mover com top */
        top: -30px;           /* desloca para cima */
        display: flex;
        justify-content: center;
        margin-bottom: -23px;  /* espaço para itens abaixo */
        z-index: 10;          /* sobreposição */
    }
    .custom-sidebar-logo img {
        max-width: 220px; 
        height: auto;
        border-radius: 7px;
    }
    </style>
    <div class="custom-sidebar-logo">
        <a href="https://github.com/rafa-trindade/petstore-pipeline" target="_blank">
            <img src="https://img.shields.io/badge/petstore--pipeline-123F5A?style=for-the-badge&logo=github&logoColor=fff&logoWidth=40&scale=1" />
        </a>
    </div>
    """,
    unsafe_allow_html=True
)


df_lojas = pd.read_parquet("data/lojas.parquet")

empresas_unicas = df_lojas['empresa'].str.title().sort_values().unique().tolist()
opcoes = ["Todas"] + empresas_unicas
    
empresa = st.sidebar.selectbox("Selecione Empresa para Análise:", opcoes)

empresa_source = {
    "Todas": geral_analysis,
    "Cobasi": cobasi_analysis,
    "Petcamp": petcamp_analysis,
    "Petland": petland_analysis,
    "Petlove": petlove_analysis,
    "Petz": petz_analysis,
    "Pop Pet Center": pop_pet_analysis
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


