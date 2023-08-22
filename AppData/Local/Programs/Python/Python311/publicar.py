i
mport streamlit as st
import pyodbc

# Configurar a conexão com o banco de dados SQL Server
server = 'DCPRD068013'
database = 'WEGWEN_PCF4'
username = 'PCF_READ'
password = 'PCF_READ@1234'
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# Criar uma conexão com o banco de dados
connection = pyodbc.connect(connection_string)

# Criar um cursor para executar consultas SQL
cursor = connection.cursor()

# Executar uma consulta SQL
cursor.execute("""
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
            WHEN CAST([wqe].[DtLastStatusChange] AS TIME) >= '05:00' AND CAST([wqe].[DtLastStatusChange] AS TIME) < '14:18' THEN '1º turno'
            WHEN CAST([wqe].[DtLastStatusChange] AS TIME) >= '14:18' AND CAST([wqe].[DtLastStatusChange] AS TIME) <= '23:24' THEN '2º turno'
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
        """)

result = cursor.fetchall()

# Fechar o cursor e a conexão quando terminar
cursor.close()
connection.close()

# Contar o total de ordens, ordens do 1º turno e ordens do 2º turno
total_ordens = len(result)
total_ordens_turno_1 = sum(1 for row in result if row[-1] == '1º turno')
total_ordens_turno_2 = sum(1 for row in result if row[-1] == '2º turno')

# Usar o Streamlit para exibir os resultados
st.write("Total de Ordens:")
st.write(f"Total Geral: {total_ordens}")
st.write(f"Total 1º turno: {total_ordens_turno_1}")
st.write(f"Total 2º turno: {total_ordens_turno_2}")








