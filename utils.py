import logging
import sys
import threading
from time import sleep
from typing import Union

class NetworkQueue:
    def __init__(self, sock, update_ui_method, period=0.015) -> None:
        super().__init__()
        self.sock = sock
        self.ll = b''
        self.period = period
        self.lock = threading.Lock()
        self.T = None
        self.update_ui_method = update_ui_method
        self.data_available = threading.Event()
        self.moving = True

    def set_sock(self, sock):
        self.sock = sock

    def start_thread(self):
        self.T = threading.Thread(target=self.run, args=())
        self.T.start()

    def move_started(self):
        self.moving = True
        self.data_available.set()  # resume polling queue

    def move_ended(self):
        self.moving = False  # from now, flush queue and then wait

    def add(self, item: Union[bytes, bytearray]):
        if self.T is not None:
            with self.lock:
                self.ll += item

    def run(self):
        try:
            while True:
                sleep(self.period)
                if self.ll:
                    with self.lock:
                        l1 = self.ll
                        self.ll = b''
                    # sys.stdout.write(f'@{len(l1)}@')
                    self.sock.sendall(l1)
                else: # if queue is empty, let's wait
                    if not self.moving:
                        self.data_available.wait()

        except BaseException as e:
            logging.exception(e)
            logging.error('Remote host disconnected, please reconnect')
            self.update_ui_method(False)
            self.sock = None
        self.T = None
        self.ll = b'' # empty the queue, discarding all unsent data
        logging.info('Flush thread ended')
