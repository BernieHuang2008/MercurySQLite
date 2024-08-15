"""
MercurySQL.gensql.exp
=====================
This file offers the `Exp` class, which is used to construct complex query expressions for the MercurySQL package.

Classes
-------
- `BasicExp`: Base class for basic expressions.
- `Exp`: Class for constructing complex query expressions.
"""

from typing import Any, Union, Tuple

from ..errors import *


# ========= Class Decorations =========
class BasicExp:
    pass


class Exp(BasicExp):
    pass


# ========= Classes =========
class BasicExp:
    def __init__(self, exp1, oper="", exp2=None):
        self.exp1 = exp1
        self.oper = oper
        self.exp2 = exp2
        self._formula = ("", ())

        self.gen_formula()

    @staticmethod
    def convert(value: Any) -> Tuple[str, tuple]:
        """
        Convert value into a form that can be used in a SQL query.

        :param value: The value to convert.
        :type value: Any

        :return: The converted value in the form of `(sql_command, paras)`.
        :rtype: Tuple[str, tuple]

        Example Usage:

        .. code-block:: python

            BasicExp.convert(1)                 # ('?', (1,))
            BasicExp.convert('Bernie')          # ('?', ('Bernie',))
            BasicExp.convert(None)              # ('', ())
            BasicExp.convert(Exp('id') == 1)    # ('(id = ?)', (1,))
            ...

        """
        if isinstance(value, BasicExp):
            formula, paras = value.formula()
        elif value is None:
            formula, paras = "", ()
        else:
            formula, paras = "___!!!PAYLOAD!!!___", (value,)

        return formula, paras

    def gen_formula(self) -> None:
        """
        [Helper] Generate the formula of the expression.

        .. note :: You can also construct a formula by yourself, just set the `_formula` attribute to a tuple in the form of `(sql_command, paras)`.
        """
        if self.oper == "":
            self._formula = self.exp1, ()
        else:
            exp1 = BasicExp.convert(self.exp1)
            exp2 = BasicExp.convert(self.exp2)

            self._formula = f"({exp1[0]} {self.oper} {exp2[0]})", tuple(
                exp1[1] + exp2[1]
            )

    def formula(self) -> Tuple[str, tuple]:
        """
        Return the formula of the expression in the form of (sql_command, paras).
        """
        return self._formula


class Exp(BasicExp):
    def __init__(self, o1, op="", o2="", **kwargs):
        """
        Acceptable addition attributes:
        - table: Table ...................... the table to search
        - _str: str ......................... the string to show when print the object
        """
        super().__init__(o1, op, o2)

        self.table = kwargs.get("table", None)
        self._str = kwargs.get("_str", "<MercurySQL.core.Exp object>")
        self.result = None

        if isinstance(o1, Exp):
            self.table = self.table or o1.table
        if isinstance(o2, Exp):
            self.table = self.table or o2.table

    def __eq__(self, __value: Union[Exp, int, str]) -> Exp:
        return Exp(self, "=", __value)

    def __ne__(self, __value: Union[Exp, int, str]) -> Exp:
        return Exp(self, "<>", __value)

    def __lt__(self, __value: Union[Exp, int, str]) -> Exp:
        return Exp(self, "<", __value)

    def __le__(self, __value: Union[Exp, int, str]) -> Exp:
        return Exp(self, "<=", __value)

    def __gt__(self, __value: Union[Exp, int, str]) -> Exp:
        return Exp(self, ">", __value)

    def __ge__(self, __value: Union[Exp, int, str]) -> Exp:
        return Exp(self, ">=", __value)

    def between(
        self, __value1: Union[Exp, int, str], __value2: Union[Exp, int, str]
    ) -> Exp:
        # construct a new Exp object manually: set the `_formula` attribute to `(sql, paras)`.
        res = Exp(self, "BETWEEN", __value1)

        exp1 = res.formula()
        exp3 = BasicExp.convert(__value2)

        # set the `_formula` attribute.
        res._formula = f"({exp1[0]} AND {exp3[0]})", tuple(exp1[1] + exp3[1])

        return res

    def in_(self, __value: Union[list, tuple, set]) -> Exp:
        return Exp(self, "IN", str(tuple(__value)))

    def like(self, __value: str) -> Exp:
        return Exp(self, "LIKE", __value)

    def __and__(self, __value: Union[Exp, int, str]) -> Exp:
        return Exp(self, "AND", __value)

    def __or__(self, __value: Union[Exp, int, str]) -> Exp:
        return Exp(self, "OR", __value)

    def __invert__(self) -> Union[Exp, int, str]:
        return Exp("", "NOT", self)

    def query(self, table=None, select="*") -> list:
        """
        Execute query.
        """
        self.table = table or self.table

        if self.table is None:
            raise NotSpecifiedError("Table not specified.")
        
        self.driver = self.table.db.driver

        condition, paras = self.formula()

        cmd = self.driver.APIs.gensql.query(self.table.table_name, select, condition, self.table.db)
        res = self.table.db.do(cmd, paras=[paras])
        return res.fetchall()

    def delete(self, table=None) -> None:
        """
        Execute delete.
        """
        self.table = table or self.table

        if self.table is None:
            raise NotSpecifiedError("Table not specified.")
        
        self.driver = self.table.db.driver

        condition, paras = self.formula()

        cmd = self.driver.APIs.gensql.delete(self.table.table_name, condition)
        self.table.db.do(cmd, paras=[paras])


    def update(self, data, /, table=None) -> None:
        """
        Execute update.
        """
        self.table = table or self.table

        self.table.update(self, data)


    def __iter__(self):
        """
        use magic method `__iter__` to search.
        """
        if self.result is None:
            if self.table is None:
                raise NotSpecifiedError("Table not specified.")
            
            data = self.query()
            keys = self.table.columns
            self.result = [dict(zip(keys, row)) for row in data]

        return iter(self.result)

    def __str__(self):
        return self._str
