import asyncore
import socket
import sys
import time


class PingPongHandler(asyncore.dispatcher):
    received = ''
    write_time = None
    buff = 'PONG'

    def handle_read(self):
        self.received += self.recv(4)
        if len(self.received) >= 4:
            if self.received[:4] == 'PING':
                self.write_time = time.time() + 1.0
            else:
                self.close()

    def readable(self):
        return self.write_time is None

    def writable(self):
        return self.write_time is not None and self.write_time < time.time()

    def handle_write(self):
        sent = self.send(self.buff)
        self.buff = self.buff[sent:]
        if not self.buff:
            self.close()


class PingPongServer(asyncore.dispatcher):

    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            PingPongHandler(sock)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 5645
    server = PingPongServer(port)
    asyncore.loop(0.1)
