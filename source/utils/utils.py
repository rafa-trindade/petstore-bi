import streamlit as st
import pandas as pd
import plotly.express as px 
import requests

def municipios_ibge():
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()

    municipios = []
    for m in data:
        microrregiao = m.get("microrregiao") or {}
        mesorregiao = microrregiao.get("mesorregiao") or {}
        uf = mesorregiao.get("UF") or {}

        municipios.append({
            "id": m.get("id"),
            "nome": m.get("nome"),
            "microrregiao": microrregiao.get("nome"),
            "mesorregiao": mesorregiao.get("nome"),
            "UF_id": uf.get("id"),
            "UF_sigla": uf.get("sigla"),
            "UF_nome": uf.get("nome")
        })

    df = pd.DataFrame(municipios)
    return df

regioes = {
    "Norte": ["AC","AP","AM","PA","RO","RR","TO"],
    "Nordeste": ["AL","BA","CE","MA","PB","PE","PI","RN","SE"],
    "Centro-Oeste": ["DF","GO","MT","MS"],
    "Sudeste": ["ES","MG","RJ","SP"],
    "Sul": ["PR","RS","SC"]
}

azul = "#2d5480" 
azul_escuro = "#2d5c80"
verde = "#176f87"
verde_claro = px.colors.sequential.Darkmint[3]
verde_escuro = "#176f87"
vermelha = "#a22938"
cinza_claro = "#c6d0d2"
cinza_escuro = "#c6d0d2"

