from ..errors import db_connect as dbc_errors

import threading


class ConnPoolRef:
    def __init__(self, thread: threading.Thread, conn, cursor, cleanup: callable):
        self.thread = thread
        self.conn = conn
        self.cursor = cursor
        self.cleanup = cleanup

    def __del__(self):
        self.cleanup()


class ConnPool:
    def __init__(self, driver, db_name: str, **conn_ops):
        self.driver = driver
        self.conn_info = (db_name, conn_ops)
        self.pool = {}

    def __del__(self):
        if len(self.pool) > 0:
            self.close()
            raise dbc_errors.connection_pool.ConnPoolNotClosedError(
                "The connection pool is not fully closed. Automatically closed all connections for you."
            )

    def _new_conn(self):
        """
        [Private] Create a new connection

        .. warning::
            THIS IS A PRIVATE METHOD, DO NOT CALL IT DIRECTLY OR IT WILL CAUSE UNEXPECTED BEHAVIOR
        """
        db_aname, conn_ops = self.conn_info
        conn = self.driver.connect(db_aname, **conn_ops)
        return conn

    def _create_conn(self, thread: threading.Thread):
        """
        [Private] Create a new connection for the target thread, and add it to the pool

        .. warning::
            THIS IS A PRIVATE METHOD, DO NOT CALL IT DIRECTLY OR IT WILL CAUSE UNEXPECTED BEHAVIOR
        """
        # ensure the id is unique and predictable
        conn_id = id(thread)

        conn = self._new_conn()
        cursor = conn.cursor()

        # TODO: We can't close the connection in this way.
        #       Because the conn is created in the 'Target Thread', while the _remove_conn
        #       method will be called in the 'Monitor Thread' when 'Target Thread' is over.
        #       So the conn can only be closed in the 'Monitor Thread', which is not allow-
        #       ed in sqlite3.
        #       I've tried the `threading.local()`, but its also executed in the Main thread.
        self.pool[conn_id] = ConnPoolRef(
            thread, conn, cursor, lambda: self._remove_conn(conn_id)
        )
        t_local = threading.local()
        t_local.conn_ref = self.pool[conn_id]

    def _remove_conn(self, conn_id):
        """
        [Private] Remove the connection from the pool

        .. warning::
            THIS IS A PRIVATE METHOD, DO NOT CALL IT DIRECTLY OR IT WILL CAUSE UNEXPECTED BEHAVIOR
        """
        ref = self.pool.pop(conn_id)
        ref.conn.close()

    def get_ref(self) -> ConnPoolRef:
        """
        Get the ConnPoolRef object for the current thread.
        Create a new connection if the current thread is not in the pool.

        :return: The ConnPoolRef object
        :rtype: ConnPoolRef
        """
        thread = threading.current_thread()
        conn_id = id(thread)

        if conn_id not in self.pool:
            self._create_conn(thread)

        return self.pool[conn_id]

    def get_conn(self):
        """
        Get the connection object for the current thread
        Create a new connection if the current thread is not in the pool.
        """
        return self.get_ref().conn

    def get_cursor(self):
        """
        Get the cursor object for the current thread
        Create a new connection if the current thread is not in the pool.
        """
        return self.get_ref().cursor
    
    def commit(self):
        """
        Commit all the current thread's connections
        """
        conn = self.get_conn()
        conn.commit()

    def close_all(self):
        """
        Close all the connections in the pool
        """
        for conn_id in list(self.pool.keys()):
            self._remove_conn(conn_id)
