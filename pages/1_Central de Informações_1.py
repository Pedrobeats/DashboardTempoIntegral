#Import das bibliotecas
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

######## Variáveis #######
banner = Image.open('imagens/bannerTI2.png')


st.image(banner)



if 'df1' not in st.session_state:
    ######## Carrega e limpa os dados #######
    @st.cache
    def carregar_dados():
        df_dadosescola = pd.read_csv(
            'https://dados.es.gov.br/dataset/05f98028-92ba-45ca-9210-cb000b03c979/resource/5dd7951a-51c0-40f6-8809-14690b1b69a5/download/dadosescola.csv',
            sep=";", engine='python')
        df_dadosescola.dropna(inplace=True)
        df_dadosescola = df_dadosescola.loc[df_dadosescola['Ano'] >= 2022]
        df_dadosescola = df_dadosescola.reset_index(drop=True)
        df_dadosescola = df_dadosescola.astype({'Inep': int})
        df_dadosmatricula = pd.read_csv(
            'https://dados.es.gov.br/dataset/05f98028-92ba-45ca-9210-cb000b03c979/resource/95ee26cf-aa81-4250-8c96-540aa32d1be5/download/dadosmatricula.csv',
            sep=";", engine='python')
        df_dadosmatricula = df_dadosmatricula.loc[df_dadosmatricula['Ano'] >= 2022]
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

##### Sidebar geral #####
menu_geral = st.sidebar.radio(
    "Selecione o que deseja ver:",
    ('Informações Gerais sobre o Tempo Integral', 'Lista de Telefones/Contatos', 'Informação por Escola', 'Indicadores PAEBES', 'Indicadores SAEB', 'Indicadores PADI'))
#### Fim sidebar geral ##


