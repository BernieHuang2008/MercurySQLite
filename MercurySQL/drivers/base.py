from typing import List, Union, Any


class BaseDriver:
    class Cursor:
        pass

    class Conn:
        pass

    class APIs:
        pass


class BaseDriver:
    """
    The base class of all drivers.
    """
    dependencies = []   # just for hints about what dependencies are needed
    version = '0.0.0'
    payload = '?'

    class Cursor:
        """
        .. note::
            The `Cursor` class here is only used for type hints, indicating the return type or parameter type of functions. In practice, instances of the `Cursor` class are not directly created or called.

        A cursor object for database operations.
        Usually, SQL libraries will provide these methods for executing SQL queries and interacting with databases.
        E.g., `sqlite3.Cursor <https://docs.python.org/3/library/sqlite3.html#cursor-objects>`_ or `pymysql.cursors.Cursor <https://pymysql.readthedocs.io/en/latest/modules/cursors.html>`_.
        """

        def execute(self, sql: str, paras: List[tuple] = []) -> BaseDriver.Cursor:
            """
            This method is used to execute SQL queries.

            :param sql: The SQL query to be executed.
            :param paras: The parameters of the SQL query.
            :return: The cursor object itself.
            """
            pass

        def fetchone(self) -> tuple:
            """
            This method is used to fetch the next row of the query result.

            :return: The next row of the query result.
            """
            pass

        def fetchall(self) -> List[tuple]:
            """
            This method is used to fetch all rows of the query result.

            :return: All rows of the query result.
            """
            pass

    class Conn:
        """
        .. note::
            The `Conn` class here is only used for type hints, indicating the return type or parameter type of functions. In practice, instances of the `Cursor` class are not directly created or called.

        A Connection object for database operations.

        Also, a SQL library will provide these methods for interacting with databases.
        E.g., `sqlite3.Connection <https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection>`_ or `pymysql.connections.Connection <https://pymysql.readthedocs.io/en/latest/modules/connections.html>`_.
        """

        def cursor(self) -> BaseDriver.Cursor:
            """
            This method is used to create a cursor object for database operations.

            :return: A cursor object for database operations.
            """
            pass

        def commit(self) -> None:
            """
            This method is used to commit (it means 'save') the changes to the database.
            """
            pass

        def close(self) -> None:
            """
            This method is used to close the connection to the database.
            """
            pass

    class APIs:
        """
        APIs is a class that provides SQL statements for database operations.

        .. warning::
            You must implement all the methods in this class.

        Every definition will be followed by an example of it's return value (in SQLite).
        """
        class gensql:
            """
            APIs in this class will return a SQL code for database operations.
            Generally, these returned codes will be executed **DIRECTLY**.
            """
            @staticmethod
            def drop_table(table_name: str) -> str:
                """
                Drop (Delete) a table.

                :param table_name: The name of the table to be dropped.
                :type table_name: str
                :return: The SQL statement to drop the table.

                Example Implementation (SQLite):

                .. code-block:: python

                    return f"DROP TABLE {table_name}"

                """
                pass
                # return f"DROP TABLE {table_name}"

            @staticmethod
            def get_all_tables() -> str:
                """
                Get all table's informations in the database.

                :return: The SQL statement to get all table's informations in the database.

                Example Implementation (SQLite):

                .. code-block:: python

                    return "SELECT name FROM sqlite_master WHERE type='table';"
                """
                pass
                # return "SELECT name FROM sqlite_master WHERE type='table';"

            @staticmethod
            def get_all_columns(table_name: str) -> str:
                """
                Get all column's informations in the table.

                :param table_name: The name of the table.
                :type table_name: str

                Example Implementation (SQLite):

                .. code-block:: python

                    return f"PRAGMA table_info({table_name});"

                """
                pass
                # return f"PRAGMA table_info({table_name});"

            @staticmethod
            def create_table_if_not_exists(table_name: str, column_name: str, column_type: str, primaryKey=False, autoIncrement=False) -> Union[str, List[str]]:
                """
                Create a table if it does not exist.

                :param table_name: The name of the table to be created.
                :type table_name: str
                :param column_name: The name of the column to be created.
                :type column_name: str
                :param column_type: The type of the column to be created.
                :type column_type: str

                Example Implementation (SQLite):

                .. code-block:: python

                    return f\"\"\"
                        CREATE TABLE IF NOT EXISTS {table_name} ({column_name} {column_type} {'PRIMARY KEY' if primaryKey else ''})
                    \"\"\"

                """

                pass
                # return f"""
                #     CREATE TABLE IF NOT EXISTS {table_name} ({column_name} {column_type} {'PRIMARY KEY' if primaryKey else ''})
                # """

            @staticmethod
            def add_column(table_name: str, column_name: str, column_type: str) -> Union[str, List[str]]:
                """
                Add a column to a table.

                :param table_name: The name of the table to be added.
                :type table_name: str
                :param column_name: The name of the column to be added.
                :type column_name: str
                :param column_type: The type of the column to be added (has been parsed by TypeParser).
                :type column_type: str

                Example Implementation (SQLite):

                .. code-block:: python

                    return f\"\"\"
                        ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}
                    \"\"\"

                """
                pass
                # return f"""
                #     ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}
                # """

            @staticmethod
            def drop_column(table_name: str, column_name: str) -> Union[str, List[str]]:
                """
                Drop (Delete) a column from a table.

                :param table_name: The name of the target table.
                :type table_name: str
                :param column_name: The name of the column to be dropped.
                :type column_name: str

                Example Implementation (SQLite):

                .. code-block:: python

                    return f\"\"\"
                        ALTER TABLE {table_name} DROP COLUMN {column_name}
                    \"\"\"

                """
                pass
                # return f"""
                #     ALTER TABLE {table_name} DROP COLUMN {column_name}
                # """

            @staticmethod
            def set_primary_key(table, keyname: str, keytype: str) -> Union[str, List[str]]:
                """
                Set a primary key for the specified table.

                :param table: The table to be set.
                :type table: Table
                :param keyname: The name of the primary key.
                :type keyname: str
                :param keytype: The type of the primary key.
                :type keytype: str

                Example Implementation (SQLite):

                .. code-block:: python

                    return [
                        f"CREATE TABLE new_table ({keyname} {keytype} PRIMARY KEY, {', '.join([f'{name} {type_}' for name, type_ in table.columns.items() if name != keyname])})",
                        f"INSERT INTO new_table SELECT * FROM {table.table_name}",
                        f"DROP TABLE {table.table_name}",
                        f"ALTER TABLE new_table RENAME TO {table.table_name}"
                    ]

                """
                pass
                # return [
                #     f"CREATE TABLE new_table ({keyname} {keytype} PRIMARY KEY, {', '.join([f'{name} {type_}' for name, type_ in table.columns.items() if name != keyname])})",
                #     f"INSERT INTO new_table SELECT * FROM {table.table_name}",
                #     f"DROP TABLE {table.table_name}",
                #     f"ALTER TABLE new_table RENAME TO {table.table_name}"
                # ]

            @staticmethod
            def insert(table_name: str, columns: str, values: str) -> str:
                """
                Insert a row into the specified table.

                :param table_name: The name of the table to be inserted.
                :type table_name: str
                :param columns: The columns to be inserted.
                :type columns: str
                :param values: The values to be inserted.
                :type values: str

                Example Implementation (SQLite):

                .. code-block:: python

                    return f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

                """
                pass
                # return f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

            @staticmethod
            def insert_or_update(table_name: str, columns: str, values: str) -> str:
                """
                Insert a row into the specified table or update it if it already exists.

                :param table_name: The name of the table to be inserted.
                :type table_name: str
                :param columns: The columns to be inserted, already been seperated by ','.
                :type columns: str
                :param values: The values to be inserted, already been seperated by ','.
                :type values: str

                Example Implementation (SQLite):

                .. code-block:: python

                    return f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({values})"

                """
                pass
                # return f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({values})"

            @staticmethod
            def update(table_name: str, columns: str, condition: str) -> str:
                """
                Update the specified table.

                :param table_name: The name of the table to be updated.
                :type table_name: str
                :param columns: The columns to be updated. Values are already in the format of 'column1=value1, column2=value2, ...', seperated by ','.
                :type columns: str
                :param condition: The condition of the update, in the general SQL format, generated by Exp.
                :type condition: str

                Example Implementation (SQLite):

                .. code-block:: python

                    return f"UPDATE {table_name} SET {columns} WHERE {condition}"

                """
                pass
                # return f"UPDATE {table_name} SET {columns} WHERE {condition}"

            @staticmethod
            def count(table_name: str, condition: str) -> str:
                """
                Count the number of rows in the specified table.

                :param table_name: The name of the table to be counted.
                :type table_name: str
                :param condition: The condition of the count, in the general SQL format, generated by Exp.
                :type condition: str

                Example Implementation (SQLite):

                .. code-block:: python

                    return f"SELECT COUNT(*) FROM {table_name} WHERE {condition}"

                """
                pass
                # return f"SELECT COUNT(*) FROM {table_name} WHERE {condition}"

            @staticmethod
            def query(
                table_name: str,
                selection: str,
                condition: str,
                db,
                limit: tuple[int] | None = None,
            ) -> str:
                """
                Query the specified table.

                :param table_name: The name of the table to be queried.
                :type table_name: str
                :param selection: The columns to be selected, seperated by ','.
                :type selection: str
                :param condition: The condition of the query, in the general SQL format, generated by Exp.
                :type condition: str
                :param db: The connection object of the database.
                :param limit: Limit the number of rows to be returned. (start, end)
                :type limit: tuple(int, int)

                Example Implementation (SQLite):

                .. code-block:: python

                    offset, n = ...
                    return f"SELECT {selection} FROM {table_name} WHERE {condition} LIMIT {offset}, {n}"

                """
                pass

            @staticmethod
            def delete(table_name: str, condition: str) -> str:
                """
                Delete the rows in specified table, which matches the condition.

                :param table_name: The name of the table to be deleted.
                :type table_name: str
                :param condition: The condition of the delete, in the general SQL format, generated by Exp.
                :type condition: str

                Example Implementation (SQLite):

                .. code-block:: python

                    return f"DELETE FROM {table_name} WHERE {condition}"
                """
                pass
                # return f"DELETE FROM {table_name} WHERE {condition}"

        @classmethod
        def get_all_tables(cls, conn: BaseDriver.Conn) -> List[str]:
            """
            Get all table's informations in the database.

            .. note:
                You can copy the implementation of this method directly.

            The default implementation is based on the `cls.gensql.get_all_tables()` method.

            :param conn: The connection object of the database.
            :type conn: BaseDriver.Conn

            :return: All table's informations in the database
            """
            cursor = conn.cursor()
            cursor.execute(cls.gensql.get_all_tables())
            return list(map(lambda x: x[0], cursor.fetchall()))

        @classmethod
        def get_all_columns(cls, conn: BaseDriver.Conn, table_name: str) -> List[str]:
            """
            Get all column's informations in the table.

            .. note:
                You can copy the implementation of this method directly.

            The default implementation is based on the `cls.gensql.get_all_columns(table_name)` method.

            :param conn: The connection object of the database.
            :type conn: BaseDriver.Conn
            :param table_name: The name of the table.
            :type table_name: str

            :return: All column's informations in the table.
            :rtype: List[str]. Each element is a list of `[column_name, column_type]`.
            """
            cursor = db.do(cls.gensql.get_all_columns(table_name))
            return list(map(lambda x: [x[1], x[2]], cursor.fetchall()))
        
        @classmethod
        def count_res(cls, db, table_name: str, condition: str) -> int:
            """
            Count the number of rows in the specified table.

            .. note:
                You can copy the implementation of this method directly.

            The default implementation is based on the `cls.gensql.count(table_name, condition)` method.

            :param db: The connection object of the database.
            :type db: BaseDriver.Conn
            :param table_name: The name of the table to be counted.
            :type table_name: str
            :param condition: The condition of the count, in the general SQL format, generated by Exp.
            :type condition: str

            :return: The number of rows in the specified table.
            :rtype: int
            """
            cursor = db.do(cls.gensql.count(table_name, condition))
            return cursor.fetchall()[0][0]

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

            .. note::
                I've provided a example implementation of this method, for SQLite.
                Look at the source code.

            Example Usage:

            .. code-block:: python

                TypeParser.parse(str)       # TEXT
                TypeParser.parse(int)       # INTEGER
                TypeParser.parse(float)     # REAL
                ...

            """
            supported_types = {
                str: 'TEXT',
                int: 'INTEGER',
                float: 'REAL',
                bool: 'BOOLEAN',
                bytes: 'BLOB'
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
            if isinstance(type_, str):    # custom type
                return type_

            # Not Supported
            raise Exception(f"Type `{str(type_)}` not supported.")

    @staticmethod
    def connect(db_name: str, **kwargs) -> BaseDriver.Conn:
        """
        Connect to the database.

        :param db_name: The name of the database to connect.
        :type db_name: str
        :param kwargs: The parameters of the connection. E.g., `host`, `port`, `user`, `password`, ...
        
        :return: The connection object of the database.
        :rtype: BaseDriver.Conn
        """
        pass
