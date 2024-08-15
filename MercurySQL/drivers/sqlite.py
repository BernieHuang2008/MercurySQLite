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
    version = "0.1.0"
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
            def count(table_name: str, condition: str) -> str:
                return f"SELECT COUNT(*) FROM {table_name} WHERE {condition}"

            @staticmethod
            def query(
                table_name: str,
                selection: str,
                condition: str,
                db,
                limit: tuple[int] | None = None,
            ) -> str:
                # No limit, return all
                if limit is None:
                    return f"SELECT {selection} FROM {table_name} WHERE {condition}"

                # Limit result
                # parse negative index.
                limit = list(limit)
                res_count = -1
                for i in range(len(limit)):
                    if limit[i] < 0:
                        if res_count == -1:
                            res_count = Driver_SQLite.APIs.count_res(
                                db, table_name, condition
                            )
                        limit[i] = res_count + limit[i] + 1

                # turn into SQL-LIMIT format
                offset, n = limit[0], limit[1] - limit[0]

                return f"SELECT {selection} FROM {table_name} WHERE {condition} LIMIT {offset}, {n}"

            @staticmethod
            def delete(table_name: str, condition: str) -> str:
                return f"DELETE FROM {table_name} WHERE {condition}"

        @classmethod
        def get_all_tables(cls, db) -> List[str]:
            cursor = db.do(cls.gensql.get_all_tables())
            return list(map(lambda x: x[0], cursor.fetchall()))

        @classmethod
        def get_all_columns(cls, db, table_name: str) -> List[str]:
            cursor = db.do(cls.gensql.get_all_columns(table_name))
            return list(map(lambda x: [x[1], x[2]], cursor.fetchall()))
        
        @classmethod
        def count_res(cls, db, table_name: str, condition: str) -> int:
            cursor = db.do(cls.gensql.count(table_name, condition))
            return cursor.fetchall()[0][0]  # use 'fetchall' to avoid circular call.

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
