# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 08:30:00 2022

@author: Jhonatan Martínez
"""

import inspect
import cx_Oracle
import pyodbc
import mysql.connector
from answer import Answer
import main_functions as mf


class Connection:
    """
    Permite la conexión y la obtención de datos desde una Base de Datos (SQL, MYSQL, ORACLE).
    Los datos de conexión están en el archivo JSON llamado **config.json**.\n
    Para su funcionamiento importa los siguientes paquetes y clases:\n
    * **inspect:** Para obtener información de la función actual.\n
    * **cx_Oracle:** Para conectar a una Base de Datos ORACLE.\n
    * **pyodbc:** Para conectar a una Base de Datos SQL.\n
    * **mysql.connector:** Para conectar a una Base de Datos MYSQL.\n
    * **Answer:** Dónde se envían el estado, mensaje y datos desde una función.\n
    * **main_functions:** Funciones principales para el funcionamiento del aplicativo.

    """

    def __init__(self):
        """
        Los datos están en la sección CONNECTION en el archivo JSON los cuales son:\n
        * **DB_TYPE:** Tipo de base de datos, se permiten a (SQL, MYSQL, ORACLE).\n
        * **DB_DRIVER:** Driver de conexión de ser necesario.\n
        * **DB_SERVER:** IP o nombre del servidor que aloja la Base de Datos.\n
        * **DB_NAME:** Nombre de la Base de Datos a la que se va a conectar.\n
        * **DB_USER:** Usuario para conectar de la Base de Datos.\n
        * **DB_PASSWORD:** Clave para conectar de la Base de Datos.\n
        """

        self.__this = self.__class__.__name__
        self.__data = self._read_setup()
        self.__connection = None

    def _close_connection(self):
        """
        Cierra la conexión a la Base de Datos.

        """
        # process variable
        process = inspect.stack()[0][3]
        try:
            # Validate status of connection
            if self.__connection is not None:
                # Close connection.
                self.__connection.close()
        except (ConnectionError, Exception) as exc:
            # Show error message in console.
            self._print_error(process=process,
                              message=exc)

    def _get_connection(self):
        """
        Realiza y establece la conexión a la Base de Datos.\n
        Los datos son leídos desde la función '_read_setup()',
        Estos datos se obtienen y agregan en el constructor de la clase.

        Returns:
            **Status (Bool):** Devuelve un estado de la función.

        """
        # status variable
        status = True
        # process variable
        process = inspect.stack()[0][3]
        try:
            # Choose the type of connection.
            match self.__data["TYPE"]:
                case 'SQL':
                    connection_string = 'DRIVER={' + self.__data["DRIVER"] + '};'
                    connection_string += 'SERVER=' + self.__data["SERVER"] + ';'
                    connection_string += 'DATABASE=' + self.__data["DATABASE"] + ';'
                    connection_string += 'UID=' + self.__data["USER"] + ';'
                    connection_string += 'PWD=' + self.__data["PASSWORD"]
                    self.__connection = pyodbc.connect(connection_string)
                case 'MYSQL':
                    self.__connection = mysql.connector.connect(
                        host=self.__data["SERVER"],
                        user=self.__data["USER"],
                        passwd=self.__data["PASSWORD"],
                        db=self.__data["DATABASE"])
                case 'ORACLE':
                    dsn = self.__data["SERVER"] + '/' + self.__data["DATABASE"]
                    self.__connection = cx_Oracle.connect(user=self.__data["USER"],
                                                          password=self.__data["PASSWORD"],
                                                          dsn=dsn,
                                                          encoding="UTF-8")
        except (cx_Oracle.Error, ConnectionError, Exception) as exc:
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

    def read_data(self, query, datatype="dict"):
        """
        Permite ejecutar una consulta en la base de datos y devuelve los datos encontrados.

        Params:
            * **query (String):** Recibe un select o un procedimiento almacenado. \n
            * **datatype (String, optional):** Identifica que tipo de dato a retornar. \n
            \t* **dict:** diccionario, por defecto. \n
            \t* **list:** lista con las columnas y otra con los valores.

        Returns:
            **answer (Class):** Devuelve estado, mensaje y datos (diccionario, lista) de la función.

        """

        # process variable
        process = inspect.stack()[0][3]
        # Invoke class Answer.
        answer = Answer()
        try:
            # Open connection
            if self._get_connection():
                # Create cursor object.
                cursor = self.__connection.cursor()
                cursor.prefetchrows = 10000
                cursor.arraysize = 10000
                # Execute query
                cursor.execute(query)
                # Gets data
                data = cursor.fetchall()
                # Gets column_names
                columns = [column[0].upper() for column in cursor.description]
                # Validate the datatype to return
                if datatype == 'dict':
                    dictionary = []
                    for item in data:
                        dictionary.append(dict(zip(columns, item)))
                    # Fill answer object with status, message and data list.
                    answer.load(status=True,
                                message='Data obtained',
                                data=dictionary)
                elif datatype == 'list':
                    # Fill answer object with status, message and data list.
                    answer.load(status=True,
                                message='Data obtained',
                                data=[columns, data])
                # Close cursor
                cursor.close()
            else:
                answer.load(status=False,
                            message="connection not established")
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
                if data["TYPE"] == "ORACLE" and data["DRIVER"] != "":
                    libraries = mf.get_current_path().get_data() + data["DRIVER"]
                    cx_Oracle.init_oracle_client(lib_dir=libraries)
        except Exception as exc:
            # Show error message in console.
            self._print_error(process=process,
                              message=exc)
        # Return data.
        return data

    def execute_query(self, query):
        """
        Permite ejecutar una consulta en la base de datos.

        Params:
            * **query (String):** Recibe un insert, update, delete o un procedimiento almacenado. \n

        Returns:
            **answer (Class):** Devuelve estado y mensaje de la función.

        """

        # process variable
        process = inspect.stack()[0][3]
        # Invoke class Answer.
        answer = Answer()
        try:
            # Open connection
            if self._get_connection():
                # Create cursor object.
                cursor = self.__connection.cursor()
                # Execute the query.
                cursor.execute(query)
                # Confirm action
                self.__connection.commit()
                # Fill answer object with status, message and data list.
                answer.load(status=True,
                            message='Query executed')
            else:
                answer.load(status=False,
                            message="connection not established to DB")
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
