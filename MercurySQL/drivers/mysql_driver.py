"""
Requirements: 
  - mysql-connector-python
"""
from .base import BaseDriver

import mysql.connector
from typing import Any, List


class Driver_MySQL(BaseDriver):
    pass


class Driver_MySQL(BaseDriver):
    """
    .. note::
        Supported MySQL Version: **8.2**
    """
    dependencies = ['mysql-connector-python']
    version = '0.1.0'
    payload = '%s'

    Conn = mysql.connector.MySQLConnection
    Cursor = mysql.connector.cursor_cext.CMySQLCursor

    class APIs:
        class gensql:
            @staticmethod
            def drop_table(table_name: str) -> str:
                return f"DROP TABLE {table_name};"

            @staticmethod
            def get_all_tables() -> str:
                return "SHOW TABLES;"

            @staticmethod
            def get_all_columns(table_name: str) -> str:
                return f"DESCRIBE `{table_name}`;"

            @staticmethod
            def create_table_if_not_exists(table_name: str, column_name: str, column_type: str, primaryKey=False, autoIncrement=False, engine='', charset='') -> str:
                return f"""
                    CREATE TABLE IF NOT EXISTS `{table_name}` (
                        `{column_name}` {column_type} {'PRIMARY KEY' if primaryKey else ''} {'AUTO_INCREMENT' if autoIncrement else ''}
                    ) {engine} {f'DEFAULT CHARSET={charset}' if charset else ''};
                """

            @staticmethod
            def add_column(table_name: str, column_name: str, column_type: str) -> str:
                return f"ALTER TABLE `{table_name}` ADD COLUMN `{column_name}` {column_type};"

            @staticmethod
            def drop_column(table_name: str, column_name: str) -> str:
                return f"ALTER TABLE `{table_name}` DROP COLUMN `{column_name}`;"

            @staticmethod
            def set_primary_key(table, keyname: str, keytype: str) -> list:
                return [
                    f"ALTER TABLE `{table.table_name}` DROP PRIMARY KEY;",
                    f"ALTER TABLE `{table.table_name}` ADD PRIMARY KEY (`{keyname}`);"
                ]

            @staticmethod
            def insert(table_name: str, columns: str, values: str) -> str:
                return f"INSERT INTO `{table_name}` ({columns}) VALUES ({values});"
            
            @staticmethod
            def insert_or_update(table_name: str, columns: str, values: str) -> str:
                update_columns = ', '.join(f'{col}=VALUES({col})' for col in columns.split(', '))
                return f"INSERT INTO `{table_name}` ({columns}) VALUES ({values}) ON DUPLICATE KEY UPDATE {update_columns};"

            @staticmethod
            def update(table_name: str, columns: str, condition: str) -> str:
                return f"UPDATE `{table_name}` SET {columns} WHERE {condition};"

            @staticmethod
            def query(table_name: str, selection: str, condition: str) -> str:
                return f"SELECT {selection} FROM `{table_name}` WHERE {condition};"

            @staticmethod
            def delete(table_name: str, condition: str) -> str:
                return f"DELETE FROM `{table_name}` WHERE {condition};"

        @classmethod
        def get_all_tables(cls, conn) -> List[str]:
            cursor = conn.cursor()
            cursor.execute(cls.gensql.get_all_tables())
            return list(map(lambda x: x[0], cursor.fetchall()))

        @classmethod
        def get_all_columns(cls, conn, table_name: str) -> List[str]:
            cursor = conn.cursor()
            cursor.execute(cls.gensql.get_all_columns(table_name))
            # [name, type, null, key, default, extra]
            return list(map(lambda x: [x[0], x[1], x[2], x[3], x[4], x[5]], cursor.fetchall()))

    class TypeParser:
        """
        Parse the type from `Python Type` -> `MySQL Type`.
        """

        @staticmethod
        def parse(type_: Any) -> str:
            """
            Compile the type to MySQL type.

            :param type_: The type to parse.
            :type type_: Any

            :return: The MySQL type.
            :rtype: str

            +-------------------+-------------+
            | Supported Types   | SQLite Type |
            +===================+=============+
            | bool              | BOOLEAN     |
            +-------------------+-------------+
            | int               | INTEGER     |
            +-------------------+-------------+
            | float             | FLOAT       |
            +-------------------+-------------+
            | str               | VARCHAR(225)|
            +-------------------+-------------+
            | bytes             | BLOB        |
            +-------------------+-------------+
            | datetime.datetime | DATETIME    |
            +-------------------+-------------+
            | datetime.date     | DATE        |
            +-------------------+-------------+
            | datetime.time     | TIME        |
            +-------------------+-------------+
            

            Example Usage:

            .. code-block:: python

                TypeParser.parse(int(10))      # INT DEFAULT 10
                TypeParser.parse(str)          # VARCHAR
                TypeParser.parse(float(1.3))   # FLOAT DEFAULT 1.3
                TypeParser.parse('\t DOUBLE DEFAULT 1.23')    # DOUBLE DEFAULT 1.23
                ...

            """
            import datetime

            supported_types = {
                bool: 'BOOLEAN',
                int: 'INT',
                float: 'FLOAT',
                str: 'VARCHAR(225)',
                bytes: 'BLOB',

                datetime.datetime: 'DATETIME',
                datetime.date: 'DATE',
                datetime.time: 'TIME',
            }

            if not isinstance(type_, tuple):
                type_ = (type_,)

            res = ""

            # round 1: Built-in Types
            if type_[0] in supported_types:
                res = supported_types[type_[0]]

            # round 2: Custom Types
            if res == "" and isinstance(type_[0], str) and type_[0].startswith('\t'):    # custom type
                return type_[0].strip()
            
            # round 3: Built-in Types With Default Value
            if type(type_[0]) != type:
                if isinstance(type_[0], bytes):
                    type_[0] = type_[0].decode()
                res = f"{supported_types[type(type_[0])]} DEFAULT {type_[0]}"

            # round 4: Not Null
            for i in range(1, len(type_)):
                if type_[i] == 'not null':
                    res += ' NOT NULL'
                else:
                    res += f" DFAULT {type_[i]}"

            # Not Supported
            if res == "":
                raise TypeError(f"Type `{str(type_)}` is not supported.")
            
            return res

    @staticmethod
    def connect(db_name: str, host: str, user: str, password: str = '', force=False) -> Conn:
        """
        Connect to a MySQL database.
        """
        if force:
            return mysql.connector.connect(
                host=host,
                user=user,
                passwd=password,
                database=db_name
            )
        else:
            conn = mysql.connector.connect(
                host=host,
                user=user,
                passwd=password
            )
            conn.backup_cursor = conn.cursor

            def cursor():
                """ Create Database if not exists. """
                conn.cursor = conn.backup_cursor

                c = conn.cursor()

                try:
                    c.execute(f'USE {db_name};')
                except mysql.connector.errors.ProgrammingError:
                    c.execute(f'CREATE DATABASE {db_name};')
                    c.execute(f'USE {db_name};')

                return c

            conn.cursor = cursor
            return conn
