import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image

st.set_page_config(layout='wide')
st.header('Dashboard Vendas - Toninho')

# Read Data
@st.cache_data
def get_data(path):
    data = pd.read_csv(path, index_col=0)
    return data

# Extract Data
#path = 'data/feature_vendas.csv'
data = get_data('data/vendas.csv')

def format_total(value):
    return '{:,.2f}'.format(value)

data.columns = ['Revenda', 'Cidade', 'Produto', 'Quantidade', 'Preço', 'Total', 'Ano', 'Mes', 'Produto Geral', 'Latitude', 'Longitude','Total Cidade']


#====================================
#======= LAYOUT DO STREAMLIT ========
#====================================

#image_path = 'img/logo-indofil.png'
image = Image.open('img/logo-indofil.png')
st.sidebar.image(image, width=120)

st.sidebar.title('Filtros')

ano_filtro = st.sidebar.multiselect('Selecione o Ano', data['Ano'].sort_values().unique(), default=[2024])

# Opções para o filtro de cidade
cidade_filtro = st.sidebar.multiselect('Selecione uma Cidade', data['Cidade'].sort_values().unique())

# Opções para o filtro de produto
produto_filtro = st.sidebar.multiselect('Selecione um Produto', data['Produto Geral'].sort_values().unique())



tab1, tab2, tab3, tab4, tab5 = st.tabs(['Planilha' ,'Faturamento', 'Produto', 'Mapa', 'Conclusões'])


# ========================== PRIMEIRA ABA - PLANILHA =======================================================================
with tab1:
    with st.container():
        st.header('Planilha de Vendas')

        df_filtrado = data.copy()
        if ano_filtro:
            df_filtrado = df_filtrado[df_filtrado['Ano'].isin(ano_filtro)]
        if cidade_filtro:
            df_filtrado = df_filtrado[df_filtrado['Cidade'].isin(cidade_filtro)]
        if produto_filtro:
            df_filtrado = df_filtrado[df_filtrado['Produto Geral'].isin(produto_filtro)]

        aux = df_filtrado.loc[:, ['Revenda', 'Cidade', 'Produto', 'Quantidade', 'Preço', 'Total', 'Ano']]
        aux = aux.sort_values('Revenda', ascending=True)
        st.dataframe(aux, width=1200, height=400)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            valor_venda = df_filtrado['Total'].sum()
            total_vendas_formatado = "{:,.2f}".format(valor_venda).replace(",", "X").replace(".", ",").replace("X", ".")
            st.markdown(f'### Total Faturado: ')
            st.markdown(f'## R$ {total_vendas_formatado}') 

        with col2:
            quantidade_venda = df_filtrado['Quantidade'].sum()
            quantidade_vendas_formatado = "{:,.2f}".format(quantidade_venda).replace(",", "X").replace(".", ",").replace("X", ".")
            st.markdown(f'### Quantidade vendida: ')
            st.markdown(f'## {quantidade_vendas_formatado} kg')              



# ========================== SEGUNDA ABA - FATURAMENTO =======================================================================
with tab2:
    with st.container():

        df_filtrado = data.copy()
        if ano_filtro:
            df_filtrado = df_filtrado[df_filtrado['Ano'].isin(ano_filtro)]
        if cidade_filtro:
            df_filtrado = df_filtrado[df_filtrado['Cidade'].isin(cidade_filtro)]
        if produto_filtro:
            df_filtrado = df_filtrado[df_filtrado['Produto Geral'].isin(produto_filtro)]

        st.markdown('### Faturamento durante o ano')
        aux1 = df_filtrado.groupby('Mes')['Total'].sum().reset_index()
        aux1['total_formatted'] = aux1['Total'].apply(format_total)
        fig = px.line(aux1, x='Mes', y='total_formatted', text='total_formatted', markers=True)
        fig.update_layout( xaxis_title='Mês',  yaxis_title='Faturamento')
        fig.update_traces(textposition="top left")
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('### Faturamento por produto')
        aux = df_filtrado.groupby('Produto Geral')['Total'].sum().reset_index().sort_values('Total', ascending=False)
        aux['total_formatted'] = aux['Total'].apply(format_total)
        fig = px.bar(aux, x='Produto Geral', y='total_formatted', text='total_formatted')
        fig.update_layout(xaxis_title='Produto', yaxis_title='Faturamento')
        fig.update_traces(textposition='outside',textfont_size=14)
        st.plotly_chart(fig, use_container_width=True)


    with st.container():
        st.markdown('### Faturamento por Revenda')
        aux = df_filtrado.groupby('Revenda').agg({'Quantidade': 'sum', 'Total': 'sum'}).reset_index().sort_values('Total', ascending=False)
        aux['total_formatted'] = aux['Total'].apply(format_total)
        fig = px.bar(aux, x='Revenda', y='total_formatted', text='total_formatted')
        fig.update_layout(xaxis_title='Revenda', yaxis_title='Faturamento')
        fig.update_traces(textfont_size=14)
        st.plotly_chart(fig, use_container_width=True)

        
