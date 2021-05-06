import socket
import ssl
import pprint
import struct


class RemoteTrackpad(object):

    class CODES:
        CONNECT = b'\x1E'

        START_MOVE = b'\xF0'
        MOVE = b'\xF1'
        LEFTCLICK = b'\xF2'
        RIGHTCLICK = b'\xF3'

    def connect(self, host='127.0.0.1', port=11111):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Require a certificate from the server. We used a self-signed certificate
        # so here ca_certs must be the server certificate itself.
        tls_sock = ssl.wrap_socket(s, cert_reqs=ssl.CERT_NONE)

        tls_sock.connect((host,port))

        print(repr(tls_sock.getpeername()))
        print(tls_sock.cipher())
        print(pprint.pformat(tls_sock.getpeercert()))

        self.sock = tls_sock
        self.sock.sendall(self.CODES.CONNECT)


    def left_click(self):
        self.sock.sendall(self.CODES.LEFTCLICK)

    def right_click(self):
        self.sock.sendall(self.CODES.RIGHTCLICK)

    def move_cursor(self, x, y, start_move=False):
        # TODO invert y coordinate w.r.t. screen height
        self.sock.sendall((self.CODES.START_MOVE if start_move else self.CODES.MOVE) + struct.pack('@h', x) + struct.pack('@h', y))



if __name__ == '__main__':
    x = RemoteTrackpad()


