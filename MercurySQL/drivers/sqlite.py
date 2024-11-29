"""
Requirements: 
  - sqlite3
"""

from .base import BaseDriver

import sqlite3
from typing import Any, List


class Driver_SQLite(BaseDriver):
    pass


class Driver_SQLite(BaseDriver):
    dependencies = ["sqlite3"]
    version = "0.1.1"
    payload = "?"

    Conn = sqlite3.Connection
    Cursor = sqlite3.Cursor

    class APIs:
        class gensql:
            @staticmethod
            def drop_table(table_name: str) -> str:
                return f"DROP TABLE {table_name}"

            @staticmethod
            def get_all_tables() -> str:
                return "SELECT name FROM sqlite_master WHERE type='table';"

            @staticmethod
            def get_all_columns(table_name: str) -> str:
                return f"PRAGMA table_info({table_name});"

            @staticmethod
            def create_table_if_not_exists(
                table_name: str,
                column_name: str,
                column_type: str,
                primaryKey=False,
                autoIncrement=False,
            ) -> str:
                return f"""
                    CREATE TABLE IF NOT EXISTS {table_name} ({column_name} {column_type} {'PRIMARY KEY' if primaryKey else ''} {'AUTOINCREMENT' if autoIncrement else ''})
                """

            @staticmethod
            def add_column(table_name: str, column_name: str, column_type: str) -> str:
                return f"""
                    ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}
                """

            @staticmethod
            def drop_column(table_name: str, column_name: str) -> str:
                return f"""
                    ALTER TABLE {table_name} DROP COLUMN {column_name}
                """

            @staticmethod
            def set_primary_key(table, keyname: str, keytype: str) -> list:
                return [
                    f"CREATE TABLE ___temp_table ({keyname} {keytype} PRIMARY KEY, {', '.join([f'{name} {type_}' for name, type_ in table.columnsType.items() if name != keyname])})",
                    f"INSERT INTO ___temp_table SELECT * FROM {table.table_name}",
                    f"DROP TABLE {table.table_name}",
                    f"ALTER TABLE ___temp_table RENAME TO {table.table_name}",
                ]

            @staticmethod
            def insert(table_name: str, columns: str, values: str) -> str:
                return f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

            @staticmethod
            def insert_or_update(table_name: str, columns: str, values: str) -> str:
                return (
                    f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({values})"
                )

            @staticmethod
            def update(table_name: str, columns: str, condition: str) -> str:
                return f"UPDATE {table_name} SET {columns} WHERE {condition}"

            @staticmethod
            def query(table_name: str, selection: str, condition: str) -> str:
                return f"SELECT {selection} FROM {table_name} WHERE {condition}"

            @staticmethod
            def delete(table_name: str, condition: str) -> str:
                return f"DELETE FROM {table_name} WHERE {condition}"

        @classmethod
        def get_all_tables(cls, db) -> List[str]:
            cursor = db.do(cls.gensql.get_all_tables())
            res = list(map(lambda x: x[0], cursor.fetchall()))
            res = list(map(cls.reformat_table_name, res))
            return res

        @classmethod
        def get_all_columns(cls, db, table_name: str) -> List[str]:
            cursor = db.do(cls.gensql.get_all_columns(table_name))
            res = list(map(lambda x: [x[1], x[2]], cursor.fetchall()))
            res = list(map(lambda x: (cls.reformat_column_name(x[0]), x[1]), res))
            return res

        @staticmethod
        def reformat_table_name(table_name: str) -> str:
            """
            Rules:
            - Lowercase
            - Replace all non-alphanumeric characters with '_'
            - Not starts with digits
            """
            # Rule 1: Lowercase
            res = table_name.lower()

            # Rule 2: Replace all non-alphanumeric characters with '_'
            for c in table_name:
                if c not in "abcdefghijklmnopqrstuvwxyz0123456789_":
                    res = res.replace(c, '_')

            # Rule 3: Not starts with digits
            if c[0] in "0123456789":
                res = "_" + res
        
            return res
        
        @staticmethod
        def reformat_column_name(column_name: str) -> str:
            """
            Rules:
            - Lowercase
            - Replace all non-alphanumeric characters with '_'
            - Not starts with digits
            """
            res = column_name.lower()

            for c in column_name:
                if c not in "abcdefghijklmnopqrstuvwxyz0123456789_":
                    res = res.replace(c, '_')

            if res[0] in "0123456789":
                res = "_" + res
        
            return res


    class TypeParser:
        """
        Parse the type from `Python Type` -> `SQL Type`.
        """

        @staticmethod
        def parse(type_: Any) -> str:
            """
            Compile the type to SQLite type.

            :param type_: The type to parse.
            :type type_: Any

            :return: The SQLite type.
            :rtype: str

            +-----------------+-------------+
            | Supported Types | SQLite Type |
            +=================+=============+
            | str             | TEXT        |
            +-----------------+-------------+
            | int             | INTEGER     |
            +-----------------+-------------+
            | float           | REAL        |
            +-----------------+-------------+
            | bool            | BOOLEAN     |
            +-----------------+-------------+
            | bytes           | BLOB        |
            +-----------------+-------------+

            Example Usage:

            .. code-block:: python

                TypeParser.parse(str)       # TEXT
                TypeParser.parse(int)       # INTEGER
                TypeParser.parse(float)     # REAL
                ...

            """
            supported_types = {
                str: "TEXT",
                int: "INTEGER",
                float: "REAL",
                bool: "BOOLEAN",
                bytes: "BLOB",
            }

            # round 1: Built-in Types
            if type_ in supported_types:
                return supported_types[type_]

            # round 2: 'Not Null' Types
            """ 
            === !!! Not Supported By SQLite !!! ===

            for t in supported_types:
                if isinstance(type_, t):
                    if type_ == t(not None):
                        return supported_types[t] + ' NOT NULL'
            """

            # round 3: Custom Types
            if isinstance(type_, str):  # custom type
                return type_

            # Not Supported
            raise TypeError(f"Type `{str(type_)}` not supported.")

    @staticmethod
    def connect(db_name: str, **kwargs) -> Driver_SQLite.Conn:
        return sqlite3.connect(db_name, **kwargs)
