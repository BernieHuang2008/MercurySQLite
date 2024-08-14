"""
This file offers the `CommandQueue` class, which is used to queue and execute commands in the MercurySQL package.

This is useful when you are working with multiple threads and want to execute commands in a specific order.
"""

import queue
import threading
import sys

FETCHALL = -1


class CommandQueue:
    def __init__(self, driver, db_name: str, **conn_ops):
        self.driver = driver
        self.conn_info = (db_name, conn_ops)

        self.queue = queue.Queue()

        # start the loop, starts to process the project now
        self.isRunning = True
        self.loop()

    def stop(self):
        self.isRunning = False

    def __del__(self):
        self.stop()

    def put(self, command):
        """
        Put a command into the queue.

        :param command: The command to put into the queue.
        :type command: Any
        """
        self.queue.put(command)

    def loop(self):
        """
        Loop through the queue and execute each command (in an new thread).
        When the queue is empty, the loop will wait for new commands.
        """

        # start a new thread
        def loop_thread():
            # start a new conn
            db_name, conn_ops = self.conn_info
            conn = self.driver.connect(db_name, **conn_ops)
            cursor = conn.cursor()

            while self.isRunning:
                try:
                    query, param, callback = self.queue.get()

                    cursor.execute(query, param)
                    conn.commit()
                    result = cursor.fetchall()

                    callback(result)
                except Exception as e:
                    print(e, file=sys.stderr)

                conn.commit()
                self.queue.task_done()
            
            cursor.close()
            conn.close()

        # Start a Daemon thread, which will be killed when the main thread is over.
        threading.Thread(target=loop_thread, daemon=True).start()

    def get_cursor(self):
        """
        Return a fake cursor that will transfer the command to the real cursor in seperate thread.

        :return: The cursor.
        :rtype: Cursor
        """

        return CQFakeCursor(self)


class CQFakeCursor:
    def __init__(self, cq):
        self.cq = cq
        self.event = threading.Event()

    def execute(self, query: str, param: tuple) -> None:
        """
        Execute a query.

        :param query: The query to execute.
        :type query: str
        :param param: The parameters for the query.
        :type param: tuple
        """
        def callback(result):
            self.result = result
            self.event.set()

        self.cq.put((query, param, callback))
        self.event.wait()  # wait

        return None

    def fetchall(self):
        """
        Fetch all results.

        :return: The results.
        :rtype: list
        """
        return self.result

    def fetchone(self):
        """
        Fetch one result.

        :return: The result.
        :rtype: Any
        """
        return self.result[0]

    def fetchmany(self, size: int):
        """
        Fetch a specific number of results.

        :param size: The number of results to fetch.
        :type size: int
        """
        return self.result[:size]
