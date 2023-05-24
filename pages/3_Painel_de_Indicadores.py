# Import das bibliotecas
import streamlit as st
import pandas as pd
from PIL import Image
from st_aggrid import AgGrid
import numpy as np
import openpyxl
import folium
from streamlit_folium import st_folium
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt
import time
import plotly.express as px
import plotly.graph_objects as go

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
        df_dadosmatricula = df_dadosmatricula.query(
            'Escola != "EEEF 27 DE OUTUBRO" and Escola != "EEEF ASSENTAMENTO UNIÃO" and Escola != "EEEF CÓRREGO DO CEDRO" and Escola != "EEEF CÓRREGO QUEIXADA" and Escola != "EEEF MARGEM DO ITAUNINHAS" and Escola != "EEEF TRES DE MAIO" and Escola != "EEEF VALDICIO BARBOSA DOS SANTOS" and Escola != "EEEF XIII DE SETEMBRO" and Escola != "EEEFM SATURNINO RIBEIRO DOS SANTOS" and Escola != "EEEFM PAULO DAMIAO TRISTÃO PURINHA" and Escola != "EEEF EGIDIO BORDONI"')
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

##### Sidebar geral #####
menu_geral = st.sidebar.radio(
    "Selecione o que deseja ver:",
    ('Indicadores PAEBES', 'Indicadores SAEB', 'Indicadores IDEB', 'Indicadores PADI', 'Indicadores Socioeconômicos'))
#### Fim sidebar geral ##

