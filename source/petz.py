import pandas as pd
import plotly.express as px
import streamlit as st
from . import utils as util
import numpy as np

@st.cache_data
def load_data():
    df = pd.read_parquet("data/lojas.parquet")
    df = df[df["empresa"].str.lower() == "petz"]
    df = df.dropna(subset=["latitude", "longitude"])
    return df


def petz_analysis():

    df_petz = load_data()

    tab1, tab2, tab3 = st.tabs(["🗺️ Cobertura", "Concorrência", "Expansão"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)

        regioes_disp = ["Todas"] + list(util.regioes.keys())
        with col1:
            regiao_sel = st.selectbox("Região:", regioes_disp)

        if regiao_sel != "Todas":
            if regiao_sel:
                estados_da_regiao = util.regioes[regiao_sel]
                df_regiao = df_petz[df_petz["estado"].isin(estados_da_regiao)]
                estados_disp = ["Todos"] + sorted(df_regiao["estado"].dropna().unique().tolist())
            else:
                estados_disp = ["Todos"]
        else:
            estados_disp = ["Todos"] 

        with col2:
            estado_sel = st.selectbox("Estado:", estados_disp, disabled=(regiao_sel == "Todas"))


        df_temp = df_petz.copy()
        if regiao_sel != "Todas" and estado_sel != "Todos":
            df_temp = df_temp[df_temp["estado"] == estado_sel]
            cidades_disp = ["Todas"] + sorted(df_temp["cidade"].dropna().unique().tolist())
        else:
            cidades_disp = ["Todas"]

        with col3:
            cidade_sel = st.selectbox("Cidade:", cidades_disp, disabled=(estado_sel == "Todos" or regiao_sel == "Todas"))


        df_filtrado = df_petz.copy()
        if regiao_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado["estado"].isin(util.regioes[regiao_sel])]
        if estado_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["estado"] == estado_sel]
        if cidade_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado["cidade"] == cidade_sel]

        total_cidades = df_filtrado["cidade"].nunique()
        total_estados = 1 if estado_sel != "Todos" else df_filtrado["estado"].nunique()

        df_cidades_ibge = util.municipios_ibge()
        df_ibge_filtrado = df_cidades_ibge.copy()

        if regiao_sel != "Todas":
            df_ibge_filtrado = df_ibge_filtrado[df_ibge_filtrado["UF_sigla"].isin(util.regioes[regiao_sel])]

        if estado_sel != "Todos":
            df_ibge_filtrado = df_ibge_filtrado[df_ibge_filtrado["UF_sigla"] == estado_sel]

        if cidade_sel != "Todas":
            df_ibge_filtrado = df_ibge_filtrado[df_ibge_filtrado["nome"] == cidade_sel]

        total_cidades_brasil = len(df_ibge_filtrado)
        total_estados_brasil = df_ibge_filtrado["UF_sigla"].nunique() if estado_sel == "Todos" else 1

        cobertura_cidades = (total_cidades / total_cidades_brasil) * 100 if total_cidades_brasil > 0 else 0
        cobertura_estados = (total_estados / total_estados_brasil) * 100 if total_estados_brasil > 0 else 0

     
        col4, col5, col6, col7 = st.columns(4)

        # Métrica: Quantidade de lojas
        with col4:
            if cidade_sel != "Todas":
                titulo_lojas = "Lojas |\n" + cidade_sel
            elif estado_sel != "Todos":
                titulo_lojas = "Lojas |\n" + estado_sel
            elif regiao_sel != "Todas":
                titulo_lojas = "Lojas |\n" + regiao_sel
            else:
                titulo_lojas = "Lojas | Brasil"
            st.metric(label=titulo_lojas, value=f"{len(df_filtrado)}")

        # Métrica: Cobertura de estados
        with col6:
            if estado_sel == "Todos":
                if regiao_sel == "Todas":
                    titulo_estado = "Cobertura de Estados | Brasil (%)"
                else:
                    titulo_estado = f"Cobertura de Estados | {regiao_sel} (%)"
                st.metric(titulo_estado, f"{cobertura_estados:.2f}%")
            else:
                st.metric("Estado:", estado_sel)

        # Métrica: Cobertura de cidades
        with col7:
            if cidade_sel == "Todas":
                if regiao_sel == "Todas":
                    titulo_cidade = "Cobertura de Cidades | Brasil (%)"
                elif estado_sel == "Todos":
                    titulo_cidade = f"Cobertura de Cidades | {regiao_sel} (%)"
                else:
                    titulo_cidade = f"Cobertura de Cidades | {estado_sel} (%)"
                valor_cidade = f"{cobertura_cidades:.2f}%"
            else:
                titulo_cidade = "Cidade:"
                valor_cidade = cidade_sel
            st.metric(label=titulo_cidade, value=valor_cidade)




        with st.container(border=True):

            lat_center, lon_center, zoom = util.calcula_centro_mapa(df_filtrado, estado_sel, cidade_sel)

            fig = px.density_mapbox(
                df_filtrado,
                lat="latitude",
                lon="longitude",
                radius=15,
                center=dict(lat=lat_center, lon=lon_center),
                zoom=zoom,
                mapbox_style="carto-positron",
                hover_data=["nome", "cidade", "estado"],
                height=600

            )
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))

            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.write("Em desenvolvimento...")

    with tab3:
        st.write("Em desenvolvimento...")