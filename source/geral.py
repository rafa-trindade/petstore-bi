import pandas as pd
import plotly.express as px
import streamlit as st

def geral_analysis():

    df = pd.read_parquet("data/lojas.parquet")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"])

    tab1, tab2 = st.tabs(["🗺️ Visão Geral", "-"])
    
    with tab1:
        col1, col2, col3, col4 = st.columns(4)

        empresas_disp = sorted(df["empresa"].dropna().str.title().unique().tolist())
        empresas_disp = ["Todas"] + empresas_disp
        with col1:
            empresa_sel = st.selectbox("Empresa:", empresas_disp, index=0)

        if empresa_sel == "Todas":
            estados_disp = sorted(df["estado"].dropna().unique().tolist())
        else:
            estados_disp = sorted(df[df["empresa"].str.capitalize() == empresa_sel]["estado"].dropna().unique().tolist())
        estados_disp = ["Todos"] + estados_disp

        with col2:
            estado_sel = st.selectbox("Estado:", estados_disp)

        df_temp = df.copy()
        if empresa_sel != "Todas":
            df_temp = df_temp[df_temp["empresa"].str.title() == empresa_sel]
        if estado_sel != "Todos":
            df_temp = df_temp[df_temp["estado"] == estado_sel]

        cidades_disp = sorted(df_temp["cidade"].dropna().unique().tolist())
        cidades_disp = ["Todas"] + cidades_disp

        with col3:
            cidade_sel = st.selectbox("Cidade:", cidades_disp)


        df_temp2 = df_temp.copy()
        if cidade_sel != "Todas":
            df_temp2 = df_temp2[df_temp2["cidade"] == cidade_sel]

        bairros_disp = sorted(df_temp2["bairro"].dropna().unique().tolist())
        bairros_disp = ["Todos"] + bairros_disp
        with col4:
            bairro_sel = st.selectbox("Bairro:", bairros_disp, index=0)


        df_filtrado = df.copy()
        if empresa_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado["empresa"].str.title() == empresa_sel]
        if estado_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["estado"] == estado_sel]
        if cidade_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado["cidade"] == cidade_sel]
        if bairro_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["bairro"] == bairro_sel]

        st.markdown(f"**{len(df_filtrado)} lojas encontradas**")


        if not df_filtrado.empty:
            if ((empresa_sel == "Todas" or empresa_sel in empresas_disp) and estado_sel == "Todos" 
                and cidade_sel == "Todas" and bairro_sel == "Todos"):
                lat_center, lon_center, zoom = -17.2350, -51.9253, 3.5
            else:
                lat_center = df_filtrado["latitude"].mean()
                lon_center = df_filtrado["longitude"].mean()
                zoom = 5.5
        else:
            lat_center, lon_center, zoom = -17.2350, -51.9253, 3.5


        if not df_filtrado.empty:
            fig = px.density_mapbox(
                df_filtrado,
                lat="latitude",
                lon="longitude",
                radius=20,
                center=dict(lat=lat_center, lon=lon_center),
                zoom=zoom,
                mapbox_style="carto-positron",
                color_continuous_scale="viridis",
                hover_data=["empresa", "nome", "logradouro", "bairro", "cidade", "estado"],
                height=600
            )

            for empresa in df_filtrado["empresa"].unique():
                df_emp = df_filtrado[df_filtrado["empresa"] == empresa]
                fig.add_scattermapbox(
                    lat=df_emp["latitude"],
                    lon=df_emp["longitude"],
                    mode="markers",
                    name=empresa,
                    marker=dict(size=8),
                    text=df_emp["nome"],
                    hoverinfo="text"
                )

            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), legend=dict(x=0, y=1))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nenhuma loja encontrada com os filtros selecionados.")