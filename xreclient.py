import socket
import ssl
import pprint
import struct

from utils import NetworkQueue


class RemoteTrackpad(object):

    class CODES:
        CONNECT = b'\x1E'

        START_MOVE = b'\xF0'
        MOVE = b'\xF1'
        LEFTCLICK = b'\xF2'
        RIGHTCLICK = b'\xF3'

    def __init__(self, update_ui_method) -> None:
        super().__init__()
        self.sock = None
        self.Q = None
        self.update_ui_method = update_ui_method

    def connect(self, host='127.0.0.1', port=11111):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)

        # Do not require a certificate from the server, visual end-to-end verification should be used
        tls_sock = ssl.wrap_socket(s, cert_reqs=ssl.CERT_NONE)

        tls_sock.connect((host,port))

        print(repr(tls_sock.getpeername()))
        print(tls_sock.cipher())
        print(pprint.pformat(tls_sock.getpeercert()))

        self.sock = tls_sock
        self.sock.sendall(self.CODES.CONNECT)
        self.Q = NetworkQueue(self.sock, self.update_ui_method)
        self.Q.start_thread()
        self.update_ui_method(True)

    def left_click(self):
        if self.Q:
            self.Q.add(self.CODES.LEFTCLICK)

    def right_click(self):
        if self.Q:
            self.Q.add(self.CODES.RIGHTCLICK)

    def move_cursor(self, x, y, start_move=False):
        if self.Q:
            self.Q.add((self.CODES.START_MOVE if start_move else self.CODES.MOVE) + struct.pack('@h', x) + struct.pack('@h', y))
