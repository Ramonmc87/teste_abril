import pyodbc
import pandas as pd
import streamlit as st

# Configuração da conexão com o banco de dados SQL Server
server = 'DCPRD068013'
database = 'WEGWEN_PCF4'
username = 'PCF_READ'
password = 'PCF_READ@1234'

# Função para realizar a consulta SQL e calcular as informações
def consultar_e_calcular_informacoes():
    # Configurar a string de conexão
    connection_string = f'Driver={{SQL Server}};Server={server};Database={database};UID={username};PWD={password};'

    # Estabelecer a conexão
    try:
        conn = pyodbc.connect(connection_string)
    except pyodbc.Error as e:
        st.error("Erro ao conectar ao SQL Server:", e)
        return None, None, None

    if conn:
        # Sua consulta SQL
        query = """
        SELECT 
        [wh].[Code] AS 'ORDEM',
        [wh].[DtPlanEnd] AS 'DATA FIM',
        [wd].[Code] AS 'COD. OPERAÇÃO',
        [wd].[Name] AS 'OPERAÇÃO',
        [wqe].[Status] AS 'STATUS OPERAÇÃO',
        [wqe].[DtLastStatusChange] AS 'DATA ÚLTIMA ALTERAÇÃO',
        [p].[Name] AS 'MATERIAL',
        [p].[Code] AS 'COD.MATERIAL',
        u.[Name] AS 'USUÁRIO ÚLTIMA ALTERAÇÃO',
        CASE
            WHEN CAST([wqe].[DtLastStatusChange] AS TIME) >= '05:00' AND CAST([wqe].[DtLastStatusChange] AS TIME) < '14:18' THEN '1º TURNO'
            WHEN CAST([wqe].[DtLastStatusChange] AS TIME) >= '14:18' AND CAST([wqe].[DtLastStatusChange] AS TIME) <= '23:24' THEN '2º TURNO'
            ELSE 'FORA DE TURNO'
        END AS 'TURNO'
    FROM [WEGWEN_PCF4].[dbo].[TBLWOHD] wh
    INNER JOIN [TBLWODet] wd ON wd.[IDWOHD] = wh.[IDWOHD]
    INNER JOIN [TBLWODetQtyEv] wqe ON wqe.[IDWODet] = wd.[IDWODet]
    INNER JOIN [TBLProduct] p ON p.[IDProduct] = wh.[IDProduct]
    LEFT JOIN [TBLUser] u ON u.[IDUser] = wqe.[IDUserLastStatusChange]
    WHERE 
        wd.[Code] NOT LIKE '%.11%'
        AND [wqe].[Status] = '50'
        AND [wd].[Code] = '1710'
        AND [wqe].[DtLastStatusChange] > '2023-08-17 00:00:00.000'
    ORDER BY
        [wqe].[DtLastStatusChange] ASC;
        """

        # Executar a consulta e obter os resultados em um DataFrame
        try:
            df = pd.read_sql(query, conn)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame()

        # Fechar a conexão
        conn.close()

        # Contar as ordens por turno
        turno_1 = len(df[df['TURNO'] == '1º TURNO'])
        turno_2 = len(df[df['TURNO'] == '2º TURNO'])
        total = len(df)
        
        return turno_1, turno_2, total

# Layout do aplicativo
st.title('Dashboard')

# Chamar a função para consultar e calcular as informações
turno_1, turno_2, total = consultar_e_calcular_informacoes()

if turno_1 is not None and turno_2 is not None and total is not None:
    st.write(f'1º TURNO: {turno_1}')
    st.write(f'2º TURNO: {turno_2}')
    st.write(f'TOTAL: {total}')
else:
    st.error('Erro de Con
