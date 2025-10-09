import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def atualizar_lat_long(df, nome_coluna='nome', lat_coluna='latitude', lon_coluna='longitude'):

    for idx, row in df[df[lat_coluna].isna() | df[lon_coluna].isna()].iterrows():
        query = row[nome_coluna]
        
        params = {
            "engine": "google_maps",
            "q": query,
            "api_key": SERPAPI_API_KEY
        }
        
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        
        try:
            location = data['local_results'][0]['gps_coordinates']
            lat_api = float(location['latitude'])
            lon_api = float(location['longitude'])
            
            df.at[idx, lat_coluna] = lat_api
            df.at[idx, lon_coluna] = lon_api
        except (KeyError, IndexError, ValueError):
            print(f"Não foi possível obter coordenadas para: {query}")
            continue
        
    return df