import os
import re
import requests
import pandas as pd
from dotenv import load_dotenv
import json

load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def atualizar_lat_long(df, nome_coluna='nome', lat_coluna='latitude', lon_coluna='longitude',
                       cidade_coluna='cidade', estado_coluna='estado'):
    for idx, row in df[df[lat_coluna].isna() | df[lon_coluna].isna()].iterrows():
        query = f"{row[nome_coluna]}"
        if cidade_coluna in df.columns and estado_coluna in df.columns:
            if pd.notna(row.get(cidade_coluna)):
                query += f", {row[cidade_coluna]}"
            if pd.notna(row.get(estado_coluna)):
                query += f" - {row[estado_coluna]}"
        
        params = {
            "engine": "google_maps",
            "q": query,
            "api_key": SERPAPI_API_KEY
        }

        response = requests.get("https://serpapi.com/search.json", params=params)
        data = response.json()
        
        try:
            # Inicializa valores
            lat_api, lon_api = None, None
            cidade_api, estado_api = None, None

            if 'local_results' in data and data['local_results']:
                result = data['local_results'][0]
                location = result.get('gps_coordinates', {})
                lat_api = float(location.get('latitude', None))
                lon_api = float(location.get('longitude', None))
                address = result.get('address', '')
            elif 'place_results' in data and 'gps_coordinates' in data['place_results']:
                result = data['place_results']
                location = result.get('gps_coordinates', {})
                lat_api = float(location.get('latitude', None))
                lon_api = float(location.get('longitude', None))
                address = result.get('address', '')
            else:
                print(f"⚠️ Nenhum resultado de coordenadas para: {query}")
                continue

            if address:
                match = re.search(r'([\w\sçãáéíóúâêôÇÃÁÉÍÓÚÂÊÔ]+)\s*-\s*([A-Z]{2})', address)
                if match:
                    cidade_api = match.group(1).strip()
                    estado_api = match.group(2).strip()

            if lat_api and lon_api:
                df.at[idx, lat_coluna] = lat_api
                df.at[idx, lon_coluna] = lon_api
            if cidade_api:
                df.at[idx, cidade_coluna] = cidade_api
            if estado_api:
                df.at[idx, estado_coluna] = estado_api

            print(f"✅ Coordenadas e localização obtidas para {query}: "
                  f"{lat_api}, {lon_api}, {cidade_api}, {estado_api}")
        
        except Exception as e:
            print(f" Erro ao obter coordenadas para {query}: {e}")
            continue
        
    return df


def preenche_campos(df, caminho_csv):

    mapa = pd.read_csv(caminho_csv, sep=";", encoding="utf-8-sig")

    if 'populacao' in mapa.columns:
        mapa['populacao'] = (
            mapa['populacao']
            .astype(str)
            .str.replace('.', '', regex=False)
            .replace('nan', None)
        )
        mapa['populacao'] = pd.to_numeric(mapa['populacao'], errors='coerce').astype('Int64')

    if 'renda_domiciliar_per_capita' in mapa.columns:
        mapa['renda_domiciliar_per_capita'] = (
            mapa['renda_domiciliar_per_capita']
            .astype(str)
            .str.replace(',', '.', regex=False)
            .replace('nan', None)
        )
        mapa['renda_domiciliar_per_capita'] = pd.to_numeric(
            mapa['renda_domiciliar_per_capita'], errors='coerce'
        ).astype('float')

    df_temp = pd.merge(
        df,
        mapa[['cidade', 'estado', 'populacao', 'renda_domiciliar_per_capita']],
        left_on=['cidade', 'estado'],
        right_on=['cidade', 'estado'],
        how='left',
        suffixes=('', '_ibge')
    )

    df['populacao'] = df['populacao'].fillna(df_temp['populacao_ibge']).astype('Int64')
    df['renda_domiciliar_per_capita'] = df['renda_domiciliar_per_capita'].fillna(
        df_temp['renda_domiciliar_per_capita_ibge']
    ).astype('float')

    return df
