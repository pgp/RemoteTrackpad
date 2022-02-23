import hashlib
import socket
import ssl
import logging
import struct

from sslmasterkey import get_ssl_master_key
from utils import NetworkQueue


class RemoteTrackpad(object):

    class CODES:
        CONNECT = b'\x1E\x21\x00'

        START_MOVE = b'\xF0'
        MOVE = b'\xF1'
        LEFTCLICK = b'\xF2'
        RIGHTCLICK = b'\xF3'

        LEFTDOWN = b'\xF4'
        LEFTUP = b'\xF5'
        RIGHTDOWN = b'\xF6'
        RIGHTUP = b'\xF7'

    def __init__(self, update_ui_method, hv_method) -> None:
        super().__init__()
        self.sock = None
        self.plain_sock = None
        self.Q = None
        self.update_ui_method = update_ui_method
        self.hv_method = hv_method

    def disconnect(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.plain_sock.shutdown(socket.SHUT_RDWR)
        except:
            pass
        logging.info('Disconnected')
        self.sock = None
        self.plain_sock = None
        self.update_ui_method(False)

    def connect(self, host='127.0.0.1', port=11111):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)

        self.plain_sock = s.dup() # we don't want to lose access to the plain TCP socket, since wrap_socket seems to close
        # the original one after embedding it

        # Do not require a certificate from the server, visual end-to-end verification should be used
        tls_sock = ssl.wrap_socket(s, cert_reqs=ssl.CERT_NONE)

        tls_sock.connect((host,port))

        logging.info(repr(tls_sock.getpeername()))
        logging.info(tls_sock.cipher())
        sha_ = hashlib.sha256(get_ssl_master_key(tls_sock))
        logging.info(f"SHA256 of this session's master secret:\n{sha_.hexdigest()}")

        self.hv_method(sha_.digest())

        self.sock = tls_sock
        self.sock.sendall(self.CODES.CONNECT)
        self.Q = NetworkQueue(self.sock, self.update_ui_method)
        self.Q.start_thread()
        self.update_ui_method(True)

    def mouse_buttons(self, code):
        if self.Q:
            self.Q.add(code)

    def move_cursor(self, x, y, start_move=False):
        if self.Q:
            self.Q.add((self.CODES.START_MOVE if start_move else self.CODES.MOVE) + struct.pack('@h', x) + struct.pack('@h', y))
