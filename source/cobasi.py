import streamlit as st
import pandas as pd
from streamlit.components.v1 import html

from .utils import utils as util
from .utils import maps as maps
from .utils import graphs as graphs


@st.cache_data
def load_data():
    df = pd.read_parquet("data/lojas.parquet")
    df = df[df["empresa"].str.lower() == "cobasi"]
    df = df.dropna(subset=["latitude", "longitude", "populacao", "renda_domiciliar_per_capita"])
    return df

def cobasi_analysis():
    df_cobasi = load_data()
    
    df_ibge = pd.read_csv("data/utils/ibge_data.csv", sep=";", encoding="utf-8-sig") 

    tab1, tab2, tab3 = st.tabs(["🥈 Concorrência", "🗺️ Cobertura", "📄 Análises"])


    with tab1:

        # --- Carregando dados ---
        df_geral = pd.read_parquet("data/lojas.parquet")
        df_geral = df_geral.dropna(subset=["latitude", "longitude", "populacao", "renda_domiciliar_per_capita"])


        mostrar_empresa = False  # controle booleano

        if mostrar_empresa:
            col_empresa, col1, col2, col3, col4 = st.columns([1, 1, 1, 1, 1])

            empresas_disponiveis = sorted(df_geral["empresa"].str.title().dropna().unique().tolist())
            empresas_disponiveis = [e for e in empresas_disponiveis if e.lower() != "cobasi"]
            empresas_disp_selectbox = ["Todas"] + empresas_disponiveis

            with col_empresa:
                with col_empresa:
                    empresa_sel = st.selectbox(
                        "Empresa para Destaque:",
                        empresas_disp_selectbox,
                        key="empresa_select_tab1",
                        disabled=True
                    )
        else:
            with st.container(border=True):

                col1, col2, col3, col4 = st.columns([ 1, 1, 1, 1])
                empresa_sel = "Todas"

        regioes_disp = ["Todas"] + list(util.regioes.keys())
        with col1:
            regiao_sel = st.selectbox("Região:", regioes_disp, key="reg_select_tab1")

        if regiao_sel != "Todas":
            estados_da_regiao = util.regioes.get(regiao_sel, [])
            df_regiao = df_geral[df_geral["estado"].isin(estados_da_regiao)]
            estados_disp = ["Todos"] + sorted(df_regiao["estado"].dropna().unique().tolist())
        else:
            estados_disp = ["Todos"]

        with col2:
            estado_sel = st.selectbox("Estado:", estados_disp, disabled=(regiao_sel == "Todas"), key="est_select_tab1")

        df_filtrado_tab1 = df_geral.copy()

        if regiao_sel != "Todas":
            df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1["estado"].isin(util.regioes[regiao_sel])]
        if estado_sel != "Todos":
            df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1["estado"] == estado_sel]

        with col4:
            pop_ranges = ["Geral (todas as cidades)", "> 50.000 habitantes", "> 100.000 habitantes",
                        "> 250.000 habitantes", "> 500.000 habitantes", "> 1.000.000 habitantes"]
            pop_sel = st.selectbox("População:", pop_ranges, key="pop_select_tab1")

        if pop_sel != "Geral (todas as cidades)":
            pop_min = int(pop_sel.split(">")[1].replace(".", "").replace(" habitantes", "").strip())
            df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1.groupby("cidade")["populacao"].transform("first") > pop_min]

        cidades_disp = ["Todas"] + sorted(df_filtrado_tab1["cidade"].dropna().unique().tolist())
        with col3:
            cidade_sel = st.selectbox("Cidade:", cidades_disp,
                                    disabled=(estado_sel == "Todos" or regiao_sel == "Todas"),
                                    key="cid_select_tab1")

        if cidade_sel != "Todas":
            df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1["cidade"] == cidade_sel]

        df_cobasi = df_filtrado_tab1[df_filtrado_tab1["empresa"].str.lower() == "cobasi"]
        df_outras = df_filtrado_tab1[df_filtrado_tab1["empresa"].str.lower() != "cobasi"]

        total_lojas_cobasi = len(df_cobasi)
        total_lojas_outras = len(df_outras)
        total_lojas = total_lojas_cobasi + total_lojas_outras


        with st.container(border=True):

            col_m1, col_m2, col_m3, col_m4 = st.columns([5,1,1,2])

            with col_m1:

                participacao = df_filtrado_tab1["empresa"].str.lower().value_counts(normalize=True)  # proporção 0-1

                participacao_cobasi = participacao.get("cobasi", 0) * 100
                indice_competitividade = 100 - participacao_cobasi
                
                hhi = round((participacao ** 2).sum() * 10000, 2)

                if hhi < 1500:
                    nivel_hhi = "🟢 Mercado Competitivo"
                elif hhi < 2500:
                    nivel_hhi = "🟡 Concorrência Moderada"
                else:
                    nivel_hhi = "🔴 Alta Concentração"

                if cidade_sel != "Todas":
                    hhi_label = f"{cidade_sel}-{estado_sel}"
                elif estado_sel != "Todos":
                    hhi_label = f"{estado_sel}"
                elif regiao_sel != "Todas":
                    hhi_label = f"{regiao_sel}"
                else:
                    hhi_label = "Brasil"

                st.markdown(f"**HHI ({hhi_label}): {int(hhi):,}** — {nivel_hhi}")


        col_m5, col_m6, col_m7 = st.columns([6, 4.5, 2.5])

        # --- Gráfico ---
        with col_m5:
            with st.container(border=True):
                fig_graph_tab1 = graphs.grafico_concorrencia_mini(
                    df_filtrado_tab1,
                    empresa_sel,
                    df_filtrado_tab1["empresa"].str.title().unique().tolist(),
                    empresa = "cobasi"
                )
                st.plotly_chart(fig_graph_tab1, use_container_width=True)

        # --- Mapa ---
        with col_m6:
            with st.container(border=True):

                fig_tab1 = maps.mapa_geral_mini(
                    df_filtrado_tab1,
                    estado_sel,
                    cidade_sel,
                    empresa_sel,
                    df_filtrado_tab1["empresa"].str.title().unique().tolist(),
                    empresa = "cobasi"
                )
                if fig_tab1 is not None:
                    maps.geojson_maps(fig_tab1, regiao_sel, estado_sel)
                else:
                    st.warning("Não há dados para exibir no mapa.")

        # --- Métricas principais ---
        with col_m7:
            col_m7.success(f"Lojas Cobasi: {total_lojas_cobasi}", icon=":material/store:")
            col_m7.info(f"Outras Lojas: {total_lojas_outras}", icon=":material/store:")
            col_m7.error(f"Total de Lojas: {total_lojas}", icon=":material/store:")

            if not df_filtrado_tab1.empty:
                col_m7.success(f"Cobasi: {participacao_cobasi:.1f}% de participação no mercado")
                col_m7.info(f"Índice de Competitividade: {indice_competitividade:.1f}%")
            else:
                col_m7.success("Sem dados para os filtros selecionados.")



    with tab2:

        with st.container(border=True):

            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        regioes_disp = ["Todas"] + list(util.regioes.keys())
        with col1:
            regiao_sel = st.selectbox("Região:", regioes_disp)

        if regiao_sel != "Todas":
            estados_da_regiao = util.regioes.get(regiao_sel, [])
            df_regiao = df_cobasi[df_cobasi["estado"].isin(estados_da_regiao)]
            estados_disp = ["Todos"] + sorted(df_regiao["estado"].dropna().unique().tolist())
        else:
            estados_disp = ["Todos"]

        with col2:
            estado_sel = st.selectbox("Estado:", estados_disp, disabled=(regiao_sel == "Todas"))

        df_filtrado_tab2 = df_cobasi.copy()
        if regiao_sel != "Todas":
            df_filtrado_tab2 = df_filtrado_tab2[df_filtrado_tab2["estado"].isin(util.regioes[regiao_sel])]
        if estado_sel != "Todos":
            df_filtrado_tab2 = df_filtrado_tab2[df_filtrado_tab2["estado"] == estado_sel]

        with col4:
            pop_ranges = ["Geral (todas as cidades)", "> 50.000 habitantes", "> 100.000 habitantes",
                        "> 250.000 habitantes", "> 500.000 habitantes", "> 1.000.000 habitantes"]
            pop_sel = st.selectbox("População:", pop_ranges, key="pop_select")  # ainda aparece apenas como filtro de cidades

        df_temp_tab2 = df_filtrado_tab2.copy()
        if pop_sel != "Geral (todas as cidades)":
            pop_min = int(pop_sel.split(">")[1].replace(".", "").replace(" habitantes", "").replace(".", "").strip())
            df_temp_tab2 = df_temp_tab2[df_temp_tab2.groupby("cidade")["populacao"].transform("first") > pop_min]

        cidades_disp = ["Todas"] + sorted(df_temp_tab2["cidade"].dropna().unique().tolist())
        with col3:
            cidade_sel = st.selectbox("Cidade:", cidades_disp, disabled=(estado_sel == "Todos" or regiao_sel == "Todas"))

        if cidade_sel != "Todas":
            df_filtrado_tab2 = df_filtrado_tab2[df_filtrado_tab2["cidade"] == cidade_sel]

        if cidade_sel == "Todas" and pop_sel != "Geral (todas as cidades)":
            df_filtrado_tab2 = df_filtrado_tab2[df_filtrado_tab2.groupby("cidade")["populacao"].transform("first") > pop_min]

        df_ibge_filtrado_tab2 = df_ibge.copy()
        if regiao_sel != "Todas":
            df_ibge_filtrado_tab2 = df_ibge_filtrado_tab2[df_ibge_filtrado_tab2["estado"].isin(util.regioes[regiao_sel])]
        if estado_sel != "Todos":
            df_ibge_filtrado_tab2 = df_ibge_filtrado_tab2[df_ibge_filtrado_tab2["estado"] == estado_sel]
        if cidade_sel != "Todas":
            df_ibge_filtrado_tab2 = df_ibge_filtrado_tab2[df_ibge_filtrado_tab2["cidade"] == cidade_sel]

        if cidade_sel == "Todas" and pop_sel != "Geral (todas as cidades)":
            df_ibge_filtrado_tab2 = df_ibge_filtrado_tab2[df_ibge_filtrado_tab2["populacao"] > pop_min]

        # --- Métricas ---
        total_cidades = df_filtrado_tab2["cidade"].nunique()
        total_estados = 1 if estado_sel != "Todos" else df_filtrado_tab2["estado"].nunique()

        total_cidades_brasil = len(df_ibge_filtrado_tab2)
        total_estados_brasil = df_ibge_filtrado_tab2["estado"].nunique() if estado_sel == "Todos" else 1

        cobertura_cidades = (total_cidades / total_cidades_brasil) * 100 if total_cidades_brasil > 0 else 0
        cobertura_estados = (total_estados / total_estados_brasil) * 100 if total_estados_brasil > 0 else 0
        #st.write(total_cidades)
        #st.write(total_cidades_brasil)


        col4, col5 = st.columns([3,2])

        with col4:
        # --- Mapa ---
            with st.container(border=True):
                fig = maps.mapa_empresas(df_filtrado_tab2, estado_sel, cidade_sel)
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
            col5.success(f"{titulo_lojas} {len(df_filtrado_tab2)}", icon=":material/store:")

            #-------------------------------

            if estado_sel == "Todos":
                titulo_estado = f"Cob. Estados | {'Brasil: ' if regiao_sel == 'Todas' else regiao_sel}: "
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
                df_cidade = df_filtrado_tab2[df_filtrado_tab2["cidade"] == cidade_sel]
                if not df_cidade.empty:
                    pop_cidade = df_cidade["populacao"].dropna().iloc[0]
                else:
                    pop_cidade = 0
                col5.info(f"População: {int(pop_cidade):,} habitantes".replace(",", "."),  icon=":material/demography:")

            #-------------------------------




    with tab3:

        st.write("Em desenvolvimento...")