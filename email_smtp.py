# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 08:00:00 2022

@author: Jhonatan Martínez
"""

import inspect
import smtplib
from email.message import EmailMessage
from answer import Answer
import main_functions as mf


class EmailSMTP:
    """
    Permite la conexión y envío de email por SMTP,
    los datos de configuración están en el archivo JSON llamado **config.json**.\n
    Para su funcionamiento importa los siguientes paquetes y clases:\n
    * **inspect:** Para obtener información de la función actual.\n
    * **smtplib:** Para conectar al servidor SMTP.\n
    * **EmailMessage:** Dónde se configura el email.\n
    * **Answer:** Dónde se envían el estado, mensaje y datos desde una función.\n
    * **main_functions:** Funciones principales para el funcionamiento del aplicativo.

    """

    def __init__(self):
        """
        Los datos están en la sección EMAIL en el archivo JSON los cuales son:\n
        * **SMTP:** Servidor del SMTP.\n
        * **PORT:** Puerto del servidor SMTP.\n
        * **FROM:** Correo desde el que se va a enviar el email.\n
        * **PASSWORD:** Clave del correo desde que se va a enviar el email.\n
        * **TO:** Correo(s) a los que se va a enviar el email.\n
        * **SUBJECT:** Asunto que va a tener el email.\n
        """
        self.__this = self.__class__.__name__
        self.__data = self._read_setup()
        self.__email = EmailMessage()
        self.__connection = None

    def _close_connection(self):
        """
        Esta función cierra la conexión al servidor SMTP.

        """

        # process variable
        process = inspect.stack()[0][3]
        try:
            # Validate status of connection
            if self.__connection is not None:
                # Close connection.
                self.__connection.quit()
        except (ConnectionError, Exception) as exc:
            # Show error message in console.
            self._print_error(process=process,
                              message=exc)

    def _get_connection(self):
        """
        Realiza y establece la conexión al servidor SMTP.\n
        Los datos son leídos desde la función '_read_setup()', desde la sección EMAIL del JSON,
        Estos datos se obtienen y agregan en el constructor de la clase.

        Returns:
            **Status (Bool):** Devuelve un estado de la función.

        """

        # status variable
        status = True
        # process variable
        process = inspect.stack()[0][3]
        try:
            # Set smtp server and port.
            self.__connection = smtplib.SMTP(self.__data["SERVER"], self.__data["PORT"])
            if self.__data["PASSWORD"] != "":
                # Identify this cliente to the SMTP server.
                self.__connection.ehlo()
                # Secure the SMTP connection.
                self.__connection.starttls()
                # Identify this cliente to the SMTP server.
                self.__connection.ehlo()
                # Login to email account.
                self.__connection.login(self.__data["FROM"], self.__data["PASSWORD"])
        except (ConnectionError, Exception) as exc:
            # Show error message in console.
            self._print_error(process=process,
                              message=exc)
            status = False
        # Return status.
        return status

    def _print_error(self, process, message):
        """
        Muestra por consola cuando existe un error en una función de la clase.

        Params:
            * **process (Str):** Nombre de la función actual. \n
            * **message (Str):** Mensaje de error a mostrar. \n

        Returns:
            **show (Str):** Mensaje completo clase, función y error.

                """
        # show variable
        show = self.__this + "-" + process + ': ' + str(message)
        # Show in console
        print(show)
        # return show
        return show

    def _read_setup(self):
        """
        Llama al método 'read_setup()' desde 'main_functions', para leer y obtener los datos desde archivo JSON.

        Returns:
            **data (Dict):** Diccionario con los datos de configuración.

        """
        # process variable
        process = inspect.stack()[0][3]
        # data variable
        data = None
        try:
            # Read CONNECTION configuration from JSON file.
            config = mf.read_setup(item=self.__this.upper())
            if config.get_status():
                # Assign values
                data = config.get_data()
        except Exception as exc:
            # Show error message in console.
            self._print_error(process=process,
                              message=exc)
        # Return data.
        return data

    def send_email(self, body, html=False):
        """
        Configura y permite enviar un correo electrónico.

        Params:
            * **body (String):** Contiene la descripción o cuerpo del email.\n
            * **html (Boolean, optional):** Email con cuerpo HTML en True. False por defecto.

        Returns:
            **Answer (Class):** Devuelve un estado y, mensaje de la función.
        """

        # process variable
        process = inspect.stack()[0][3]
        # Invoke class Answer.
        answer = Answer()
        try:
            # Connect to the SMTP server.
            if self._get_connection():
                email = EmailMessage()
                # Add content to the email and with type html.
                if html:
                    email.set_content(body, 'html')
                else:
                    email.set_content(body)
                # Send message by email.
                email["subject"] = self.__data["SUBJECT"]
                email["From"] = self.__data["FROM"]
                email["To"] = self.__data["TO"]
                self.__connection.send_message(email)
                # Fill answer object with status and message.
                answer.load(status=True,
                            message='Email sent to: ' + self.__data["TO"])
            else:
                answer.load(status=False,
                            message="connection not established to SMTP")
        except (ConnectionError, Exception) as exc:
            # Fill answer object with status and error message.
            answer.load(status=False,
                        message=self._print_error(process=process,
                                                  message=exc))
        finally:
            # Close connection
            self._close_connection()
        # Return answer object.
        return answer
