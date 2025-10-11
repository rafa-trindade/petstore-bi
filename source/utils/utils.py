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

def aplicar_estilo():
    st.markdown(
        """
        <style> 

            #MainMenu {visibility: hidden;}    
            footer {visibility: hidden;}
            header {visibility: hidden;} 

            [data-testid="baseButton-headerNoPadding"] {
                color: #2d4f72;
            }

            
            .st-emotion-cache-1jicfl2 {
                padding: 2.5rem 5rem 1rem;        

            /* Estilo para o container principal das notificações */
            [data-testid="stNotification"][role="alert"] {
                border-radius: 10px !important; /* Mantém a borda arredondada */
            }

            /* Estilo para o conteúdo específico das notificações */
            [data-testid="stNotificationContentInfo"] {
                background-color: #3A7C89 !important; /* Cor de fundo para st.info */
                color: #fff !important; /* Cor do texto para st.info */
            }
            [data-testid="stNotificationContentSuccess"] {
                background-color: #123F5A !important; /* Cor de fundo para st.success */
                color: #fff !important; /* Cor do texto para st.success */
            }
            [data-testid="stNotificationContentError"] {
                background-color: #418B9A !important; /* Cor de fundo para st.error */
                color: #fff !important; /* Cor do texto para st.error */
            }

            /* Estilo para garantir que o container principal também tenha o mesmo fundo */
            [data-testid="stNotification"][role="alert"]:has([data-testid="stNotificationContentInfo"]) {
                background-color: #3A7C89 !important; /* Cor de fundo para o container principal de st.info */
                color: #fff !important; /* Cor do texto para o container principal de st.info */
            }
            [data-testid="stNotification"][role="alert"]:has([data-testid="stNotificationContentSuccess"]) {
                background-color: #123F5A !important; /* Cor de fundo para o container principal de st.success */
                color: #fff !important; /* Cor do texto para o container principal de st.success */
            }
            [data-testid="stNotification"][role="alert"]:has([data-testid="stNotificationContentError"]) {
                background-color: #418B9A !important; /* Cor de fundo para o container principal de st.error */
                color: #fff !important; /* Cor do texto para o container principal de st.error */
            }

        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            position: fixed; 
            bottom: 0;
            left: 0;
            right: 0; 
            width: 100%; 
            background-color: #c6d0d2; 
            padding: 2.5px; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            color: #2B5482; 
            font-size: 14px;
            gap: 8px
        ">
            <span>Developed by </span>
            <a href="https://github.com/rafa-trindade" target="_blank">
                <img style="border-radius: 4px;" src="https://img.shields.io/badge/-Rafael%20Trindade-123F5A?style=flat-square&logo=github&logoColor=E4E3E3" alt="GitHub Badge">
            </a>
        </div>

        """,
        unsafe_allow_html=True
    )
    