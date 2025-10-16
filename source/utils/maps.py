import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import json

from . import utils as util

def mapa_geral(df, est, cid):
    lat_center, lon_center, zoom = calcula_centro_mapa(df, est, cid)

    # --- Mapa de densidade ---
    fig = px.density_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        radius=10,
        center=dict(lat=lat_center, lon=lon_center),
        zoom=zoom,
        mapbox_style="carto-positron",
        color_continuous_scale="Darkmint_r",
        hover_data=["empresa", "nome", "logradouro", "bairro", "cidade", "estado"],
        height=400
    )

    fig.update_layout(coloraxis_showscale=False)

    cores = px.colors.sequential.Darkmint_r 
    empresas = df["empresa"].unique()
    num_cores = len(cores)

    for i, empresa in enumerate(empresas):
        df_emp = df[df["empresa"] == empresa]
        cor = cores[i % num_cores]  
        fig.add_scattermapbox(
            lat=df_emp["latitude"],
            lon=df_emp["longitude"],
            mode="markers",
            name=empresa.title(),
            marker=dict(size=5, color=cor),
            text=df_emp["nome"].str.title() + " - " + df_emp["cidade"] + "-" + df_emp["estado"],
            hoverinfo="text"
        )

    return fig

def mapa_geral_mini(df, estado_sel, cidade_sel, empresa_sel, empresas_disponiveis, empresa):
    lat_center, lon_center, zoom = calcula_centro_mapa_mini(df, estado_sel, cidade_sel)

    df["empresa_clean"] = df["empresa"].str.strip().str.title()
    empresa = empresa.title()
    empresa_sel = empresa_sel.title()

    if empresa_sel != "Todas":
        df = df[df["empresa_clean"].str.lower().isin([empresa.lower(), empresa_sel.lower()])]

    paleta = px.colors.sequential.Darkmint_r
    cores = {empresa: paleta[0]}

    if empresa_sel != "Todas":
        cores[empresa_sel] = paleta[2]
        empresas_restantes = [
            e for e in empresas_disponiveis
            if e.lower() not in [empresa.lower(), empresa_sel.lower()]
        ]
    else:
        empresas_restantes = [
            e for e in empresas_disponiveis
            if e.lower() != empresa.lower()
        ]

    for i, e in enumerate(empresas_restantes):
        cor_index = i + 2
        if cor_index >= len(paleta):
            cor_index = cor_index % len(paleta)
        cores[e.title()] = paleta[cor_index]

    df["color"] = df["empresa_clean"].map(cores)

    df_empresa = df[df["empresa_clean"] == empresa]
    df_outros = df[df["empresa_clean"] != empresa]

    fig = go.Figure()

    if not df_outros.empty:
        fig.add_scattermapbox(
            lat=df_outros["latitude"],
            lon=df_outros["longitude"],
            mode="markers",
            marker=dict(
                size=10,
                color=df_outros["color"],
                opacity=0.9,
                showscale=False
            ),
            text=df_outros["empresa_clean"] + " - " + df_outros["cidade"] + "-" + df_outros["estado"],
            hoverinfo="text",
            name="Outras"
        )

    if not df_empresa.empty:
        fig.add_scattermapbox(
            lat=df_empresa["latitude"],
            lon=df_empresa["longitude"],
            mode="markers",
            marker=dict(size=10, color="white", opacity=0.9),
            hoverinfo="none",
            name=""
        )

        fig.add_scattermapbox(
            lat=df_empresa["latitude"],
            lon=df_empresa["longitude"],
            mode="markers",
            marker=dict(size=10, color=df_empresa["color"], opacity=1),
            text=df_empresa["empresa_clean"] + " - " + df_empresa["cidade"] + "-" + df_empresa["estado"],
            hoverinfo="text",
            name=empresa
        )

    # Layout
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=lat_center, lon=lon_center),
            zoom=zoom,
        ),
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        height=400
    )

    return fig


def geojson_maps(fig, reg, est):

    with open("source/utils/br_states.geojson", "r") as f:
        geojson = json.load(f)

    locations = [f["properties"]["sigla"] for f in geojson["features"]]

    z = [0]*len(locations)
    line_widths = [0.4]*len(locations)
    line_colors = ["#3A7C89"]*len(locations)

    if reg != "Todas" and est == "Todos":
        estados_da_regiao = util.regioes[reg] 
        z = [1.8 if sigla in estados_da_regiao else 0 for sigla in locations]
        line_widths = [1.8 if sigla in estados_da_regiao else 0.4 for sigla in locations]
        line_colors = ["#3A7C89" if sigla in estados_da_regiao else "#3A7C89" for sigla in locations]

    elif est != "Todos":
        z = [1.8 if sigla == est else 0 for sigla in locations]
        line_widths = [1.8 if sigla == est else 0.4 for sigla in locations]
        line_colors = ["#3A7C89" if sigla == est else "#3A7C89" for sigla in locations]

    fig.add_trace(go.Choroplethmapbox(
        geojson=geojson,
        locations=locations,
        z=z,
        colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],      
        showscale=False,
        marker_line_width=line_widths,
        marker_line_color=line_colors,
        featureidkey="properties.sigla",
        hoverinfo="skip",
        autocolorscale=False
    ))

    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), legend=dict(x=0, y=1))
    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})


def calcula_centro_mapa(df_filtrado, estado_sel, cidade_sel):

    default_lat, default_lon, default_zoom = -15.2350, -53.9253, 2.8  

    if not df_filtrado.empty:
        if estado_sel == "Todos" and cidade_sel == "Todas":
            return default_lat, default_lon, default_zoom
        else:
            lat_center = df_filtrado["latitude"].mean()
            lon_center = df_filtrado["longitude"].mean()
            zoom = 5.5
            return lat_center, lon_center, zoom
    else:
        return default_lat, default_lon, default_zoom
    

def calcula_centro_mapa_mini(df_filtrado, estado_sel, cidade_sel):

    # Centro padrão do Brasil
    default_lat, default_lon, default_zoom = -15.2350, -53.9253, 2.6 

    if not df_filtrado.empty:
        if estado_sel == "Todos" and cidade_sel == "Todas":
            return default_lat, default_lon, default_zoom
        else:
            lat_center = df_filtrado["latitude"].mean()
            lon_center = df_filtrado["longitude"].mean()
            zoom = 3
            return lat_center, lon_center, zoom
    else:
        return default_lat, default_lon, default_zoom