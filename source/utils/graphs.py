import plotly.express as px
import plotly.express as px

def grafico_concorrencia_mini(df, empresa_sel, empresas_disponiveis, empresa):
    df["empresa_clean"] = df["empresa"].str.strip().str.title()
    
    paleta = px.colors.sequential.Darkmint_r
    cores = {}

    # Usa a variável 'empresa' passada como parâmetro
    cores[empresa.title()] = paleta[0]

    if empresa_sel != "Todas":
        cores[empresa_sel.title()] = paleta[2]
        empresas_restantes = [
            e for e in empresas_disponiveis
            if e.lower() != empresa.lower() and e.lower() != empresa_sel.lower()
        ]
    else:
        empresas_restantes = [
            e for e in empresas_disponiveis
            if e.lower() != empresa.lower()
        ]

    for i, e in enumerate(empresas_restantes):
        cor_index = i + 1
        if cor_index >= len(paleta):
            cor_index = cor_index % len(paleta)
        cores[e.title()] = paleta[cor_index]

    # Agrupa os dados
    df_grafico = df.groupby(["cidade", "empresa_clean"]).size().reset_index(name="num_lojas")

    # --- Filtro principal: empresa base + empresa selecionada ---
    if empresa_sel != "Todas":
        df_grafico = df_grafico[df_grafico["empresa_clean"].str.lower().isin([empresa.lower(), empresa_sel.lower()])]
    else:
        # Se "Todas", mostra a base e todas as demais
        df_grafico = df_grafico[df_grafico["empresa_clean"].isin(empresas_disponiveis)]

    # Top 5 cidades
    df_totais_cidade = df_grafico.groupby("cidade")["num_lojas"].sum().reset_index()
    df_totais_cidade = df_totais_cidade.rename(columns={"num_lojas": "total_lojas"})
    top_cidades = df_totais_cidade.nlargest(5, 'total_lojas')['cidade']

    df_grafico = df_grafico[df_grafico['cidade'].isin(top_cidades)]

    # --- Gráfico ---
    fig = px.bar(
        df_grafico,
        x='cidade',
        y='num_lojas',
        color='empresa_clean',
        text='num_lojas',
        color_discrete_map=cores
    )

    cidade_order = df_totais_cidade.set_index('cidade').loc[top_cidades]['total_lojas'].sort_values(ascending=False).index
    fig.update_layout(
        xaxis=dict(
            categoryorder='array',
            categoryarray=cidade_order,
            title=None,        
            showticklabels=True  
        ),
        yaxis=dict(
            title="Número de Lojas"
        ),
        width=900,
        height=400,
        legend_title_text='',
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(x=0.9, y=1),
    )

    fig.update_traces(marker_line_color="black", marker_line_width=0.2)

    return fig
