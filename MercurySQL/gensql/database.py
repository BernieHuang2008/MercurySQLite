"""
Copyright (c) Bernie Huang 2023, all rights reserved.

MercurySQL.gensql.database
==========================
This file contains the DataBase class, and a tool function `set_driver` as well.

Classes
-------
- `DataBase`: Represents a SQL database and provides methods for creating tables, executing SQL commands, and retrieving table objects.

Methods
-------
- `set_driver`: Set the default driver for the `DataBase` class.
"""
from typing import List

from ..orm.command_queue import CommandQueue
from ..drivers import BaseDriver
from ..errors import *

from .table import Table


from ..drivers import sqlite


# ========== Class Decorations ==========
class DataBase:
    pass


# ========= Collect Infos =========
import os

real_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(real_path, "..", "VERSION"), encoding="utf-8") as f:
    __version__ = f.read().strip()


# ========= Tool Functions =========
default_driver = None


def set_driver(driver):
    """
    Set the default driver for the database, so you won't need to specify the driver for each DB every time.
    """
    global default_driver
    default_driver = driver


def check_version(version: str) -> bool:
    """
    Check whether the version is supported.

    :param version: The version to check.
    :type version: str

    :return: Whether the version is supported.
    :rtype: bool
    """
    cv = list(map(int, __version__.split(".")))  # current version
    dv = list(map(int, version.split(".")))  # driver version

    vdiff = [cv[i] - dv[i] for i in range(len(cv))]

    # major version
    if vdiff[0] != 0:
        return False
    # minor version (driver is older)
    if vdiff[1] > 0:
        return False

    return True


