#Import das bibliotecas
import streamlit as st
import pandas as pd
from PIL import Image
from st_aggrid import AgGrid
import numpy as np
import openpyxl
import plotly.express as px

######## Variáveis #######
banner = Image.open('imagens/bannerTI2.png')


st.image(banner)



if 'df1' not in st.session_state:
    ######## Carrega e limpa os dados #######
    @st.cache
    def carregar_dados(allow_output_mutation=True):
        df_dadosescola = pd.read_csv(
            'https://dados.es.gov.br/dataset/05f98028-92ba-45ca-9210-cb000b03c979/resource/5dd7951a-51c0-40f6-8809-14690b1b69a5/download/dadosescola.csv',
            sep=";", engine='python')
        df_dadosescola.dropna(inplace=True)
        df_dadosescola = df_dadosescola.loc[df_dadosescola['Ano'] >= 2023]
        df_dadosescola = df_dadosescola.reset_index(drop=True)
        df_dadosescola = df_dadosescola.astype({'Inep': int})
        df_dadosmatricula = pd.read_csv(
            'https://dados.es.gov.br/dataset/05f98028-92ba-45ca-9210-cb000b03c979/resource/95ee26cf-aa81-4250-8c96-540aa32d1be5/download/dadosmatricula.csv',
            sep=";", engine='python')
        df_dadosmatricula = df_dadosmatricula.loc[df_dadosmatricula['Ano'] >= 2023]
        df_dadosmatricula = df_dadosmatricula.reset_index(drop=True)
        df_dadosmatricula = df_dadosmatricula.query(
            'TipoEnsino == "ENSINO FUNDAMENTAL - 9 ANOS" or TipoEnsino ==  "ENSINO MÉDIO" or TipoEnsino == "ENSINO MÉDIO INTEGRADO"')
        df_dadosmatricula = df_dadosmatricula.query(
            'Turno == "INTEGRAL" or Turno ==  "INTERMEDIÁRIO - MANHÃ" or Turno == "INTERMEDIÁRIO - TARDE"')
        df_dadosmatricula = df_dadosmatricula.query(
            'Serie == "6º ANO" or Serie == "7º ANO" or Serie == "8º ANO" or Serie == "9º ANO" or Serie == "1ª SÉRIE" or Serie == "2ª SÉRIE" or Serie == "3ª SÉRIE"')
        df_dadosmatricula = df_dadosmatricula.query(
            'NivelOrganizacional == "Estadual"')
        df_dadosmatricula = df_dadosmatricula.query('Escola != "EEEF 27 DE OUTUBRO" and Escola != "EEEF ASSENTAMENTO UNIÃO" and Escola != "EEEF CÓRREGO DO CEDRO" and Escola != "EEEF CÓRREGO QUEIXADA" and Escola != "EEEF MARGEM DO ITAUNINHAS" and Escola != "EEEF TRES DE MAIO" and Escola != "EEEF VALDICIO BARBOSA DOS SANTOS" and Escola != "EEEF XIII DE SETEMBRO" and Escola != "EEEFM SATURNINO RIBEIRO DOS SANTOS" and Escola != "EEEFM PAULO DAMIAO TRISTÃO PURINHA" and Escola != "EEEF EGIDIO BORDONI"')
        df_dadosmatricula = df_dadosmatricula.drop(
            columns=['InicioPeriodo', 'FimPeriodo', 'Submodalidade', 'Modalidade'])
        df_mapadaeducacao = pd.read_csv(
            'https://dados.es.gov.br/dataset/05f98028-92ba-45ca-9210-cb000b03c979/resource/d19135e1-8e8e-4b09-ac02-4fed123f8358/download/mapaeducacao.csv',
            sep=";", engine='python')
        df_base2023 = pd.read_excel('base2023.xlsx', sheet_name=0)
        return df_dadosescola, df_dadosmatricula, df_mapadaeducacao, df_base2023

    df1, df2, df3, df4 = carregar_dados()
    st.session_state['df1'] = df1
    st.session_state['df2'] = df2
    st.session_state['df3'] = df3
    st.session_state['df4'] = df4

    relatorio_geral = st.empty()
    with relatorio_geral.container():
        with st.expander("Clique aqui para expandir e consultar a planilha com todas as Matriculas de Tempo Integral por Turma"):
            st.title('Quantidade total de Matrículas no Tempo Integral')
            st.dataframe(st.session_state.df2)


