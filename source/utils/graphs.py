import pandas as pd
import plotly.graph_objects as go
from itertools import product
import plotly.express as px

def grafico_concorrencia_mini(df, empresa_sel, empresas_disponiveis, empresa):

    df['empresa_clean'] = df['empresa'].str.strip().str.title()

    paleta = px.colors.sequential.Darkmint_r
    cores = {}

    cores[empresa.title()] = paleta[0]

    if empresa_sel != "Todas" and empresa_sel.lower() != empresa.lower():
        cores[empresa_sel.title()] = paleta[2]

    empresas_restantes = [e for e in empresas_disponiveis if e.lower() not in [empresa.lower(), empresa_sel.lower()]]
    for i, e in enumerate(empresas_restantes):
        cor_index = (i + 1) % len(paleta)
        cores[e.title()] = paleta[cor_index]

    df_totais_cidade = df.groupby("cidade")["empresa_clean"].count().reset_index()
    top_cidades = df_totais_cidade.nlargest(5, "empresa_clean")["cidade"]

    df = df[df['cidade'].isin(top_cidades)]

    combinacoes = pd.DataFrame(list(product(top_cidades, [e.title() for e in empresas_disponiveis])),
                               columns=['cidade', 'empresa_clean'])
    
    df_grafico = combinacoes.merge(
        df.groupby(['cidade','empresa_clean']).size().reset_index(name='num_lojas'),
        on=['cidade','empresa_clean'],
        how='left'
    )
    df_grafico['num_lojas'] = df_grafico['num_lojas'].fillna(0)

    cidade_order = df_grafico.groupby('cidade')['num_lojas'].sum().sort_values(ascending=False).index

    fig = go.Figure()

    empresa_base_y = df_grafico[df_grafico['empresa_clean']==empresa.title()].set_index('cidade').reindex(cidade_order, fill_value=0)['num_lojas']
    fig.add_trace(go.Bar(
        x=cidade_order,
        y=empresa_base_y,
        name=empresa.title(),
        marker_color=cores[empresa.title()],
        text=empresa_base_y,
        textposition='auto'
    ))

    if empresa_sel != "Todas" and empresa_sel.lower() != empresa.lower():
        empresa_sel_y = df_grafico[df_grafico['empresa_clean']==empresa_sel.title()].set_index('cidade').reindex(cidade_order, fill_value=0)['num_lojas']
        fig.add_trace(go.Bar(
            x=cidade_order,
            y=empresa_sel_y,
            name=empresa_sel.title(),
            marker_color=cores[empresa_sel.title()],
            text=empresa_sel_y,
            textposition='auto'
        ))

    for e in empresas_restantes:
        e_y = df_grafico[df_grafico['empresa_clean']==e.title()].set_index('cidade').reindex(cidade_order, fill_value=0)['num_lojas']
        fig.add_trace(go.Bar(
            x=cidade_order,
            y=e_y,
            name=e.title(),
            marker_color=cores[e.title()],
            text=e_y,
            textposition='inside',
            textangle=0         
        ))

    fig.update_layout(
        barmode='stack',
        xaxis_title=None,
        yaxis_title='Número de Lojas',
        width=900,
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(x=0.9, y=1)

    )

    return fig
