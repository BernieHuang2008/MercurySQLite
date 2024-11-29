"""
MercurySQLite
=============

A Pythonic wrapper for the built-in sqlite3 library.

This package provides classes for interacting with a SQLite database, including:

- DataBase: Represents a SQLite database and provides methods for creating tables, executing SQL commands, and retrieving table objects.

- Table: Represents a table in the SQLite database and provides methods for adding columns, deleting columns, inserting rows, and executing queries.

- Exp: Represents a query expression that can be used to construct complex queries.

Please refer to the individual class documentation for more details.
"""

from .gensql import DataBase, Table, set_driver
from . import drivers

class SQL:
    """Wrap everything together"""
    DataBase = DataBase
    Table = Table
    set_driver = set_driver
    drivers = drivers
