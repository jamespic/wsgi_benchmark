from __future__ import absolute_import
from wsgiref.simple_server import make_server, WSGIServer
from SocketServer import ForkingMixIn
from wsgi_benchmark.handlers import app

class ForkingWSGIServer(WSGIServer, ForkingMixIn):
    pass

if __name__ == '__main__':
    server = make_server('', 8765, app, server_class=ForkingWSGIServer)
    server.serve_forever()
