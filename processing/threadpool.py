import multiprocessing
import queue
import threading


class Threadpool(object):
    def __init__(self, thread_count=multiprocessing.cpu_count()):
        self.__q = queue.Queue()
        self.__thread_count = thread_count
        self.__threads = []

    def add_work(self, item, *args):
        self.__q.put([item, *args])

    def start_work(self):
        for _ in range(self.__thread_count):
            t = threading.Thread(target=self.__worker)
            t.start()
            self.__threads.append(t)

        self.__q.join()
        for _ in range(self.__thread_count):
            self.__q.put(None)

        for t in self.__threads:
            t.join()

    def __worker(self):
        while True:
            item = self.__q.get()
            if item is None:
                break
            fnc = item[0]
            args = item[1:]
            fnc(args)
            self.__q.task_done()
