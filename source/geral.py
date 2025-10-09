import streamlit as st
import pandas as pd

from .utils import utils as util
from .utils import maps as maps


@st.cache_data
def load_data():
    df = pd.read_parquet("data/lojas.parquet")
    df = df.dropna(subset=["latitude", "longitude"])
    return df


def geral_analysis():
    df_geral = load_data()
    
    df_ibge = pd.read_csv("data/utils/ibge_data.csv", sep=";", encoding="utf-8-sig")  # colunas: cidade, estado, populacao

    tab1, tab2, tab3 = st.tabs(["🗺️ Cobertura", "Concorrência", "Expansão"])

    with tab1:
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        regioes_disp = ["Todas"] + list(util.regioes.keys())
        with col1:
            regiao_sel = st.selectbox("Região:", regioes_disp)

        if regiao_sel != "Todas":
            estados_da_regiao = util.regioes.get(regiao_sel, [])
            df_regiao = df_geral[df_geral["estado"].isin(estados_da_regiao)]
            estados_disp = ["Todos"] + sorted(df_regiao["estado"].dropna().unique().tolist())
        else:
            estados_disp = ["Todos"]

        with col2:
            estado_sel = st.selectbox("Estado:", estados_disp, disabled=(regiao_sel == "Todas"))

        df_filtrado = df_geral.copy()
        if regiao_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado["estado"].isin(util.regioes[regiao_sel])]
        if estado_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["estado"] == estado_sel]

        with col4:
            pop_ranges = ["Geral (todas as cidades)", "> 50.000 habitantes", "> 100.000 habitantes", "> 250.000 habitantes", "> 500.000 habitantes"]
            pop_sel = st.selectbox("População:", pop_ranges, key="pop_select")  # ainda aparece apenas como filtro de cidades

        df_temp = df_filtrado.copy()
        if pop_sel != "Geral (todas as cidades)":
            pop_min = int(pop_sel.split(">")[1].replace(".", "").replace(" habitantes", "").replace(".", "").strip())
            df_temp = df_temp[df_temp.groupby("cidade")["populacao"].transform("first") > pop_min]

        cidades_disp = ["Todas"] + sorted(df_temp["cidade"].dropna().unique().tolist())
        with col3:
            cidade_sel = st.selectbox("Cidade:", cidades_disp, disabled=(estado_sel == "Todos" or regiao_sel == "Todas"))

        if cidade_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado["cidade"] == cidade_sel]

        if cidade_sel == "Todas" and pop_sel != "Geral (todas as cidades)":
            df_filtrado = df_filtrado[df_filtrado.groupby("cidade")["populacao"].transform("first") > pop_min]

        df_ibge_filtrado = df_ibge.copy()
        if regiao_sel != "Todas":
            df_ibge_filtrado = df_ibge_filtrado[df_ibge_filtrado["estado"].isin(util.regioes[regiao_sel])]
        if estado_sel != "Todos":
            df_ibge_filtrado = df_ibge_filtrado[df_ibge_filtrado["estado"] == estado_sel]
        if cidade_sel != "Todas":
            df_ibge_filtrado = df_ibge_filtrado[df_ibge_filtrado["cidade"] == cidade_sel]

        if cidade_sel == "Todas" and pop_sel != "Geral (todas as cidades)":
            df_ibge_filtrado = df_ibge_filtrado[df_ibge_filtrado["populacao"] > pop_min]

        # --- Métricas ---
        total_cidades = df_filtrado["cidade"].nunique()
        total_estados = 1 if estado_sel != "Todos" else df_filtrado["estado"].nunique()

        total_cidades_brasil = len(df_ibge_filtrado)
        total_estados_brasil = df_ibge_filtrado["estado"].nunique() if estado_sel == "Todos" else 1

        cobertura_cidades = (total_cidades / total_cidades_brasil) * 100 if total_cidades_brasil > 0 else 0
        cobertura_estados = (total_estados / total_estados_brasil) * 100 if total_estados_brasil > 0 else 0
        #st.write(total_cidades)
        #st.write(total_cidades_brasil)


        col4, col5, col6, col7 = st.columns(4)

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

        with col5:
            if estado_sel == "Todos":
                titulo_estado = f"Cobertura de Estados | {'Brasil' if regiao_sel == 'Todas' else regiao_sel} (%)"
                st.metric(titulo_estado, f"{cobertura_estados:.2f}%")
            else:
                st.metric("Estado:", estado_sel)

        with col6:
            if cidade_sel == "Todas":
                label_base = "Brasil" if regiao_sel == "Todas" else (regiao_sel if estado_sel == "Todos" else estado_sel)
                if pop_sel == "Geral (todas as cidades)":
                    titulo_cidade = f"Cobertura de Cidades | {label_base} (%)"
                else:
                    titulo_cidade = f'Cobertura de Cidades {pop_sel} | {label_base} (%)'
                valor_cidade = f"{cobertura_cidades:.2f}%"
            else:
                titulo_cidade = "Cidade:"
                valor_cidade = cidade_sel
            st.metric(label=titulo_cidade, value=valor_cidade)

        with col7:
            if cidade_sel != "Todas":
                df_cidade = df_filtrado[df_filtrado["cidade"] == cidade_sel]
                if not df_cidade.empty:
                    pop_cidade = df_cidade["populacao"].dropna().iloc[0]
                else:
                    pop_cidade = 0
                st.metric(label=f"População | {cidade_sel}", value=f"{int(pop_cidade):,}".replace(",", "."))



        # --- Mapa ---
        with st.container():
            fig = maps.mapa_geral(df_filtrado, estado_sel, cidade_sel)
            if fig is not None:
                maps.geojson_maps(fig, regiao_sel, estado_sel)
            else:
                st.warning("Não há dados para exibir no mapa.")
