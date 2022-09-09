# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 08:30:00 2022

@author: Jhonatan Martínez
"""

import inspect
import requests
import main_functions as mf
from answer import Answer


class WorkFlow:
    """
    Permite la conexión a un endpoint por medio del paquete requests
    """

    def __init__(self):
        """
        Los datos están en la sección WORKFLOW en el archivo JSON los cuales son:\n
        * **URL:** URL a realizar el request.\n
        * **PARAMETERS:** Diccionario con los parámetros para no enviarlos por la URL.\n
        * **VERIFY:** Si usa SSL y se va a necesitar certificado.\n
        * **CERT:** Ruta dónde se almacena el certificado para la conexión a la URL.\n
        * **HEADERS:** Diccionario con los headers necesarios para la conexión a la URL.\n
        """

        self.__this = self.__class__.__name__
        self.__data = self._read_setup()

    def get_response(self, params=None):
        """
        Hace un llamado a la URL especificada en el config.json y devuelve un response

        Returns:
            **answer (Class):** Devuelve un estado, mensaje y data (response) de la función.

        """

        # Invoke class Answer.
        answer = Answer()
        # process variable
        process = inspect.stack()[0][3]
        # path variable
        path = mf.get_current_path().get_data()
        try:
            # Validate parameters
            if self.__data["PARAMETERS"] != "":
                # Organize parameters
                params = self._organize_parameters(params=params)
            else:
                # Set none in params
                params = None
            # Execute request
            response = requests.get(url=self.__data["URL"],
                                    params=params,
                                    headers=self.__data["HEADERS"] if self.__data["HEADERS"] != "" else None,
                                    verify=bool(self.__data["VERIFY"]),
                                    cert=path + self.__data["CERT"] if self.__data["CERT"] != "" else None)
            # Fill answer object with status, message and data.
            answer.load(status=True,
                        message="status:" + str(response.status_code) + " - " + response.text,
                        data=response)
        except Exception as exc:
            # Fill answer object with status and error message.
            answer.load(status=False,
                        message=self._print_error(process=process,
                                                  message=exc))
        # Return answer
        return answer

    def _organize_parameters(self, params):
        """
        Organiza los parámetros de una consulta conforme a los datos descritos en el config.json

        Params:
            **params (Dict):** Diccionario de datos. \n

        Returns:
            **organized_parameters (Dict):** Devuelve diccionario organizado.

        """

        # organized parameters variable
        organized_parameters = {}
        # process variable
        process = inspect.stack()[0][3]
        try:
            # loop on parameters
            for item in self.__data["PARAMETERS"]:
                organized_parameters[str(item).lower()] = str(params[str(item).upper()]).replace("%", "$")
        except Exception as exc:
            # Show error message in console.
            self._print_error(process=process,
                              message=exc)
        return organized_parameters

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
