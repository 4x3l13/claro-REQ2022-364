# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 17:00:00 2022

@author: Jhonatan Martínez
"""

import inspect
import main_functions as mf
from answer import Answer
from connection import Connection
from email_smtp import EmailSMTP
from work_flow import WorkFlow


class Req2022364:
    """
    Esta es la clase principal de la aplicación, trabaja en BackEnd, no posee FrontEnd.\n
    En el archivo de configuración **config.json** están las diferentes secciones
    para las configuraciones de conexiones.\n
    ¿Qué realiza la aplicación?:\n
    * Conectar a una Base de Datos y consultar el o los sectores en la tabla TISON
    que estén en estado mantenimiento a través de un procedimiento almacenado.\n
    * Si encuentra datos envía una petición a una URL por cada registro
    para que se le actualice el estado a modo normal.\n
    * Envía un email notificando la operación realizada o error en su defecto.\n
    * Guarda un log localmente.
    """

    def __init__(self):
        self.__this = self.__class__.__name__
        self.__data = self._read_setup()
        self._print_error(process="init", message=self.__data)
        self._load()

    def _load(self):
        """
        This method has all the logic of the program.
        """
        # Create Log folders if they don't exist.'
        folder = self._create_folder()
        # Validate folder creation status
        if folder.get_status():
            # Write on the Log file.
            self._write_log_file(message="Application has been launched")
            self._write_log_file(message=folder.get_message())
            # Start function to connect to DB and get data
            data = self._get_data()
            # Start function to get request from workflow
            request = self._get_request(data=data)
            # Start function to send email
            self._send_email(data=data, request=request)
            # Write on the Log file.
            self._write_log_file(message="Application has been finished")

    def _create_folder(self):
        """
        Llama la función 'create_folder()' desde 'main_functions' y le envía el nombre de la carpeta
        la cual será creada en la raíz del aplicativo.

        Returns:
            **answer (Class):** Devuelve un estado y mensaje de la función.

        """

        # process variable
        process = inspect.stack()[0][3]
        # Invoke class Answer.
        answer = Answer()
        try:
            # Folder names to create.
            folders = ["Log"]
            # Start loop on folders
            for folder in folders:
                # Create folder.
                mf.create_folder(folder_name=folder)
            # Fill answer object with status, message and data.
            answer.load(status=True,
                        message="Folders are Ok")
        except Exception as exc:
            # Fill answer object with status and error message.
            answer.load(status=False,
                        message=self._print_error(process=process,
                                                  message=exc))
        # Return answer object.
        return answer

    def _get_body(self, data, request):
        """
        Esta función crea un string tipo HTML para enviar en el cuerpo de un email.

        Params:
            **data (list):** Los datos obtenidos de la DB.
            **request (list):** Repuesta del workflow.

        Returns
            **html (String):** Devuelve el cuerpo en HTML para el email.

        """

        # process variable
        process = inspect.stack()[0][3]
        # Write on the Log file.
        self._write_log_file(message="Building html body")
        html = """
                <html>
                    <head>
                    </head>
                    <body>
                        A continuación se adjunta lo realizado por la tarea:
                        <br/>
            """
        try:
            # First part of the HTML document.
            html += """
                        <table border=1>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>SECTOR</th>
                                    <th>MENSAJE</th>
                                </tr>
                            </thead>
                            <tbody>
                    """
            # Loop the data rows
            for index, item in enumerate(data):
                html += "<tr>"
                html += "<td>" + str(item["TISONID"]) + "</td>"
                html += "<td>" + str(item["SECTOR"]) + "</td>"
                html += "<td>" + str(request[index]) + "</td>"
                html += "</tr>"
            # Final part of the HTML document.
            html += """
                            </tbody>
                        </table>
                    """
        except Exception as exc:
            # Show error message in console.
            self._print_error(process=process,
                              message=exc)
        finally:
            html += """
                    </body>
                </html>
            """
        # Return answer object.
        return html

    def _get_data(self):
        """
        Obtiene la data desde la base de datos.

        Returns
            **queries (List):** Devuelve una lista con diccionarios por fila encontrada.

        """
        # Variable process
        process = inspect.stack()[0][3]
        # Invoke class Connection.
        connection = Connection()
        # Write on the Log file.
        self._write_log_file(message="Start process " + process)
        # queries variable
        queries = None
        try:
            # Validate setup status
            if self.__data["CONNECTION"] == 1:
                # Execute query
                data = connection.read_data(query=self.__data["QUERY"])
                # Validate status data
                if data.get_status():
                    # Write on the Log file.
                    self._write_log_file(data.get_message() + " from " + self.__data["QUERY"])
                    # Get data
                    queries = data.get_data()
                else:
                    # Write on the Log file.
                    self._write_log_file(data.get_message())
                    # Send email
                    self._send_email(data=data.get_message(), request=None)
            else:
                # Write on the Log file.
                self._write_log_file(message="CONNECTION in SETUP is not enabled")
        except Exception as exc:
            # Show error message in console
            self._write_log_file(message=self.__this + process + ': ' + str(exc))
        finally:
            # Write on the Log file.
            self._write_log_file(message="End process " + process)
        # Return queries list.
        return queries

    def _get_request(self, data):
        """
        Realiza la petición al endpoint (workflow) y obtiene su respuesta.

        Returns
            **responses (List):** Devuelve una lista con los mensajes retornados del endpoint.

        """

        # Variable process
        process = inspect.stack()[0][3]
        # Write on the Log file.
        self._write_log_file(message="Start process " + process)
        # Invoke class WorkFlow.
        workflow = WorkFlow()
        # responses variable
        responses = []
        try:
            # Validate setup status
            if self.__data["WORKFLOW"] == 1:
                # Loop on data dictionary
                for item in data:
                    # Fill text variable
                    text = workflow.get_response(item).get_message()
                    # Fill responses list to return
                    responses.append(text)
                    # Write on the Log file.
                    self._write_log_file(message="ID: " + str(item["TISONID"]) + " - " + text)
            else:
                # Write on the Log file.
                self._write_log_file(message="WORKFLOW in SETUP is not enabled")
        except Exception as exc:
            # Show error message in console
            self._write_log_file(message=self.__this + process + ': ' + str(exc))
        finally:
            # Write on the Log file.
            self._write_log_file(message="End process " + process)
        # Return responses list.
        return responses

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

    def _send_email(self, data, request):
        """
        Llama la función 'send_email' de la clase 'EmailSMTP' para enviar un correo electrónico.

        Params:
            **body (String):** Cuerpo del correo electrónico.

        """

        # Variable process
        process = inspect.stack()[0][3]
        # Write on the Log file.
        self._write_log_file(message="Start process " + process)
        # Invoke class EmailSMTP.
        email = EmailSMTP()
        try:
            # Validate setup status
            if self.__data["EMAIL"] == 1:
                # body variable
                body = ""
                # Validate data in request param
                if request is not None:
                    # Get body
                    body = self._get_body(data=data, request=request)
                else:
                    # Get body
                    body = data
                # Send email and Write on the Log file.
                self._write_log_file(message=email.send_email(body=body, html=True).get_message())
            else:
                # Write on the Log file.
                self._write_log_file(message="EMAIL in SETUP is not enabled")
        except Exception as exc:
            # Write on the Log file.
            self._write_log_file(message=self.__this + process + ': ' + str(exc))
        finally:
            # Write on the Log file.
            self._write_log_file(message="End process " + process)

    def _write_log_file(self, message):
        """
        Llama a 'write_file_text()' desde 'main_functions' y guarda el texto en el archivo plano.

        Params:
            **message (String):** Dato a copiar en el archivo plano.
        """

        # Variable final_message.
        final_message = '[' + mf.get_current_time().get_data() + ']: ' + message + '.'
        # Write on the Log file.
        mf.write_file_text(file_name='Log/Log' + mf.get_current_date().get_data(),
                           message=final_message + '\n')
        # Show message in console.
        print(final_message)


if __name__ == '__main__':
    main = Req2022364()