# ========================== TERCEIRA ABA - PRODUTO =======================================================================
with tab3:
    with st.container():

        df_filtrado = data.copy()
        if ano_filtro:
            df_filtrado = df_filtrado[df_filtrado['Ano'].isin(ano_filtro)]
        if cidade_filtro:
            df_filtrado = df_filtrado[df_filtrado['Cidade'].isin(cidade_filtro)]
        if produto_filtro:
            df_filtrado = df_filtrado[df_filtrado['Produto Geral'].isin(produto_filtro)]


        st.markdown('### Variação Preço Medio Durante o ano')
        aux3 = df_filtrado[['Produto Geral', 'Preço', 'Mes']].groupby(['Produto Geral', 'Mes']).mean().reset_index().sort_values('Mes')
        aux3['Preço'] = aux3['Preço'].round(2)
        fig = px.line(aux3, x='Mes', y='Preço', color='Produto Geral', markers=True, text='Preço' )
        fig.update_layout( xaxis_title='Mês',  yaxis_title='Preço Médio')
        fig.update_traces(textposition="top left")
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('### Quantidade vendida por mês de cada produto')
        aux1 = df_filtrado[['Produto Geral', 'Quantidade', 'Mes']].groupby(['Produto Geral', 'Mes']).sum().reset_index().sort_values('Mes', ascending=True)
        fig = px.line( aux1, x='Mes', y='Quantidade', color='Produto Geral', text='Quantidade', markers=True )
        fig.update_layout( xaxis_title='Mês',  yaxis_title='Quantidade Total')
        fig.update_traces(textposition="top left")
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('### Produtos mais vendidos')
        aux3 = df_filtrado[['Produto', 'Quantidade']].groupby('Produto').sum().reset_index().sort_values('Quantidade', ascending=False)
        fig = px.bar(aux3, x='Produto', y='Quantidade', text='Quantidade')
        fig.update_layout( xaxis_title='Produto',  yaxis_title='Quantidade Total')
        fig.update_traces(textposition='outside',textfont_size=14)
        st.plotly_chart(fig, use_container_width=True)

    
# ========================== QUARTA ABA - MAPA =======================================================================
with tab4:

    df_filtrado = data.copy()
    if ano_filtro:
        df_filtrado = df_filtrado[df_filtrado['Ano'].isin(ano_filtro)]
    if cidade_filtro:
        df_filtrado = df_filtrado[df_filtrado['Cidade'].isin(cidade_filtro)]
    if produto_filtro:
        df_filtrado = df_filtrado[df_filtrado['Produto Geral'].isin(produto_filtro)]

    # Exibição do título
    st.markdown('### Densidade de Vendas por Cidade')

     # Recalcular total_por_cidade com base nos dados filtrados
    cidades_agrupadas = (
        df_filtrado.groupby(['Cidade', 'Latitude', 'Longitude'])['Total']
        .sum()
        .reset_index()
        .rename(columns={'Total': 'total_por_cidade'})
    )

    latitude_inicial = -22.2343858  
    longitude_inicial = -45.9327241  

    # Geração do mapa
    fig_mapa = px.scatter_mapbox(
        cidades_agrupadas,
        lat='Latitude',
        lon='Longitude',
        text='Cidade',
        size='total_por_cidade',
        custom_data=['total_por_cidade'],
        size_max=25,
        zoom=5,
        color_discrete_sequence=['darkblue']  # Define a cor azul escura
    )

    # Configuração do mapa
    fig_mapa.update_traces(marker=dict(opacity=0.8))  # Ajusta opacidade das bolhas
    fig_mapa.update_layout(
    mapbox_style='open-street-map',
    mapbox=dict(center=dict(lat=latitude_inicial, lon=longitude_inicial), zoom=6))
    fig_mapa.update_layout(height=600, margin={'r': 0, 'l': 0, 'b': 0, 't': 0})

    # Exibição no Streamlit
    st.plotly_chart(fig_mapa, use_container_width=True)

