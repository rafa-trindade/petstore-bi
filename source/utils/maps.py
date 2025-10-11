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
        radius=15,
        center=dict(lat=lat_center, lon=lon_center),
        zoom=zoom,
        mapbox_style="carto-positron",
        color_continuous_scale="Darkmint_r",
        hover_data=["empresa", "nome", "logradouro", "bairro", "cidade", "estado"],
        height=600
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
            marker=dict(size=8, color=cor),
            text=df_emp["nome"].str.title() + " - " + df_emp["cidade"] + "-" + df_emp["estado"],
            hoverinfo="text"
        )

    return fig

def mapa_geral_mini(df, estado_sel, cidade_sel, empresa_sel, empresas_disponiveis, empresa):
    # Calcula o centro do mapa
    lat_center, lon_center, zoom = calcula_centro_mapa_mini(df, estado_sel, cidade_sel)

    # Normaliza os nomes das empresas
    df["empresa_clean"] = df["empresa"].str.strip().str.title()
    empresa = empresa.title()
    empresa_sel = empresa_sel.title()

    # 🔍 --- FILTRO DE EMPRESAS ---
    if empresa_sel != "Todas":
        # mostra apenas a empresa base e a selecionada
        df = df[df["empresa_clean"].str.lower().isin([empresa.lower(), empresa_sel.lower()])]

    # Paleta e cores
    paleta = px.colors.sequential.Darkmint_r
    cores = {}
    cores[empresa] = paleta[0]

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

    # Aplica as cores ao DF filtrado
    df["color"] = df["empresa_clean"].map(cores)

    # Cria o mapa
    fig = go.Figure()

    fig.add_scattermapbox(
        lat=df["latitude"],
        lon=df["longitude"],
        mode="markers",
        marker=dict(
            size=10,
            color=df["color"],
            showscale=False
        ),
        text=df["empresa_clean"] + " - " + df["cidade"] + "-" + df["estado"],
        hoverinfo="text",
        name=""
    )

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




def mapa_empresas(df, est, cid):
    lat_center, lon_center, zoom = calcula_centro_mapa(df, est, cid)

    fig = px.density_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        radius=15,
        center=dict(lat=lat_center, lon=lon_center),
        zoom=zoom,
        mapbox_style="carto-positron",
        hover_data=["nome", "cidade", "estado"],
        height=600,
        color_continuous_scale=px.colors.sequential.Darkmint_r  
    )

    fig.update_layout(
        coloraxis_showscale=False  
    )

    return fig

def mapa_empresas_mini(df, est, cid):
    lat_center, lon_center, zoom = calcula_centro_mapa(df, est, cid)

    fig = px.density_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        radius=15,
        center=dict(lat=lat_center, lon=lon_center),
        zoom=zoom,
        mapbox_style="carto-positron",
        hover_data=["nome", "cidade", "estado"],
        height=250
    )

    fig.update_layout(
        coloraxis_showscale=False,
        showlegend=False    

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
    st.plotly_chart(fig, use_container_width=True)


def calcula_centro_mapa(df_filtrado, estado_sel, cidade_sel):

    default_lat, default_lon, default_zoom = -15.2350, -53.9253, 3.3  

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