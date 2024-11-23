from Middle.midd import MyQuery as query
from ServicesAPI import get_pdf_service as API
from emailSMTP import sp_send_email as email_smtp
from datetime import datetime

class Operation:

    
    
    @staticmethod
    def get_List_Orders_to_Send(pPageNumber, pStartDate, pEndDate):
        try:
            list_orders = query.listen_orders(pPageNumber, pStartDate, pEndDate)
            list_orders_to_send = []
            for myOrder in list_orders:
                is_valid = query.pruebas_orden_H4(myOrder['NUMERO_ORDEN'])
                if len(is_valid) != 0:
                    list_orders_to_send.append({
                        "ID_ORDEN": myOrder['ID_ORDEN'],
                        "NUMERO_ORDEN": myOrder['NUMERO_ORDEN'],
                        "DOCUMENTO_PACIENTE": myOrder['DOCUMENTO_PACIENTE'],
                        "NOMBRE_PACIENTE": myOrder['NOMBRE_PACIENTE'],
                        "CORREO_PACIENTE": myOrder['CORREO_PACIENTE']
                    })
                
            return list_orders_to_send
        except Exception as e:
            print(f"Error en la operación [ Order to send ]: {e}")

    @staticmethod
    def Send_email(pStartDate, pEndDate):
        
        fecha_actual = datetime.now()  
        fecha_formateada = fecha_actual.strftime("%Y-%m-%d %I:%M:%S %p")  
        flag_paginate = 1
    
        while True:
            has_order = Operation.get_List_Orders_to_Send(flag_paginate, pStartDate, pEndDate)
            order_for_view = ''
            date_for_view = ''
            mail_for_view = ''
            
            if len(has_order) > 0:
                #print(f'lista {has_order}')
                # pOrderId, pOrderNumber, pDocumentNumber, pPatient_name)
                download_instance = API.Download_Service()
                
                print(has_order)
                flag_paginate += 1
                
            else:
                break

# Operation.Send_email('2024-11-18', '2024-11-18')
# Operation.get_List_Orders_to_Send(2, )