#### Indicadores PAEBES ########################################################################
if menu_geral == 'Indicadores PAEBES':
    st.title('Indicadores PAEBES')
    ## Selecionando/Filtrando Dataframe da PAEBES##

    dfpaebes = st.session_state.df4[['CÓD. INEP', 'REGIONAL', 'MUNICÍPIO', 'ESCOLA',
                                     'ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL',
                                     'MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)', 'CARGA HORÁRIA', 'TURNO(S)',
                                     'OFERTA DE TEMPO INTEGRAL', 'POSSUI CURSO TECNICO?', 'PROF PAEBES EF MAT 2019',
                                     'PROF PAEBES EF MAT 2021', 'PROF PAEBES EF LP 2019', 'PROF PAEBES EF LP 2021',
                                     'PROF PAEBES EF CN 2019', 'PROF PAEBES EF CN 2021', 'PROF PAEBES EM MAT 2019',
                                     'PROF PAEBES EM MAT 2021', 'PROF PAEBES EM LP 2019', 'PROF PAEBES EM LP 2021',
                                     'PROF PAEBES EM BIO 2019', 'PROF PAEBES EM BIO 2021', 'PROF PAEBES EM QUI 2019',
                                     'PROF PAEBES EM QUI 2021', 'PROF PAEBES EM FIS 2019', 'PROF PAEBES EM FIS 2021',
                                     'Média total PAEBES EF 2019', 'Média total EM PAEBES 2019',
                                     'Média total PAEBES EF 2021', 'Média total PAEBES EM 2021']]

    menu_paebes = st.sidebar.radio("Tipo de relatório:",
                                   ('Visão Geral do PAEBES do Tempo Integral', 'Ranking das escolas',
                                    'PAEBES por Escola'))
    if menu_paebes == 'Visão Geral do PAEBES do Tempo Integral':
        #### Criação de Filtros ###
        with st.expander("Filtrar por regionais"):
            paebes_escolha_regional = st.multiselect('Selecione as regionais:',
                                                     dfpaebes['REGIONAL'].unique(), dfpaebes['REGIONAL'].unique())

        paebes_escolha_ano = st.select_slider('Filtrar escolas por ano de Implantação:',
                                              options=dfpaebes['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique(),
                                              value=dfpaebes['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique().max())
        dfpaebes_filtrado = dfpaebes.loc[dfpaebes['REGIONAL'].isin(paebes_escolha_regional)].reset_index(drop=True)
        lista_selecao_ano_implantacao = []
        for item in dfpaebes['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique():
            if item <= paebes_escolha_ano:
                lista_selecao_ano_implantacao.append(item)
        dfpaebes_filtrado = dfpaebes_filtrado.loc[dfpaebes_filtrado['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].isin(
            lista_selecao_ano_implantacao)].reset_index(drop=True)
        ### Fim dos Filtros ###

        ## Criação da DF de resultados do PAEBES por REGIONAL ##
        df_paebes_media_regional = dfpaebes_filtrado.groupby(by=['REGIONAL']).mean(numeric_only=True).reset_index()

        selecao_ano_paebes = st.radio('Selecione o ano:', ('2019', '2021'))

        if selecao_ano_paebes == '2019':

            st.subheader('PAEBES 2019 Ensino Médio - Média geral por regional')
            fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='Média total EM PAEBES 2019',
                         text_auto=True).update_xaxes(categoryorder='total descending')
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)
            st.subheader('PAEBES 2019 Ensino Médio - Proeficiência Média geral por componente curricular:')
            tab2019EM1, tab2019EM2, tab2019EM3, tab2019EM4, tab2019EM5 = st.tabs(["Matemática",
                                                                                  "Língua Portuguesa",
                                                                                  "Biologia", "Química",
                                                                                  "Física"])
            with tab2019EM1:
                fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='PROF PAEBES EM MAT 2019',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2019EM2:
                fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='PROF PAEBES EM LP 2019',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2019EM3:
                fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='PROF PAEBES EM BIO 2019',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2019EM4:
                fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='PROF PAEBES EM QUI 2019',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2019EM5:
                fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='PROF PAEBES EM FIS 2019',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)

            st.subheader('PAEBES 2019 Ensino Fundamental - Média geral por regional')
            fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='Média total PAEBES EF 2019',
                         text_auto=True).update_xaxes(categoryorder='total descending')
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.subheader('PAEBES 2019 Ensino Fundamental - Proeficiência Média geral por componente curricular:')
            tab2019EF1, tab2019EF2, tab2019EF3 = st.tabs(["Matemática", "Língua Portuguesa", "Ciências da Natureza"])

            with tab2019EF1:
                fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='PROF PAEBES EF MAT 2019',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2019EF2:
                fig = px.bar(df_paebes_media_regional, x='REGIONAL', y="PROF PAEBES EF LP 2019",
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2019EF3:
                fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='PROF PAEBES EF CN 2019',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)

        elif selecao_ano_paebes == '2021':
            st.subheader('PAEBES 2021 Ensino Médio - Média geral por regional')
            fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='Média total PAEBES EM 2021',
                         text_auto=True).update_xaxes(categoryorder='total descending')
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.subheader('PAEBES 2021 Ensino Médio - Proeficiência Média geral por componente curricular:')
            tab2021EM1, tab2021EM2, tab2021EM3, tab2021EM4, tab2021EM5 = st.tabs(["Matemática",
                                                                                  "Língua Portuguesa",
                                                                                  "Biologia", "Química",
                                                                                  "Física"])
            with tab2021EM1:
                fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='PROF PAEBES EM MAT 2021',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EM2:
                fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='PROF PAEBES EM LP 2021',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EM3:
                fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='PROF PAEBES EM BIO 2021',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EM4:
                fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='PROF PAEBES EM QUI 2021',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EM5:
                fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='PROF PAEBES EM FIS 2021',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)

            st.subheader('PAEBES 2021 Ensino Fundamental - Média geral por regional')
            fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='Média total PAEBES EF 2021',
                         text_auto=True).update_xaxes(categoryorder='total descending')
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.subheader('PAEBES 2021 Ensino Fundamental - Proeficiência Média geral por componente curricular:')
            tab2021EF1, tab2021EF2, tab2021EF3 = st.tabs(["Matemática", "Língua Portuguesa", "Ciências da Natureza"])
            with tab2021EF1:
                fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='PROF PAEBES EF MAT 2021',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EF2:
                fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='PROF PAEBES EF LP 2021',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EF3:
                fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='PROF PAEBES EF CN 2021',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)

    if menu_paebes == 'Ranking das escolas':
        #### Criação de Filtros ###
        with st.expander("Filtrar por regionais"):
            paebes_escolha_regional = st.multiselect('Selecione as regionais:',
                                                     dfpaebes['REGIONAL'].unique(), dfpaebes['REGIONAL'].unique())

        paebes_escolha_ano = st.select_slider('Filtrar escolas por ano de Implantação:',
                                              options=dfpaebes['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique(),
                                              value=dfpaebes['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique().max())
        dfpaebes_filtrado = dfpaebes.loc[dfpaebes['REGIONAL'].isin(paebes_escolha_regional)].reset_index(drop=True)
        lista_selecao_ano_implantacao = []
        for item in dfpaebes['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique():
            if item <= paebes_escolha_ano:
                lista_selecao_ano_implantacao.append(item)
        dfpaebes_filtrado = dfpaebes_filtrado.loc[dfpaebes_filtrado['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].isin(
            lista_selecao_ano_implantacao)].reset_index(drop=True)

        paebes_escolha_modalidade = st.multiselect('Selecione a modalidade:',
                                                   dfpaebes[
                                                       'MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)'].unique(),
                                                   dfpaebes[
                                                       'MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)'].unique())

        dfpaebes_filtrado = dfpaebes_filtrado.loc[
            dfpaebes_filtrado['MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)'].isin(
                paebes_escolha_modalidade)].reset_index(drop=True)

        paebes_escolha_carga_horaria = st.multiselect('Selecione a carga horária:',
                                                      dfpaebes[
                                                          'CARGA HORÁRIA'].unique(),
                                                      dfpaebes[
                                                          'CARGA HORÁRIA'].unique())

        dfpaebes_filtrado = dfpaebes_filtrado.loc[
            dfpaebes_filtrado['CARGA HORÁRIA'].isin(
                paebes_escolha_carga_horaria)].reset_index(drop=True)

        paebes_escolha_turno = st.multiselect('Selecione o turno:',
                                              dfpaebes[
                                                  'TURNO(S)'].unique(),
                                              dfpaebes[
                                                  'TURNO(S)'].unique())

        dfpaebes_filtrado = dfpaebes_filtrado.loc[
            dfpaebes_filtrado['TURNO(S)'].isin(
                paebes_escolha_turno)].reset_index(drop=True)

        selecao_ano_paebes = st.radio('Selecione o ano de aplicação do PAEBES:', ('2019', '2021'))

        ### Fim dos Filtros ###

        ### Gráficos ##
        if selecao_ano_paebes == '2019':
            st.header('Ensino Médio')

            ### Top 10 escolas  Ensino médio ##
            st.subheader('Média geral PAEBES 2019 - Escolas com Melhores Resultados')
            fig = px.bar(dfpaebes_filtrado[['Média total EM PAEBES 2019', 'ESCOLA']].sort_values(
                'Média total EM PAEBES 2019', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='Média total EM PAEBES 2019', text_auto=True, color='Média total EM PAEBES 2019')
            st.plotly_chart(fig)

            ### Top 10 - Por disciplinas Médio ###
            st.subheader("Melhores resulados por disciplina")
            tab2019EM1, tab2019EM2, tab2019EM3, tab2019EM4, tab2019EM5 = st.tabs(["Matemática",
                                                                                  "Língua Portuguesa",
                                                                                  "Biologia", "Química",
                                                                                  "Física"])
            with tab2019EM1:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM MAT 2019', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM MAT 2019', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM MAT 2019', text_auto=True, color='PROF PAEBES EM MAT 2019')
                st.plotly_chart(fig)
            with tab2019EM2:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM LP 2019', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM LP 2019', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM LP 2019', text_auto=True, color='PROF PAEBES EM LP 2019')
                st.plotly_chart(fig)
            with tab2019EM3:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM BIO 2019', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM BIO 2019', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM BIO 2019', text_auto=True, color='PROF PAEBES EM BIO 2019')
                st.plotly_chart(fig)
            with tab2019EM4:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM QUI 2019', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM QUI 2019', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM QUI 2019', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2019EM5:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM FIS 2019', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM FIS 2019', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM FIS 2019', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)

            st.header('Ensino Fundamental')
            ### Top 10 escolas  Ensino Fundamental 2019 ##
            st.subheader('Média geral PAEBES 2019 - Escolas com Melhores Resultados')
            fig = px.bar(dfpaebes_filtrado[['Média total PAEBES EF 2019', 'ESCOLA']].sort_values(
                'Média total PAEBES EF 2019', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='Média total PAEBES EF 2019', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            ### Top 10 - Por disciplinas Fundamental 2019 ###
            st.subheader("Melhores resultados por disciplina")
            tab2019EF1, tab2019EF2, tab2019EF3 = st.tabs(["Matemática",
                                                          "Língua Portuguesa",
                                                          "Ciências da Natureza"])
            with tab2019EF1:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EF MAT 2019', 'ESCOLA']].sort_values(
                    'PROF PAEBES EF MAT 2019', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EF MAT 2019', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2019EF2:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EF LP 2019', 'ESCOLA']].sort_values(
                    'PROF PAEBES EF LP 2019', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EF LP 2019', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2019EF3:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EF CN 2019', 'ESCOLA']].sort_values(
                    'PROF PAEBES EF CN 2019', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EF CN 2019', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)

            st.header('Ensino Médio')

            ### Top 10 escolas  Ensino médio - Escolas com Resultados mais desafiadores ##
            st.subheader('Média geral PAEBES 2019 - Escolas com Resultados mais desafiadores')
            fig = px.bar(dfpaebes_filtrado[['Média total EM PAEBES 2019', 'ESCOLA']].sort_values(
                'Média total EM PAEBES 2019', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='Média total EM PAEBES 2019', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            ### Top 10 - Por disciplinas Médio ###
            st.subheader("Menores resultados por disciplina")
            tab2019EM1, tab2019EM2, tab2019EM3, tab2019EM4, tab2019EM5 = st.tabs(["Matemática",
                                                                                  "Língua Portuguesa",
                                                                                  "Biologia", "Química",
                                                                                  "Física"])
            with tab2019EM1:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM MAT 2019', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM MAT 2019', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM MAT 2019', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2019EM2:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM LP 2019', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM LP 2019', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM LP 2019', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2019EM3:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM BIO 2019', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM BIO 2019', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM BIO 2019', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2019EM4:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM QUI 2019', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM QUI 2019', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM QUI 2019', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2019EM5:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM FIS 2019', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM FIS 2019', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM FIS 2019', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)

            st.header('Ensino Fundamental')
            ### Top 10 escolas  Ensino Fundamental 2019 - Escolas com Resultados mais desafiadores##
            st.subheader('Média geral PAEBES 2019 - Escolas com Resultados mais desafiadores')
            fig = px.bar(dfpaebes_filtrado[['Média total PAEBES EF 2019', 'ESCOLA']].sort_values(
                'Média total PAEBES EF 2019', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='Média total PAEBES EF 2019', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            ### Top 10 - Por disciplinas Fundamental 2019 ###
            st.subheader("Menores resultados por disciplina")
            tab2019EF1, tab2019EF2, tab2019EF3 = st.tabs(["Matemática",
                                                          "Língua Portuguesa",
                                                          "Ciências da Natureza"])
            with tab2019EF1:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EF MAT 2019', 'ESCOLA']].sort_values(
                    'PROF PAEBES EF MAT 2019', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EF MAT 2019', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2019EF2:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EF LP 2019', 'ESCOLA']].sort_values(
                    'PROF PAEBES EF LP 2019', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EF LP 2019', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2019EF3:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EF CN 2019', 'ESCOLA']].sort_values(
                    'PROF PAEBES EF CN 2019', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EF CN 2019', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)

        if selecao_ano_paebes == '2021':
            st.header('Ensino Médio')

            ### Top 10 escolas  Ensino médio ##
            st.subheader('Média geral PAEBES 2021 - Escolas com melhores resultados')
            fig = px.bar(dfpaebes_filtrado[['Média total PAEBES EM 2021', 'ESCOLA']].sort_values(
                'Média total PAEBES EM 2021', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='Média total PAEBES EM 2021', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            ### Top 10 - Por disciplinas Médio ###
            st.subheader("Melhores resultados por disciplina")
            tab2021EM1, tab2021EM2, tab2021EM3, tab2021EM4, tab2021EM5 = st.tabs(["Matemática",
                                                                                  "Língua Portuguesa",
                                                                                  "Biologia", "Química",
                                                                                  "Física"])
            with tab2021EM1:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM MAT 2021', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM MAT 2021', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM MAT 2021', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EM2:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM LP 2021', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM LP 2021', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM LP 2021', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EM3:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM BIO 2021', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM BIO 2021', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM BIO 2021', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EM4:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM QUI 2021', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM QUI 2021', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM QUI 2021', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EM5:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM FIS 2021', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM FIS 2021', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM FIS 2021', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)

            st.header('Ensino Fundamental')
            ### Top 10 escolas  Ensino Fundamental 2021 ##
            st.subheader('Média geral PAEBES 2021 - Escolas com resultados mais desafiadores')
            fig = px.bar(dfpaebes_filtrado[['Média total PAEBES EF 2021', 'ESCOLA']].sort_values(
                'Média total PAEBES EF 2021', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='Média total PAEBES EF 2021', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            ### Top 10 - Por disciplinas Fundamental 2021 ###
            st.subheader("Menores resultados por disciplina")
            tab2021EF1, tab2021EF2, tab2021EF3 = st.tabs(["Matemática",
                                                          "Língua Portuguesa",
                                                          "Ciências da Natureza"])
            with tab2021EF1:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EF MAT 2021', 'ESCOLA']].sort_values(
                    'PROF PAEBES EF MAT 2021', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EF MAT 2021', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EF2:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EF LP 2021', 'ESCOLA']].sort_values(
                    'PROF PAEBES EF LP 2021', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EF LP 2021', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EF3:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EF CN 2021', 'ESCOLA']].sort_values(
                    'PROF PAEBES EF CN 2021', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EF CN 2021', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)

            st.header('Ensino Médio')

            ### Top 10 escolas  Ensino médio ##
            st.subheader('Média geral PAEBES 2021 - Escolas com resultados mais desafiadores')
            fig = px.bar(dfpaebes_filtrado[['Média total PAEBES EM 2021', 'ESCOLA']].sort_values(
                'Média total PAEBES EM 2021', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='Média total PAEBES EM 2021', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            ### Top 10 - Por disciplinas Médio ###
            st.subheader("Menores resultados por disciplina")
            tab2021EM1, tab2021EM2, tab2021EM3, tab2021EM4, tab2021EM5 = st.tabs(["Matemática",
                                                                                  "Língua Portuguesa",
                                                                                  "Biologia", "Química",
                                                                                  "Física"])
            with tab2021EM1:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM MAT 2021', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM MAT 2021', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM MAT 2021', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EM2:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM LP 2021', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM LP 2021', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM LP 2021', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EM3:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM BIO 2021', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM BIO 2021', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM BIO 2021', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EM4:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM QUI 2021', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM QUI 2021', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM QUI 2021', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EM5:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EM FIS 2021', 'ESCOLA']].sort_values(
                    'PROF PAEBES EM FIS 2021', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EM FIS 2021', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)

            st.header('Ensino Fundamental')
            ### Top 10 escolas  Ensino Fundamental 2021 ##
            st.subheader('Média geral PAEBES 2021 - Escolas com resultados mais desafiadores')
            fig = px.bar(dfpaebes_filtrado[['Média total PAEBES EF 2021', 'ESCOLA']].sort_values(
                'Média total PAEBES EF 2021', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='Média total PAEBES EF 2021', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            ### Top 10 - Por disciplinas Fundamental 2021 ###
            st.subheader("Menores resultados por disciplina")
            tab2021EF1, tab2021EF2, tab2021EF3 = st.tabs(["Matemática",
                                                          "Língua Portuguesa",
                                                          "Ciências da Natureza"])
            with tab2021EF1:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EF MAT 2021', 'ESCOLA']].sort_values(
                    'PROF PAEBES EF MAT 2021', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EF MAT 2021', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EF2:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EF LP 2021', 'ESCOLA']].sort_values(
                    'PROF PAEBES EF LP 2021', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EF LP 2021', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab2021EF3:
                fig = px.bar(dfpaebes_filtrado[['PROF PAEBES EF CN 2021', 'ESCOLA']].sort_values(
                    'PROF PAEBES EF CN 2021', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                             y='PROF PAEBES EF CN 2021', text_auto=True)
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)

    if menu_paebes == 'PAEBES por Escola':
        escolha_escola = st.selectbox('Selecione a escola:', dfpaebes['ESCOLA'].unique())
        dfpaebes_filtrado = dfpaebes.loc[dfpaebes['ESCOLA'] == escolha_escola]

        st.title(f'{escolha_escola}')

        st.header('Ensino Fundamental')

        ####GRAFICOS####
        st.subheader('Lingua Portuguesa')
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=dfpaebes_filtrado['ESCOLA'], y=dfpaebes_filtrado['PROF PAEBES EF LP 2019'],
                                 name='Proeficiencia Língua Portuguesa 2019'))
            fig.update_traces(marker_color='firebrick')

            fig.add_trace(go.Bar(x=dfpaebes_filtrado['ESCOLA'], y=dfpaebes_filtrado['PROF PAEBES EF LP 2021'],
                                 name='Proeficiencia Língua Portuguesa 2021'))
            st.plotly_chart(fig)
        with col2:
            st.metric('Resultado 2021 e variação 2019/2021', value=dfpaebes_filtrado['PROF PAEBES EF LP 2021'],
                      delta=int(dfpaebes_filtrado['PROF PAEBES EF LP 2021'].fillna(value=0) - dfpaebes_filtrado[
                          'PROF PAEBES EF LP 2019'].fillna(value=0)))
            st.write('Das 156 escolas de Tempo Integral em 2023, ')
            for df_paebes_indices in ['PROF PAEBES EF LP 2019', 'PROF PAEBES EF LP 2021']:

                listas_indicadores_paebes = dfpaebes[['ESCOLA', df_paebes_indices]].sort_values(df_paebes_indices,
                                                                                                ascending=False).reset_index(
                    drop=True)
                listas_indicadores_paebes = listas_indicadores_paebes.loc[
                    listas_indicadores_paebes['ESCOLA'] == escolha_escola].dropna(0)

                escola_posicao = str(listas_indicadores_paebes.index.min()+1)
                if escola_posicao == 'nan':
                    pass
                else:
                    st.write(f"a escola está na posição {escola_posicao}, na {df_paebes_indices}")

        st.subheader('Matemática')
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=dfpaebes_filtrado['ESCOLA'], y=dfpaebes_filtrado['PROF PAEBES EF MAT 2019'],
                                 name='PAEBES Matemática 2019'))
            fig.update_traces(marker_color='firebrick')
            fig.add_trace(go.Bar(x=dfpaebes_filtrado['ESCOLA'], y=dfpaebes_filtrado['PROF PAEBES EF MAT 2021'],
                                 name='PAEBES Matemática 2021'))
            st.plotly_chart(fig)

        with col2:
            st.metric('Resultado 2021 e variação 2019/2021', value=dfpaebes_filtrado['PROF PAEBES EF LP 2021'],
                      delta=int(dfpaebes_filtrado['PROF PAEBES EF LP 2021'].fillna(value=0) - dfpaebes_filtrado[
                          'PROF PAEBES EF LP 2019'].fillna(value=0)))
            st.write('Das 156 escolas de Tempo Integral em 2023, ')
            for df_paebes_indices in ['PROF PAEBES EF MAT 2019', 'PROF PAEBES EF MAT 2021']:

                listas_indicadores_paebes = dfpaebes[['ESCOLA', df_paebes_indices]].sort_values(df_paebes_indices,
                                                                                                ascending=False).reset_index(
                    drop=True)
                listas_indicadores_paebes = listas_indicadores_paebes.loc[
                    listas_indicadores_paebes['ESCOLA'] == escolha_escola].dropna(0)

                escola_posicao = str(listas_indicadores_paebes.index.min()+1)
                if escola_posicao == 'nan':
                    pass
                else:
                    st.write(f"a escola está na posição {escola_posicao}, na {df_paebes_indices}")

        st.subheader('Ciências da Natureza')
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=dfpaebes_filtrado['ESCOLA'], y=dfpaebes_filtrado['PROF PAEBES EF CN 2019'],
                                 name='Proeficiencia Ciência da Natureza 2019'))
            fig.update_traces(marker_color='firebrick')
            fig.add_trace(go.Bar(x=dfpaebes_filtrado['ESCOLA'], y=dfpaebes_filtrado['PROF PAEBES EF CN 2021'],
                                 name='Proeficiencia Ciências da Natureza 2021'))
            st.plotly_chart(fig)

        with col2:
            st.metric('Resultado 2021 e variação 2019/2021', value=dfpaebes_filtrado['PROF PAEBES EF LP 2021'],
                      delta=int(dfpaebes_filtrado['PROF PAEBES EF LP 2021'].fillna(value=0) - dfpaebes_filtrado[
                          'PROF PAEBES EF LP 2019'].fillna(value=0)))
            st.write('Das 156 escolas de Tempo Integral em 2023, ')
            for df_paebes_indices in ['PROF PAEBES EF MAT 2019', 'PROF PAEBES EF MAT 2021']:

                listas_indicadores_paebes = dfpaebes[['ESCOLA', df_paebes_indices]].sort_values(df_paebes_indices,
                                                                                                ascending=False).reset_index(
                    drop=True)
                listas_indicadores_paebes = listas_indicadores_paebes.loc[
                    listas_indicadores_paebes['ESCOLA'] == escolha_escola].dropna(0)

                escola_posicao = str(listas_indicadores_paebes.index.min()+1)
                if escola_posicao == 'nan':
                    pass
                else:
                    st.write(f"a escola está na posição {escola_posicao}, na {df_paebes_indices}")

        st.header('Ensino Médio')

        st.subheader('Lingua Portuguesa')
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=dfpaebes_filtrado['ESCOLA'], y=dfpaebes_filtrado['PROF PAEBES EM LP 2019'],
                                 name='Proeficiencia Língua Portuguesa 2019'))
            fig.update_traces(marker_color='firebrick')
            fig.add_trace(go.Bar(x=dfpaebes_filtrado['ESCOLA'], y=dfpaebes_filtrado['PROF PAEBES EM LP 2021'],
                                 name='Proeficiencia Língua Portuguesa 2021'))
            st.plotly_chart(fig)
        with col2:
            st.metric('Resultado 2021 e variação 2019/2021', value=dfpaebes_filtrado['PROF PAEBES EM LP 2021'],
                      delta=int(dfpaebes_filtrado['PROF PAEBES EM LP 2021'].fillna(value=0) - dfpaebes_filtrado[
                          'PROF PAEBES EM LP 2019'].fillna(value=0)))
            st.write('Das 156 escolas de Tempo Integral em 2023, ')
            for df_paebes_indices in ['PROF PAEBES EM MAT 2019', 'PROF PAEBES EM MAT 2021']:

                listas_indicadores_paebes = dfpaebes[['ESCOLA', df_paebes_indices]].sort_values(df_paebes_indices,
                                                                                                ascending=False).reset_index(
                    drop=True)
                listas_indicadores_paebes = listas_indicadores_paebes.loc[
                    listas_indicadores_paebes['ESCOLA'] == escolha_escola].dropna(0)

                escola_posicao = str(listas_indicadores_paebes.index.min()+1)
                if escola_posicao == 'nan':
                    pass
                else:
                    st.write(f"a escola está na posição {escola_posicao}, na {df_paebes_indices}")

        st.subheader('Matemática')
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=dfpaebes_filtrado['ESCOLA'], y=dfpaebes_filtrado['PROF PAEBES EM MAT 2019'],
                                 name='PAEBES Matemática 2019'))
            fig.update_traces(marker_color='firebrick')
            fig.add_trace(go.Bar(x=dfpaebes_filtrado['ESCOLA'], y=dfpaebes_filtrado['PROF PAEBES EM MAT 2021'],
                                 name='PAEBES Matemática 2021'))
            st.plotly_chart(fig)

        with col2:
            st.metric('Resultado 2021 e variação 2019/2021', value=dfpaebes_filtrado['PROF PAEBES EM MAT 2021'],
                      delta=int(dfpaebes_filtrado['PROF PAEBES EM MAT 2021'].fillna(value=0) - dfpaebes_filtrado[
                          'PROF PAEBES EM MAT 2019'].fillna(value=0)))
            st.write('Das 156 escolas de Tempo Integral em 2023, ')
            for df_paebes_indices in ['PROF PAEBES EM MAT 2019', 'PROF PAEBES EM MAT 2021']:

                listas_indicadores_paebes = dfpaebes[['ESCOLA', df_paebes_indices]].sort_values(df_paebes_indices,
                                                                                                ascending=False).reset_index(
                    drop=True)
                listas_indicadores_paebes = listas_indicadores_paebes.loc[
                    listas_indicadores_paebes['ESCOLA'] == escolha_escola].dropna(0)

                escola_posicao = str(listas_indicadores_paebes.index.min()+1)
                if escola_posicao == 'nan':
                    pass
                else:
                    st.write(f"a escola está na posição {escola_posicao}, na {df_paebes_indices}")

        st.subheader('Biologia')
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=dfpaebes_filtrado['ESCOLA'], y=dfpaebes_filtrado['PROF PAEBES EM BIO 2019'],
                                 name='PAEBES Biologia 2019'))
            fig.update_traces(marker_color='firebrick')
            fig.add_trace(go.Bar(x=dfpaebes_filtrado['ESCOLA'], y=dfpaebes_filtrado['PROF PAEBES EM BIO 2021'],
                                 name='PAEBES Biologia 2021'))
            st.plotly_chart(fig)

        with col2:
            st.metric('Resultado 2021 e variação 2019/2021', value=dfpaebes_filtrado['PROF PAEBES EM BIO 2021'],
                      delta=int(dfpaebes_filtrado['PROF PAEBES EM BIO 2021'].fillna(value=0) - dfpaebes_filtrado[
                          'PROF PAEBES EM BIO 2019'].fillna(value=0)))
            st.write('Das 156 escolas de Tempo Integral em 2023, ')
            for df_paebes_indices in ['PROF PAEBES EM BIO 2019', 'PROF PAEBES EM BIO 2021']:

                listas_indicadores_paebes = dfpaebes[['ESCOLA', df_paebes_indices]].sort_values(df_paebes_indices,
                                                                                                ascending=False).reset_index(
                    drop=True)
                listas_indicadores_paebes = listas_indicadores_paebes.loc[
                    listas_indicadores_paebes['ESCOLA'] == escolha_escola].dropna(0)

                escola_posicao = str(listas_indicadores_paebes.index.min()+1)
                if escola_posicao == 'nan':
                    pass
                else:
                    st.write(f"a escola está na posição {escola_posicao}, na {df_paebes_indices}")

        st.subheader('Química')
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=dfpaebes_filtrado['ESCOLA'], y=dfpaebes_filtrado['PROF PAEBES EM QUI 2019'],
                                 name='PAEBES Química 2019'))
            fig.update_traces(marker_color='firebrick')
            fig.add_trace(go.Bar(x=dfpaebes_filtrado['ESCOLA'], y=dfpaebes_filtrado['PROF PAEBES EM QUI 2021'],
                                 name='PAEBES Química 2021'))
            st.plotly_chart(fig)

        with col2:
            st.metric('Resultado 2021 e variação 2019/2021', value=dfpaebes_filtrado['PROF PAEBES EM QUI 2021'],
                      delta=int(dfpaebes_filtrado['PROF PAEBES EM QUI 2021'].fillna(value=0) - dfpaebes_filtrado[
                          'PROF PAEBES EM QUI 2019'].fillna(value=0)))
            st.write('Das 156 escolas de Tempo Integral em 2023, ')
            for df_paebes_indices in ['PROF PAEBES EM QUI 2019', 'PROF PAEBES EM QUI 2021']:

                listas_indicadores_paebes = dfpaebes[['ESCOLA', df_paebes_indices]].sort_values(df_paebes_indices,
                                                                                                ascending=False).reset_index(
                    drop=True)
                listas_indicadores_paebes = listas_indicadores_paebes.loc[
                    listas_indicadores_paebes['ESCOLA'] == escolha_escola].dropna(0)

                escola_posicao = str(listas_indicadores_paebes.index.min()+1)
                if escola_posicao == 'nan':
                    pass
                else:
                    st.write(f"a escola está na posição {escola_posicao}, na {df_paebes_indices}")

        st.subheader('Física')
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=dfpaebes_filtrado['ESCOLA'], y=dfpaebes_filtrado['PROF PAEBES EM FIS 2019'],
                                 name='PAEBES Física 2019'))
            fig.update_traces(marker_color='firebrick')
            fig.add_trace(go.Bar(x=dfpaebes_filtrado['ESCOLA'], y=dfpaebes_filtrado['PROF PAEBES EM FIS 2021'],
                                 name='PAEBES Física 2021'))
            st.plotly_chart(fig)

        with col2:
            st.metric('Resultado 2021 e variação 2019/2021', value=dfpaebes_filtrado['PROF PAEBES EM FIS 2021'],
                      delta=int(dfpaebes_filtrado['PROF PAEBES EM FIS 2021'].fillna(value=0) - dfpaebes_filtrado[
                          'PROF PAEBES EM FIS 2019'].fillna(value=0)))
            st.write('Das 156 escolas de Tempo Integral em 2023, ')
            for df_paebes_indices in ['PROF PAEBES EM FIS 2019', 'PROF PAEBES EM FIS 2021']:

                listas_indicadores_paebes = dfpaebes[['ESCOLA', df_paebes_indices]].sort_values(df_paebes_indices,
                                                                                                ascending=False).reset_index(
                    drop=True)
                listas_indicadores_paebes = listas_indicadores_paebes.loc[
                    listas_indicadores_paebes['ESCOLA'] == escolha_escola].dropna(0)

                escola_posicao = str(listas_indicadores_paebes.index.min()+1)
                if escola_posicao == 'nan':
                    pass
                else:
                    st.write(f"a escola está na posição {escola_posicao}, na {df_paebes_indices}")

