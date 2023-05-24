    #Import das bibliotecas
    import streamlit as st
    import pandas as pd
    from PIL import Image

    ######## Variáveis #######
    banner = Image.open('imagens/bannerTI2.png')
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

st.sidebar.success("Selecione um relatório acima.")

st.markdown(
    """
    # Painel do Tempo Integral

    Esta é a base de informações do Tempo Integral com os dados de 2023. O intuito deste webapp é 
    **reunir e consolidar**
    todas as informações necessárias para consulta e análise das escolas em Tempo Integral de 2023, que hoje se 
    encontram em diversos locais diferentes.
    
    """)


st.markdown(
    """
#### Informações Gerais sobre o Tempo Integral:

Informações resumidas e gráficos gerado a respeito da oferta de Tempo Integral no Espírito Santo, de acordo com a 
regional e/ou ano de Implantação.

Todas informações e gráficos são gerados automaticamente com o cruzamento de dados entre a [bases de dados abertos 
do Espírito Santo](https://dados.es.gov.br/), (utilizando resultados filtrados da API) e a base de dados interna 
do Tempo Integral.

##### Lista de telefone/contatos:
Lista de telefone e contatos das escolas em Tempo Integral implantadas.

Os telefones das escolas são gerados automaticamente da API da [bases de dados abertos 
do Espírito Santo](https://dados.es.gov.br/). Os telefones celulares foram retirados da base de dados interna do 
Tempo Integral.

##### Informação por escola:
Informações detalhadas por escola.



""")

st.markdown(
    """
    #### Matrículas:

    Esta categoria possui dados diretamente coletados da API de dados da [base de dados abertos 
    do Espírito Santo](https://dados.es.gov.br/) e todos os gráficos e dados são atualizados automaticamente, através do
    cruzamento de dados com outra base de informações do portal.

    ##### Relatório Geral de Matrículas do Tempo Integral:
    Todas as matrículas das escolas em Tempo Integral filtradas e detalhadas por Município, Escola, Serie, Turno ou
    Tipo de Ensino.

    ##### Soma das Matrículas:

    Faz a soma de matriculas de Tempo Integral por Escola ou por Série, com o resultado da soma para ser exportado em 
    facilmente durante a produção de gráficos ou relatórios do Tempo Integral.

    """
)

st.markdown("""
#### Painel de Indicadores:
##### Indicadores PAEBES:
Informações a respeito dos resultados do [PAEBES (Programa de Avaliação da Educação Básica do Espírito Santo 
(Paebes)](https://avaliacaoemonitoramentoespiritosanto.caeddigital.net/),
das escolas em Tempo Integral. Resultados extraídos da base do PAEBES e filtrado apenas com as escolas de Tempo 
Integral.

##### Indicadores SAEB:

Resultado dos indicadores do SAEB das escolas em tempo Integral. Dados abertos disponíveis em 
[na base do MEC](https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/saeb/resultados).

##### Indicadores PADI:

Resultado dos indicadores da PADI  (Pesquisa de Acompanhamento e Desenvolvimento do Integral - antigo checklist) 
das escolas em tempo Integral. A PADI é realizada em parceria com o 
[Instituto Sonho Grande](https://www.sonhogrande.org/l/pt) e é um instrumento que reflete o semestre anterior para 
que a gestão paute a construção do Plano de Ação em ações focadas.

Dados gerados através do envio da Base de Dados do Instituto Sonho Grande a Assessoria de Tempo Integral.

##### Indicadores Socio-Econônomicos:

O Indicador de Nível Socioeconômico (Inse), construído pela Diretoria de Avaliação da
Educação Básica (Daeb), com base nos resultados do questionário do estudante do Saeb 2019,
tem como objetivo contextualizar resultados obtidos em avaliações e exames aplicados por este
instituto no âmbito da educação básica. Dessa forma, possibilita-se conhecer a realidade social
de escolas e redes de ensino, bem como auxiliar na implementação, no monitoramento e na
avaliação de políticas públicas, visando ao aumento da qualidade e da equidade educacional. 
 
Base de dados disponível em [Instituto Sonho Grande](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/nivel-socioeconomico).



        Webapp criado via Python/Streamlit por Pedro Moreno Barbosa Sant'Anna

"""
)


