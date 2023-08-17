import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image

st.set_page_config(layout='wide')
st.header('Dashboard Vendas 2023 - Toninho')

# Read Data
@st.cache_data
def get_data(path):
    data = pd.read_csv(path, index_col=0)
    return data

# Extract Data
#path = 'data/feature_vendas.csv'
data = get_data('data/feature_vendas.csv')

def format_total(value):
    return '{:,.2f}'.format(value)

df1 = data.loc[data['ano'] == 2023, ['revenda', 'cidade', 'produto', 'quantidade', 'preço', 'total', 'produto_geral']]

#====================================
#======= LAYOUT DO STREAMLIT ========
#====================================

#image_path = 'img/logo-indofil.png'
image = Image.open('img/logo-indofil.png')

# Título na barra lateral

st.sidebar.title('Filtros')
st.sidebar.image(image, width=120)

# Opções para o filtro de cidade
cidade_filtro = st.sidebar.multiselect('Selecione uma Cidade', df1['cidade'].sort_values().unique())

# Opções para o filtro de produto
produto_filtro = st.sidebar.multiselect('Selecione um Produto', df1['produto_geral'].sort_values().unique())



tab1, tab2, tab3, tab4 = st.tabs(['Planilha' ,'Faturamento', 'Produto', 'Mapa'])

with tab1:
    with st.container():
        st.header('Planilha de Vendas')
        # Filtrar os dados baseado nos filtros da barra lateral
        if (cidade_filtro != []) & (produto_filtro != []):
            df1 = df1.loc[(df1['cidade'].isin(cidade_filtro)) & (df1['produto_geral'].isin(produto_filtro)) , :]
        elif (cidade_filtro != []) & (produto_filtro == []):
            df1 = df1.loc[df1['cidade'].isin(cidade_filtro), :]
        elif (cidade_filtro == []) & (produto_filtro != []):
            df1 = df1.loc[df1['produto_geral'].isin(produto_filtro) , :]
        else:
            df1 = df1.loc[:, :]

        df1.columns = ['Revenda', 'Cidade', 'Produto', 'Quantidade', 'Preço', 'Total', 'Produto Geral']
        st.dataframe(df1, width=1200, height=400)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            valor_venda = df1['Total'].sum()
            total_vendas_formatado = "{:,.2f}".format(valor_venda).replace(",", "X").replace(".", ",").replace("X", ".")
            st.markdown(f'### Total Faturado: ')
            st.markdown(f'## R$ {total_vendas_formatado}') 

        with col2:
            quantidade_venda = df1['Quantidade'].sum()
            quantidade_vendas_formatado = "{:,.2f}".format(quantidade_venda).replace(",", "X").replace(".", ",").replace("X", ".")
            st.markdown(f'### Quantidade vendida: ')
            st.markdown(f'## {quantidade_vendas_formatado} kg')              


with tab2:
    with st.container():
        st.header('Faturamento durante o ano')
        aux = data.loc[data['ano'] == 2023]
        aux1 = aux.groupby('mes')['total'].sum().reset_index()
        aux1['total_formatted'] = aux1['total'].apply(format_total)
        fig = px.line(aux1, x='mes', y='total_formatted', text='total_formatted', markers=True)
        fig.update_layout( xaxis_title='Mês',  yaxis_title='Faturamento')
        fig.update_traces(textposition="top left")
        st.plotly_chart(fig, use_container_width=True)


    with st.container():
        aux = data.loc[data['ano'] == 2023, :]
        aux1 = aux.groupby('revenda').agg({'quantidade': 'sum', 'total': 'sum'}).reset_index().sort_values('total', ascending=False)
        aux1['total_formatted'] = aux1['total'].apply(format_total)
        fig = px.bar(aux1, x='revenda', y='total_formatted', text='total_formatted', title='Faturamento por Revenda' )
        fig.update_layout( xaxis_title='Revenda',  yaxis_title='Faturamento')
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    with st.container():
        st.markdown('### Variação Preço Medio Durante o ano')
        aux2 = data.loc[data['ano'] == 2023, :]
        aux3 = aux2[['produto', 'preço', 'mes']].groupby(['produto', 'mes']).mean().reset_index().sort_values('mes')
        aux3['preço'] = aux3['preço'].round(2)
        fig = px.line(aux3, x='mes', y='preço', color='produto', markers=True, text='preço' )
        fig.update_layout( xaxis_title='Mês',  yaxis_title='Preço Médio')
        fig.update_traces(textposition="top left")
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('### Quantidade vendida por mês de cada produto')
        aux = data.loc[data['ano'] == 2023, :]
        aux1 = aux[['produto_geral', 'quantidade', 'mes']].groupby(['produto_geral', 'mes']).sum().reset_index().sort_values('mes', ascending=True)
        fig = px.line( aux1, x='mes', y='quantidade', color='produto_geral', text='quantidade', markers=True )
        fig.update_layout( xaxis_title='Mês',  yaxis_title='Quantidade Total')
        fig.update_traces(textposition="top left")
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('### Produtos mais vendidos')
        aux2 = data.loc[data['ano'] == 2023]
        aux3 = aux2[['produto', 'quantidade']].groupby('produto').sum().reset_index().sort_values('quantidade', ascending=False)
        fig = px.bar(aux3, x='produto', y='quantidade', text='quantidade')
        fig.update_layout( xaxis_title='Produto',  yaxis_title='Quantidade Total')
        st.plotly_chart(fig, use_container_width=True)

    

with tab4:
    st.markdown('### Densidade de Vendas por Cidade')
    aux4 = data.loc[data['ano'] == 2023]
    cities = aux4[['cidade', 'latitude', 'longitude', 'total']].copy()
    cities['total_comprado'] = cities.groupby('cidade')['total'].transform('sum')

    fig_mapa = px.scatter_mapbox( cities, lat='latitude', lon='longitude', text='cidade', size='total_comprado', custom_data=['total_comprado'], size_max=25, zoom=5 )
    fig_mapa.update_traces(texttemplate='%{text}<br>Faturado: %{customdata:.,2f}', textposition='top center')

    # Add text labels for each city
 #   for _, row in cities.iterrows():
 #       fig_mapa.add_trace(px.scatter_mapbox(lat=[row['latitude']], lon=[row['longitude']],
 #                                       text=[row['cidade']]).data[0])

    fig_mapa.update_layout(mapbox_style='open-street-map')
    fig_mapa.update_layout(height=600, margin={'r':0, 'l':0, 'b':0, 't': 0})
    st.plotly_chart(fig_mapa, use_container_width=True)