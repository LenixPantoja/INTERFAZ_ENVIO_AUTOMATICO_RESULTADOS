import os
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import ssl
import smtplib
import logging
import xml.etree.ElementTree as ET
import socket
from tkinter import scrolledtext, messagebox

""" -------------------------------------------------------------------------------------------- """
hostname = socket.gethostname()

""" ------------------------------------------------------- """
password_application = ''
email_sender = ''
""" ------------------------------------------------------- """

config_file = 'ITOperaciones_h4.config'


tree = ET.parse(config_file)
root = tree.getroot()

app_settings = root.find('appSettings')


settings = {}
for add in app_settings.findall('add'):
    key = add.get('key')      
    value = add.get('value')  
    settings[key] = value    

for key, value in settings.items():
    if key == 'authKey':
        password_application = value
    if key == 'email':
        email_sender = value

if password_application == '':
    messagebox.showerror("Error", "No se enocontro la clave de la aplicación de gmail.")
""" -------------------------------------------------------------------------------------------- """

class Email:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        filename='Logs\Enviados.log',
                        filemode='a'
                        )

    @staticmethod
    def enviar_correo(pTextBody, pSubject, pPathFile, pEmail, pOrdenNumber):
        
        fecha_actual = datetime.now()
        
        fecha_formateada = fecha_actual.strftime("%Y%m%d")

        password = password_application
        email_receiver = pEmail
        subject = pSubject
        body = pTextBody

        
        message = MIMEMultipart()
        message["From"] = email_sender
        message["To"] = email_receiver
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        
        with open(pPathFile, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(pPathFile)}",
        )

        message.attach(part)

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(email_sender, password)
                smtp.send_message(message)
                logging.info(f"Correo enviado a: {email_receiver} - Orden: {pOrdenNumber}\n")
                print("Correo enviado con éxito.")
        except Exception as e:
            logging.error(f"Error al enviar el correo: {e} - Orden: {pOrdenNumber}")
            #messagebox.showerror("Error de envío", f"No se envió el correo.{e}.")
            print(f"Error al enviar el correo: {e}")




send = Email()
subject = 'Resultados de Laboratorio JULLY ANDREA MORA ARCINIEGAS Orden: 11130658'
body = '''
Cordial saludo.
Apreciado Usuario Adjunto a este e-mail encontrará el resultado de sus estudios en formato de Adobe Reader (pdf), pertenecientes a los laboratorios clínicos realizados en CLINIZAD.
Si tiene algún inconveniente abriendo este archivo, comuníquese a nuestro centro de contacto 7244387 Opción 0 de lunes a viernes de 7:00 am a 7:00 pm y los días sábados de 7:00 am a 2:30 pm También puede escribirnos al correo electrónico: clienteclinizad@gmail.com, donde con gusto lo https://www.facebook.com/pg/ClinizadLaboratoriodeEspecialidades/reviews/?ref=page_internal
         
Atentamente
Laboratorio de Especialidades CLINIZAD


        Si ha recibido este correo por error, por favor hacer caso omiso'''
""" 
send.enviar_correo(body, 
                   subject, 
                   r"D:\PROYECTOS_CLINIZAD\IT_ENVIO_CORREOS_HEMOGRAMAS\ITOperacione_H4\PDF_enviados\27177509.pdf", 
                   "elchamakolenixdev@gmail.com")
 """