############################################### Indicadores SAEB ######################################################
if menu_geral == 'Indicadores SAEB':
    st.title('Indicadores SAEB')
    ## Selecionando/Filtrando Dataframe da SAEB##

    dfsaeb = st.session_state.df4[['CÓD. INEP', 'REGIONAL', 'MUNICÍPIO', 'ESCOLA',
                                   'ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL',
                                   'MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)', 'CARGA HORÁRIA', 'TURNO(S)',
                                   'OFERTA DE TEMPO INTEGRAL', 'POSSUI CURSO TECNICO?', 'SAEB EF 2019',
                                   'SAEB EF 2021', 'SAEB EM 2019', 'SAEB EM 2021']]

    menu_saeb = st.sidebar.radio("Tipo de relatório:",
                                 ('Visão Geral do SAEB do Tempo Integral', 'Ranking das escolas',
                                  'SAEB por Escola'))
    if menu_saeb == 'Visão Geral do SAEB do Tempo Integral':
        #### Criação de Filtros ###
        with st.expander("Filtrar por regionais"):
            saeb_escolha_regional = st.multiselect('Selecione as regionais:',
                                                   dfsaeb['REGIONAL'].unique(), dfsaeb['REGIONAL'].unique())

        saeb_escolha_ano = st.select_slider('Filtrar escolas por ano de Implantação:',
                                            options=dfsaeb['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique(),
                                            value=dfsaeb['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique().max())
        dfsaeb_filtrado = dfsaeb.loc[dfsaeb['REGIONAL'].isin(saeb_escolha_regional)].reset_index(drop=True)
        lista_selecao_ano_implantacao = []
        for item in dfsaeb['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique():
            if item <= saeb_escolha_ano:
                lista_selecao_ano_implantacao.append(item)
        dfsaeb_filtrado = dfsaeb_filtrado.loc[dfsaeb_filtrado['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].isin(
            lista_selecao_ano_implantacao)].reset_index(drop=True)
        ### Fim dos Filtros ###

        ## Criação da DF de resultados do PAEBES por REGIONAL ##
        df_saeb_media_regional = dfsaeb_filtrado.groupby(by=['REGIONAL']).mean().reset_index()

        selecao_ano_saeb = st.radio('Selecione o ano:', ('2019', '2021'))

        if selecao_ano_saeb == '2019':
            st.subheader('SAEB 2019 Ensino Médio - Média geral por regional')
            fig = px.bar(df_saeb_media_regional, x='REGIONAL', y='SAEB EM 2019',
                         text_auto=True).update_xaxes(categoryorder='total descending')
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.subheader('SAEB 2019 Ensino Fundamental - Média geral por regional')
            fig = px.bar(df_saeb_media_regional, x='REGIONAL', y='SAEB EF 2019',
                         text_auto=True).update_xaxes(categoryorder='total descending')
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

        if selecao_ano_saeb == '2021':
            st.subheader('SAEB 2021 Ensino Médio - Média geral por regional')
            fig = px.bar(df_saeb_media_regional, x='REGIONAL', y='SAEB EM 2021',
                         text_auto=True).update_xaxes(categoryorder='total descending')
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.subheader('SAEB 2021 Ensino Fundamental - Média geral por regional')
            fig = px.bar(df_saeb_media_regional, x='REGIONAL', y='SAEB EF 2021',
                         text_auto=True).update_xaxes(categoryorder='total descending')
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

    if menu_saeb == 'Ranking das escolas':
        #### Criação de Filtros ###
        with st.expander("Filtrar por regionais"):
            saeb_escolha_regional = st.multiselect('Selecione as regionais:',
                                                   dfsaeb['REGIONAL'].unique(), dfsaeb['REGIONAL'].unique())

        saeb_escolha_ano = st.select_slider('Filtrar escolas por ano de Implantação:',
                                            options=dfsaeb['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique(),
                                            value=dfsaeb['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique().max())
        dfsaeb_filtrado = dfsaeb.loc[dfsaeb['REGIONAL'].isin(saeb_escolha_regional)].reset_index(drop=True)
        lista_selecao_ano_implantacao = []
        for item in dfsaeb['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique():
            if item <= saeb_escolha_ano:
                lista_selecao_ano_implantacao.append(item)
        dfsaeb_filtrado = dfsaeb_filtrado.loc[dfsaeb_filtrado['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].isin(
            lista_selecao_ano_implantacao)].reset_index(drop=True)

        saeb_escolha_modalidade = st.multiselect('Selecione a modalidade:',
                                                 dfsaeb['MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)'].unique(),
                                                 dfsaeb['MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)'].unique())

        dfsaeb_filtrado = dfsaeb_filtrado.loc[dfsaeb_filtrado['MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)'].isin(
            saeb_escolha_modalidade)].reset_index(drop=True)

        saeb_escolha_carga_horaria = st.multiselect('Selecione a carga horária:',
                                                    dfsaeb[
                                                        'CARGA HORÁRIA'].unique(),
                                                    dfsaeb[
                                                        'CARGA HORÁRIA'].unique())

        dfsaeb_filtrado = dfsaeb_filtrado.loc[
            dfsaeb_filtrado['CARGA HORÁRIA'].isin(
                saeb_escolha_carga_horaria)].reset_index(drop=True)

        saeb_escolha_turno = st.multiselect('Selecione o turno:',
                                            dfsaeb[
                                                'TURNO(S)'].unique(),
                                            dfsaeb[
                                                'TURNO(S)'].unique())

        dfsaeb_filtrado = dfsaeb_filtrado.loc[
            dfsaeb_filtrado['TURNO(S)'].isin(
                saeb_escolha_turno)].reset_index(drop=True)

        selecao_ano_saeb = st.radio('Selecione o ano de aplicação do PAEBES:', ('2019', '2021'))

        ### Fim dos Filtros ###

        if selecao_ano_saeb == '2019':
            st.header('Ensino Médio')

            ### Top 10 escolas  Ensino médio ##
            st.subheader('Média geral SAEB 2019 - Escolas com Melhores Resultados')
            fig = px.bar(dfsaeb_filtrado[['SAEB EM 2019', 'ESCOLA']].sort_values('SAEB EM 2019',
                                                                                          ascending=False).dropna(
                0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='SAEB EM 2019', text_auto=True)
            fig.update_traces(marker_color='firebrick')

            st.plotly_chart(fig)

            st.header('Ensino Fundamental')
            ### Top 10 escolas  Ensino Fundamental 2019 ##
            st.subheader('Média geral SAEB 2019 - Escolas com Melhores Resultados')
            fig = px.bar(dfsaeb_filtrado[['SAEB EF 2019', 'ESCOLA']].sort_values(
                'SAEB EF 2019', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='SAEB EF 2019', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.header('Ensino Médio')

            ### Top 10 escolas  Ensino médio ##
            st.subheader('Média geral SAEB 2019 - Escolas com resultados mais desafiadores')
            fig = px.bar(dfsaeb_filtrado[['SAEB EM 2019', 'ESCOLA']].sort_values('SAEB EM 2019',
                                                                                          ascending=True).dropna(
                0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='SAEB EM 2019', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.header('Ensino Fundamental')
            ### Top 10 escolas  Ensino Fundamental 2019 ##
            st.subheader('Média geral SAEB 2019 - Escolas com resultados mais desafiadores')
            fig = px.bar(dfsaeb_filtrado[['SAEB EF 2019', 'ESCOLA']].sort_values(
                'SAEB EF 2019', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='SAEB EF 2019', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

        if selecao_ano_saeb == '2021':
            st.header('Ensino Médio')
            ### Top 10 escolas  Ensino médio 2021##
            st.subheader('Média geral SAEB 2021 - Escolas com Melhores Resultados')
            fig = px.bar(dfsaeb_filtrado[['SAEB EM 2021', 'ESCOLA']].sort_values('SAEB EM 2021',
                                                                                          ascending=False).dropna(
                0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='SAEB EM 2021', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.header('Ensino Fundamental')
            ### Top 10 escolas  Ensino Fundamental 2021 ##
            st.subheader('Média geral SAEB 2021 - Escolas com melhores resultados')
            fig = px.bar(dfsaeb_filtrado[['SAEB EF 2021', 'ESCOLA']].sort_values(
                'SAEB EF 2021', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='SAEB EF 2021', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.header('Ensino Médio')
            ### Top 10 escolas  Ensino médio 2021##
            st.subheader('Média geral SAEB 2021 - Escolas com resultados mais desafiadores')
            fig = px.bar(dfsaeb_filtrado[['SAEB EM 2021', 'ESCOLA']].sort_values('SAEB EM 2021',
                                                                                          ascending=True).dropna(
                0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='SAEB EM 2021', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.header('Ensino Fundamental')
            ### Top 10 escolas  Ensino Fundamental 2021 ##
            st.subheader('Média geral SAEB 2021 - Escolas com resultados mais desafiadores')
            fig = px.bar(dfsaeb_filtrado[['SAEB EF 2021', 'ESCOLA']].sort_values(
                'SAEB EF 2021', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='SAEB EF 2021', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

    if menu_saeb == 'SAEB por Escola':
        escolha_escola = st.selectbox('Selecione a escola:', dfsaeb['ESCOLA'].unique())
        dfsaeb_filtrado = dfsaeb.loc[dfsaeb['ESCOLA'] == escolha_escola]

        st.title(f'{escolha_escola}')

        ####GRAFICOS####
        st.header('Ensino Fundamental')
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=dfsaeb_filtrado['ESCOLA'], y=dfsaeb_filtrado['SAEB EF 2019'],
                                 name='Ensino Fundamental resultados do SAEB 2019'))
            fig.update_traces(marker_color='firebrick')
            fig.add_trace(go.Bar(x=dfsaeb_filtrado['ESCOLA'], y=dfsaeb_filtrado['SAEB EF 2021'],
                                 name='Ensino Fundamental resultados do SAEB 2021'))
            st.plotly_chart(fig)
        with col2:
            # Gambiarra para mostrar o delta com menos casas decimais
            delta_float_str = float(dfsaeb_filtrado['SAEB EF 2021'].fillna(value=0) - dfsaeb_filtrado[
                'SAEB EF 2019'].fillna(value=0))
            delta_float_str = str(delta_float_str)[:5]
            delta_float_str = float(delta_float_str)
            # Fim da Gambiarra#
            st.metric('Resultado 2021 e variação 2019/2021', value=dfsaeb_filtrado['SAEB EF 2019'],
                      delta=delta_float_str)
            st.write(' ')
            st.write(' ')
            st.write('Das 156 escolas de Tempo Integral em 2023, ')
            for df_saeb_indices in ['SAEB EF 2019', 'SAEB EF 2021']:

                listas_indicadores_saeb = dfsaeb[['ESCOLA', df_saeb_indices]].sort_values(df_saeb_indices,
                                                                                          ascending=False).reset_index(
                    drop=True)
                listas_indicadores_saeb = listas_indicadores_saeb.loc[
                    listas_indicadores_saeb['ESCOLA'] == escolha_escola].dropna(0)

                escola_posicao = str(listas_indicadores_saeb.index.min()+1)
                if escola_posicao == 'nan':
                    pass
                else:
                    st.write(f"a escola está na posição {escola_posicao}, no {df_saeb_indices}")



        st.header('Ensino Médio')
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=dfsaeb_filtrado['ESCOLA'], y=dfsaeb_filtrado['SAEB EM 2019'],
                                 name='Ensino Médio resultados do SAEB 2019'))
            fig.update_traces(marker_color='firebrick')
            fig.add_trace(go.Bar(x=dfsaeb_filtrado['ESCOLA'], y=dfsaeb_filtrado['SAEB EM 2021'],
                                 name='Ensino Médio resultados do SAEB 2021'))
            st.plotly_chart(fig)
        with col2:
            # Gambiarra para mostrar o delta com menos casas decimais
            delta_float_str = float(dfsaeb_filtrado['SAEB EM 2021'].fillna(value=0) - dfsaeb_filtrado[
                'SAEB EM 2019'].fillna(value=0))
            delta_float_str = str(delta_float_str)[:5]
            delta_float_str = float(delta_float_str)
            # Fim da Gambiarra#
            st.metric('Resultado 2021 e variação 2019/2021', value=dfsaeb_filtrado['SAEB EM 2019'],
                      delta=delta_float_str)
            st.write(' ')
            st.write(' ')
            st.write('Das 156 escolas de Tempo Integral em 2023, ')
            for df_saeb_indices in ['SAEB EM 2019', 'SAEB EM 2021']:

                listas_indicadores_saeb = dfsaeb[['ESCOLA', df_saeb_indices]].sort_values(df_saeb_indices,
                                                                                          ascending=False).reset_index(
                    drop=True)
                listas_indicadores_saeb = listas_indicadores_saeb.loc[
                    listas_indicadores_saeb['ESCOLA'] == escolha_escola].dropna(0)

                escola_posicao = str(listas_indicadores_saeb.index.min()+1)
                if escola_posicao == 'nan':
                    pass
                else:
                    st.write(f"a escola está na posição {escola_posicao}, no {df_saeb_indices}")

############################################### Indicadores IDEB ######################################################
if menu_geral == 'Indicadores IDEB':
    st.title('Indicadores IDEB')
    ## Selecionando/Filtrando Dataframe da IDEB##

    dfideb = st.session_state.df4[['CÓD. INEP', 'REGIONAL', 'MUNICÍPIO', 'ESCOLA',
                                   'ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL',
                                   'MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)', 'CARGA HORÁRIA', 'TURNO(S)',
                                   'OFERTA DE TEMPO INTEGRAL', 'POSSUI CURSO TECNICO?', 'IDEB EF 2019',
                                   'IDEB EF 2021', 'IDEB EM 2019', 'IDEB EM 2021']]

    menu_ideb = st.sidebar.radio("Tipo de relatório:",
                                 ('Visão Geral do IDEB do Tempo Integral', 'Ranking das escolas',
                                  'IDEB por Escola'))
    if menu_ideb == 'Visão Geral do IDEB do Tempo Integral':
        #### Criação de Filtros ###
        with st.expander("Filtrar por regionais"):
            ideb_escolha_regional = st.multiselect('Selecione as regionais:',
                                                   dfideb['REGIONAL'].unique(), dfideb['REGIONAL'].unique())

        ideb_escolha_ano = st.select_slider('Filtrar escolas por ano de Implantação:',
                                            options=dfideb['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique(),
                                            value=dfideb['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique().max())
        dfideb_filtrado = dfideb.loc[dfideb['REGIONAL'].isin(ideb_escolha_regional)].reset_index(drop=True)
        lista_selecao_ano_implantacao = []
        for item in dfideb['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique():
            if item <= ideb_escolha_ano:
                lista_selecao_ano_implantacao.append(item)
        dfideb_filtrado = dfideb_filtrado.loc[dfideb_filtrado['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].isin(
            lista_selecao_ano_implantacao)].reset_index(drop=True)
        ### Fim dos Filtros ###

        ## Criação da DF de resultados do IDEB por REGIONAL ##
        df_ideb_media_regional = dfideb_filtrado.groupby(by=['REGIONAL']).mean().reset_index()

        selecao_ano_ideb = st.radio('Selecione o ano:', ('2019', '2021'))

        if selecao_ano_ideb == '2019':
            st.subheader('IDEB 2019 Ensino Médio - Média geral por regional')
            fig = px.bar(df_ideb_media_regional, x='REGIONAL', y='IDEB EM 2019',
                         text_auto=True).update_xaxes(categoryorder='total descending')
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.subheader('IDEB 2019 Ensino Fundamental - Média geral por regional')
            fig = px.bar(df_ideb_media_regional, x='REGIONAL', y='IDEB EF 2019',
                         text_auto=True).update_xaxes(categoryorder='total descending')
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

        if selecao_ano_ideb == '2021':
            st.subheader('IDEB 2021 Ensino Médio - Média geral por regional')
            fig = px.bar(df_ideb_media_regional, x='REGIONAL', y='IDEB EM 2021',
                         text_auto=True).update_xaxes(categoryorder='total descending')
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.subheader('IDEB 2021 Ensino Fundamental - Média geral por regional')
            fig = px.bar(df_ideb_media_regional, x='REGIONAL', y='IDEB EF 2021',
                         text_auto=True).update_xaxes(categoryorder='total descending')
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

    if menu_ideb == 'Ranking das escolas':
        #### Criação de Filtros ###
        with st.expander("Filtrar por regionais"):
            ideb_escolha_regional = st.multiselect('Selecione as regionais:',
                                                   dfideb['REGIONAL'].unique(), dfideb['REGIONAL'].unique())

        ideb_escolha_ano = st.select_slider('Filtrar escolas por ano de Implantação:',
                                            options=dfideb['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique(),
                                            value=dfideb['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique().max())
        dfideb_filtrado = dfideb.loc[dfideb['REGIONAL'].isin(ideb_escolha_regional)].reset_index(drop=True)
        lista_selecao_ano_implantacao = []
        for item in dfideb['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique():
            if item <= ideb_escolha_ano:
                lista_selecao_ano_implantacao.append(item)
        dfideb_filtrado = dfideb_filtrado.loc[dfideb_filtrado['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].isin(
            lista_selecao_ano_implantacao)].reset_index(drop=True)

        ideb_escolha_modalidade = st.multiselect('Selecione a modalidade:',
                                                 dfideb['MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)'].unique(),
                                                 dfideb['MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)'].unique())

        dfideb_filtrado = dfideb_filtrado.loc[dfideb_filtrado['MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)'].isin(
            ideb_escolha_modalidade)].reset_index(drop=True)

        ideb_escolha_carga_horaria = st.multiselect('Selecione a carga horária:',
                                                    dfideb[
                                                        'CARGA HORÁRIA'].unique(),
                                                    dfideb[
                                                        'CARGA HORÁRIA'].unique())

        dfideb_filtrado = dfideb_filtrado.loc[
            dfideb_filtrado['CARGA HORÁRIA'].isin(
                ideb_escolha_carga_horaria)].reset_index(drop=True)

        ideb_escolha_turno = st.multiselect('Selecione o turno:',
                                            dfideb[
                                                'TURNO(S)'].unique(),
                                            dfideb[
                                                'TURNO(S)'].unique())

        dfideb_filtrado = dfideb_filtrado.loc[
            dfideb_filtrado['TURNO(S)'].isin(
                ideb_escolha_turno)].reset_index(drop=True)

        selecao_ano_ideb = st.radio('Selecione o ano de aplicação do IDEB:', ('2019', '2021'))

        ### Fim dos Filtros ###

        if selecao_ano_ideb == '2019':
            st.header('Ensino Médio')

            ### Top 10 escolas  Ensino médio ##
            st.subheader('Média geral IDEB 2019 - Escolas com Melhores Resultados')
            fig = px.bar(dfideb_filtrado[['IDEB EM 2019', 'ESCOLA']].sort_values('IDEB EM 2019',
                                                                                          ascending=False).dropna(
                0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='IDEB EM 2019', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.header('Ensino Fundamental')
            ### Top 10 escolas  Ensino Fundamental 2019 ##
            st.subheader('Média geral IDEB 2019 - Escolas com Melhores Resultados')
            fig = px.bar(dfideb_filtrado[['IDEB EF 2019', 'ESCOLA']].sort_values(
                'IDEB EF 2019', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='IDEB EF 2019', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.header('Ensino Médio')

            ### Top 10 escolas  Ensino médio ##
            st.subheader('Média geral IDEB 2019 - Escolas com resultados mais desafiadores')
            fig = px.bar(dfideb_filtrado[['IDEB EM 2019', 'ESCOLA']].sort_values('IDEB EM 2019',
                                                                                          ascending=True).dropna(
                0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='IDEB EM 2019', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.header('Ensino Fundamental')
            ### Top 10 escolas  Ensino Fundamental 2019 ##
            st.subheader('Média geral IDEB 2019 - Escolas com resultados mais desafiadores')
            fig = px.bar(dfideb_filtrado[['IDEB EF 2019', 'ESCOLA']].sort_values(
                'IDEB EF 2019', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='IDEB EF 2019', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

        if selecao_ano_ideb == '2021':
            st.header('Ensino Médio')
            ### Top 10 escolas  Ensino médio 2021##
            st.subheader('Média geral IDEB 2021 - Escolas com Melhores Resultados')
            fig = px.bar(dfideb_filtrado[['IDEB EM 2021', 'ESCOLA']].sort_values('IDEB EM 2021',
                                                                                          ascending=False).dropna(
                0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='IDEB EM 2021', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.header('Ensino Fundamental')
            ### Top 10 escolas  Ensino Fundamental 2021 ##
            st.subheader('Média geral IDEB 2021 - Escolas com melhores resultados')
            fig = px.bar(dfideb_filtrado[['IDEB EF 2021', 'ESCOLA']].sort_values(
                'IDEB EF 2021', ascending=False).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='IDEB EF 2021', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.header('Ensino Médio')
            ### Top 10 escolas  Ensino médio 2021##
            st.subheader('Média geral IDEB 2021 - Escolas com resultados mais desafiadores')
            fig = px.bar(dfideb_filtrado[['IDEB EM 2021', 'ESCOLA']].sort_values('IDEB EM 2021',
                                                                                          ascending=True).dropna(
                0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='IDEB EM 2021', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.header('Ensino Fundamental')
            ### Top 10 escolas  Ensino Fundamental 2021 ##
            st.subheader('Média geral IDEB 2021 - Escolas com resultados mais desafiadores')
            fig = px.bar(dfideb_filtrado[['IDEB EF 2021', 'ESCOLA']].sort_values(
                'IDEB EF 2021', ascending=True).dropna(0).reset_index(drop=True).head(10), x='ESCOLA',
                         y='IDEB EF 2021', text_auto=True)
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

    if menu_ideb == 'IDEB por Escola':
        escolha_escola = st.selectbox('Selecione a escola:', dfideb['ESCOLA'].unique())
        dfideb_filtrado = dfideb.loc[dfideb['ESCOLA'] == escolha_escola]

        st.title(f'{escolha_escola}')

        ####GRAFICOS####
        st.header('Ensino Fundamental')
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=dfideb_filtrado['ESCOLA'], y=dfideb_filtrado['IDEB EF 2019'],
                                 name='Ensino Fundamental resultados do IDEB 2019'))
            fig.update_traces(marker_color='firebrick')
            fig.add_trace(go.Bar(x=dfideb_filtrado['ESCOLA'], y=dfideb_filtrado['IDEB EF 2021'],
                                 name='Ensino Fundamental resultados do IDEB 2021'))

            st.plotly_chart(fig)
        with col2:
            # Gambiarra para mostrar o delta com menos casas decimais
            delta_float_str = float(dfideb_filtrado['IDEB EF 2021'].fillna(value=0) - dfideb_filtrado[
                'IDEB EF 2019'].fillna(value=0))
            delta_float_str = str(delta_float_str)[:5]
            delta_float_str = float(delta_float_str)
            # Fim da Gambiarra#
            st.metric('Resultado 2021 e variação 2019/2021', value=dfideb_filtrado['IDEB EF 2019'],
                      delta=delta_float_str)
            st.write(' ')
            st.write(' ')
            st.write('Das 156 escolas de Tempo Integral em 2023, ')
            for df_ideb_indices in ['IDEB EF 2019', 'IDEB EF 2021']:

                listas_indicadores_ideb = dfideb[['ESCOLA', df_ideb_indices]].sort_values(df_ideb_indices,
                                                                                          ascending=False).reset_index(
                    drop=True)
                listas_indicadores_ideb = listas_indicadores_ideb.loc[
                    listas_indicadores_ideb['ESCOLA'] == escolha_escola].dropna(0)

                escola_posicao = str(listas_indicadores_ideb.index.min()+1)
                if escola_posicao == 'nan':
                    pass
                else:
                    st.write(f"a escola está na posição {escola_posicao}, no {df_ideb_indices}")

        st.header('Ensino Médio')
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=dfideb_filtrado['ESCOLA'], y=dfideb_filtrado['IDEB EM 2019'],
                                 name='Ensino Médio resultados do IDEB 2019'))
            fig.update_traces(marker_color='firebrick')
            fig.add_trace(go.Bar(x=dfideb_filtrado['ESCOLA'], y=dfideb_filtrado['IDEB EM 2021'],
                                 name='Ensino Médio resultados do IDEB 2021'))
            st.plotly_chart(fig)
        with col2:
            # Gambiarra para mostrar o delta com menos casas decimais
            delta_float_str = float(dfideb_filtrado['IDEB EM 2021'].fillna(value=0) - dfideb_filtrado[
                'IDEB EM 2019'].fillna(value=0))
            delta_float_str = str(delta_float_str)[:5]
            delta_float_str = float(delta_float_str)
            # Fim da Gambiarra#
            st.metric('Resultado 2021 e variação 2019/2021', value=dfideb_filtrado['IDEB EM 2019'],
                      delta=delta_float_str)
            st.write(' ')
            st.write(' ')
            st.write('Das 156 escolas de Tempo Integral em 2023, ')
            for df_ideb_indices in ['IDEB EM 2019', 'IDEB EM 2021']:

                listas_indicadores_ideb = dfideb[['ESCOLA', df_ideb_indices]].sort_values(df_ideb_indices,
                                                                                          ascending=False).reset_index(
                    drop=True)
                listas_indicadores_ideb = listas_indicadores_ideb.loc[
                    listas_indicadores_ideb['ESCOLA'] == escolha_escola].dropna(0)

                escola_posicao = str(listas_indicadores_ideb.index.min()+1)
                if escola_posicao == 'nan':
                    pass
                else:
                    st.write(f"a escola está na posição {escola_posicao}, no {df_ideb_indices}")



############################################ Indicadores PADI #########################################################

if menu_geral == 'Indicadores PADI':
    st.title('Indicadores PADI')
    ## Selecionando/Filtrando Dataframe da PADI##

    dfpadi = st.session_state.df4[['CÓD. INEP', 'REGIONAL', 'MUNICÍPIO', 'ESCOLA',
                                   'ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL',
                                   'MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)', 'CARGA HORÁRIA', 'TURNO(S)',
                                   'OFERTA DE TEMPO INTEGRAL', 'POSSUI CURSO TECNICO?', 'PADI 2022.1 GERAL',
                                   'PADI 2022.1 OPERACAO', 'PADI 2022.1 MODELO', 'PADI 2022.1 GESTAO',
                                   'PADI 2022.1 PERCEPCAO', 'PADI 2022.3 GERAL', 'PADI 2022.3 OPERACAO',
                                   'PADI 2022.3 MODELO', 'PADI 2022.3 GESTAO', 'PADI 2022.3 PERCEPCAO',
                                   'PADI ano 2022']]

    menu_padi = st.sidebar.radio("Tipo de relatório:",
                                 ('Visão Geral da PADI do Tempo Integral', 'Ranking das escolas',
                                  'PADI por Escola'))
    if menu_padi == 'Visão Geral da PADI do Tempo Integral':

        #### Criação de Filtros ###
        with st.expander("Filtrar por regionais"):
            padi_escolha_regional = st.multiselect('Selecione as regionais:',
                                                   dfpadi['REGIONAL'].unique(), dfpadi['REGIONAL'].unique())

        padi_escolha_ano = st.select_slider('Filtrar escolas por ano de Implantação:',
                                            options=dfpadi['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique(),
                                            value=dfpadi['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique().max())
        dfpadi_filtrado = dfpadi.loc[dfpadi['REGIONAL'].isin(padi_escolha_regional)].reset_index(drop=True)
        lista_selecao_ano_implantacao = []
        for item in dfpadi['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique():
            if item <= padi_escolha_ano:
                lista_selecao_ano_implantacao.append(item)
        dfpadi_filtrado = dfpadi_filtrado.loc[dfpadi_filtrado['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].isin(
            lista_selecao_ano_implantacao)].reset_index(drop=True)
        ### Fim dos Filtros ###


        selecao_aplicacao_padi = st.radio('Selecione a aplicação:', ('2022.1', '2022.3'))
        df_padi_media_regional = dfpadi_filtrado.groupby(by=['REGIONAL']).mean().reset_index()

        if selecao_aplicacao_padi == '2022.1':
            st.subheader('PADI 2022.1 - Média geral por regional')
            fig = px.bar(df_padi_media_regional, x='REGIONAL', y='PADI 2022.1 GERAL',
                         text_auto=True).update_xaxes(categoryorder='total descending')
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.subheader('PADI 2022.1 - Média geral das regionais por Eixo:')
            tab_operacao, tab_modelo, tab_gestao, tab_percepcao = st.tabs(["Eixo Operação",
                                                                                  "Eixo Modelo do Tempo Integral",
                                                                                  "Eixo Gestão",
                                                                                "Eixo Percepção do tempo integral"
                                                                                  ])
            with tab_operacao:
                fig = px.bar(df_padi_media_regional, x='REGIONAL', y='PADI 2022.1 OPERACAO',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab_modelo:
                fig = px.bar(df_padi_media_regional, x='REGIONAL', y='PADI 2022.1 MODELO',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab_gestao:
                fig = px.bar(df_padi_media_regional, x='REGIONAL', y='PADI 2022.1 GESTAO',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab_percepcao:
                fig = px.bar(df_padi_media_regional, x='REGIONAL', y='PADI 2022.1 PERCEPCAO',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)

        if selecao_aplicacao_padi == '2022.3':
            st.subheader('PADI 2022.3 - Média geral por regional')
            fig = px.bar(df_padi_media_regional, x='REGIONAL', y='PADI 2022.3 GERAL',
                         text_auto=True).update_xaxes(categoryorder='total descending')
            fig.update_traces(marker_color='firebrick')
            st.plotly_chart(fig)

            st.subheader('PADI 2022.3 - Média geral por das regionais por Eixo:')
            tab_operacao, tab_modelo, tab_gestao, tab_percepcao = st.tabs(["Eixo Operação",
                                                                           "Eixo Modelo do Tempo Integral",
                                                                           "Eixo Gestão",
                                                                           "Eixo Percepção do tempo integral"
                                                                           ])
            with tab_operacao:
                fig = px.bar(df_padi_media_regional, x='REGIONAL', y='PADI 2022.3 OPERACAO',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab_modelo:
                fig = px.bar(df_padi_media_regional, x='REGIONAL', y='PADI 2022.3 MODELO',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab_gestao:
                fig = px.bar(df_padi_media_regional, x='REGIONAL', y='PADI 2022.3 GESTAO',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)
            with tab_percepcao:
                fig = px.bar(df_padi_media_regional, x='REGIONAL', y='PADI 2022.3 PERCEPCAO',
                             text_auto=True).update_xaxes(categoryorder='total descending')
                fig.update_traces(marker_color='firebrick')
                st.plotly_chart(fig)

    if menu_padi == 'Ranking das escolas':

        #### Criação de Filtros ###
        with st.expander("Filtrar por regionais"):
            padi_escolha_regional = st.multiselect('Selecione as regionais:',
                                                   dfpadi['REGIONAL'].unique(), dfpadi['REGIONAL'].unique())

        padi_escolha_ano = st.select_slider('Filtrar escolas por ano de Implantação:',
                                            options=dfpadi['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique(),
                                            value=dfpadi['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique().max())
        dfpadi_filtrado = dfpadi.loc[dfpadi['REGIONAL'].isin(padi_escolha_regional)].reset_index(drop=True)
        lista_selecao_ano_implantacao = []
        for item in dfpadi['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique():
            if item <= padi_escolha_ano:
                lista_selecao_ano_implantacao.append(item)
        dfpadi_filtrado = dfpadi_filtrado.loc[dfpadi_filtrado['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].isin(
            lista_selecao_ano_implantacao)].reset_index(drop=True)
        ### Fim dos Filtros ###

        selecao_aplicacao_padi = st.radio('Escolha a aplicação:', ['2022.1', '2022.3'])

        if selecao_aplicacao_padi == '2022.1':

            ##### Função que faz o TOP 10:
            def top10(col):
                fig = px.bar(dfpadi_filtrado[[col, 'ESCOLA']].sort_values(col, ascending=False).dropna(
                                                            0).reset_index(drop=True).head(10), x='ESCOLA',
                                                            y=col, text_auto=True)
                fig.update_traces(marker_color='firebrick')
                return st.plotly_chart(fig)
            #### Função que faz os BOT10:
            def bot10(col):
                fig = px.bar(dfpadi_filtrado[[col, 'ESCOLA']].sort_values(col, ascending=True).dropna(
                                                            0).reset_index(drop=True).head(10), x='ESCOLA',
                                                            y=col, text_auto=True)
                fig.update_traces(marker_color='firebrick')
                return st.plotly_chart(fig)



            st.header('Melhores resultados')

            st.subheader('Melhores Médias gerais da PADI')
            top10('PADI 2022.1 GERAL')
            st.subheader('Melhores Médias do Eixo Operação')
            top10('PADI 2022.1 OPERACAO')
            st.subheader('Melhores Médias do Eixo Modelo do Tempo Integral')
            top10('PADI 2022.1 MODELO')
            st.subheader('Melhores Médias do Eixo Gestão Pedagógica')
            top10('PADI 2022.1 GESTAO')
            st.subheader('Melhores Médias do Eixo Percepção do Tempo Integral')
            top10('PADI 2022.1 PERCEPCAO')

            st.header('Resultados mais desafiadores')

            padi_bot10_lista = [['Menores Médias gerais da PADI','PADI 2022.1 GERAL'],
                     ['Menores Médias do Eixo Operação','PADI 2022.1 OPERACAO'],
                     ['Menores Médias do Eixo Modelo do Tempo Integral','PADI 2022.1 MODELO'],
                     ['Menores Médias do Eixo Gestão Pedagógica','PADI 2022.1 GESTAO'],
                     ['Menores Médias do Eixo Percepção do Tempo Integral','PADI 2022.1 PERCEPCAO']
                     ]
            for item in padi_bot10_lista:
                st.subheader(f'{item[0]}')
                bot10(item[1])

    if menu_padi == 'PADI por Escola':

        escolha_escola = st.selectbox('Selecione a escola:', dfpadi['ESCOLA'].unique())
        dfpadi_filtrado = dfpadi.loc[dfpadi['ESCOLA'] == escolha_escola]

        st.title(f'{escolha_escola}')

        ####GRAFICOS####
        st.header('PADI - Média Geral')
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=dfpadi_filtrado['ESCOLA'], y=dfpadi_filtrado['PADI 2022.1 GERAL'],
                                 name='PADI Aplicação 2022.1'))
            fig.update_traces(marker_color='firebrick')
            fig.add_trace(go.Bar(x=dfpadi_filtrado['ESCOLA'], y=dfpadi_filtrado['PADI 2022.3 GERAL'],
                                 name='PADI Aplicação 2022.3'))
            st.plotly_chart(fig)
        with col2:
            # Gambiarra para mostrar o delta com menos casas decimais
            delta_float_str = float(dfpadi_filtrado['PADI 2022.3 GERAL'].fillna(value=0) - dfpadi_filtrado[
                'PADI 2022.1 GERAL'].fillna(value=0))
            delta_float_str = str(delta_float_str)[:5]
            delta_float_str = float(delta_float_str)
            # Fim da Gambiarra#
            st.metric('Resultado PADI 2022.3 e variação entres as aplicações', value=dfpadi_filtrado['PADI 2022.1 GERAL'],
                      delta=delta_float_str)
            st.write(' ')
            st.write(' ')
            qtd_escolas_fez_padi_22 = dfpadi.loc[dfpadi['PADI ano 2022'] == 'Fez PADI']
            qtd_escolas_fez_padi_22 = str(qtd_escolas_fez_padi_22.index.max()+1)
            st.write(qtd_escolas_fez_padi_22)
            st.write(f'Das {qtd_escolas_fez_padi_22} escolas de Tempo Integral que fizeram PADI em 2023, ')
            for df_padi_indices in ['PADI 2022.1 GERAL', 'PADI 2022.3 GERAL']:

                listas_indicadores_padi = dfpadi[['ESCOLA', df_padi_indices]].sort_values(df_padi_indices,
                                                                                          ascending=False).reset_index(
                    drop=True)
                listas_indicadores_padi = listas_indicadores_padi.loc[
                    listas_indicadores_padi['ESCOLA'] == escolha_escola].dropna(0)

                escola_posicao = str(listas_indicadores_padi.index.min() + 1)
                if escola_posicao == 'nan':
                    pass
                else:
                    st.write(f"a escola está na posição {escola_posicao}, no {df_padi_indices}")

        #Eixos da Padi:
        def eixospadi(eixo20221, eixo20223):
            fig = go.Figure()
            fig.add_trace(go.Bar(x=dfpadi_filtrado['ESCOLA'], y=dfpadi_filtrado[eixo20221],
                                 name="PADI 2022.1"))
            fig.update_traces(marker_color='firebrick')
            fig.add_trace(go.Bar(x=dfpadi_filtrado['ESCOLA'], y=dfpadi_filtrado[eixo20223],
                                 name="PADI 2022.3"))
            fig.update_xaxes(showticklabels=False)
            st.plotly_chart(fig)

            delta_float_str = float(dfpadi_filtrado[eixo20223].fillna(value=0) - dfpadi_filtrado[
                eixo20221].fillna(value=0))
            delta_float_str = str(delta_float_str)[:5]
            delta_float_str = float(delta_float_str)
            # Fim da Gambiarra#
            st.metric('Variação entres as aplicações',
                      value=dfpadi_filtrado[eixo20221],
                      delta=delta_float_str)

        tab1, tab2, tab3, tab4 = st.columns(4)
        with tab1:
            st.subheader('Operação:')
            eixospadi('PADI 2022.1 OPERACAO', 'PADI 2022.3 OPERACAO')
        with tab2:
            st.subheader('Modelo:')
            eixospadi('PADI 2022.1 MODELO', 'PADI 2022.3 MODELO')
        with tab3:
            st.subheader('Gestão:')
            eixospadi('PADI 2022.1 GESTAO', 'PADI 2022.3 GESTAO')
        with tab4:
            st.subheader('Percepção:')
            eixospadi('PADI 2022.1 PERCEPCAO', 'PADI 2022.3 PERCEPCAO')

####################################### Indicadores Socioeconômicos #################################################

if menu_geral == 'Indicadores Socioeconômicos':
    st.title('Indicador Socioeconômico INSE')
    ## Selecionando/Filtrando Dataframe da PADI##

    dfsocioeconomico = st.session_state.df4[['CÓD. INEP', 'REGIONAL', 'MUNICÍPIO', 'ESCOLA',
                                   'ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL',
                                   'MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)', 'CARGA HORÁRIA', 'TURNO(S)',
                                   'OFERTA DE TEMPO INTEGRAL', 'POSSUI CURSO TECNICO?', 'INSE_VALOR_ABSOLUTO',
                                   'INSE_CLASSIFICACAO', 'PC_NIVEL_1', 'PC_NIVEL_2', 'PC_NIVEL_3', 'PC_NIVEL_4',
                                   'PC_NIVEL_5', 'PC_NIVEL_6', 'PC_NIVEL_7', 'PC_NIVEL_8']]


    menu_socioeconomico = st.sidebar.radio("Tipo de relatório:",
                                 ('Visão Geral do Tempo Integral', 'Ranking das escolas',
                                  'Socioeconomico por Escola'))
    if menu_socioeconomico == 'Visão Geral do Tempo Integral':
        #### Criação de Filtros ###
        with st.expander("Filtrar por regionais"):
            socioeconomico_escolha_regional = st.multiselect('Selecione as regionais:',
                                                   dfsocioeconomico['REGIONAL'].unique(), dfsocioeconomico['REGIONAL'].unique())

        socioeconomico_escolha_ano = st.select_slider('Filtrar escolas por ano de Implantação:',
                                            options=dfsocioeconomico['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique(),
                                            value=dfsocioeconomico['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique().max())
        dfsocioeconomico_filtrado = dfsocioeconomico.loc[dfsocioeconomico['REGIONAL'].isin(socioeconomico_escolha_regional)].reset_index(drop=True)
        lista_selecao_ano_implantacao = []
        for item in dfsocioeconomico['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique():
            if item <= socioeconomico_escolha_ano:
                lista_selecao_ano_implantacao.append(item)
        dfsocioeconomico_filtrado = dfsocioeconomico_filtrado.loc[dfsocioeconomico_filtrado['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].isin(
            lista_selecao_ano_implantacao)].reset_index(drop=True)
        ### Fim dos Filtros ###

        selecao_aplicacao_socio = st.radio('Selecione a aplicação:', ('2019','2020'))
        df_socioeconomico_media_regional = dfsocioeconomico_filtrado.groupby(by=['REGIONAL']).mean().reset_index()

        if selecao_aplicacao_socio == '2019':

            st.subheader('Socioeconomico SAEB 2019 - Média dos valores absolutos por regional')

            infoniveis = {'Nível I': ["Até 3,00"], 'Nível II': ["3,00 a 4,00"], 'Nível III': ["4,00 a 4,50"],
                          'Nível IV': ["4,50 a 5,00"], 'Nível V': ["5,00 a 5,50"]
                , 'Nível VI': ["5,50 a 6,00"], 'Nível VII': ["6,00 a 7,00"], 'Nível VIII': ["7,00 ou mais"]}
            index_label = ["Valor Absoluto"]
            st.dataframe(pd.DataFrame(data=infoniveis, index=index_label), use_container_width= True)
            with st.expander("Ler a descrição dos Níveis socioeconômico dos estudantes", expanded=False):
                st.markdown(
                    """ 
        #### Nível I:
        Este é o nível inferior da escala, no qual os estudantes têm dois ou mais desvios-padrão
        abaixo da média nacional do Inse. Considerando a maioria dos estudantes, o pai/responsável
        não completou o 5º ano do ensino fundamental e a mãe/responsável tem o 5º ano do ensino
        fundamental incompleto ou completo. A maioria dos estudantes deste nível possui uma
        geladeira, um ou dois quartos, uma televisão e um banheiro. Mas não possui muitos dos bens
        e serviços pesquisados (i.e., computador, carro, wi-fi, mesa para estudar, garagem, microondas, aspirador de pó, 
        máquina de lavar roupa e freezer).
        #### Nível II:
        Neste nível, os estudantes estão entre um e dois desvios-padrão abaixo da média nacional do
        Inse. Considerando a maioria dos estudantes, a mãe/responsável e/ou o pai/responsável tem
        o 5º ano do ensino fundamental incompleto ou completo. A maioria possui uma geladeira, um
        ou dois quartos, uma televisão e um banheiro. Mas não possui muitos dos bens e serviços
        pesquisados, exceto uma parte dos estudantes deste nível passa a ter freezer, máquina de
        lavar roupa e três ou mais quartos para dormir em sua casa.
        #### Nível III:
        Neste nível, os estudantes estão entre meio e um desvio-padrão abaixo da média nacional
        do Inse. Considerando a maioria dos estudantes, a mãe/responsável e o pai/responsável têm
        o ensino fundamental incompleto ou completo e/ou ensino médio completo. A maioria possui
        uma geladeira, um ou dois quartos, uma televisão, um banheiro, wi-fi e máquina de lavar
        roupas, mas não possui computador, carro, garagem e aspirador de pó. Parte dos estudantes
        passa a ter também freezer e forno de micro-ondas.
        #### Nível IV:
        Neste nível, os estudantes estão até meio desvio-padrão abaixo da média nacional do Inse.
        Considerando a maioria dos estudantes, a mãe/responsável e o pai/responsável têm o ensino
        fundamental incompleto ou completo e/ou ensino médio completo. A maioria possui uma
        geladeira, um ou dois quartos, um banheiro, wi-fi, máquina de lavar roupas e freezer, mas não
        possui aspirador de pó. Parte dos estudantes deste nível passa a ter também computador,
        carro, mesa de estudos, garagem, forno de micro-ondas e uma ou duas televisões. .
        #### Nível V:
        Neste nível, os estudantes estão até meio desvio-padrão acima da média nacional do Inse.
        Considerando a maioria dos estudantes, a mãe/responsável tem o ensino médio completo
        ou ensino superior completo, o pai/responsável tem do ensino fundamental completo até o
        ensino superior completo. A maioria possui uma geladeira, um ou dois quartos, um banheiro,
        wi-fi, máquina de lavar roupas, freezer, um carro, garagem, forno de micro-ondas. Parte dos
        estudantes deste nível passa a ter também dois banheiros. .
        #### Nível VI:
        Neste nível, os estudantes estão de meio a um desvio-padrão acima da média nacional do
        Inse. Considerando a maioria dos estudantes, a mãe/responsável e/ou o pai/responsável têm
        o ensino médio completo ou o ensino superior completo. A maioria possui uma geladeira,
        dois ou três ou mais quartos, um banheiro, wi-fi, máquina de lavar roupas, freezer, um carro,
        garagem, forno de micro-ondas, mesa para estudos e aspirador de pó. Parte dos estudantes
        deste nível passa a ter também dois ou mais computadores e três ou mais televisões. 
        #### Nível VII:
        Neste nível, os estudantes estão de um a dois desvios-padrão acima da média nacional do
        Inse. Considerando a maioria dos estudantes, a mãe/responsável e/ou o pai/responsável têm
        ensino médio completo ou ensino superior completo. A maioria possui uma geladeira, três
        ou mais quartos, um banheiro, wi-fi, máquina de lavar roupas, freezer, um carro, garagem,
        forno de micro-ondas, mesa para estudos e aspirador de pó. Parte dos estudantes deste nível
        passa a ter também dois ou mais carros, três ou mais banheiros e duas ou mais geladeiras.
        #### Nível VIII:
        Este é o nível superior da escala, no qual os estudantes estão dois desvios-padrão ou mais
        acima da média nacional do Inse. Considerando a maioria dos estudantes, a mãe/responsável
        e/ou o pai/responsável têm ensino superior completo. Além de possuírem os bens dos níveis
        anteriores, a maioria dos estudantes deste nível passa a ter duas ou mais geladeiras, dois ou
        mais computadores, três ou mais televisões, três ou mais banheiros e dois ou mais carros.

                    """
                )

            fig = px.bar(df_socioeconomico_media_regional, x='REGIONAL', y='INSE_VALOR_ABSOLUTO',
                         text_auto=True).update_xaxes(categoryorder='total descending')
            fig.update_traces(marker_color='firebrick')
            fig.update_layout(yaxis_title="INSE Valor Absoluto")
            st.plotly_chart(fig)

            dfquantidade_tipo_regional = dfsocioeconomico_filtrado[['REGIONAL', 'INSE_CLASSIFICACAO']].value_counts().to_frame().reset_index(level=['REGIONAL','INSE_CLASSIFICACAO'])
            dfquantidade_tipo_regional.columns = ['REGIONAL', 'Nível', 'Quantidade']

            fig = px.bar(dfquantidade_tipo_regional, x='REGIONAL', y='Quantidade', color='Nível', text_auto=True).update_xaxes(categoryorder='total descending')
            # fig.update_traces(marker_color='firebrick')
            fig.update_layout(yaxis_title="Quantidade de escolas")
            st.plotly_chart(fig)


        if selecao_aplicacao_socio == '2020':
            st.write('Resultados ainda não disponibilizados pelo MEC')


    if menu_socioeconomico == 'Ranking das escolas':
        #### Criação de Filtros ###
        with st.expander("Filtrar por regionais"):
            socioeconomico_escolha_regional = st.multiselect('Selecione as regionais:',
                                                             dfsocioeconomico['REGIONAL'].unique(),
                                                             dfsocioeconomico['REGIONAL'].unique())

        socioeconomico_escolha_ano = st.select_slider('Filtrar escolas por ano de Implantação:',
                                                      options=dfsocioeconomico[
                                                          'ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique(),
                                                      value=dfsocioeconomico[
                                                          'ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique().max())
        dfsocioeconomico_filtrado = dfsocioeconomico.loc[
            dfsocioeconomico['REGIONAL'].isin(socioeconomico_escolha_regional)].reset_index(drop=True)
        lista_selecao_ano_implantacao = []
        for item in dfsocioeconomico['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique():
            if item <= socioeconomico_escolha_ano:
                lista_selecao_ano_implantacao.append(item)
        dfsocioeconomico_filtrado = dfsocioeconomico_filtrado.loc[
            dfsocioeconomico_filtrado['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].isin(
                lista_selecao_ano_implantacao)].reset_index(drop=True)
        ### Fim dos Filtros ###

        selecao_aplicacao_socio = st.radio('Selecione a aplicação:', ('2019', '2020'))

        if selecao_aplicacao_socio == '2019':
            ##### Função que faz o TOP 10:
            def top10(col):
                fig = px.bar(dfsocioeconomico_filtrado[[col, 'ESCOLA']].sort_values(col, ascending=False).dropna(
                    0).reset_index(drop=True).head(10), x='ESCOLA',
                             y=col, text_auto=True)
                fig.update_traces(marker_color='firebrick')
                return st.plotly_chart(fig)


            #### Função que faz os BOT10:
            def bot10(col):
                fig = px.bar(dfsocioeconomico_filtrado[[col, 'ESCOLA']].sort_values(col, ascending=True).dropna(
                    0).reset_index(drop=True).head(10), x='ESCOLA',
                             y=col, text_auto=True)
                fig.update_traces(marker_color='firebrick')
                return st.plotly_chart(fig)


            st.header('Melhores resultados')

            st.subheader('Melhores valores do Índice Socioeconomico 2019:')
            top10('INSE_VALOR_ABSOLUTO')
            st.subheader('Menores valores do Índice Socioeconomico 2019:')
            bot10('INSE_VALOR_ABSOLUTO')

    if menu_socioeconomico == 'Socioeconomico por Escola':
        escolha_escola = st.selectbox('Selecione a escola:', dfsocioeconomico['ESCOLA'].unique())
        dfsocioeconomico_filtrado = dfsocioeconomico.loc[dfsocioeconomico['ESCOLA'] == escolha_escola]

        st.title(f'{escolha_escola}')

        ####GRAFICOS####
        regional_da_escola = str(dfsocioeconomico.loc[dfsocioeconomico['ESCOLA'] == escolha_escola]['REGIONAL'].values)[2:-2]

        media_inse_regional = dfsocioeconomico.loc[dfsocioeconomico['REGIONAL'] == regional_da_escola]['INSE_VALOR_ABSOLUTO'].mean()

        fig = go.Figure()
        fig.add_trace(go.Bar(x=dfsocioeconomico_filtrado['ESCOLA'], y=dfsocioeconomico_filtrado['INSE_VALOR_ABSOLUTO'],
                             name='Valor absoluto do INSE', text=dfsocioeconomico_filtrado['INSE_VALOR_ABSOLUTO']))
        fig.update_traces(marker_color='firebrick')

        fig.add_trace(go.Bar(y=[media_inse_regional],
                             name='Média da Regional', text=[media_inse_regional]))

        st.plotly_chart(fig)

