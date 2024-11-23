from dotenv import load_dotenv
import pyodbc
from tkinter import scrolledtext, messagebox
import os

# Load environment variables
load_dotenv()

# Define environment variables
SERVER = ""
USER = ""
PASSWORD = ""
DATABASE = ""

# SERVER = os.getenv('DB_SERVER')
# USER = os.getenv('DB_USER')
# PASSWORD = os.getenv('DB_PASSWORD')
# DATABASE = os.getenv('DB_DATABASE')

class connect:
    def Conexion():
        try:
            conexion = pyodbc.connect(
                'DRIVER={ODBC Driver 18 for SQL Server};'
                'SERVER=' + SERVER +
                ';DATABASE=' + DATABASE +
                ';UID=' + USER +
                ';PWD=' + PASSWORD +
                ';TrustServerCertificate=YES;'
            )
            return conexion

        except Exception as e:
            messagebox.showerror("Error", f"{e}")

class MyQuery:
    
    def listen_orders(pPageNumber, pStartDate, pEndDate):
        conexion = connect.Conexion()
        cursor = conexion.cursor()
        cursor.execute(f'''
                        	SELECT DISTINCT 
                                o_id AS 'ID_ORDEN',
                                    o_numero AS 'NUMERO_ORDEN',
                                    h_numero AS 'DOCUMENTO_PACIENTE',
                                    h_nombres AS 'NOMBRE_PACIENTE',
                                    LTRIM(
                                        RTRIM(
                                            ISNULL(h_apellido1, '') + 
                                            CASE 
                                                WHEN h_apellido1 IS NOT NULL AND h_apellido2 IS NOT NULL THEN ' ' 
                                                ELSE '' 
                                            END + 
                                            ISNULL(h_apellido2, '')
                                        )
                                    ) AS 'APELLIDOS_PACIENTE',
                                    h_mail AS 'CORREO_PACIENTE',
                                    em_id AS 'ID_EMPRESA',
                                    o_estado_Orden AS 'ESTADO_ORDEN'
                                    
                                FROM [LabCore].dbo.Ordenes
                                
                                    inner join [LabCore].dbo.Laboratorios on l_ord_id=o_id
                                    inner join [LabCore].dbo.Estudios on l_est_id=e_id
                                    inner join [LabCore].dbo.pruebas on p_id = l_pru_id
                                    inner join [LabCore].dbo.Historias on o_his_id=h_id
                                    inner join [LabCore].dbo.Empresas on o_emp_id = em_id

                                WHERE e_id = 95 AND 
                                        o_estado_Orden >= 4 AND 
                                        o_fecha >= '{pStartDate} 00:00:00.000' AND 
                                        o_fecha <= '{pEndDate} 23:59:00.000'    
                ''')
            
        order_list = [{
                        "ID_ORDEN": row.ID_ORDEN,
                        "NUMERO_ORDEN": row.NUMERO_ORDEN,
                        "DOCUMENTO_PACIENTE": row.DOCUMENTO_PACIENTE,
                        "NOMBRE_PACIENTE":str(row.NOMBRE_PACIENTE) + str(row.APELLIDOS_PACIENTE),
                        "CORREO_PACIENTE":row.CORREO_PACIENTE,
                        "ESTADO_ORDEN":row.ESTADO_ORDEN
                        }for row in cursor.fetchall()]
        return order_list
    
    def pruebas_orden_H4(pNumberOrder):
        conexion = connect.Conexion()
        cursor = conexion.cursor()
        cursor.execute(f'''
                            SELECT 
                                o_numero,
								e_id,
                                e_nombre,
                                l_estado
                                
                            FROM LabsOrdenHistoPrueba_View
                            
                            WHERE 
                                o_numero = '{pNumberOrder}' AND
                                e_id = 95
                ''')
            
        order_list = [{
                        "ORDEN_NUMERO": row.o_numero,
                        "ESTUDIO_ID": row.e_id,
                        "ESTUDIO_NOMBRE":row.e_nombre,
                        "PRUEBA_ESTADO":row.l_estado
                        }for row in cursor.fetchall()]
        return order_list
query = MyQuery
# print(query.pruebas_estado_orden('09270011'))
# print(query.listen_orders(2,'2024-11-18','2024-11-18'))
#print(query.pruebas_orden_H4('01230561'))