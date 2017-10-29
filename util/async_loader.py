# encoding: utf8

from direct.stdpy import thread
from direct.stdpy import threading
import Queue
import logging

__author__ = 'Leon'


class AsyncLoader(threading.Thread):
    def __init__(self, queue_size=128):
        threading.Thread.__init__(self)
        self._queue = Queue.Queue(queue_size)
        self._exit_flag = False
        self._destroyed = False

    def __del__(self):
        assert self._destroyed

    def run(self):
        while True:
            if self._exit_flag:
                break
            job = self._queue.get()
            try:
                job[0](*job[1])
            except Exception, e:
                import traceback
                logging.error('exception %s, %s', e, traceback.format_exc())
                break

    def add_job(self, fn, args=[]):
        assert not self._destroyed
        assert isinstance(args, list)
        self._queue.put((fn, args))

    def destroy(self):
        self._destroyed = True
        logging.warn("waiting for unfinished tasks to be done")
        self._queue.join()

