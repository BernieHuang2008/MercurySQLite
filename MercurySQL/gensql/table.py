"""
MercurySQL.gensql.table
=======================
This file contains the `Table` class and related classes for handling tables & queries in the SQL database.

Classes
-------
- `Table`: Represents a table in the SQL database and provides methods for adding columns, deleting columns, inserting rows, and executing queries.
- `QueryResult`: Represents the result of a query and provides methods for accessing the query results.
"""

from typing import Any
from ..errors import *
from .exp import Exp


# ========== Class Decorations ==========
class Table:
    pass


class QueryResult:
    class QueryResultRow:
        pass


# ========== Classes ==========
class Table:
    """
    Represents a table in a SQL database. Can be created by `db.createTable()`.
    
    It provides methods for adding columns, deleting columns, inserting rows, and executing queries, etc.
    """

    def __init__(self, db, table_name: str):
        """
        Initialize a table object.

        :param db: The database object.
        :type db: DataBase
        :param table_name: The name of the table.
        :type table_name: str

        Example Usage:

        .. code-block:: python

            db = DataBase('test.db')
            table = db['test']

        How It Works:
            - gather all infomations of the table, including columns name and their types.
            - set `isEmpty` to True if the table doesn't have any columns. This variable will effect how the `newColumn()` method works.
        """
        self.db = db
        self.table_name = self.driver.APIs.reformat_table_name(table_name)
        self.driver = db.driver

        all_tables = self.driver.APIs.get_all_tables(self.db)
        self.isEmpty = table_name not in all_tables

        self._gather_info()

    def _gather_info(self):
        """
        [Helper] Gather all infomations of the table, including:
            - `columns`: list[str] .................. name of all columns
            - `columnsType`: dict[str, str] .......... the type of each column
        """
        if not self.isEmpty:
            self.column_info = self.driver.APIs.get_all_columns(
                self.db, self.table_name
            )
        else:
            self.column_info = []

        self.columns = list(map(lambda x: x[0], self.column_info))  # [name, type]
        self.columnsType = {
            self.column_info[i][0]: self.column_info[i][1]
            for i in range(len(self.column_info))
        }

    def __getitem__(self, key: str) -> Exp:
        """
        get a column from the table, mainly used to construct query.

        :param key: The name of the column.
        :type key: str

        :return: An Exp object.

        Example Usage:

        1. Construct a query expression.

        .. code-block:: python

            table = db['test']
            exp = table['id'] == 1
            res = table.select(exp)

        2. Get the definition of a column.

        .. code-block:: python

            table = db['test']
            print(table['id'])  # INTEGER PRIMARY KEY

        How It Works:
            - return an `Exp` object with `table` and `_str` attributes setted.
            - `table` is used to execute the query using `list(...)`, even if table not specified. **[NOT RECOMMENDED]**
            - `_str` is used to print the definition of a column using `str(...)`.
            - raise an Exception if column not exists.
        """
        key = self.driver.APIs.reformat_column_name(key)

        if key not in self.columns:
            raise NotExistsError(f"Column `{key}` not exists.")

        return Exp(key, table=self, _str=self.columnsType[key])

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Create a new column in the table.

        :param key: The name of the column.
        :type key: str
        :param value: The type of the column.
        :type value: Any. Can be single un-parsed type (e.g. `int`, `str(5)`, ...) OR a tuple in the form of `(type, options)`. (e.g. `(int, 'primary key', 'auto increment')`)

        Options in `value`:

        - **'primary key'** — Set the column as the primary key of the table.
        - **'auto increment'** — Set the column as an auto-incremented column.

        Example Usage:

        .. code-block:: python

            table = db['test']
            table['name'] = str
            table['id'] = int, 'primary key', 'auto increment'

        How It Works:
            - get options from `value` if it has parameters (Judge it by whether it's a tuple, so you can use it as the L3 of example showed).
            - Actually create the column, using `newColumn()` method.
        """
        key = self.driver.APIs.reformat_column_name(key)

        options = {
            "primary key": False,
            "auto increment": False,
        }

        if isinstance(value, tuple):
            # (type, options)
            for i in range(1, len(value)):
                options[value[i].lower()] = True
            value = value[0]

        self.newColumn(
            key,
            value,
            primaryKey=options["primary key"],
            autoIncrement=options["auto increment"],
            force=True,
        )

    def __delitem__(self, key: str) -> None:
        """
        Delete an existing column in this table.
        An Exception will be raised if column not exist.
        Same as `delColumn()`.

        :param key: The name of the column.
        :type key: str

        Example Usage:

        .. code-block:: python

            table = db['test']
            del table['name']  # same as table.delColumn('name')

        """
        key = self.driver.APIs.reformat_column_name(key)

        self.delColumn(key)

    def select(self, exp: Exp = None, selection: str = "*") -> QueryResult:
        """
        Select data from the table.

        :param exp: The query expression.
        :type exp: Exp
        :param selection: The columns to select, default is '*'(all columns).
        :type selection: str

        :return: A list of data.
        :rtype: list

        Example Usage:

        .. code-block:: python

            table = db['test']
            table.select(table['id'] == 1)  # select all columns where id = 1

        How It Works:
            - Construct a `QueryResult` object, which will execute the query whthin it's `QueryResult.__init__()` method.
            - return a `QueryResult` object with results.
        """
        if exp is None:
            exp = Exp(1, "=", 1)

        return QueryResult(self, exp, selection)

    def newColumn(
        self, name: str, type_: Any, force=False, primaryKey=False, autoIncrement=False
    ) -> None:
        """
        Add a new column to the table.

        :param name: The name of the column.
        :type name: str
        :param type_: The type of the column.
        :type type_: Any
        :param force: Allow to skip when processing an existing column.
        :type force: bool
        :param primaryKey: Whether the column is a primary key.
        :type primaryKey: bool
        :param autoIncrement: Whether the column is auto-incremented.
        :type autoIncrement: bool

        Example Usage:

        .. code-block:: python

            table = db['test']
            table.newColumn('name', str)
            table.newColumn('id', int, primaryKey=True)

        How It Works:
            - Create a new table with this column, if table is empty.
            - Add the column to an existing table.
            - Set as the `primary key` column if `primaryKey` is True.
            - Record its name and type in `self.columns` and `self.columnsType`.
        """
        name = self.driver.APIs.reformat_column_name(name)

        if name in self.columns:
            if not force:
                raise DuplicateError(f"Column `{name}` already exists.")
            else:
                return

        type_ = self.driver.TypeParser.parse(type_)

        if self.isEmpty:
            # create it first
            cmd = self.driver.APIs.gensql.create_table_if_not_exists(
                self.table_name,
                name,
                type_,
                primaryKey=primaryKey,
                autoIncrement=autoIncrement,
            )
            self.db.do(cmd)
            self.isEmpty = False
        else:
            cmd = self.driver.APIs.gensql.add_column(self.table_name, name, type_)
            self.db.do(cmd)

            if primaryKey:
                self.setPrimaryKey(name, type_)

        self.columns.append(name)
        self.columnsType[name] = type_

    def struct(
        self,
        columns: dict,
        skipError=True,
        primaryKey: str = None,
        autoIncrement=False,
        force=True,
    ) -> None:
        """
        Set the structure of the table.

        :param columns: The structure of the table.
        :type columns: dict
        :param skipError: Allow to skip when column exist and have the same type at the same time.
        :type skipError: bool
        :param primaryKey: The primary key of the table.
        :type primaryKey: str

        Example Usage:

        .. code-block:: python

            table = db['test']
            table.struct({
                'id': int,
                'name': str
            }, primaryKey='id')

        """

        # Warning: `force` will be removed in next big version
        skipError = skipError and force

        for name, type_ in columns.items():
            name = self.driver.APIs.reformat_column_name(name)

            type_origin = type_
            type_ = self.driver.TypeParser.parse(type_)
            isPrimaryKey = name == primaryKey

            if name in self.columns:
                if type_.lower() != self.columnsType[name].lower():
                    raise ConfilictError(
                        f"Column `{name}` with different types (`{self.columnsType[name]}`) already exists. While trying to add column `{name}` with type `{type_}`."
                    )
                elif not skipError:
                    raise DuplicateError(
                        f"Column `{name}` already exists. You can use `force=True` to avoid this error."
                    )
            else:
                self.newColumn(
                    name,
                    type_origin,
                    primaryKey=isPrimaryKey,
                    autoIncrement=autoIncrement,
                )

    def delColumn(self, name: str) -> None:
        name = self.driver.APIs.reformat_column_name(name)

        if name not in self.columns:
            # column not exist
            raise NotExistsError(f"Column `{name}` not exist!")
        elif len(self.columns) == 1:
            # the last column, delete the table instead
            self.db.deleteTable(self.table_name)
        else:
            # delete the column
            self.columns.remove(name)
            cmd = self.driver.APIs.gensql.drop_column(name)
            self.db.do(cmd)

    def setPrimaryKey(self, keyname: str, keytype: str) -> None:
        """
        Set a column as the primary key of the table.

        :param keyname: The name of the column.
        :type keyname: str
        :param keytype: The type of the column, been parsed by `TypeParser`.
        :type keytype: str

        Example Usage:

        .. code-block:: python

            table = db['test']
            table.setPrimaryKey('id')

        """
        keyname = self.driver.APIs.reformat_column_name(keyname)
        
        cmd = self.driver.APIs.gensql.set_primary_key(self, keyname, keytype)
        self.db.do(cmd)

    def insert(self, __auto=False, **kwargs) -> None:
        """
        Insert a row into the table.

        :param \_\_auto: Whether to update the row if it already exists.
        :type \_\_auto: bool
        :param \*\*kwargs: The data to insert.

        Example Usage:

        .. code-block:: python

            table = db['test']
            table.insert(id=1, name='Bernie', age=15, __auto=True)

        """
        # get keys and clean them
        keys = list(kwargs.keys())
        if "__auto" in keys:
            __auto = kwargs["__auto"]
            keys.remove("__auto")
        
        keys = list(map(self.driver.APIs.reformat_column_name, keys))

        columns = ", ".join(keys)
        values = ", ".join([self.driver.payload for _ in range(len(keys))])

        # Determine the SQL command based on the value of `__auto`
        if __auto:
            cmd = self.driver.APIs.gensql.insert_or_update(
                self.table_name, columns, values
            )
        else:
            cmd = self.driver.APIs.gensql.insert(self.table_name, columns, values)

        self.db.do(cmd, paras=[tuple(kwargs[k] for k in keys)])

    def update(self, exp: Exp, data: dict = {}, **kwargs) -> None:
        """
        Update the table.

        .. note:: We Recommend to use `(tb['id'] == 1).update(...)` then this function, for cleaner code style.

        .. warning::
           The argument of `Exp.update(...)` doesn't supports kwargs format (`name=bernie`). It only supports dict format (`{"name": "bernie"}`).
           We recommended to use 'dict format' in both `table.update` and `Exp.update`.

        ..

        :param exp: The query expression.
        :type exp: Exp
        :param data: The data to update.
        :type data: dict

        Example Usage:

        .. code-block:: python

            table = db['test']
            table.update(table['id'] == 1, name='Bernie', age=15)
            # OR
            (table['id'] == 1).update({"name": "Bernie", "age": 15})    # recommended

        """

        if not data:
            data = kwargs

        data = {self.driver.APIs.reformat_column_name(k): v for k, v in data.items()}

        columns = ", ".join([f"{key} = {self.driver.payload}" for key in data.keys()])
        values = tuple(data.values())

        condition, paras = exp.formula()

        cmd = self.driver.APIs.gensql.update(self.table_name, columns, condition)
        self.db.do(cmd, paras=[values + paras])


class QueryResult:
    """
    [Helper Class]
    The result of a query.

    Example Usage:

    .. code-block:: python

        res = table.select(exp)
        for row in res:
            print(row)

    """

    class QueryResultRow:
        """
        [Helper Class]
        Representing a single row of the query result.
        You can use QueryResult[i] to get it, and use it by `row.column_name`.

        Example Usage:

        .. code-block:: python

            res = table.select(exp)
            row = res[0]
            print(row.id)

        """

        def __init__(self, data: dict):
            self.data = data

        def __getitem__(self, __name: str) -> Any:
            """
            The main method of this class, used to get the value of a column.

            :param __name: The name of the column.
            :type __name: str

            :return: The value of the column.
            """
            data = object.__getattribute__(self, "data")
            if __name == "data":
                return data
            else:
                return data[__name]

        def __iter__(self):
            """
            Make it possible to iterate through.
            It will work as a `dict`.
            """
            return iter(self.data)

    def __init__(self, table: Table, exp: Exp, selection: str = "*"):
        values = exp.query(table, selection)
        keys = (
            table.columns
            if selection == "*"
            else list(map(lambda x: x.strip(), selection.split(",")))
        )
        self.data = [dict(zip(keys, row)) for row in values]

    def __getitem__(self, index: int) -> QueryResultRow:
        return self.QueryResultRow(self.data[index])

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)