else:
    relatorio_geral = st.empty()
    with st.expander("Clique aqui para expandir e consultar a planilha com todas as Matriculas de Tempo Integral por Turma"):
        st.title('Quantidade total de Matrículas no Tempo Integral')
        st.dataframe(st.session_state.df2)




tipo_relatorio = st.sidebar.radio(
    "Selecione o que deseja ver:",
    ('Relatório Geral de Matrículas do Tempo Integral', 'Soma de Matrículas do Tempo Integral'))

if tipo_relatorio == 'Soma de Matrículas do Tempo Integral':
    relatorio_geral.empty()
    # Calcula a soma
    soma = st.session_state.df2
    soma = soma.drop(
        columns=['Ano', 'Codigo', 'Municipio', 'Inep', 'Turno', 'VagasOfertadas', 'VagasOciosas', 'IdEscola',
                 'TipoEnsino', 'idTipoEnsino', 'NivelOrganizacional', 'Id'])
    soma = soma.groupby(["Escola", "Serie"])["TotalMatriculados"].sum().reset_index()

    # Fim da Dataframe de soma
    tipo_soma = st.sidebar.radio("Selecione o que deseja somar:",
    ('Por escola', 'Por Serie'))

    if tipo_soma == 'Por escola':
        st.session_state.selecao_escola = st.multiselect(
            'ou escolha a escola:',
            st.session_state.df2['Escola'].unique()
        )

        nova_df = soma.loc[soma['Escola'].isin(st.session_state.selecao_escola)]
        st.dataframe(nova_df)
        #AgGrid(nova_df, theme='streamlit', fit_columns_on_grid_load=True)
        soma_matriculas = nova_df['TotalMatriculados'].sum()
        st.subheader(f'Total de Matrículas: {soma_matriculas}')

    if tipo_soma == 'Por Serie':
        st.session_state.selecao_serie = st.multiselect(
            'Escolha a série',
            st.session_state.df2['Serie'].unique()
        )

        nova_df = soma.loc[soma['Serie'].isin(st.session_state.selecao_serie)]
        st.dataframe(nova_df)
        # AgGrid(nova_df, theme='streamlit', fit_columns_on_grid_load=True)
        soma_matriculas = nova_df['TotalMatriculados'].sum()
        st.subheader(f'Total de Matrículas: {soma_matriculas}')



elif tipo_relatorio == 'Relatório Geral de Matrículas do Tempo Integral':

    st.title('Detalhamento:')
    conteudo_grafico = st.selectbox(
        'Qual dado gostaria de ver?',
        ('Municipio', 'Escola', 'Serie', 'Turno', 'TipoEnsino'))


    soma2 = st.session_state.df2[[conteudo_grafico, 'TotalMatriculados']]
    soma2 = soma2.groupby([conteudo_grafico]).sum()
    soma2 = soma2.reset_index()

    #Gráfico
    st.subheader('Quantidade de Turmas')
    grafico_px = px.histogram(st.session_state.df2, x=conteudo_grafico,
                                                 color=conteudo_grafico,
                                                 text_auto=True).update_xaxes(categoryorder='total descending')
    st.plotly_chart(grafico_px)

    st.subheader('Quantidade de Matrículas')
    st.dataframe(soma2)

    #AgGrid(soma2, fit_columns_on_grid_load=True)

    soma_matriculas = soma2['TotalMatriculados'].sum()
    st.subheader(f'Total de Matrículas: {soma_matriculas}')


