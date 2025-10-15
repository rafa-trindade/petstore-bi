import pandas as pd
import numpy as np
import streamlit as st

def popopulacao_250K (df_empresa, df_ibge, range_pop = 250000):

    empresa_pop_maior_250k = df_empresa[df_empresa['populacao'] > 250000][['cidade', 'estado']].drop_duplicates().shape[0]
    ibge_pop_maior_250k = df_ibge[df_ibge['populacao'] > 250000][['cidade', 'estado']].shape[0]
    indice_mais_250k = (empresa_pop_maior_250k / ibge_pop_maior_250k * 100) if ibge_pop_maior_250k != 0 else 0
    
    ibge_250k = df_ibge[df_ibge['populacao'] > 250000][['cidade', 'estado', 'populacao']]
    cobasi_250k = df_empresa[df_empresa['populacao'] > 250000][['cidade', 'estado']]
    cidades_nao_contadas = ibge_250k.merge(cobasi_250k, on=['cidade', 'estado'], how='left', indicator=True)
    cidades_nao_contadas = cidades_nao_contadas[cidades_nao_contadas['_merge'] == 'left_only']
    cidades_nao_contadas = cidades_nao_contadas.sort_values(by='populacao', ascending=False)
    lista_cidades_nao_contadas = (cidades_nao_contadas
                                .apply(lambda row: f"{row['cidade']}-{row['estado']}", axis=1)
                                .tolist())
    lista_cidades_nao_contadas = ", ".join(lista_cidades_nao_contadas)

    return {
        "indice": indice_mais_250k,
        "cidades_ausentes": lista_cidades_nao_contadas,
        "numero_cidades": len(cidades_nao_contadas)
    }



def hhi_regiao(df_empresa, df_geral, meta_hhi=1800):

    participacao = df_geral["empresa"].str.lower().value_counts(normalize=True)
    hhi_geral = round((participacao ** 2).sum() * 10000, 2)

    interpretacao = np.select(
        [
            hhi_geral == 10000,
            hhi_geral < 1500,
            (hhi_geral >= 1500) & (hhi_geral <= 2500),
            (hhi_geral > 2500) & (hhi_geral < 10000)
        ],
        [
            "Monopólio",
            "Mercado Competitivo",
            "Moderadamente Concentrado",
            "Altamente Concentrado"
        ],
        default="Sem Dados"
    ).item()

    hhi_por_cidade = (
        df_geral.groupby(["cidade", "estado", "empresa"])
        .size()
        .groupby(level=[0, 1])
        .apply(lambda x: ((x / x.sum()) ** 2).sum() * 10000)
        .reset_index(name="hhi")
    )

    participacao_cobasi = (
        df_empresa.groupby(["cidade", "estado"])["empresa"].count() /
        df_geral.groupby(["cidade", "estado"])["empresa"].count()
    ).reset_index(name="participacao_cobasi")

    df_analise = hhi_por_cidade.merge(participacao_cobasi, on=["cidade", "estado"], how="left")
    df_analise["participacao_cobasi"] = df_analise["participacao_cobasi"].fillna(0)  
    df_analise["gap_expansao"] = (df_analise["hhi"] > meta_hhi) & (df_analise["participacao_cobasi"] < 0.5)

    cidades_prioritarias = df_analise[df_analise["gap_expansao"]]
    lista_cidades = cidades_prioritarias.apply(lambda x: f"{x['cidade']}-{x['estado']}", axis=1).tolist()
    texto_cidades = ", ".join(lista_cidades)

    resumo = {
        "hhi_geral": hhi_geral,
        "interpretacao": interpretacao,
        "meta_hhi": meta_hhi,
        "numero_cidades": len(lista_cidades),
        "cidades_prioritarias": texto_cidades
    }
    return resumo



def capitais(df_empresa, df_capitais):    
    
    df_capitais = df_capitais.copy()
    df_empresa = df_empresa.copy()

    df_capitais["cidade_estado"] = df_capitais["cidade"].str.strip() + "-" + df_capitais["estado"].str.strip()
    df_empresa["cidade_estado"] = df_empresa["cidade"].str.strip() + "-" + df_empresa["estado"].str.strip()


    capitais_presentes = (
        df_capitais.merge(
            df_empresa[['cidade_estado']], on='cidade_estado', how='inner'
        )
        .drop_duplicates(subset=['cidade_estado'])
    )

    indice = (len(capitais_presentes) / len(df_capitais)) * 100 if len(df_capitais) > 0 else 0
    
    capitais_ausentes = df_capitais.merge(
        df_empresa[['cidade_estado']], on='cidade_estado', how='left', indicator=True
    )
    capitais_ausentes = capitais_ausentes[capitais_ausentes['_merge'] == 'left_only']


    lista_cidades_nao_contadas = capitais_ausentes["cidade_estado"].tolist()
    texto_cidades = ", ".join(lista_cidades_nao_contadas)

    return {
        "indice": indice,
        "cidades_ausentes": texto_cidades,
        "numero_cidades": len(lista_cidades_nao_contadas)
    }



