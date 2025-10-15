import streamlit as st
import pandas as pd
from streamlit.components.v1 import html

from .utils import utils as util
from .utils import maps as maps
from .utils import graphs as graphs
from .utils import kpi as kpi

@st.cache_data
def load_data():
    df = pd.read_parquet("data/lojas.parquet")
    df = df[df["empresa"].str.lower() == "petlove"]
    df = df.dropna(subset=["latitude", "longitude", "populacao", "renda_domiciliar_per_capita"])
    return df


def petlove_analysis():
    df_petlove = load_data()
    df_ibge = pd.read_csv("data/utils/ibge_data.csv", sep=";", encoding="utf-8-sig") 
    df_capitais = pd.read_csv("data/utils/capitais.csv", sep=";", encoding="utf-8-sig") 

    df_geral = pd.read_parquet("data/lojas.parquet")
    df_geral = df_geral.dropna(subset=["latitude", "longitude", "populacao", "renda_domiciliar_per_capita"])

    ultima_atualizacao = df_geral.loc[0, 'ultima_atualizacao']

    col_1, col_2 = st.columns([3,1])
    with col_1:
        st.success("**Petlove** | Visão Geral", icon=":material/store:")
    with col_2:
        st.info(f"Úlima Atualização: {ultima_atualizacao}", icon=":material/info:")
        
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
    df_ibge_filtrado = df_ibge.copy()
    df_capitais_filtrado = df_capitais.copy()

    if regiao_sel != "Todas":
        df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1["estado"].isin(util.regioes[regiao_sel])]
        df_ibge_filtrado = df_ibge_filtrado[df_ibge_filtrado["estado"].isin(util.regioes[regiao_sel])]
        df_capitais_filtrado =  df_capitais[df_capitais["estado"].isin(util.regioes[regiao_sel])]
    if estado_sel != "Todos":
        df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1["estado"] == estado_sel]
        df_ibge_filtrado = df_ibge_filtrado[df_ibge_filtrado["estado"] == estado_sel]
        df_capitais_filtrado = df_capitais[df_capitais["estado"] == estado_sel]

    with col4:
        pop_ranges = ["Geral (todas as cidades)", "> 50.000 habitantes", "> 100.000 habitantes",
                    "> 250.000 habitantes", "> 500.000 habitantes", "> 1.000.000 habitantes"]
        pop_sel = st.selectbox("População:", pop_ranges, key="pop_select_tab1")

    df_filtrado_pop = df_filtrado_tab1.copy()

    if pop_sel != "Geral (todas as cidades)":
        pop_min = int(pop_sel.split(">")[1].replace(".", "").replace(" habitantes", "").strip())
        df_filtrado_pop = df_filtrado_tab1[df_filtrado_tab1.groupby("cidade")["populacao"].transform("first") > pop_min]

    cidades_disp = ["Todas"] + sorted(df_filtrado_tab1["cidade"].dropna().unique().tolist())
    with col3:
        cidade_sel = st.selectbox("Cidade:", cidades_disp,
                                disabled=(estado_sel == "Todos" or regiao_sel == "Todas"),
                                key="cid_select_tab1")

    if cidade_sel != "Todas":
        df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1["cidade"] == cidade_sel]
        df_ibge_filtrado = df_ibge_filtrado[df_ibge_filtrado["cidade"] == cidade_sel]
        df_filtrado_pop = df_filtrado_pop[df_filtrado_pop["cidade"] == cidade_sel]


    df_petlove_filtrado = df_filtrado_tab1[df_filtrado_tab1["empresa"].str.lower() == "petlove"]
    df_petlove_filtrado_pop = df_filtrado_pop[df_filtrado_pop["empresa"].str.lower() == "petlove"]
    df_outras = df_filtrado_tab1[df_filtrado_tab1["empresa"].str.lower() != "petlove"]
    df_outras_pop = df_filtrado_pop[df_filtrado_pop["empresa"].str.lower() != "petlove"]


    total_lojas_petlove = len(df_petlove_filtrado)
    total_lojas_outras = len(df_outras)

    total_lojas_petlove_pop = len(df_petlove_filtrado_pop)
    total_lojas_outras_pop = len(df_outras_pop)
    total_lojas_pop = total_lojas_petlove_pop + total_lojas_outras_pop


    col_m5, col_m6, col_m7 = st.columns([6, 4.5, 2.5])

    # --- Gráfico ---
    with col_m5:
        with st.container(border=True):
            fig_graph_tab1 = graphs.grafico_concorrencia_mini(
                df_filtrado_pop,
                empresa_sel,
                df_filtrado_pop["empresa"].str.title().unique().tolist(),
                empresa = "petlove"
            )
            st.plotly_chart(fig_graph_tab1, use_container_width=True)

    # --- Mapa ---
    with col_m6:
        with st.container(border=True):

            fig_tab1 = maps.mapa_geral_mini(
                df_filtrado_pop,
                estado_sel,
                cidade_sel,
                empresa_sel,
                df_filtrado_pop["empresa"].str.title().unique().tolist(),
                empresa = "petlove"
            )
            if fig_tab1 is not None:
                maps.geojson_maps(fig_tab1, regiao_sel, estado_sel)
            else:
                st.warning("Não há dados para exibir no mapa.")

  
    with col_m7:
        col_m7.success(f"Lojas Petlove: {total_lojas_petlove_pop}", icon=":material/store:")
        col_m7.info(f"Outras Empresas: {total_lojas_outras_pop}", icon=":material/store:")
        col_m7.error(f"Total de Lojas: {total_lojas_pop}", icon=":material/store:")

        participacao = df_filtrado_tab1["empresa"].str.lower().value_counts(normalize=True)
        participacao_petlove = participacao.get("petlove", 0) * 100
        
        if not df_filtrado_tab1.empty:
            col_m7.success(f"Petlove: {participacao_petlove:.1f}% de participação no mercado")
        else:
            col_m7.success("Sem dados para os filtros selecionados.")


    if df_filtrado_tab1.empty:
        st.warning("Sem dados para calcular indicadores de concorrência.")
    else:
        df_filtrado_tab1 = df_filtrado_tab1.copy()
        df_petlove_filtrado = df_petlove_filtrado.copy()
        df_ibge_filtrado = df_ibge_filtrado.copy()

        df_filtrado_tab1["cidade"] = df_filtrado_tab1["cidade"].str.title().str.strip()
        df_petlove_filtrado["cidade"] = df_petlove_filtrado["cidade"].str.title().str.strip()
        df_ibge_filtrado["cidade"] = df_ibge_filtrado["cidade"].str.title().str.strip()

        # =========================================================
        # === Indicadores avançados de concorrência
        # =========================================================

        # Presença em cidades > 250 mil hab
        df_okr1 = kpi.popopulacao_250K(df_petlove_filtrado, df_ibge_filtrado)
        
        # Capitais
        df_okr2 = kpi.capitais(df_petlove_filtrado, df_capitais_filtrado)

        # Exclusivida em cidades > 100 mil hab
        df_okr3 = kpi.cidades_exclusivas_e_sem_empresas("petlove", df_filtrado_tab1, df_ibge_filtrado)

        # Expansão por indice de saturacao
        df_okr4 = kpi.indice_saturacao_expansao("petlove", df_filtrado_tab1, df_ibge_filtrado)

        # HHI
        df_okr5 = kpi.hhi_regiao(df_petlove_filtrado, df_filtrado_tab1)

    

        # =========================================================
        # === Tabela de OKRs ===
        # =========================================================
        if regiao_sel == "Todas":
            filtro = "Brasil"
        else:
            filtro = f"{regiao_sel}"

            if estado_sel == "Todos":
                filtro = f"{regiao_sel}"
            else:
                filtro = f"{estado_sel}"

                if cidade_sel == "Todas":
                    filtro = f"{estado_sel}"
                else:
                    filtro = f"{cidade_sel}-{estado_sel}"
               

        if cidade_sel == "Todas":
            f"{df_okr1['indice']:.1f}%"
        else:
            "-"

        okr_data = [
            {
                "OKR": "OKR1",
                "Indicador": "Presença em Cidades > 250 mil Habitantes",
                "Filtro": f"{filtro}",
                "Atual": f"{df_okr1['indice']:.1f}%" if cidade_sel == "Todas" else "-",
                "Meta": f"100%" if cidade_sel == "Todas" else "-",
                "Observação": "% Cidades > 250 mil Habitantes com Petlove presente"
            },
            {
                "OKR": "OKR2",
                "Indicador": "Cobertura Capitais Regionais",
                "Filtro": f"{filtro}",
                "Atual": f"{df_okr2['indice']:.1f}%" if cidade_sel == "Todas" else "-",
                "Meta": f"100%" if cidade_sel == "Todas" else "-",
                "Observação": f"% Capitais regionais com Petlove presente"
            },
            {
                "OKR": "OKR3",
                "Indicador": "Cidades > 100 mil Habitantes exclusivas Petlove",
                "Filtro": f"{filtro}",
                "Atual": f"{df_okr3['indice']}" if cidade_sel == "Todas" else "-",
                "Meta": f"+10%" if cidade_sel == "Todas" else "-",
                "Observação": f"Qtd. Cidades >100 mil Habitantes com presença exclusiva da Petlove"
            },

            {
                "OKR": "OKR4",
                "Indicador": "Índice de Saturação da Região",
                "Filtro": f"{filtro}",
                "Atual": f"{df_okr4['indice']:.1f}" if cidade_sel == "Todas" else "-",
                "Meta": f"<1.5" if cidade_sel == "Todas" else "-",
                "Observação": f"{df_okr4['interpretacao']}"
            },
            {
                "OKR": "OKR5",
                "Indicador": "HHI Médio da Região",
                "Filtro": f"{filtro}",
                "Atual": f"{df_okr5['hhi_geral']:.0f}",
                "Meta": "<1800",
                "Observação": f"Posição Atual da Região: {df_okr5['interpretacao']}"
            },

        ]

        df_okr = pd.DataFrame(okr_data)

        # =========================================================
        # === Seção de OKRs e métricas ===
        # =========================================================
        st.success("OKRs Estratégicos", icon=":material/analytics:")

        col_okr_1, col_okr_2, col_okr_3 = st.columns(3)
        with col_okr_1:
            st.markdown("""
            - **Objetivo 1:** Fortalecer presença nas regiões de maior potencial  
                - KR1: Atingir presença em 100% das cidades com > 250 mil habitantes  
                - KR2: Atingir cobertura em todas as capitais regionais  
            """)

        with col_okr_2:
            st.markdown("""
            - **Objetivo 2:** Aumentar a participação nas cidades estratégicas  
                - KR3: Aumentar número de cidades exclusivas com > 100 mil habitantes  
            """)

        with col_okr_3:
            st.markdown("""
            - **Objetivo 3:** Expandir com foco em equilíbrio competitivo  
                - KR4: Expandir presença em cidades de alta população e baixa saturação (<1,5) 
                - KR5: Melhorar o equilíbrio competitivo na região, visando HHI médio abaixo de 1800  
            """)

        st.info("Observação: Alguns valores podem variar de acordo com filtros aplicados", icon=":material/info:")



        st.dataframe(df_okr, width="stretch", height="auto", hide_index=True)


        st.success("Análise de Expansão (GAP)", icon=":material/map:")

        col_values = df_okr1.get("cidades_ausentes")
        if col_values is not None and col_values not in [None, ""] and str(col_values).strip() != "":     
            with st.expander("GAP-OKR1"):
                st.markdown(f"""
                |GAP| {df_okr1["numero_cidades"]} Cidades - Região: {filtro}  | Indicador |
                |----------|----------------------------------------|--------------------------|
                | GAP-OKR1 | {df_okr1["cidades_ausentes"]} |Cidades >250 mil habitantes sem presença da Petlove |
                """, unsafe_allow_html=True)

        col_values = df_okr2.get("cidades_ausentes")
        if col_values is not None and col_values not in [None, ""] and str(col_values).strip() != "":     
            with st.expander("GAP-OKR2"):
                st.markdown(f"""
                |GAP| {df_okr2["numero_cidades"]} Cidades - Região: {filtro}|Indicador |
                |----------|----------------------------------------| --------------------------|
                | GAP-OKR2 | {df_okr2["cidades_ausentes"]} | Capitais Regionais sem presença da Petlove |
                """, unsafe_allow_html=True)

        col_values = df_okr3.get("cidades_ausentes")
        if col_values is not None and col_values not in [None, ""] and str(col_values).strip() != "":     
            with st.expander("GAP-OKR3"):
                st.markdown(f"""
                |GAP| {df_okr3["numero_cidades"]} Cidades - Região: {filtro}|Indicador |
                |----------|----------------------------------------| --------------------------|
                | GAP-OKR3 | {df_okr3["cidades_ausentes"]} | Cidades >100 mil habitantes sem registro de empresas ativas  |
                """, unsafe_allow_html=True)

        col_values = df_okr4.get("cidades_para_expansao")
        if col_values is not None and col_values not in [None, ""] and str(col_values).strip() != "":     
            with st.expander("GAP-OKR4"):
                st.markdown(f"""
                |GAP| {df_okr4["numero_cidades"]} Cidades - Região: {filtro}|Indicador |
                |----------|----------------------------------------| --------------------------|
                | GAP-OKR4 | {df_okr4["cidades_para_expansao"]} | Cidades >100 mil habitantes prioritárias para expansão - maior população e baixa saturação (<1.5) |
                """, unsafe_allow_html=True)

        with st.expander("GAP-OKR5"):
            st.markdown(f"""
            |GAP| {df_okr5["numero_cidades"]} Cidades - Região: {filtro}|Indicador |
            |----------|----------------------------------------| --------------------------|
            | GAP-OKR5 | {df_okr5["cidades_prioritarias"]} | Cidades com alta concentração de mercado e baixa ou nula penetração da Petlove |
            """, unsafe_allow_html=True)

        st.markdown("---")