# ========== Classes ==========
class DataBase:
    """
    Select/Create/Connect a SQL database.

    The instance of this class represents a SQL database, and provides methods for creating tables, executing SQL, and retrieving table objects.
    """

    def __init__(self, db_name: str, driver=None, **kwargs):
        """
        Create a new database object.

        :param db_name: The name of the database.
        :type db_name: str

        Example Usage:

        .. code-block:: python

            db = DataBase('test.db')

        How It Works:
            - start a connection to the SQL database, using the driver specified by `driver` parameter or `set_driver()` method.
            - create a new `CommandQueue` to handle all SQL commands in this DB.
            - gather all infomations of the database, for further usages.
        """
        if driver is None:
            driver = default_driver

        if not issubclass(driver, BaseDriver):
            raise NotSpecifiedError("Driver not specified.")
        else:
            self.driver = driver

        if not check_version(driver.version):  # check version
            raise DriverIncompatibleError(driver.__name__, driver.version, __version__)

        # self.driver = driver()  # normal way
        # self.conn_pool = ConnPool(self.driver, db_name, **kwargs)  # connection pool
        self.cq = CommandQueue(driver, db_name, **kwargs)
        # self.conn = driver.connect(db_name, **kwargs)  # normal way
        # self.cursor = self.conn.cursor()

        self.info = {"name": db_name}

        self.template = None
        self.template_params = {}

        self._gather_info()

    def _gather_info(self):
        """
        [Helper]
        Gather all infomations of the database, including:
          - all tables
        """
        self.tables = self.driver.APIs.get_all_tables(self)
        self.tables = {tname: Table(self, tname) for tname in self.tables}

    def do(self, *sql: str, paras: List[tuple] = []):
        """
        Execute a sql command on the database.

        :param sql: The sql command(s).
        :type sql: str
        :param paras: The parameters for the sql command(s).
        :type paras: List[tuple]

        :return: The cursor of the database.
        :rtype: Driver.Cursor

        Example Usage:

        .. code-block:: python

            db = DataBase('test.db')
            db.do("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            db.do("INSERT INTO test (name) VALUES (?)", paras=[('Bernie',)])
            db.do(
                "SQL1",
                "SQL2",
                paras=[
                       (paras1, paras2),
                       (paras3, paras4)
                ])

        How It Works:
            - execute sql commands one by one, with parameters
            - commit after all commands are executed
        """
        # Recommended to use `db.do(sql1, sql2)` instead of `db.do([sql1, sql2])`.
        if isinstance(sql[0], list):
            sql = sql[0]

        if len(paras) < len(sql):
            paras += [()] * (len(sql) - len(paras))

        # start a new cursor
        # c = self.conn.cursor()    # normal way
        # c = self.conn_pool.get_cursor()   # connection pool
        c = self.cq.get_cursor()

        # for each sql command
        for i in range(len(sql)):
            cmd = sql[i].replace(
                "___!!!PAYLOAD!!!___", self.driver.payload
            )  # replace payload

            c.execute(cmd, paras[i])

        # commit changes
        # try:
            # self.conn.commit()    # normal way
            # self.conn_pool.commit()   # connection pool
        # except:
            # pass

        return c

    def setTemplate(self, template: dict, **kwargs) -> None:
        """
        Set the template, so new table's structure will be setted to this template.
        You can specifd the template by using `template=...` parameter into `db.createTable()` method.
        Or set it after the table is created, using `table.struct()`.

        :param template: The template to set.
        :type template: dict
        :param \*\*kwargs: The parameters for the template. E.g., `primaryKey='id'`.

        Example Usage:

        .. code-block:: python

            db = DataBase('test.db')
            db.setTemplate({
                'id': int,
                'name': str
            })
            table = db.createTable('test')

        """
        self.template = template
        self.template_params = kwargs

    def createTable(
        self, *table_names: str, force: bool = False, template=None
    ) -> Table:
        """
        create a table in the database.

        :param table_names: The name of the table.
        :type table_names: str
        :param force: Allow to return an existing table.
        :type force: bool

        :return: A Table object.
        :rtype: Table

        Example Usage:

        .. code-block:: python

            db = DataBase('test.db')
            table = db.createTable('test')

        How It Works:
            - create table(s) if not exists
            - if already exists, return the existing table(s) in a NEW `Table` Object.
            - if exists and `force` set to False, raise an Exception.
        """
        # using template in `self.template` if not specified
        if template is None:
            template = self.template

        tables = []
        already_exists = False

        for table_name in table_names:
            if table_name in self.tables:
                already_exists = True
                if not force:
                    raise DuplicateError(f"Table `{table_name}` already exists.")

            table = Table(self, table_name)

            # set template
            if not already_exists and template is not None:
                table.struct(template, **self.template_params)

            # must be executed after `_gather_into()`, because the following code will use a mapping between table name and table object
            self.tables[table_name] = table

            tables.append(table)

        return tables if len(tables) > 1 else tables[0]

    def __getitem__(self, key: str) -> Table:
        """
        Create / Choose a table from the database.

        :param key: The name of the table.
        :type key: str

        :return: A Table object.
        :rtype: Table

        Example Usage:

        .. code-block:: python

            db = DataBase('test.db')
            table = db['test']

        How It Works:
            - if exists, return the existing table (the OLD `Table` Object)
            - if not exists, create a new table by `createTable()`.

        .. note::
           The only difference between `__getitem__()` and `createTable()` is that `__getitem__()` will return the **OLD** `Table` Object if exists, while `createTable()` will return a **NEW** `Table` Object.

           **See the "How It Works" section in `createTable()` for more details.**
        """
        if key in self.tables:
            return self.tables[key]
        else:
            return self.createTable(key, force=True)

    def deleteTable(self, *table_names: str) -> None:
        """
        delete a table in the database.

        :param table_names: The name of the table.
        :type table_names: str

        Example Usage:

        .. code-block:: python

            db = DataBase('test.db')
            db.deleteTable('test')

        How It Works:
            - delete table(s) if exists
            - raise an Exception if not exists.
        """
        for table_name in table_names:
            if table_name not in self.tables:
                raise NotExistsError(f"Table `{table_name}` not exists.")

            cmd = self.driver.APIs.gensql.drop_table(table_name)
            self.do(cmd)

            del self.tables[table_name]

    def __delitem__(self, key: str) -> None:
        """
        Delete a table from the database, same as `deleteTable()`.

        :param key: The name of the table.
        :type key: str

        Example Usage:

        .. code-block:: python

            db = DataBase('test.db')
            del db['test']  # same as db.deleteTable('test')

        """
        self.deleteTable(key)

    # def __del__(self):    # connection pool
    #     """
    #     Close the connection when the object is deleted.
    #     """
    #     try:
    #         self.conn_pool.close_all()
    #         # self.conn.close()
    #     except AttributeError:
    #         # Not initialized
    #         pass
