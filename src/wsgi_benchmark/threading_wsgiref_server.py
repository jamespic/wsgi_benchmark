from __future__ import absolute_import
from wsgiref.simple_server import make_server, WSGIServer
from SocketServer import ThreadingMixIn
from wsgi_benchmark.handlers import app

class ThreadingWSGIServer(WSGIServer, ThreadingMixIn):
    pass

if __name__ == '__main__':
    server = make_server('', 8765, app, server_class=ThreadingWSGIServer)
    server.serve_forever()
