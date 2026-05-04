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

data.columns = ['Revenda', 'Cidade', 'Estado', 'Produto', 'Quantidade', 'Preço', 'Total', 'Ano', 'Mes', 'Nome Mes', 'Produto Geral', 'Latitude', 'Longitude', 'Total Cidade', 'Safra', 'Mes Safra']



#====================================
#======= LAYOUT DO STREAMLIT ========
#====================================

#image_path = 'img/logo-indofil.png'
image = Image.open('img/logo-indofil.png')
st.sidebar.image(image, width=120)

st.sidebar.title('Filtros')

# Opções para o filtro de safra
safra_filtro = st.sidebar.multiselect('Selecione a Safra',data['Safra'].sort_values().unique(), default=[data['Safra'].max()])

# Opções para o filtro de produto
produto_filtro = st.sidebar.multiselect('Selecione um Produto', data['Produto Geral'].sort_values().unique())



tab1, tab2, tab3, tab4 = st.tabs(['Planilha' ,'Faturamento', 'Produto', 'Mapa'])


# ==================== APLICAÇÃO GLOBAL DOS FILTROS =====================
df_filtrado = data.copy()
if safra_filtro:
    df_filtrado = df_filtrado[df_filtrado['Safra'].isin(safra_filtro)]
if produto_filtro:
    df_filtrado = df_filtrado[df_filtrado['Produto Geral'].isin(produto_filtro)]


# ========================== PRIMEIRA ABA - PLANILHA =======================================================================
with tab1:
    

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            valor_venda = df_filtrado['Total'].sum()
            total_vendas_formatado = "{:,.2f}".format(valor_venda).replace(",", "X").replace(".", ",").replace("X", ".")
            st.markdown(f'### Total Faturado')
            st.markdown(f'## R$ {total_vendas_formatado}') 

        with col2:
            quantidade_venda = df_filtrado['Quantidade'].sum()
            quantidade_vendas_formatado = "{:,.2f}".format(quantidade_venda).replace(",", "X").replace(".", ",").replace("X", ".")
            st.markdown(f'### Quantidade vendida')
            st.markdown(f'## {quantidade_vendas_formatado} kg')     

        with col3:
            revendas_atendidas = df_filtrado['Revenda'].nunique()
            st.markdown(f'### Revendas Atendidas')
            st.markdown(f'## {revendas_atendidas}')

        with col4:
            cidades_atendidas = df_filtrado['Cidade'].nunique()
            st.markdown(f'### Cidades Atendidas')
            st.markdown(f'## {cidades_atendidas}')


    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():
        st.markdown('### Planilha de Vendas')
        aux = df_filtrado.loc[:, ['Revenda', 'Cidade', 'Produto', 'Quantidade', 'Preço', 'Total', 'Safra']].reset_index(drop=True)
        aux = aux.sort_values('Revenda', ascending=True)
        st.dataframe(aux, width=1200, height=400)        


# ========================== SEGUNDA ABA - FATURAMENTO =======================================================================
with tab2:
    with st.container():

        st.markdown('### Faturamento durante o ano')
        aux1 = df_filtrado.groupby(['Mes Safra', 'Nome Mes'])['Total'].sum().reset_index()
        aux1['total_formatted'] = aux1['Total'].apply(format_total)
        fig = px.line(aux1, x='Nome Mes', y='total_formatted', text='total_formatted', markers=True)
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

        st.markdown('### Variação Preço Medio Durante o ano')
        aux3 = df_filtrado[['Produto Geral', 'Preço', 'Mes Safra', 'Nome Mes']].groupby(['Produto Geral', 'Mes Safra', 'Nome Mes'], as_index=False).mean()
        aux3['Preço'] = aux3['Preço'].round(2)
        aux3 = aux3.sort_values('Mes Safra')

        # Define a ordem correta dos meses para o eixo X
        ordem_meses = aux3.sort_values('Mes Safra')['Nome Mes'].unique().tolist()

        # Cria o gráfico
        fig = px.line(aux3,x='Nome Mes', y='Preço', color='Produto Geral', markers=True, text='Preço', category_orders={'Nome Mes': ordem_meses})
        fig.update_layout( xaxis_title='Mês',  yaxis_title='Preço Médio')
        fig.update_traces(textposition="top left")
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('### Quantidade faturada por mês de cada produto')
        aux1 = df_filtrado[['Produto Geral', 'Quantidade', 'Mes Safra', 'Nome Mes']].groupby(['Produto Geral', 'Mes Safra', 'Nome Mes' ]).sum().reset_index()
        # Define a ordem correta dos meses para o eixo X
        aux1 = aux1.sort_values('Mes Safra')
        ordem_meses = aux1['Nome Mes'].unique().tolist()

        fig = px.line( aux1, x='Nome Mes', y='Quantidade', color='Produto Geral', text='Quantidade', markers=True, category_orders={'Nome Mes': ordem_meses}) 
        fig.update_layout( xaxis_title='Mês',  yaxis_title='Quantidade Total')
        fig.update_traces(textposition="top left")
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('### Produtos mais vendidos')
        aux3 = df_filtrado[['Produto Geral', 'Quantidade']].groupby('Produto Geral').sum().reset_index().sort_values('Quantidade', ascending=False)
        fig = px.bar(aux3, x='Produto Geral', y='Quantidade', text='Quantidade')
        fig.update_layout( xaxis_title='Produto',  yaxis_title='Quantidade Total')
        fig.update_traces(textposition='outside',textfont_size=14)
        st.plotly_chart(fig, use_container_width=True)

    
# ========================== QUARTA ABA - MAPA =======================================================================
with tab4:


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