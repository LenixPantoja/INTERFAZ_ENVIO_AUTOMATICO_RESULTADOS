import xml.etree.ElementTree as ET
import socket
import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkinter import simpledialog
from tkcalendar import Calendar  
import os
import json
from datetime import datetime
import base64
from ServicesAPI import get_pdf_service as API

import Operations
from emailSMTP import sp_send_email as email_smtp

hostname = socket.gethostname()

""" ------------------------------------------------------- """
license_application = ''
hostname_computer = ''
flutter = ""
""" ------------------------------------------------------- """



config_file_xml = 'ITOperaciones_h4.config'


tree = ET.parse(config_file_xml)
root = tree.getroot()

app_settings = root.find('appSettings')

settings = {}
for add in app_settings.findall('add'):
    key = add.get('key')      
    value = add.get('value')  
    settings[key] = value     

for key, value in settings.items():
    if key == 'machine':
        hostname_computer = value
    if key == 'licence':
        license_application = value




# print(hostname_computer)
# print(license_application)
# print(flutter)
"""  ----------------------------------------------------------------------------------------------------- """    
import threading
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkcalendar import Calendar
import json
import os
import sys  # Importamos sys para cerrar el programa

# Variables globales para manejar el hilo y su estado


class InterfazApp:
    def __init__(self, root):
        self.root = root
        self.worker_thread = None
        self.stop_thread = False
        self.log = None
        self.icon_base64 = ""
        self.root.title("Interfaz envío resultados - H4")
        self.root.geometry("600x300")
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

        self.crear_menu()
        self.crear_interfaz()
        
        self.load_config()

        # Configura el icono después de cargar la configuración
        self.set_icon()
        
    def load_config(self):
        config_file = 'config.xml'
        print(config_file)# Ruta del archivo de configuración XML
        if os.path.isfile(config_file):
            tree = ET.parse(config_file)
            root = tree.getroot()
                
            self.icon_base64 = root.find('icon_base64').text
                #messagebox.showinfo("Cargar Configuración", "Configuración cargada automáticamente desde config.xml.")
            """  try:
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar la configuración: {e}") """
        else:
            messagebox.showwarning("Archivo de Configuración No Encontrado", "No se encontró el archivo config.xml. Asegúrate de que exista en el directorio de la aplicación.")

    def set_icon(self):
        if self.icon_base64:
            try:
                # Decodifica la cadena Base64 a bytes y establece el icono
                icon_data = base64.b64decode(self.icon_base64)
                icon_image = tk.PhotoImage(data=icon_data)
                self.root.iconphoto(True, icon_image)
            except Exception as e:
                messagebox.showerror("Error", f"Error al establecer el icono: {e}")
        
    def crear_interfaz(self):
        frame_botones = tk.Frame(self.root)
        frame_botones.pack(pady=10)

        self.btn_conectar = tk.Button(frame_botones, text="Conectar", command=self.conectar)
        self.btn_conectar.pack(side=tk.LEFT, padx=10)

        self.btn_desconectar = tk.Button(frame_botones, text="Desconectar", command=self.desconectar, state=tk.DISABLED)
        self.btn_desconectar.pack(side=tk.LEFT, padx=10)

        self.log = scrolledtext.ScrolledText(self.root, width=70, height=10, wrap=tk.WORD)
        self.log.pack(pady=10)

    def conectar(self):
        if self.worker_thread and self.worker_thread.is_alive():
            self.log.insert(tk.END, "Ya hay un proceso en ejecución.\n")
            self.log.see(tk.END)
            return

        self.btn_conectar.config(state=tk.DISABLED)
        self.btn_desconectar.config(state=tk.NORMAL)
        self.log.insert(tk.END, "Conectado...\n")
        self.log.see(tk.END)

        self.stop_thread = False

        self.worker_thread = threading.Thread(target=self.proceso_conectar, daemon=True)
        self.worker_thread.start()

    def proceso_conectar(self):
        fecha_actual = datetime.now()
        fecha_formateada = fecha_actual.strftime("%Y-%m-%d %I:%M:%S %p")

        start_date, end_date = self.cargar_rango()

        flag_paginate = 1
        while not self.stop_thread:
            # Aquí se asume la lógica de la clase `Operations` y sus métodos.
            OP = Operations.Operation()
            has_order = OP.get_List_Orders_to_Send(flag_paginate, start_date, end_date)

            if not has_order:
                break

            for order in has_order:
                if self.stop_thread:
                    return

                correo = email_smtp.Email()
                download_instance = API.Download_Service()
                path_pdf = download_instance.Download_Pdf_Service(
                    order["ID_ORDEN"],
                    order["NUMERO_ORDEN"],
                    order["DOCUMENTO_PACIENTE"],
                    order["NOMBRE_PACIENTE"],
                )

                subjet = f'Resultados de Laboratorio {order["NOMBRE_PACIENTE"]} Orden: {order["NUMERO_ORDEN"]}'
                body = '''
                        <html>
                            <body>
                                <p>Cordial saludo.</p>

                                <p>Adjunto a este e-mail encontrará el resultado de sus estudios en formato de Adobe Reader (PDF), pertenecientes a los laboratorios clínicos realizados en CLINIZAD.</p>
                                <p>Si tiene algún inconveniente abriendo este archivo, comuníquese a nuestro centro de contacto <b>7244387 Opción 0</b> de lunes a viernes de 7:00 am a 7:00 pm y los días sábados de 7:00 am a 2:30 pm. También puede escribirnos al correo electrónico: <b>clienteclinizad@gmail.com, donde con gusto lo ayudaremos.</p>
                                
                                <p><b>Atentamente</b></p> <br/>
                                <b><b>Laboratorio de Especialidades CLINIZAD</b></p>
                                        
                                <p><b>Si ha recibido este correo por error, por favor hacer caso omiso.</b></p>
                            </body>
                        </html>
                '''
                correo.enviar_correo(body, subjet, path_pdf, order["CORREO_PACIENTE"], order["NUMERO_ORDEN"])
                self.root.after(0, self.actualizar_log, fecha_formateada, order["CORREO_PACIENTE"], order["NUMERO_ORDEN"])

            flag_paginate += 1

        self.root.after(0, self.finalizar_conexion)

    def actualizar_log(self, fecha, correo, orden):
        if '@' in correo:
            self.log.insert(tk.END, f"{fecha} correo enviado a: {correo} - Orden número: {orden}\n")
        else:
            self.log.insert(tk.END, f"{fecha} error al enviar el correo a: {correo} - Orden número: {orden}\n")
        self.log.see(tk.END)

    def desconectar(self):
        self.stop_thread = True

        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2)

        self.cerrar_completamente()

    def cerrar_ventana(self):
        self.desconectar()

    def cerrar_completamente(self):
        self.root.destroy()
        sys.exit(0)

    def finalizar_conexion(self):
        self.btn_conectar.config(state=tk.NORMAL)
        self.btn_desconectar.config(state=tk.DISABLED)
        self.log.insert(tk.END, "Proceso finalizado.\n")
        self.log.see(tk.END)

    def guardar_rango(self, fecha_inicio, fecha_fin):
        data = {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
        with open("rango_fechas.json", "w") as f:
            json.dump(data, f)

    def cargar_rango(self):
        if os.path.exists("rango_fechas.json"):
            with open("rango_fechas.json", "r") as f:
                data = json.load(f)
                return data.get("fecha_inicio", ""), data.get("fecha_fin", "")
        return "", ""

    def seleccionar_fecha(self, cuadro_texto):
        def fecha_seleccionada():
            fecha = calendario.get_date()
            cuadro_texto.delete(0, tk.END)
            cuadro_texto.insert(0, fecha)
            ventana_calendario.destroy()

        ventana_calendario = tk.Toplevel(self.root)
        ventana_calendario.title("Seleccionar Fecha")
        ventana_calendario.geometry("250x250")

        calendario = Calendar(ventana_calendario, date_pattern="yyyy-mm-dd")
        calendario.pack(pady=20)

        tk.Button(ventana_calendario, text="Seleccionar", command=fecha_seleccionada).pack(pady=10)

    def definir_rango(self):
        if self.btn_conectar.cget("state") == tk.DISABLED:
            messagebox.showerror("Error", "Debe desconectar la interfaz antes de modificar los rangos.")
            return

        def guardar():
            fecha_inicio = entry_inicio.get()
            fecha_fin = entry_fin.get()
            self.guardar_rango(fecha_inicio, fecha_fin)
            messagebox.showinfo("Éxito", "Rango guardado correctamente")
            ventana_rango.destroy()

        ventana_rango = tk.Toplevel(self.root)
        ventana_rango.title("Definir Rango de Fechas")
        ventana_rango.geometry("350x250")

        tk.Label(ventana_rango, text="Fecha Inicio:").pack(pady=5)
        entry_inicio = tk.Entry(ventana_rango, width=20)
        entry_inicio.pack(pady=5)
        tk.Button(ventana_rango, text="Seleccionar Fecha Inicio", command=lambda: self.seleccionar_fecha(entry_inicio)).pack(pady=5)

        tk.Label(ventana_rango, text="Fecha Fin:").pack(pady=5)
        entry_fin = tk.Entry(ventana_rango, width=20)
        entry_fin.pack(pady=5)
        tk.Button(ventana_rango, text="Seleccionar Fecha Fin", command=lambda: self.seleccionar_fecha(entry_fin)).pack(pady=5)

        fecha_inicio, fecha_fin = self.cargar_rango()
        entry_inicio.insert(0, fecha_inicio)
        entry_fin.insert(0, fecha_fin)

        tk.Button(ventana_rango, text="Guardar", command=guardar).pack(pady=10)

    def crear_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        config_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Parámetros", menu=config_menu)
        config_menu.add_command(label="Definir Rango", command=self.definir_rango)

if __name__ == "__main__":
    if hostname == hostname_computer:
        root = tk.Tk()
        app = InterfazApp(root)
        root.mainloop()
    else:
        messagebox.showerror("Error", "Interfaz NO licenciada.")