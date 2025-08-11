#The venv we can use to run this code is the one created in the Alura Immersion course


import streamlit as st #Streamlit is a framework to create web apps in Python
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="Data Visualization App",
    page_icon="📊",
    layout="wide",
) # Set the page title, icon, and layout

# Load the dataset -> it came from a pre-processed CSV file
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# --- Create the sidebar with filters ---
# The sidebar will allow users to filter the data displayed in the charts
st.sidebar.title("Data Visualization App")
st.sidebar.markdown("Use the filters below to customize the data displayed in the charts.")
st.sidebar.header("Filters")



# Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)



# --- Filter the dataframe based on the selected options in the sidebar ---
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
    # In summary this line filters the dataframe based on the selected options in the sidebar
    # isin is a method that checks if each element in the dataframe column is present in the list of selected options
]

# KPIs (Key Performance Indicators):
st.subheader("Key Performance Indicators (KPIs)")
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()   
    salario_minimo = df_filtrado['usd'].min()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado['cargo'].mode()[0] # This mode() method returns the most frequent value in the 'cargo' column
else:
    salario_medio = 0
    salario_maximo = 0
    salario_minimo = 0
    total_registros = 0
    cargo_mais_frequente = "N/A"

col1, col2, col3, col4,col5 = st.columns(5) #st.columns creates a layout with 4 columns
col1.metric("Salário Médio", f"R$ {salario_medio:,.0f}")
col2.metric("Salário Máximo", f"R$ {salario_maximo:,.0f}")
col3.metric("Salário Mínimo", f"R$ {salario_minimo:,.0f}")
col4.metric("Total de Registros", f"{total_registros:,}")
col5.metric("Cargo Mais Frequente", cargo_mais_frequente)

st.markdown("---")  # Add a horizontal line to separate the KPIs from the charts

st.subheader("Grafos:")

col_graf1, col_graf2 = st.columns(2)  # Create two columns for the charts
with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title='Top 10 Cargos com Maior Salário Médio Anual (USD)',
            labels={'usd': 'Salário Médio Anual (USD)', 'cargo': 'Cargo'},
            color='usd',
            color_continuous_scale=px.colors.sequential.Plasma # This sets the color scale for the bar chart
        )
        grafico_cargos.update_layout(
            xaxis_title='Salário Médio Anual (USD)',
            yaxis_title='Cargo',
            yaxis = {'categoryorder': 'total ascending'},  # This orders the y-axis by the total ascending
        )
        st.plotly_chart(grafico_cargos, use_container_width=True) # Display the chart in the first column
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de cargos.")
    
with col_graf2:
  if not df_filtrado.empty:
      grafico_hist = px.histogram(
          df_filtrado,
          x='usd',
          nbins=30,
          title='Distribuição dos Salários Anuais (USD)',
          labels={'usd': 'Salário Anual (USD)'},
          color_discrete_sequence=['#636EFA']  # This sets the color of the histogram bars
      )
      grafico_hist.update_layout(
            xaxis_title='Salário Anual (USD)',
            yaxis_title='Contagem',
            bargap=0.1  # This sets the gap between the bars in the histogram
        )
      st.plotly_chart(grafico_hist, use_container_width=True)  # Display the histogram in the second column
  else:
      st.warning("Nenhum dado disponível para exibir o gráfico de distribuição de salários.")

col_graf3, col_graf4 = st.columns(2)  # Create two more columns for additional charts
with col_graf3:
    if not df_filtrado.empty:
        remoto_contafem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contafem.columns = ['Tipo de Trabalho', 'Contagem']
        grafico_remoto = px.pie(
            remoto_contafem,
            values='Contagem',
            names='Tipo de Trabalho',
            title='Distribuição de Tipos de Trabalho',
            hole = 0.3,  # This creates a donut chart
            color_discrete_sequence=px.colors.qualitative.Set3  # This sets the color scheme for the pie chart
        )
        grafico_remoto.update_traces(textposition='inside', textinfo='percent+label')
        grafico_remoto.update_layout(
            xaxis_title='Tipo de Trabalho',
            yaxis_title='Contagem',
        )
        st.plotly_chart(grafico_remoto, use_container_width=True)  # Display the chart in the third column
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de registros por ano.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(
            media_ds_pais,
            locations='residencia_iso3',
            locationmode='ISO-3',
            color='usd',
            hover_name='residencia_iso3',
            title='Salário Médio de Data Scientists por País (USD)',
            color_continuous_scale=px.colors.sequential.Plasma,  # This sets the color scale for the choropleth map
            labels={'usd': 'Salário Médio Anual (USD)'}
        )
        grafico_paises.update_layout(title_x=0.5)  # Center the title of the map
        st.plotly_chart(grafico_paises,use_container_width=True)  # Display the choropleth map in the fourth column
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de salários por país.")


st.subheader("Sobre o Projeto")
st.dataframe(df_filtrado)