#Import das bibliotecas
import streamlit as st
import pandas as pd
from PIL import Image

######## Variáveis #######
banner = Image.open('imagens/bannerTI2.png')

####### Interface #######

st.set_page_config(
    page_title="Base Tempo Integral 2023",
    page_icon="👋", layout="wide"
)

st.image(banner)

######## Carrega e limpa os dados #######
@st.cache(allow_output_mutation=True)
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
st.dataframe(st.session_state.df2)

st.dataframe(df1)
st.dataframe(df2)
st.dataframe(df3)
st.dataframe(df4)

st.sidebar.success("Selecione um relatório acima.")

st.markdown(
    """
    Lero lero lero
"""
)
