import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import json

from . import utils as util

def mapa_geral(df, est, cid):
    lat_center, lon_center, zoom = calcula_centro_mapa(df, est, cid)

    fig = px.density_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        radius=15,
        center=dict(lat=lat_center, lon=lon_center),
        zoom=zoom,
        mapbox_style="carto-positron",
        color_continuous_scale="viridis",
        hover_data=["empresa", "nome", "logradouro", "bairro", "cidade", "estado"],
        height=600
    )

    for empresa in df["empresa"].unique():
        df_emp = df[df["empresa"] == empresa]
        fig.add_scattermapbox(
            lat=df_emp["latitude"],
            lon=df_emp["longitude"],
            mode="markers",
            name=empresa.title(),
            marker=dict(size=8),
            text=df_emp["nome"].str.title() + " - " + df_emp["cidade"] + "-" + df_emp["estado"],
            hoverinfo="text"
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
        height=600
    )

    return fig


def geojson_maps(fig, reg, est):

    with open("source/utils/br_states.geojson", "r") as f:
        geojson = json.load(f)

    locations = [f["properties"]["sigla"] for f in geojson["features"]]

    z = [0]*len(locations)
    line_widths = [0.4]*len(locations)
    line_colors = ["#5A7DA2"]*len(locations)

    if reg != "Todas" and est == "Todos":
        estados_da_regiao = util.regioes[reg] 
        z = [1.8 if sigla in estados_da_regiao else 0 for sigla in locations]
        line_widths = [1.8 if sigla in estados_da_regiao else 0.4 for sigla in locations]
        line_colors = ["#5A7DA2" if sigla in estados_da_regiao else "#5A7DA2" for sigla in locations]

    elif est != "Todos":
        z = [1.8 if sigla == est else 0 for sigla in locations]
        line_widths = [1.8 if sigla == est else 0.4 for sigla in locations]
        line_colors = ["#5A7DA2" if sigla == est else "#5A7DA2" for sigla in locations]

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

    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))

    st.plotly_chart(fig, use_container_width=True)


def calcula_centro_mapa(df_filtrado, estado_sel, cidade_sel):

    # Centro padrão do Brasil
    default_lat, default_lon, default_zoom = -17.2350, -51.9253, 3.4  

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