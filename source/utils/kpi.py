import numpy as np

# Presença em cidades > 250 mil hab
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
  """
  Calcula o índice HHI e identifica cidades com potencial de expansão para a empresa (ex: Cobasi).

  Parâmetros:
  -----------
  df_empresa : DataFrame
      Dados apenas da empresa (ex: Cobasi), já filtrado para a região/estado desejado.
  df_geral : DataFrame
      Dados de todas as empresas (incluindo a Cobasi), já filtrado para a mesma região/estado.
  meta_hhi : int, opcional
      Limite de concentração de mercado (padrão = 1800).

  Retorna:
  --------
  dict
      Resumo com HHI geral, interpretação e lista de cidades prioritárias.
  DataFrame
      Detalhamento por cidade (HHI, participação Cobasi, indicador de gap).
  """

  # === 1. HHI geral do mercado ===
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

  # === 2. HHI por cidade ===
  hhi_por_cidade = (
      df_geral.groupby(["cidade", "estado", "empresa"])
      .size()
      .groupby(level=[0, 1])
      .apply(lambda x: ((x / x.sum()) ** 2).sum() * 10000)
      .reset_index(name="hhi")
  )

  # === participação da Cobasi ===
  participacao_cobasi = (
      df_empresa.groupby(["cidade", "estado"])["empresa"].count() /
      df_geral.groupby(["cidade", "estado"])["empresa"].count()
  ).reset_index(name="participacao_cobasi")

  # === 4. calcular gaps ===
  df_analise = hhi_por_cidade.merge(participacao_cobasi, on=["cidade", "estado"], how="left")
  df_analise["participacao_cobasi"].fillna(0, inplace=True)
  df_analise["gap_expansao"] = (df_analise["hhi"] > meta_hhi) & (df_analise["participacao_cobasi"] < 0.5)

  # === 5. lista de cidades prioritárias ===
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


def capitais (df_empresa, df_ibge):
  capitais_brasil = [
    "Rio Branco", "Maceió", "Macapá", "Manaus", "Salvador", "Fortaleza", "Brasília",
    "Vitória", "Goiânia", "São Luís", "Cuiabá", "Campo Grande", "Belo Horizonte",
    "Belém", "João Pessoa", "Curitiba", "Recife", "Teresina", "Rio De Janeiro",
    "Natal", "Porto Alegre", "Porto Velho", "Boa Vista", "Florianópolis",
    "São Paulo", "Aracaju", "Palmas"
  ]

  cidades_filtradas = df_ibge["cidade"].dropna().unique()
  capitais_presentes = [c for c in capitais_brasil if c in cidades_filtradas]
  capitais_cobasi = [c for c in capitais_presentes if c in df_empresa["cidade"].unique()]
  num_capitais_total = len(capitais_presentes)
  num_capitais_cobasi = len(capitais_cobasi)
  perc_capitais_cobasi = (num_capitais_cobasi / num_capitais_total * 100) if num_capitais_total > 0 else 0

 

