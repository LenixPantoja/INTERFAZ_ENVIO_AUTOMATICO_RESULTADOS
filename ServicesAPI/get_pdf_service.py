import requests
import threading
import time
import os
import concurrent.futures

API_GUZMAN_BASE_URL = 'http://192.168.10.224:8010/'

class Download_Service:
    """
    API View para descargar resultados totales de órdenes y registrar logs.

    Esta API maneja la descarga de archivos PDF de órdenes desde un servicio externo,
    la obtención de órdenes específicas de una empresa y procedencia dadas, y el registro
    de eventos de descarga en un archivo de registro.

    Métodos:
    - refreshToken: Actualiza el token de autenticación cada dos minutos.
    - obtenerToken: Obtiene un nuevo token de autenticación del servicio de tokens.
    - actualizarTokenCadaDosMinutos: Hilo que actualiza el token automáticamente cada dos minutos.
    - Download_Pdf_Service: Descarga un archivo PDF para una orden específica utilizando el token actual.
    - Download_Multiple_Pdfs: Descarga múltiples archivos PDF en paralelo para una lista de órdenes.
    - Fetch_Orders_Empresas_Procedencia: Obtiene órdenes específicas de una empresa y procedencia dentro de un rango de fechas.
    - post: Procesa una solicitud POST para obtener órdenes, registrar un log y descargar archivos PDF.

    Atributos:
    - tokenView: Token de autenticación actual para el servicio externo.
    - lock: Mutex para sincronización de acceso al token.
    """

    def __init__(self):
        """
        Inicializa la instancia de la clase.
        
        Establece el token de vista como None, inicializa un bloqueo de subproceso
        para sincronización y refresca el token inicial.
        """
        self.tokenView = None
        self.lock = threading.Lock()
        self.refreshToken()

    def refreshToken(self):
        """
        Refresca el token de autenticación inicial y comienza un hilo para actualizarlo periódicamente.
        """
        self.tokenView = self.obtenerToken()
        threading.Thread(target=self.actualizarTokenCadaDosMinutos, daemon=True).start()

    def obtenerToken(self):
        """
        Obtiene un nuevo token de autenticación del servicio externo.

        Returns:
        str: Token de autenticación obtenido.
        None: Si ocurre un error al obtener el token.
        """
        url = f'{API_GUZMAN_BASE_URL}api/token'
        params = {
            'username': '',
            'password': ''
        }
        response = requests.post(url, params=params)
        if response.status_code == 200:
            data = response.json()
            tokenView = data['Token']
            return tokenView
        else:
            print(f"Error: {response.status_code}")
            return None

    def actualizarTokenCadaDosMinutos(self):
        """
        Actualiza automáticamente el token cada dos minutos mientras el programa está en ejecución.
        """
        while True:
            with self.lock:
                self.tokenView = self.obtenerToken()
            # print(f"Token actualizado: {self.tokenView}")
            time.sleep(120)

    def Download_Pdf_Service(self, pOrderId, pOrderNumber, pDocumentNumber, pPatient_name):
        """
        Descarga un archivo PDF para una orden específica utilizando el token de autenticación actual.

        Args:
        pOrderId (int): ID de la orden.
        pOrderNumber (str): Número de la orden.
        """
        print(f'Descargando PDF para el paciente: {pDocumentNumber} con Order Number: {pOrderNumber}')
        with self.lock:
            token = self.tokenView
        if not token:
            print("Token no disponible. No se puede realizar la solicitud.")
            return

        url_service_generator_pdf = f'{API_GUZMAN_BASE_URL}api/OrderData'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        # Input body in api services
        data = {"OrderNumber": pOrderId}
        # Save pdf in the folder PDFDownload.
        output_dir = os.path.join(os.getcwd(), 'PDFDownload')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        try:
            response = requests.post(url_service_generator_pdf, json=data, headers=headers)
            response.raise_for_status()
            # If the response is OK save pdf whit patient identification number and order number
            pdf_filename = os.path.join(output_dir, f'{pDocumentNumber} - {pPatient_name}{pOrderNumber}.pdf')
            with open(pdf_filename, 'wb') as pdf_file:
                pdf_file.write(response.content)
               
            print(f'PDF descargado y guardado como {pdf_filename}')
            return pdf_filename
        
        except requests.exceptions.RequestException as e:
            print(f'Error al hacer la solicitud: {e}')



                