# ========================== QUINTA ABA - CONCLUSÕES =======================================================================
with tab5:
    st.markdown('## Conclusões - Dez 2024')

    # 1. Porcentagem de queda no faturamento
    faturamento_2023 = data[data['Ano'] == 2023]['Total'].sum()
    faturamento_2024 = data[data['Ano'] == 2024]['Total'].sum()
    queda_faturamento = ((faturamento_2023 - faturamento_2024) / faturamento_2023) * 100
    st.markdown(f"1. O faturamento caiu em 2024 representando uma queda de **{queda_faturamento:.2f}%** em relação a 2023.")

    # 2. Novas revendas atingidas e as que deixaram de comprar
    revendas_2023 = set(data[data['Ano'] == 2023]['Revenda'].unique())
    revendas_2024 = set(data[data['Ano'] == 2024]['Revenda'].unique())
    novas_revendas = len(revendas_2024 - revendas_2023)
    revendas_perdidas = len(revendas_2023 - revendas_2024)
    st.markdown(f"2. Em 2024, atingimos **{novas_revendas} novas revendas**, enquanto **{revendas_perdidas} revendas** deixaram de comprar em relação a 2023.")


    st.markdown(f"3. O pico de vendas em 2023 foi em **Agosto** e em 2024 foi em **Março**.")
    
    # 4. Top 3 compradores de 2024
    top_compradores_2024 = (
        data[data['Ano'] == 2024]
        .groupby('Revenda')['Total']
        .sum()
        .sort_values(ascending=False)
        .head(3)
    )
    top_3_compradores = top_compradores_2024.index.tolist()
    st.markdown(f"4. Os **Top 3 compradores de 2024** foram: **{', '.join(top_3_compradores)}**.")

    # 5. Aumento do preço médio de Manfil e Moximate
    manfil_preco_2023 = (
        data[(data['Ano'] == 2023) & (data['Produto Geral'] == 'Manfil')]
        ['Preço']
        .mean()
    )
    manfil_preco_2024 = (
        data[(data['Ano'] == 2024) & (data['Produto Geral'] == 'Manfil')]
        ['Preço']
        .mean()
    )
    moximate_preco_2023 = (
        data[(data['Ano'] == 2023) & (data['Produto Geral'] == 'Moximate')]
        ['Preço']
        .mean()
    )
    moximate_preco_2024 = (
        data[(data['Ano'] == 2024) & (data['Produto Geral'] == 'Moximate')]
        ['Preço']
        .mean()
    )

    aumento_manfil = ((manfil_preco_2024 - manfil_preco_2023) / manfil_preco_2023) * 100
    aumento_moximate = ((moximate_preco_2024 - moximate_preco_2023) / moximate_preco_2023) * 100
    st.markdown(f"5. O preço médio do **Manfil** aumentou **{aumento_manfil:.2f}%** de 2023 para 2024. O preço médio do **Moximate** aumentou **{aumento_moximate:.2f}%** no mesmo período.")

    # 6. Produtos mais comprados em ambos os anos
    produtos_mais_comprados = (
        data.groupby('Produto Geral')['Quantidade']
        .sum()
        .sort_values(ascending=False)
        .head(2)
        .index.tolist()
    )
    st.markdown(f"6. Os produtos mais comprados em ambos os anos foram: **{produtos_mais_comprados[1]} de 25kg** e **{produtos_mais_comprados[0]} de 10kg**.")