def cidades_exclusivas_e_sem_empresas(empresa_nome, df_todas_empresas, df_ibge, range_pop=100000):

    for df in [df_todas_empresas, df_ibge]:
        df['cidade'] = df['cidade'].astype(str).str.strip().str.upper()
        df['estado'] = df['estado'].astype(str).str.strip().str.upper()
    
    empresa_nome = empresa_nome.strip().upper()

    ibge_100k = df_ibge[df_ibge['populacao'] > range_pop][['cidade','estado','populacao']]

    cidades_empresa = df_todas_empresas[df_todas_empresas['empresa'].str.upper() == empresa_nome][['cidade','estado']].drop_duplicates()
    cidades_todas_empresas = df_todas_empresas[['cidade','estado']].drop_duplicates()

    outras_empresas = cidades_todas_empresas.merge(
        cidades_empresa,
        on=['cidade','estado'],
        how='left',
        indicator=True
    )
    outras_empresas = outras_empresas[outras_empresas['_merge'] == 'left_only'][['cidade','estado']]

    cidades_exclusivas = cidades_empresa.merge(
        outras_empresas,
        on=['cidade','estado'],
        how='left',
        indicator=True
    )
    cidades_exclusivas = cidades_exclusivas[cidades_exclusivas['_merge'] == 'left_only']
    cidades_exclusivas = cidades_exclusivas.merge(ibge_100k, on=['cidade','estado'], how='inner')

    cidades_sem_empresas = ibge_100k.merge(
        cidades_todas_empresas,
        on=['cidade','estado'],
        how='left',
        indicator=True
    )
    cidades_sem_empresas = cidades_sem_empresas[cidades_sem_empresas['_merge'] == 'left_only']

    if len(cidades_sem_empresas) > 0:
        lista_cidades_ausentes = ", ".join(
            cidades_sem_empresas
            .sort_values(by='populacao', ascending=False)
            .apply(lambda r: f"{r['cidade']}-{r['estado']}", axis=1)
            .tolist()
        )
    else:
        lista_cidades_ausentes = None

    return {
        "indice": int(len(cidades_exclusivas)),
        "cidades_ausentes": lista_cidades_ausentes,
        "numero_cidades": int(len(cidades_sem_empresas))
    }



def indice_saturacao_expansao(empresa_nome, df_todas_empresas, df_ibge, pop_min=100_000):

    for df in [df_todas_empresas, df_ibge]:
        df['cidade'] = df['cidade'].astype(str).str.strip().str.upper()
        df['estado'] = df['estado'].astype(str).str.strip().str.upper()

    empresa_nome = empresa_nome.strip().upper()

    df_ibge_filtrado = df_ibge[df_ibge['populacao'] >= pop_min].copy()

    lojas_total = (
        df_todas_empresas.groupby(['cidade', 'estado'])
        .size()
        .reset_index(name='lojas_total')
    )

    lojas_empresa = (
        df_todas_empresas[df_todas_empresas['empresa'].str.upper() == empresa_nome]
        .groupby(['cidade', 'estado'])
        .size()
        .reset_index(name='lojas_empresa')
    )

    df_analise = df_ibge_filtrado.merge(lojas_total, on=['cidade', 'estado'], how='left')
    df_analise = df_analise.merge(lojas_empresa, on=['cidade', 'estado'], how='left')
    df_analise['lojas_total'] = df_analise['lojas_total'].fillna(0)
    df_analise['lojas_empresa'] = df_analise['lojas_empresa'].fillna(0)

    indice_saturacao = df_analise['lojas_total'].mean()

    def saturacao_max(pop):
        if pop < 100_000:
            return 1
        elif pop <= 500_000:
            return 2
        else:
            return 5

    df_analise['saturacao_max'] = df_analise['populacao'].apply(saturacao_max)

    df_analise['espaco_livre'] = df_analise['saturacao_max'] - df_analise['lojas_empresa']

    cidades_para_expansao = df_analise[df_analise['espaco_livre'] > 0].copy()

    top20 = cidades_para_expansao.sort_values(by='populacao', ascending=False).head(20)

    lista_cidades_para_expansao = [
        f"{str(row['cidade']).title()}-{str(row['estado']).upper()} (+{int(row['espaco_livre'])})"
        for _, row in top20.iterrows()
    ]

    cidades_para_expansao_str = ", ".join(lista_cidades_para_expansao)

    numero_cidades = len(lista_cidades_para_expansao)

    if indice_saturacao < 1.5:
        interpretacao = "Mercado com baixa saturação geral - alto potencial de expansão"
    elif indice_saturacao <= 2.5:
        interpretacao = "Mercado moderadamente saturado - oportunidades em polos regionais"
    else:
        interpretacao = "Mercado altamente saturado - foco em otimização antes de novas aberturas"

    return {
        "indice": round(indice_saturacao, 2),
        "cidades_para_expansao": cidades_para_expansao_str,
        "numero_cidades": numero_cidades,
        "interpretacao": interpretacao
    }
