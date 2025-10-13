import streamlit as st
import pandas as pd

from .utils import utils as util
from .utils import maps as maps


@st.cache_data
def load_data():
    df = pd.read_parquet("data/lojas.parquet")
    df = df.dropna(subset=["latitude", "longitude", "populacao", "renda_domiciliar_per_capita"])
    return df


def geral_analysis():
    df_geral = load_data()
    
    df_ibge = pd.read_csv("data/utils/ibge_data.csv", sep=";", encoding="utf-8-sig")  

    ultima_atualizacao = df_geral.loc[0, 'ultima_atualizacao']

    col_1, col_2 = st.columns([3,1])
    with col_1:
        st.success("**Visão Geral** | Todas as Empresas ", icon=":material/store:")
    with col_2:
        st.info(f"Úlima Atualização: {ultima_atualizacao}", icon=":material/info:")
        

    with st.container(border=True):
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
        pop_ranges = ["Geral (todas as cidades)", "> 50.000 habitantes", "> 100.000 habitantes",
                    "> 250.000 habitantes", "> 500.000 habitantes", "> 1.000.000 habitantes"]
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
    #   st.write(total_cidades)
    #st.write(total_cidades_brasil)


    col4, col5 = st.columns([3,1])

    with col4:
    # --- Mapa ---
        with st.container(border=True):
            fig = maps.mapa_geral(df_filtrado, estado_sel, cidade_sel)
            if fig is not None:
                maps.geojson_maps(fig, regiao_sel, estado_sel)
            else:
                st.warning("Não há dados para exibir no mapa.")

    with col5:
        #-------------------------------
        if cidade_sel != "Todas":
            titulo_lojas = f"Total Lojas | {cidade_sel}: "
        elif estado_sel != "Todos":
            titulo_lojas = f"Total Lojas | {estado_sel}: "
        elif regiao_sel != "Todas":
            titulo_lojas = f"Total Lojas | {regiao_sel}: "
        else:
            titulo_lojas = "Total Lojas | Brasil: "
        col5.success(f"{titulo_lojas} {len(df_filtrado)}", icon=":material/store:")

        #-------------------------------

        if estado_sel == "Todos":
            titulo_estado = f"Cobertura dos Estados | {'Brasil: ' if regiao_sel == 'Todas' else regiao_sel}: "
            col5.info(f"{titulo_estado} {cobertura_estados:.2f}%", icon=":material/map:")  
        else:
            col5.info(f"Estado: {estado_sel}", icon=":material/map:")

        #-------------------------------

        if cidade_sel == "Todas":
            label_base = "Brasil" if regiao_sel == "Todas" else (regiao_sel if estado_sel == "Todos" else estado_sel)
            if pop_sel == "Geral (todas as cidades)":
                titulo_cidade = f"Cob. Cidades | {label_base}"
            else:
                titulo_cidade = f'Cob. Cidades {pop_sel} | {label_base}'
            valor_cidade = f"{cobertura_cidades:.2f}%"
        else:
            titulo_cidade = "Cidade:"
            valor_cidade = cidade_sel
        col5.error(f"{titulo_cidade} {valor_cidade}", icon=":material/location_city:")  

        #-------------------------------

        if cidade_sel != "Todas":
            df_cidade = df_filtrado[df_filtrado["cidade"] == cidade_sel]
            if not df_cidade.empty:
                pop_cidade = df_cidade["populacao"].dropna().iloc[0]
            else:
                pop_cidade = 0
            col5.success(f"População: {int(pop_cidade):,} habitantes".replace(",", "."),  icon=":material/demography:")

        #-------------------------------