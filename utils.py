import logging
import threading
from time import sleep
from typing import Union


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class NetworkQueue:
    def __init__(self, sock, update_ui_method, period=0.015) -> None:
        super().__init__()
        self.sock = sock
        self.ll = []
        self.period = period
        self.lock = threading.Lock()
        self.T = None
        self.update_ui_method = update_ui_method

    def set_sock(self, sock):
        self.sock = sock

    def start_thread(self):
        self.T = threading.Thread(target=self.run, args=())
        self.T.start()

    def add(self, item: Union[bytes, bytearray]):
        if self.T is not None:
            with self.lock:
                self.ll.append(item)

    def run(self):
        try:
            while True:
                sleep(self.period)
                if self.ll:
                    with self.lock:
                        l1 = self.ll
                        self.ll = []
                    for x in chunks(l1, 100):
                        self.sock.sendall(b''.join(x))
        except BaseException as e:
            logging.exception(e)
            logging.error('Remote host disconnected, please reconnect')
            self.update_ui_method(False)
            self.sock = None
        self.T = None
        self.ll = [] # empty the queue, discarding all unsent data
        logging.info('Flush thread ended')