#### Informações Gerais sobre o Tempo Integral ####
if menu_geral == 'Informações Gerais sobre o Tempo Integral':
    st.title('Informações Gerais sobre o Tempo Integral')
    dfbase = st.session_state['df4']
    dfmatriculas = st.session_state.df2

    with st.sidebar.expander("Filtrar por Regional(ais):"):
        escolha_regional = st.multiselect(
            'Escolha a(s) Regional(ais):',
            dfbase['REGIONAL'].unique(),default=dfbase['REGIONAL'].unique())
    dfmapa = dfbase.loc[dfbase['REGIONAL'].isin(escolha_regional)]
    with st.sidebar.expander("Filtrar por ano de Implantação:", expanded=True):
        selecao_ano_implantacao = st.select_slider('Ano de Implantação',
                                                   options=dfbase['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique(), value=dfbase['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique().max())
    lista_selecao_ano_implantacao = []
    lista_selecao_ano_implantacao.append(selecao_ano_implantacao)
    dfmapa = dfmapa.loc[dfmapa['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].isin(lista_selecao_ano_implantacao)]
    qt_implantadas = str(len(dfbase[dfbase['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'] <= selecao_ano_implantacao]))

    ###### Colunas para organizar #####
    col1, col2 = st.columns(2)
    with col1:
        qt_implantada_ano = str(len(dfmapa.loc[dfmapa['REGIONAL'].isin(escolha_regional)]))
        st.markdown(f"""
                   Até {selecao_ano_implantacao} foram implantandas {qt_implantadas} pelo Governo Estadual do Espírito Santo.
                    Apenas em {selecao_ano_implantacao} foram implantadas {qt_implantada_ano} escolas em Tempo Integral.   
                """)
        st.write(" ")
        with st.expander("Veja as escolas implantadas até {}".format(selecao_ano_implantacao)):
            for escola in dfmapa['ESCOLA']:
                lista_escolas_ate = []
                lista_escolas_ate.append(escola)
                for itemescola in lista_escolas_ate:
                    st.write(itemescola)
        st.write(" ")
        with st.expander("Veja os municípios com escolas implantadas até {}".format(selecao_ano_implantacao)):
            for mun in dfmapa['MUNICÍPIO']:
                lista_mun_ate = []
                lista_mun_ate.append(mun)
                for itemmun in lista_mun_ate:
                    st.write(itemmun)




    with col2:
        # MAPA: Cria e centraliza em São Pedro, a primeira escola
        m = folium.Map(location=[-20.2866, -40.3372], zoom_start=6)
        for index, escola in dfmapa.iterrows():
            folium.Marker(
                [escola['COORDY'].replace(",", "."), escola['COORDX'].replace(",", ".")],
                popup=escola['TELEFONE ESCOLA'], tooltip=escola['ESCOLA']
            ).add_to(m)
        # Renderiza o Mapa
        st_data = st_folium(m, width=300, height=300)
        st.caption(" (Clique no ícone da escola para ver o telefone)")
        # Fim do MAPA#

    ################# FIM DAS COLUNAS #################

    #### INICIO GRAFICOS ###

    ######## INICIO GRÁFICOS####

    # Criar DF para os gráficos #
    dfgraficos = dfbase.loc[dfbase['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'] <= selecao_ano_implantacao]
    ######## INICIO GRÁFICO QUANTIDADE DE ESCOLAS POR REGIONAL####

    st.subheader("Escolas Implantadas por Regional até {}".format(selecao_ano_implantacao))
    grafico_qt_escola_regional = px.histogram(dfgraficos, x='REGIONAL', color='REGIONAL', text_auto=True).update_xaxes(categoryorder='total descending')
    st.plotly_chart(grafico_qt_escola_regional)


    ######## INICIO GRÁFICO QUANTIDADE DE ESCOLAS POR TURNO####

    st.subheader("Escolas Implantadas por Turno até {}".format(selecao_ano_implantacao))
    grafico_qt_escola_turno = px.histogram(dfgraficos, x='TURNO(S)', color='TURNO(S)', text_auto=True).update_xaxes(categoryorder='total descending')
    st.plotly_chart(grafico_qt_escola_turno)

    ######## INICIO GRÁFICO QUANTIDADE DE MODALIDADES INTEGRAL####
    st.subheader("Escolas Implantadas por Modalidade até {}".format(selecao_ano_implantacao))
    grafico_qt_escola_modalidades = px.histogram(dfgraficos, x='MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)',
                                                 color='MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)', text_auto=True).update_xaxes(categoryorder='total descending')
    st.plotly_chart(grafico_qt_escola_modalidades)


    ######## INICIO GRÁFICO QUANTIDADE DE OFERTA DE TEMPO INTEGRAL####
    st.subheader("Escolas Implantadas por Oferta até {}".format(selecao_ano_implantacao))
    grafico_qt_escola_oferta = px.histogram(dfgraficos, x='OFERTA DE TEMPO INTEGRAL',
                                                 color='OFERTA DE TEMPO INTEGRAL', text_auto=True).update_xaxes(categoryorder='total descending')
    st.plotly_chart(grafico_qt_escola_oferta)


#### Lista de Telefones/Contatos ####
elif menu_geral == 'Lista de Telefones/Contatos':
    ###Criação e limpeza das Dataframe###
    dfbase = st.session_state['df4']
    dfcontatos = dfbase[['REGIONAL', 'MUNICÍPIO', 'ESCOLA', 'ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL', 'MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)',
                         'CARGA HORÁRIA', 'TURNO(S)', 'OFERTA DE TEMPO INTEGRAL', 'POSSUI CURSO TECNICO?', 'CURSO1', 'CURSO2', 'CURSO3', 'CURSO4',
                         'DIRETOR NOME', 'DIRETOR TEL1', 'DIRETOR TEL2', 'CP NOME', 'CP TEL', 'CASF NOME', 'CASF TEL1', 'Email Escola',
                         'ENDEREÇO', 'BAIRRO', 'CEP', 'LONG', 'LAT', 'COORDX', 'COORDY', 'TELEFONE ESCOLA', 'SUPERINTENDENTE:', 'TEL SUPERINTENTENDE',
                         'EMAIL SUPERINTENDENTE', 'ASSESSOR PEDAGÓGICO:', 'TEL SUP. PEDAG.', 'EMAIL ASS PEDAG.', 'SUPERVISOR TI', 'TEL SUPER TI', 'EMAIL SUPER TI',
                         ]]
    ###Fim Criação e limpeza das Dataframe###

    st.title('Informações Gerais sobre o Tempo Integral')
    st.subheader('Lista de Telefones/Contatos')
    # Início da opção de pesquisa #
    modo_pesquisa = st.radio("Selecione o modo de pesquisa:",
             ('Listar todas escolas de uma regional', 'Listar escolas de um município', 'Escolher a escola',))
    if modo_pesquisa == 'Listar todas escolas de uma regional':
        escolha_regional = st.multiselect(
            'Escolha a(s) Regional(ais):',
            dfcontatos['REGIONAL'].unique())
        contato_filtrado = dfcontatos.loc[dfcontatos['REGIONAL'].isin(escolha_regional)]
    elif modo_pesquisa == 'Listar escolas de um município':
        escolha_municipio = st.multiselect(
            'Escolha o(s) municipio(s):',
            dfcontatos['MUNICÍPIO'].unique())
        contato_filtrado = dfcontatos.loc[dfcontatos['MUNICÍPIO'].isin(escolha_municipio)]
    elif modo_pesquisa == 'Escolher a escola':
        escolha_escola = st.multiselect(
            'Ou escolha a escola:',
            dfcontatos['ESCOLA'].unique())
        contato_filtrado = dfcontatos.loc[dfcontatos['ESCOLA'].isin(escolha_escola)]

    #Resultado da busca#

    contatos_filtrados_renomeados = contato_filtrado.rename(columns={'DIRETOR NOME':'Nome do Diretor', 'DIRETOR TEL1':'Telefone do diretor', 'DIRETOR TEL2':'Telefone alternativo do diretor',
                                                                     'CP NOME':'Nome do Coordenador pedagógico', 'CP TEL':'Telefone do Coordenador Pedagógico','CASF NOME':'Nome do CASF',
                                                                     'CASF TEL1':'Telefone do CASF','Email Escola':'Email da escola','TELEFONE ESCOLA':'Telefone da Escola', 'SUPERINTENDENTE:':'Superintendente',
                                                                     'TEL SUPERINTENTENDE':'Telefone do Superintendente', 'EMAIL SUPERINTENDENTE':'Email do Superintendente', 'ASSESSOR PEDAGÓGICO:':'Assessor Pedagógico',
                                                                     'TEL SUP. PEDAG.':'Telefone Assessor Pedagógico','EMAIL ASS PEDAG.':'Email assessor pedagógico', 'SUPERVISOR TI':'Supervisor do Tempo Integral',
                                                                     'TEL SUPER TI':'Telefone do Supervisor do Tempo Integral', 'EMAIL SUPER TI':'Email do Supervisor do Tempo Integral'}                                                            )
    for escola in contatos_filtrados_renomeados['ESCOLA'].values:
        st.header('Escola:')
        st.subheader(escola)
        with st.expander("Ver as informações da escola"):
            for col in ['Nome do Diretor', 'Telefone do diretor', 'Telefone alternativo do diretor', 'Nome do Coordenador pedagógico', 'Telefone do Coordenador Pedagógico',
                        'Nome do CASF', 'Telefone do CASF', 'Email da escola','Telefone da Escola', 'Superintendente', 'Telefone do Superintendente',
                             'Email do Superintendente', 'Assessor Pedagógico', 'Telefone Assessor Pedagógico', 'Email assessor pedagógico', 'Supervisor do Tempo Integral', 'Telefone do Supervisor do Tempo Integral', 'Email do Supervisor do Tempo Integral',
                             ]:
                st.subheader(col)
                st.write(contatos_filtrados_renomeados.loc[contatos_filtrados_renomeados['ESCOLA'].str.contains(escola, na=False)][col].to_string()[3:])
    #Fim do resultado da Busca#

#### Informação por Escola ####
elif menu_geral == 'Informação por Escola':
    st.title('Informação por Escola')
    dfbase = st.session_state['df4']
    dfmatriculas = st.session_state.df2


    escolha_escola = st.sidebar.selectbox(
        'Escolha a escola',
        dfbase['ESCOLA'].unique()
    )


#### Indicadores PAEBES ####
elif menu_geral == 'Indicadores PAEBES':
    st.title('Indicadores PAEBES')
    ## Selecionando/Filtrando Dataframe da PAD##

    dfpaebes = st.session_state.df4[['CÓD. INEP', 'REGIONAL', 'MUNICÍPIO', 'ESCOLA',
                                     'ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL',
                                     'MODALIDADES INTEGRAL (Propedeutica/Técnica/Mista)', 'CARGA HORÁRIA', 'TURNO(S)',
                                     'OFERTA DE TEMPO INTEGRAL', 'POSSUI CURSO TECNICO?', 'PROF PAEBES EF MAT 2019',
                                     'PROF PAEBES EF MAT 2021', 'PROF PAEBES EF LP 2019 ', 'PROF PAEBES EF LP 2021 ',
                                     'PROF PAEBES EF CN 2019', 'PROF PAEBES EF CN 2021', 'PROF PAEBES EM MAT 2019',
                                     'PROF PAEBES EM MAT 2021', 'PROF PAEBES EM LP 2019', 'PROF PAEBES EM LP 2021',
                                     'PROF PAEBES EM BIO 2019', 'PROF PAEBES EM BIO 2021', 'PROF PAEBES EM QUI 2019',
                                     'PROF PAEBES EM QUI 2021', 'PROF PAEBES EM FIS 2019', 'PROF PAEBES EM FIS 2021',
                                     'Média total PAEBES EF 2019', 'Média total EM PAEBES 2019',
                                     'Média total PAEBES EF 2021', 'Média total PAEBES EM 2021']]

    menu_paebes = st.sidebar.radio("Tipo de relatório:",
             ('Visão Geral do PAEBES do Tempo Integral', 'PAEBES por Escola'))
    if menu_paebes == 'Visão Geral do PAEBES do Tempo Integral':
        st.header('Média do PAEBES')

        #### Criação de Filtros ###
        with st.sidebar.expander("Filtrar por regionais"):
            paebes_escolha_regional = st.multiselect('Selecione as regionais:',
    dfpaebes['REGIONAL'].unique(), dfpaebes['REGIONAL'].unique())

        paebes_escolha_ano = st.sidebar.select_slider('Ano de Implantação:',
    options=dfpaebes['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique(), value=dfpaebes['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique().max())
        dfpaebes_filtrado = dfpaebes.loc[dfpaebes['REGIONAL'].isin(paebes_escolha_regional)].reset_index(drop=True)
        lista_selecao_ano_implantacao = []
        for item in dfpaebes['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].unique():
            if item <= paebes_escolha_ano:
                lista_selecao_ano_implantacao.append(item)
        dfpaebes_filtrado = dfpaebes_filtrado.loc[dfpaebes_filtrado['ANO DE IMPLEMENTAÇÃO DO TEMPO INTEGRAL'].isin(
            lista_selecao_ano_implantacao)].reset_index(drop=True)


        ### Fim dos Filtros ###

        ## Criação da DF de resultados do PAEBES por REGIONAL ##
        df_paebes_media_regional = dfpaebes_filtrado.groupby(by=['REGIONAL']).mean().reset_index()
        st.dataframe(df_paebes_media_regional.columns)


        st.subheader('PAEBES 2019 Ensino Médio - Média geral por regional')
        fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='Média total EM PAEBES 2019', color='REGIONAL', text_auto=True).update_xaxes(categoryorder='total descending')
        st.plotly_chart(fig)

        st.subheader('PAEBES 2019 Ensino Fundamental - Média geral por regional')
        fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='Média total PAEBES EF 2019', color='REGIONAL',
                     text_auto=True).update_xaxes(categoryorder='total descending')
        st.plotly_chart(fig)

        st.subheader('PAEBES 2021 Ensino Médio - Média geral por regional')
        fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='Média total PAEBES EM 2021', color='REGIONAL',
                     text_auto=True).update_xaxes(categoryorder='total descending')
        st.plotly_chart(fig)

        st.subheader('PAEBES 2021 Ensino Fundamental - Média geral por regional')
        fig = px.bar(df_paebes_media_regional, x='REGIONAL', y='Média total PAEBES EF 2021', color='REGIONAL',
                     text_auto=True).update_xaxes(categoryorder='total descending')
        st.plotly_chart(fig)




#### Indicadores SAEB ####
elif menu_geral == 'Indicadores SAEB':
    st.title('Indicadores SAEB')

#### Indicadores PADI ####
elif menu_geral == 'Indicadores PADI':
    st.title('Indicadores PADI')

